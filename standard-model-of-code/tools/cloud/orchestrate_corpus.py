#!/usr/bin/env python3
"""
Corpus Orchestrator for Cloud Execution

Manages the entire corpus run with:
- Parallel job submission to GCP
- Progress monitoring
- Auto-retry for failures
- Auto-replacement for persistent failures
- Results aggregation
- Live dashboard

Usage:
    python3 tools/cloud/orchestrate_corpus.py corpus_999.yaml \
        --gcs-bucket elements-archive-2026 \
        --parallelism 50 \
        --mode batch  # or 'cloudrun' or 'local'
"""

import os
import sys
import json
import yaml
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

try:
    from google.cloud import storage, batch_v1
    HAS_GCP = True
except ImportError:
    HAS_GCP = False


@dataclass
class RepoStatus:
    """Status tracking for a single repo."""
    name: str
    url: str
    ref: str
    language: str
    status: str = "pending"  # pending, running, success, failed, timeout, replaced
    attempts: int = 0
    job_id: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    metrics: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    replacement_for: Optional[str] = None


@dataclass
class CorpusRun:
    """State for entire corpus run."""
    corpus_id: str
    started_at: str
    gcs_bucket: str
    gcs_prefix: str
    repos: Dict[str, RepoStatus] = field(default_factory=dict)
    replacements: Dict[str, str] = field(default_factory=dict)  # failed -> replacement
    completed_at: Optional[str] = None

    @property
    def pending(self) -> List[RepoStatus]:
        return [r for r in self.repos.values() if r.status == "pending"]

    @property
    def running(self) -> List[RepoStatus]:
        return [r for r in self.repos.values() if r.status == "running"]

    @property
    def succeeded(self) -> List[RepoStatus]:
        return [r for r in self.repos.values() if r.status == "success"]

    @property
    def failed(self) -> List[RepoStatus]:
        return [r for r in self.repos.values() if r.status in ("failed", "timeout")]

    def summary(self) -> str:
        total = len(self.repos)
        return (f"Total: {total} | "
                f"✅ {len(self.succeeded)} | "
                f"🔄 {len(self.running)} | "
                f"⏳ {len(self.pending)} | "
                f"❌ {len(self.failed)}")


