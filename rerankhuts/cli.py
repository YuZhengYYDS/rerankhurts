"""A small command dispatcher around the frozen experiment implementations.

Use the appropriate Pixi environment; this module never installs dependencies,
changes recorded experiments, or substitutes new code for a frozen backend.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E3_RUN = "experiments/runs/e3_m3"
SIM_RUN = "experiments/runs/simulation_pilot_v2"
SIM_DATA = "experiments/simulation/data/pilot_v2"
SIM_RESULTS = "experiments/simulation/results/pilot_v2"
E3_REVISIONS = (
    "--dense-revision", "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a",
    "--reranker-revision", "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e",
    "--tokenizer-revision", "86b5e0934494bd15c9632b12f734a8a67f723594",
)
COMMANDS = {
    "status": "Show manuscript, authors and completed experiment counts (offline).",
    "verify": "Verify frozen hashes, E3 traces and simulation paired counts (offline).",
    "e0": "Recompute the historical audit into build/reanalysis/e0 (offline).",
    "e3": "Run/resume the pinned oncology experiment (GPU environment).",
    "sim-generate": "Recreate the frozen synthetic data; refuses conflicting data.",
    "sim-run": "Run/resume the pinned simulation inference (GPU environment).",
    "sim-evaluate": "Re-score simulation traces into build/reanalysis/simulation (GPU environment).",
    "analyze-e3": "Recompute E3 contrasts/figure in build/reanalysis/e3 (offline).",
    "interactions-e3": "Recompute the separate eight E3 interactions in build/reanalysis/e3.",
    "tables": "Refresh the manuscript tables from verified frozen outputs.",
    "paper": "Compile the clean paper (paper environment).",
    "package": "Build full/paper archives; --split adds code/results archives.",
    "verify-package": "Validate archive paths, hashes and payload membership (offline).",
    "test": "Run the test suite in the current Pixi environment.",
    "strengthen-models": "Download/verify immutable local model snapshots (GPU environment).",
    "strengthen-generate": "Generate the frozen 360-world strengthening workload.",
    "strengthen-audit": "Independently parse and audit the new synthetic data (offline).",
    "strengthen-run": "Run/resume the 124-configuration strengthening experiment (GPU).",
    "strengthen-evaluate": "Independently score delivered spans from strengthening traces (GPU dependencies).",
    "strengthen-analyze": "Compute world-level contrasts and summaries for strengthening results.",
    "strengthen-answers": "Run the actual local answer model and evidence controls (GPU).",
    "strengthen-timing": "Measure complete online requests without reused query/pair scores (GPU).",
    "strengthen-verify": "Verify strengthening data, traces, answers and timing without models (offline).",
}
COMPOSITE = {"verify", "tables", "analyze-e3", "interactions-e3"}


def commands_for(name: str, extra: list[str]) -> list[list[str]]:
    """Return argument vectors, never shell strings or dynamically loaded code."""
    if name in COMPOSITE and extra:
        raise ValueError(f"{name} uses the frozen workload and accepts no extra arguments")
    if name == "verify":
        return [
            ["scripts/check_frozen_files.py"],
            ["validation/check_e3.py", "--run", E3_RUN,
             "--output", "build/verification/e3"],
            ["validation/audit_simulation_endpoint_pairs.py",
             "--output", "build/verification/simulation_endpoint_pairs.json"],
        ]
    if name == "tables":
        return [["scripts/check_frozen_files.py"],
                ["paper/build_e3_table.py", E3_RUN],
                ["paper/build_simulation_table.py", SIM_RESULTS]]
    if name in {"analyze-e3", "interactions-e3"}:
        script = (["scripts/analyze_factorial.py"] if name == "analyze-e3" else
                  ["-m", "experiments.analyze_factorial"])
        return [script + ["--run", "build/reanalysis/e3"]]
    plans = {
        "e0": ["validation/audit_metrics.py", "--output", "build/reanalysis/e0"],
        "e3": ["-m", "experiments.run_factorial", "--device", "cuda",
               "--rerank-batch-size", "8", "--output", E3_RUN, *E3_REVISIONS],
        "sim-generate": ["-m", "experiments.simulation.generate"],
        "sim-run": ["-m", "experiments.simulation.backend", "--device", "cuda",
                    "--rerank-batch-size", "8"],
        "sim-evaluate": ["-m", "experiments.simulation.evaluate", "--data", SIM_DATA,
                         "--run", SIM_RUN, "--output", "build/reanalysis/simulation"],
        "paper": ["scripts/build_paper.py"],
        "package": ["scripts/package_release.py"],
        "verify-package": ["scripts/verify_release.py"],
        "test": ["-m", "pytest", "tests", "-q"],
        "strengthen-models": ["-m", "experiments.strengthening.download_models"],
        "strengthen-generate": ["-m", "experiments.strengthening.generate"],
        "strengthen-audit": ["-m", "experiments.strengthening.audit_data"],
        "strengthen-run": ["-m", "experiments.strengthening.backend"],
        "strengthen-evaluate": ["-m", "experiments.strengthening.evaluate"],
        "strengthen-analyze": ["-m", "experiments.strengthening.analyze"],
        "strengthen-answers": ["-m", "experiments.strengthening.downstream"],
        "strengthen-timing": ["-m", "experiments.strengthening.timing"],
        "strengthen-verify": ["scripts/check_strengthening_files.py"],
    }
    return [plans[name] + extra]


def run_steps(steps: list[list[str]], *, root: Path = ROOT, dry_run: bool = False) -> int:
    for args in steps:
        argv = [sys.executable, *args]
        print(json.dumps({"cwd": str(root), "argv": argv}, ensure_ascii=False), flush=True)
        if not dry_run:
            result = subprocess.run(argv, cwd=root, check=False)
            if result.returncode:
                return result.returncode
    return 0


def stage_e3_analysis(root: Path = ROOT) -> None:
    """Copy only analysis inputs; every recomputed output stays under build/."""
    destination = root / "build/reanalysis/e3"
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("manifest.json", "status.json", "per_question.csv", "summary.csv"):
        shutil.copy2(root / E3_RUN / name, destination / name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print commands without running or copying anything.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in COMMANDS.items():
        sub.add_parser(name, help=help_text, add_help=False)
    args, extra = parser.parse_known_args(argv)
    if args.command in COMPOSITE | {"status"} and extra == ["--help"]:
        print(f"{args.command}: {COMMANDS[args.command]}\nNo additional options.")
        return 0
    if args.command == "status":
        if extra:
            parser.error("status accepts no extra arguments")
        print((ROOT / "release_status.json").read_text(encoding="utf-8"))
        return 0
    try:
        steps = commands_for(args.command, extra)
    except ValueError as error:
        parser.error(str(error))
    try:
        if args.command in {"analyze-e3", "interactions-e3"}:
            result = run_steps([["scripts/check_frozen_files.py"]], dry_run=args.dry_run)
            if result:
                return result
            if not args.dry_run:
                stage_e3_analysis()
        return run_steps(steps, dry_run=args.dry_run)
    except (OSError, KeyboardInterrupt) as error:
        print(f"Command could not finish: {error}", file=sys.stderr)
        return 130 if isinstance(error, KeyboardInterrupt) else 1


if __name__ == "__main__":
    raise SystemExit(main())
