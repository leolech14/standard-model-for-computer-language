#!/usr/bin/env python3
"""
Single Repo Cloud Runner

Analyzes one repository with full error handling, timeouts, and retry logic.
Designed to run as a Cloud Run Job or GCP Batch task.

Environment Variables:
    REPO_URL: Git URL to clone
    REPO_REF: Branch/tag/SHA to checkout
    REPO_NAME: Name for output files
    GCS_BUCKET: Bucket for results (e.g., elements-archive-2026)
    GCS_PREFIX: Prefix path in bucket
    MAX_RETRIES: Number of retry attempts (default: 3)
    TIMEOUT_SECONDS: Analysis timeout (default: 900)
"""

import os
import sys
import json
import time
import shutil
import hashlib
import subprocess
import traceback
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# Optional GCS upload
try:
    from google.cloud import storage
    HAS_GCS = True
except ImportError:
    HAS_GCS = False


class RepoAnalyzer:
    """Robust single-repo analyzer with retry and error handling."""

    def __init__(
        self,
        repo_url: str,
        repo_ref: str,
        repo_name: str,
        output_dir: str = "/tmp/collider_output",
        max_retries: int = 3,
        timeout_seconds: int = 900,
        gcs_bucket: Optional[str] = None,
        gcs_prefix: str = "corpus_results"
    ):
        self.repo_url = repo_url
        self.repo_ref = repo_ref
        self.repo_name = repo_name
        self.output_dir = Path(output_dir)
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.gcs_bucket = gcs_bucket
        self.gcs_prefix = gcs_prefix

        self.clone_dir = Path(f"/tmp/repos/{repo_name}")
        self.result: Dict[str, Any] = {
            "name": repo_name,
            "url": repo_url,
            "ref": repo_ref,
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "duration_seconds": None,
            "retries": 0,
            "errors": [],
        }

    def run(self) -> Dict[str, Any]:
        """Execute analysis with full retry logic."""
        self.result["started_at"] = datetime.now(timezone.utc).isoformat()

        for attempt in range(1, self.max_retries + 1):
            self.result["retries"] = attempt - 1

            try:
                print(f"\n{'='*60}")
                print(f"[{self.repo_name}] Attempt {attempt}/{self.max_retries}")
                print(f"{'='*60}")

                # Clean previous attempt
                self._cleanup()

                # Clone
                if not self._clone():
                    continue

                # Analyze
                if not self._analyze():
                    continue

                # Extract metrics
                if not self._extract_metrics():
                    continue

                # Upload to GCS
                if self.gcs_bucket:
                    self._upload_to_gcs()

                # Success!
                self.result["status"] = "success"
                break

            except Exception as e:
                error_msg = f"Attempt {attempt}: {type(e).__name__}: {str(e)}"
                self.result["errors"].append(error_msg)
                print(f"[ERROR] {error_msg}")
                traceback.print_exc()

                if attempt == self.max_retries:
                    self.result["status"] = "failed"

        self.result["completed_at"] = datetime.now(timezone.utc).isoformat()

        if self.result["started_at"] and self.result["completed_at"]:
            start = datetime.fromisoformat(self.result["started_at"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(self.result["completed_at"].replace("Z", "+00:00"))
            self.result["duration_seconds"] = (end - start).total_seconds()

        # Write result summary
        self._write_result()

        return self.result

    def _cleanup(self):
        """Clean up previous attempt artifacts."""
        if self.clone_dir.exists():
            shutil.rmtree(self.clone_dir)
        self.clone_dir.parent.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _clone(self) -> bool:
        """Clone repository with timeout."""
        print(f"[CLONE] {self.repo_url} @ {self.repo_ref}")

        try:
            # Clone with depth 1 for speed
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", self.repo_ref,
                 self.repo_url, str(self.clone_dir)],
                capture_output=True,
                text=True,
                timeout=300  # 5 min clone timeout
            )

            if result.returncode != 0:
                # Try without --branch (might be a SHA)
                result = subprocess.run(
                    ["git", "clone", self.repo_url, str(self.clone_dir)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    # Checkout specific ref
                    subprocess.run(
                        ["git", "checkout", self.repo_ref],
                        cwd=self.clone_dir,
                        capture_output=True,
                        timeout=60
                    )

            if not self.clone_dir.exists():
                self.result["errors"].append(f"Clone failed: {result.stderr}")
                return False

            # Get actual SHA
            sha_result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.clone_dir,
                capture_output=True,
                text=True
            )
            self.result["sha"] = sha_result.stdout.strip()

            print(f"[CLONE] Success: {self.result.get('sha', 'unknown')}")
            return True

        except subprocess.TimeoutExpired:
            self.result["errors"].append("Clone timeout (5 min)")
            return False
        except Exception as e:
            self.result["errors"].append(f"Clone error: {str(e)}")
            return False

    def _analyze(self) -> bool:
        """Run Collider analysis with timeout."""
        print(f"[ANALYZE] Running Collider (timeout: {self.timeout_seconds}s)")

        output_path = self.output_dir / self.repo_name / self.result.get("sha", "unknown")
        output_path.mkdir(parents=True, exist_ok=True)

        try:
            result = subprocess.run(
                ["python3", "cli.py", "full", str(self.clone_dir),
                 "--output", str(output_path)],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                cwd="/app"  # Collider root in container
            )

            if result.returncode != 0:
                self.result["errors"].append(f"Collider failed: {result.stderr[-500:]}")
                return False

            # Find output JSON
            json_files = list(output_path.glob("*llm-oriented*.json")) + \
                        list(output_path.glob("unified_analysis.json"))

            if not json_files:
                self.result["errors"].append("No output JSON found")
                return False

            self.result["output_json"] = str(json_files[0])
            print(f"[ANALYZE] Success: {json_files[0].name}")
            return True

        except subprocess.TimeoutExpired:
            self.result["errors"].append(f"Analysis timeout ({self.timeout_seconds}s)")
            self.result["status"] = "timeout"
            return False
        except Exception as e:
            self.result["errors"].append(f"Analysis error: {str(e)}")
            return False

    def _extract_metrics(self) -> bool:
        """Extract key metrics from analysis output."""
        print("[METRICS] Extracting coverage metrics")

        try:
            with open(self.result["output_json"]) as f:
                data = json.load(f)

            nodes = data.get("nodes", [])
            if not nodes:
                self.result["errors"].append("No nodes in output")
                return False

            # Count atoms
            from collections import Counter
            atoms = Counter()
            for node in nodes:
                atom = node.get("atom") or node.get("base_atom") or "Unknown"
                atoms[atom] += 1

            total = sum(atoms.values())
            sorted_atoms = atoms.most_common()

            # Calculate metrics
            self.result["metrics"] = {
                "n_nodes": total,
                "n_edges": len(data.get("edges", [])),
                "n_files": len(data.get("files", [])),
                "unique_atoms": len(atoms),
                "top_1_mass": sorted_atoms[0][1] / total * 100 if sorted_atoms else 0,
                "top_2_mass": sum(c for _, c in sorted_atoms[:2]) / total * 100 if len(sorted_atoms) >= 2 else 0,
                "top_4_mass": sum(c for _, c in sorted_atoms[:4]) / total * 100 if len(sorted_atoms) >= 4 else 0,
                "unknown_rate": atoms.get("Unknown", 0) / total * 100,
                "dominant_atom": sorted_atoms[0][0] if sorted_atoms else None,
            }

            print(f"[METRICS] nodes={total}, top4={self.result['metrics']['top_4_mass']:.1f}%, unknown={self.result['metrics']['unknown_rate']:.2f}%")
            return True

        except Exception as e:
            self.result["errors"].append(f"Metrics extraction error: {str(e)}")
            return False

    def _upload_to_gcs(self):
        """Upload results to Google Cloud Storage."""
        if not HAS_GCS:
            print("[GCS] google-cloud-storage not installed, skipping upload")
            return

        print(f"[GCS] Uploading to gs://{self.gcs_bucket}/{self.gcs_prefix}/")

        try:
            client = storage.Client()
            bucket = client.bucket(self.gcs_bucket)

            # Upload JSON
            if self.result.get("output_json"):
                json_path = Path(self.result["output_json"])
                blob_name = f"{self.gcs_prefix}/{self.repo_name}/{json_path.name}"
                blob = bucket.blob(blob_name)
                blob.upload_from_filename(str(json_path))
                self.result["gcs_json"] = f"gs://{self.gcs_bucket}/{blob_name}"

            # Upload result summary
            result_blob_name = f"{self.gcs_prefix}/{self.repo_name}/result.json"
            result_blob = bucket.blob(result_blob_name)
            result_blob.upload_from_string(
                json.dumps(self.result, indent=2),
                content_type="application/json"
            )
            self.result["gcs_result"] = f"gs://{self.gcs_bucket}/{result_blob_name}"

            print(f"[GCS] Uploaded: {self.result.get('gcs_result')}")

        except Exception as e:
            self.result["errors"].append(f"GCS upload error: {str(e)}")

    def _write_result(self):
        """Write result summary to local file."""
        result_path = self.output_dir / f"{self.repo_name}_result.json"
        with open(result_path, "w") as f:
            json.dump(self.result, f, indent=2)
        print(f"[RESULT] Written to {result_path}")


def main():
    """Entry point for cloud execution."""
    # Get configuration from environment
    repo_url = os.environ.get("REPO_URL")
    repo_ref = os.environ.get("REPO_REF", "main")
    repo_name = os.environ.get("REPO_NAME")
    gcs_bucket = os.environ.get("GCS_BUCKET")
    gcs_prefix = os.environ.get("GCS_PREFIX", "corpus_999")
    max_retries = int(os.environ.get("MAX_RETRIES", "3"))
    timeout_seconds = int(os.environ.get("TIMEOUT_SECONDS", "900"))

    if not repo_url or not repo_name:
        print("ERROR: REPO_URL and REPO_NAME environment variables required")
        sys.exit(1)

    analyzer = RepoAnalyzer(
        repo_url=repo_url,
        repo_ref=repo_ref,
        repo_name=repo_name,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds,
        gcs_bucket=gcs_bucket,
        gcs_prefix=gcs_prefix,
    )

    result = analyzer.run()

    # Exit code based on status
    if result["status"] == "success":
        print(f"\n✅ SUCCESS: {repo_name}")
        sys.exit(0)
    elif result["status"] == "timeout":
        print(f"\n⏱️ TIMEOUT: {repo_name}")
        sys.exit(2)
    else:
        print(f"\n❌ FAILED: {repo_name}")
        sys.exit(1)


if __name__ == "__main__":
    main()