class CorpusOrchestrator:
    """Orchestrates corpus analysis across cloud infrastructure."""

    # Replacement repos by language (fallbacks when a repo fails persistently)
    REPLACEMENT_REPOS = {
        "python": [
            {"name": "click", "url": "https://github.com/pallets/click", "ref": "main"},
            {"name": "requests", "url": "https://github.com/psf/requests", "ref": "main"},
            {"name": "pendulum", "url": "https://github.com/sdispater/pendulum", "ref": "master"},
        ],
        "typescript": [
            {"name": "dayjs", "url": "https://github.com/iamkun/dayjs", "ref": "dev"},
            {"name": "zustand", "url": "https://github.com/pmndrs/zustand", "ref": "main"},
        ],
        "javascript": [
            {"name": "axios", "url": "https://github.com/axios/axios", "ref": "v1.x"},
            {"name": "moment", "url": "https://github.com/moment/moment", "ref": "develop"},
        ],
        "go": [
            {"name": "viper", "url": "https://github.com/spf13/viper", "ref": "master"},
            {"name": "logrus", "url": "https://github.com/sirupsen/logrus", "ref": "master"},
        ],
        "rust": [
            {"name": "clap", "url": "https://github.com/clap-rs/clap", "ref": "master"},
            {"name": "tokio", "url": "https://github.com/tokio-rs/tokio", "ref": "master"},
        ],
        "java": [
            {"name": "junit5", "url": "https://github.com/junit-team/junit5", "ref": "main"},
            {"name": "mockito", "url": "https://github.com/mockito/mockito", "ref": "main"},
        ],
    }

    def __init__(
        self,
        corpus_path: str,
        gcs_bucket: str,
        gcs_prefix: str = "corpus_999",
        parallelism: int = 50,
        max_retries: int = 3,
        timeout_seconds: int = 900,
        mode: str = "local",  # local, batch, cloudrun
    ):
        self.corpus_path = Path(corpus_path)
        self.gcs_bucket = gcs_bucket
        self.gcs_prefix = gcs_prefix
        self.parallelism = parallelism
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.mode = mode

        # Load corpus
        with open(corpus_path) as f:
            self.corpus_data = yaml.safe_load(f)

        # Initialize run state
        corpus_id = f"{self.corpus_data.get('corpus_id', 'corpus')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.run = CorpusRun(
            corpus_id=corpus_id,
            started_at=datetime.now(timezone.utc).isoformat(),
            gcs_bucket=gcs_bucket,
            gcs_prefix=f"{gcs_prefix}/{corpus_id}",
        )

        # Populate repos
        for repo in self.corpus_data.get("repos", []):
            self.run.repos[repo["name"]] = RepoStatus(
                name=repo["name"],
                url=repo["url"],
                ref=str(repo.get("ref", "main")),  # Ensure string
                language=repo.get("language", "unknown"),
            )

        print(f"Loaded {len(self.run.repos)} repos from {corpus_path}")

    def execute(self) -> CorpusRun:
        """Execute the full corpus run."""
        print(f"\n{'='*70}")
        print(f"CORPUS RUN: {self.run.corpus_id}")
        print(f"Mode: {self.mode} | Parallelism: {self.parallelism}")
        print(f"GCS: gs://{self.gcs_bucket}/{self.run.gcs_prefix}/")
        print(f"{'='*70}\n")

        if self.mode == "local":
            self._execute_local()
        elif self.mode == "batch":
            self._execute_gcp_batch()
        elif self.mode == "cloudrun":
            self._execute_cloud_run()
        else:
            raise ValueError(f"Unknown mode: {self.mode}")

        self.run.completed_at = datetime.now(timezone.utc).isoformat()
        self._save_final_results()

        return self.run

    def _execute_local(self):
        """Execute repos locally with thread pool."""
        print(f"[LOCAL] Starting with {self.parallelism} parallel workers")

        with ThreadPoolExecutor(max_workers=self.parallelism) as executor:
            # Submit initial batch
            futures = {}
            for repo in self.run.pending[:self.parallelism]:
                future = executor.submit(self._run_single_repo_local, repo)
                futures[future] = repo
                repo.status = "running"
                repo.started_at = datetime.now(timezone.utc).isoformat()

            # Process as they complete
            while futures or self.run.pending:
                # Wait for any completion
                for future in as_completed(futures, timeout=60):
                    repo = futures.pop(future)
                    try:
                        result = future.result()
                        self._handle_result(repo, result)
                    except Exception as e:
                        repo.status = "failed"
                        repo.errors.append(str(e))

                    # Submit next pending
                    remaining_pending = self.run.pending
                    if remaining_pending:
                        next_repo = remaining_pending[0]
                        future = executor.submit(self._run_single_repo_local, next_repo)
                        futures[future] = next_repo
                        next_repo.status = "running"
                        next_repo.started_at = datetime.now(timezone.utc).isoformat()

                # Print progress
                print(f"\r[PROGRESS] {self.run.summary()}", end="", flush=True)

                if not futures and not self.run.pending:
                    break

        print(f"\n[COMPLETE] {self.run.summary()}")

    def _run_single_repo_local(self, repo: RepoStatus) -> Dict[str, Any]:
        """Run single repo analysis locally."""
        from tools.cloud.run_single_repo import RepoAnalyzer

        analyzer = RepoAnalyzer(
            repo_url=repo.url,
            repo_ref=repo.ref,
            repo_name=repo.name,
            output_dir=f"/tmp/corpus/{self.run.corpus_id}",
            max_retries=self.max_retries,
            timeout_seconds=self.timeout_seconds,
            gcs_bucket=self.gcs_bucket,
            gcs_prefix=self.run.gcs_prefix,
        )

        return analyzer.run()

    def _handle_result(self, repo: RepoStatus, result: Dict[str, Any]):
        """Handle result from completed repo analysis."""
        repo.completed_at = datetime.now(timezone.utc).isoformat()
        repo.duration_seconds = result.get("duration_seconds")
        repo.attempts = result.get("retries", 0) + 1

        if result["status"] == "success":
            repo.status = "success"
            repo.metrics = result.get("metrics")
        elif result["status"] == "timeout":
            repo.status = "timeout"
            repo.errors = result.get("errors", [])
            self._try_replacement(repo)
        else:
            repo.status = "failed"
            repo.errors = result.get("errors", [])
            self._try_replacement(repo)

    def _try_replacement(self, failed_repo: RepoStatus):
        """Try to replace a persistently failing repo."""
        replacements = self.REPLACEMENT_REPOS.get(failed_repo.language, [])

        for replacement in replacements:
            if replacement["name"] not in self.run.repos and \
               replacement["name"] not in self.run.replacements.values():
                # Add replacement
                new_repo = RepoStatus(
                    name=replacement["name"],
                    url=replacement["url"],
                    ref=replacement["ref"],
                    language=failed_repo.language,
                    replacement_for=failed_repo.name,
                )
                self.run.repos[replacement["name"]] = new_repo
                self.run.replacements[failed_repo.name] = replacement["name"]
                print(f"\n[REPLACE] {failed_repo.name} → {replacement['name']}")
                return

        print(f"\n[NO REPLACEMENT] {failed_repo.name} ({failed_repo.language})")

    def _execute_gcp_batch(self):
        """Execute using GCP Batch API."""
        if not HAS_GCP:
            raise ImportError("google-cloud-batch not installed")

        # TODO: Implement GCP Batch submission
        print("[BATCH] GCP Batch execution not yet implemented")
        print("[BATCH] Falling back to local execution")
        self._execute_local()

    def _execute_cloud_run(self):
        """Execute using Cloud Run Jobs."""
        if not HAS_GCP:
            raise ImportError("google-cloud-run not installed")

        # TODO: Implement Cloud Run Jobs submission
        print("[CLOUDRUN] Cloud Run execution not yet implemented")
        print("[CLOUDRUN] Falling back to local execution")
        self._execute_local()

    def _save_final_results(self):
        """Save aggregated results locally and to GCS."""
        results = {
            "corpus_id": self.run.corpus_id,
            "started_at": self.run.started_at,
            "completed_at": self.run.completed_at,
            "summary": {
                "total": len(self.run.repos),
                "success": len(self.run.succeeded),
                "failed": len(self.run.failed),
                "replacements": len(self.run.replacements),
            },
            "repos": {name: asdict(repo) for name, repo in self.run.repos.items()},
            "replacements": self.run.replacements,
        }

        # Local save
        local_path = Path(f"artifacts/atom-research/{self.run.corpus_id}")
        local_path.mkdir(parents=True, exist_ok=True)

        with open(local_path / "corpus_results.json", "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n[SAVED] {local_path / 'corpus_results.json'}")

        # GCS save
        if HAS_GCP:
            try:
                client = storage.Client()
                bucket = client.bucket(self.gcs_bucket)
                blob = bucket.blob(f"{self.run.gcs_prefix}/corpus_results.json")
                blob.upload_from_string(
                    json.dumps(results, indent=2),
                    content_type="application/json"
                )
                print(f"[GCS] gs://{self.gcs_bucket}/{self.run.gcs_prefix}/corpus_results.json")
            except Exception as e:
                print(f"[GCS ERROR] {e}")


