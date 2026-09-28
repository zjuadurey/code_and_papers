"""Private subprocess entry for the optional Microsoft QDK resource estimator."""
import contextlib
import importlib.metadata
import json
import os
import sys


def main() -> int:
    os.environ["QDK_PYTHON_TELEMETRY"] = "none"
    os.environ["QSHARP_PYTHON_TELEMETRY"] = "none"
    try:
        request = json.load(sys.stdin)
        version = importlib.metadata.version("qdk")
        if version != request["qdk_version"]:
            raise RuntimeError(f"Expected qdk {request['qdk_version']}; found {version}")
        with contextlib.redirect_stdout(sys.stderr):
            from qdk.qre import estimate, PSSPC, LatticeSurgery, ErrorComposition
            from qdk.qre.application import OpenQASMApplication
            from qdk.qre.models import GateBased, SurfaceCode, RoundBasedFactory
            profile = request["profile"]
            app = OpenQASMApplication(request["application"]["source"])
            architecture = GateBased(error_rate=profile["error_rate"],
                                     gate_time=profile["gate_time_ns"],
                                     measurement_time=profile["measurement_time_ns"])
            table = estimate(app, architecture,
                             isa_query=SurfaceCode.q() * RoundBasedFactory.q(),
                             trace_query=PSSPC.q() * LatticeSurgery.q(),
                             max_error=request["max_error"],
                             composition=ErrorComposition.UnionBound, use_graph=False)
        rows = [{"physical_qubits": int(e.qubits), "runtime_ns": float(e.runtime),
                 "error_bound": float(e.error)} for e in table]
        output = {"status": "ok" if rows else "no_estimate", "rows": rows,
                  "backend": "qdk.qre", "backend_version": version,
                  "model": "GateBased/SurfaceCode/RoundBasedFactory; PSSPC/LatticeSurgery",
                  "use_graph": False,
                  "stats": {k: getattr(table.stats, k) for k in
                            ("num_traces", "num_isas", "total_jobs", "successful_estimates", "pareto_results")}}
        print(json.dumps(output, allow_nan=False))
        return 0
    except (ImportError, importlib.metadata.PackageNotFoundError) as exc:
        print(json.dumps({"status": "unavailable", "rows": [], "error": str(exc)}))
        return 2
    except Exception as exc:
        print(json.dumps({"status": "error", "rows": [], "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
