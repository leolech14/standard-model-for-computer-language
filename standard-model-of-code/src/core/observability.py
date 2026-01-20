"""
🔬 COLLIDER OBSERVABILITY MODULE
Per-stage performance tracking for the analysis pipeline.

Provides:
- PipelineStageResult: Dataclass for individual stage metrics
- PerformanceManager: Collector and reporter for pipeline metrics
- observe_stage: Decorator for wrapping stage functions
- StageTimer: Context manager for manual timing

Inspired by the ProbeResult pattern in newman_suite.py.
"""
import functools
import resource
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class PipelineStageResult:
    """Canonical representation of a stage's execution metrics.

    Follows the ProbeResult pattern from newman_suite.py.
    """
    stage_name: str
    status: str  # OK, FAIL, WARN, SKIP
    latency_ms: float
    memory_delta_kb: int = 0  # Memory change during stage
    output_summary: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_name": self.stage_name,
            "status": self.status,
            "latency_ms": round(self.latency_ms, 1),
            "memory_delta_kb": self.memory_delta_kb,
            "output_summary": self.output_summary,
            "error": self.error
        }


class PerformanceManager:
    """Collects and manages pipeline stage metrics.

    Thread-safe singleton pattern for collecting metrics across
    the 12-stage pipeline.
    """

    def __init__(self, verbose: bool = False):
        self.stages: List[PipelineStageResult] = []
        self.verbose = verbose
        self._start_memory_kb: int = 0
        self._peak_memory_kb: int = 0
        self._pipeline_start: float = 0.0

    def start_pipeline(self) -> None:
        """Mark the start of pipeline execution."""
        self._pipeline_start = time.perf_counter()
        self._start_memory_kb = self._get_memory_kb()
        self._peak_memory_kb = self._start_memory_kb

    def add_result(self, result: PipelineStageResult) -> None:
        """Add a stage result and track peak memory."""
        self.stages.append(result)

        # Track peak memory
        current_memory = self._get_memory_kb()
        if current_memory > self._peak_memory_kb:
            self._peak_memory_kb = current_memory

        # Verbose output
        if self.verbose:
            self._print_stage_result(result)

    def _get_memory_kb(self) -> int:
        """Get current memory usage in KB (platform-aware)."""
        try:
            usage = resource.getrusage(resource.RUSAGE_SELF)
            # macOS reports in bytes, Linux in KB
            if sys.platform == "darwin":
                return int(usage.ru_maxrss / 1024)
            else:
                return int(usage.ru_maxrss)
        except Exception:
            return 0

    def _print_stage_result(self, result: PipelineStageResult) -> None:
        """Print a formatted line for verbose mode."""
        status_icon = {"OK": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}.get(result.status, "❓")

        # Format timing
        if result.latency_ms >= 1000:
            time_str = f"{result.latency_ms / 1000:.2f}s"
        else:
            time_str = f"{result.latency_ms:.0f}ms"

        # Format memory delta
        if result.memory_delta_kb > 0:
            if result.memory_delta_kb >= 1024:
                mem_str = f"+{result.memory_delta_kb / 1024:.0f}MB"
            else:
                mem_str = f"+{result.memory_delta_kb}KB"
        elif result.memory_delta_kb < 0:
            mem_str = f"{result.memory_delta_kb / 1024:.0f}MB"
        else:
            mem_str = "~0"

        # Format output summary
        summary_parts = []
        for key, val in result.output_summary.items():
            if isinstance(val, int):
                summary_parts.append(f"{val:,} {key}")
        summary_str = f"({', '.join(summary_parts)})" if summary_parts else ""

        # Print aligned output
        name_width = 40
        time_width = 8
        mem_width = 8
        print(f"   {status_icon} {result.stage_name:<{name_width}} {time_str:>{time_width}} {mem_str:>{mem_width}}  {summary_str}")

    def get_slowest_stage(self) -> Optional[Dict[str, Any]]:
        """Return the slowest stage by latency."""
        if not self.stages:
            return None
        slowest = max(self.stages, key=lambda s: s.latency_ms)
        return {"name": slowest.stage_name, "latency_ms": round(slowest.latency_ms, 1)}

    def to_dict(self) -> Dict[str, Any]:
        """Generate the canonical performance output structure."""
        total_latency = sum(s.latency_ms for s in self.stages)
        ok_count = sum(1 for s in self.stages if s.status == "OK")
        fail_count = sum(1 for s in self.stages if s.status == "FAIL")
        warn_count = sum(1 for s in self.stages if s.status == "WARN")
        total_count = len(self.stages)

        return {
            "summary": {
                "total_stages": total_count,
                "ok_count": ok_count,
                "fail_count": fail_count,
                "warn_count": warn_count,
                "total_latency_ms": round(total_latency, 1),
                "slowest_stage": self.get_slowest_stage(),
                "peak_memory_kb": self._peak_memory_kb,
                "success_rate": round(ok_count / total_count, 2) if total_count else 0.0
            },
            "stages": [s.to_dict() for s in self.stages]
        }

    def print_summary(self) -> None:
        """Print a formatted summary table for --timing mode."""
        if not self.stages:
            return

        print("\n" + "─" * 72)
        print("PIPELINE PERFORMANCE SUMMARY")
        print("─" * 72)

        total_latency = sum(s.latency_ms for s in self.stages)
        ok_count = sum(1 for s in self.stages if s.status == "OK")

        # Print each stage
        for result in self.stages:
            self._print_stage_result(result)

        print("─" * 72)

        # Summary line
        if total_latency >= 1000:
            total_str = f"{total_latency / 1000:.2f}s"
        else:
            total_str = f"{total_latency:.0f}ms"

        if self._peak_memory_kb >= 1024:
            peak_str = f"{self._peak_memory_kb / 1024:.0f}MB"
        else:
            peak_str = f"{self._peak_memory_kb}KB"

        print(f"   {'TOTAL':<44} {total_str:>8} (peak: {peak_str})")
        print(f"   Stages: {ok_count}/{len(self.stages)} OK")

        slowest = self.get_slowest_stage()
        if slowest:
            print(f"   Bottleneck: {slowest['name']} ({slowest['latency_ms']:.0f}ms)")
        print("─" * 72)