def main():
    parser = argparse.ArgumentParser(description="Orchestrate corpus analysis")
    parser.add_argument("corpus", help="Path to corpus YAML file")
    parser.add_argument("--gcs-bucket", default="elements-archive-2026",
                        help="GCS bucket for results")
    parser.add_argument("--gcs-prefix", default="corpus_999",
                        help="GCS prefix path")
    parser.add_argument("--parallelism", type=int, default=10,
                        help="Number of parallel jobs")
    parser.add_argument("--max-retries", type=int, default=3,
                        help="Max retries per repo")
    parser.add_argument("--timeout", type=int, default=900,
                        help="Timeout in seconds per repo")
    parser.add_argument("--mode", choices=["local", "batch", "cloudrun"],
                        default="local", help="Execution mode")

    args = parser.parse_args()

    orchestrator = CorpusOrchestrator(
        corpus_path=args.corpus,
        gcs_bucket=args.gcs_bucket,
        gcs_prefix=args.gcs_prefix,
        parallelism=args.parallelism,
        max_retries=args.max_retries,
        timeout_seconds=args.timeout,
        mode=args.mode,
    )

    run = orchestrator.execute()

    # Exit code
    success_rate = len(run.succeeded) / len(run.repos) if run.repos else 0
    if success_rate >= 0.9:
        print(f"\n✅ CORPUS COMPLETE: {success_rate:.1%} success rate")
        sys.exit(0)
    else:
        print(f"\n⚠️ CORPUS INCOMPLETE: {success_rate:.1%} success rate")
        sys.exit(1)


if __name__ == "__main__":
    main()