class StageTimer:
    """Context manager for timing individual stages.

    Usage:
        with StageTimer(manager, "Stage 1: Base Analysis") as timer:
            result = analyze(...)
            timer.set_output(nodes=len(result.nodes), edges=len(result.edges))
    """

    def __init__(self, manager: PerformanceManager, stage_name: str):
        self.manager = manager
        self.stage_name = stage_name
        self._start_time: float = 0.0
        self._start_memory: int = 0
        self._output_summary: Dict[str, Any] = {}
        self._status: str = "OK"
        self._error: Optional[str] = None

    def __enter__(self) -> "StageTimer":
        self._start_time = time.perf_counter()
        self._start_memory = self.manager._get_memory_kb()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        end_time = time.perf_counter()
        end_memory = self.manager._get_memory_kb()

        latency_ms = (end_time - self._start_time) * 1000
        memory_delta = end_memory - self._start_memory

        if exc_type is not None:
            self._status = "FAIL"
            self._error = f"{exc_type.__name__}: {exc_val}"

        result = PipelineStageResult(
            stage_name=self.stage_name,
            status=self._status,
            latency_ms=latency_ms,
            memory_delta_kb=memory_delta,
            output_summary=self._output_summary,
            error=self._error
        )

        self.manager.add_result(result)
        return False  # Don't suppress exceptions

    def set_output(self, **kwargs: Any) -> None:
        """Set output summary metrics."""
        self._output_summary.update(kwargs)

    def set_status(self, status: str, error: Optional[str] = None) -> None:
        """Manually set status (OK, WARN, SKIP, FAIL)."""
        self._status = status
        self._error = error


def observe_stage(manager: PerformanceManager, stage_name: str):
    """Decorator for wrapping stage functions with timing.

    Usage:
        @observe_stage(manager, "Stage 1: Base Analysis")
        def _run_stage_1(path, opts):
            return analyze(path, **opts)

    The decorator automatically:
    - Measures execution time
    - Tracks memory delta
    - Captures exceptions as FAIL status
    - Generates output_summary from return value
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            start_memory = manager._get_memory_kb()

            status = "FAIL"
            output_summary = {}
            error_str = None

            try:
                result = func(*args, **kwargs)
                status = "OK"

                # Auto-generate output summary from result
                if isinstance(result, dict):
                    if 'nodes' in result:
                        output_summary['nodes'] = len(result['nodes']) if isinstance(result['nodes'], list) else result['nodes']
                    if 'edges' in result:
                        output_summary['edges'] = len(result['edges']) if isinstance(result['edges'], list) else result['edges']
                elif isinstance(result, (list, tuple)):
                    output_summary['items'] = len(result)
                elif hasattr(result, 'nodes') and hasattr(result, 'edges'):
                    # AnalysisResult-like object
                    output_summary['nodes'] = len(result.nodes) if hasattr(result.nodes, '__len__') else 0
                    output_summary['edges'] = len(result.edges) if hasattr(result.edges, '__len__') else 0

                return result

            except Exception as e:
                error_str = f"{type(e).__name__}: {e}"
                raise

            finally:
                end_time = time.perf_counter()
                end_memory = manager._get_memory_kb()

                latency_ms = (end_time - start_time) * 1000
                memory_delta = end_memory - start_memory

                stage_result = PipelineStageResult(
                    stage_name=stage_name,
                    status=status,
                    latency_ms=latency_ms,
                    memory_delta_kb=memory_delta,
                    output_summary=output_summary,
                    error=error_str
                )
                manager.add_result(stage_result)

        return wrapper
    return decorator
