"""Regenerate the per-view evaluation folders, then the revision-only tables.

`build_revision_assets.py` runs `paper_support_analysis.py` once, over the
combined 78-question results, and writes its tables to the top level of
`result_revision/`. Two further views of the same experiment are reported in the
paper and were previously produced by hand, with no driver in the repo:

  result_revision/newrr_eval/   the re-ranker family, audited 78-question set
  result_revision/p4_eval/      the expanded 155-question benchmark

Those views are not decorative. `make_revision_tables.py` reads
`newrr_eval/newrr_pairwise_vs_baseline.csv` and
`p4_eval/p4_pairwise_vs_baseline.csv` for the delta/p columns of the re-ranker
table, and `curate_paper_assets.py` draws the stage-retention figure from
`newrr_eval/newrr_stage_gold_retention.csv`. Without this driver a reader could
rebuild every top-level table and still not reproduce the paper's central
re-ranker table -- which is exactly what a reviewer flagged about the original
submission.

`paper_support_analysis.py` is env-driven, so each view is one invocation with
its own `RESULT_DIR` and `ANALYSIS_PREFIX` (the prefix names every file it
writes, which is what keeps two views from overwriting each other).

Order matters: the views must exist before `make_revision_tables.py` reads them.

Usage:
    python -m legacy.run_view_analyses --dry-run
    python -m legacy.run_view_analyses
    python -m legacy.run_view_analyses --only newrr
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

from rerankhuts.paths import oncology_path


BASE = Path(__file__).resolve().parents[1]
REV = BASE / "result_revision"

# `run_rag_eval.py` writes one file per mode, so the combined result file each
# view is read from has to be stitched back together by
# `combine_revision_results.py`. That call was made by hand and no driver
# recorded it, which is how the expanded view kept scoring eleven modes after
# `rerank_llm` had been added to the P4 batch: the per-mode file existed and was
# current, but the combined file the view actually reads still held the previous
# round's rows (its latency columns gave the stale run away). Refresh them here,
# before any view reads them.
#
# Stems whose combined file `run_rag_eval.py` writes itself need no entry UNLESS
# a mode was added out-of-band (a corrective run that writes only the new mode
# and points at a throwaway combined file). `p4_iso_v2corpus_78q` is exactly that
# case after `rerank_source_aware` was added: its per-mode file exists but its
# combined file, written by the earlier batch run, does not know the mode. Keep
# it here so a re-stitch from per-mode files picks the new mode up.
COMBINES = [
    (
        "supp_new_rerankers",
        "baseline,rerank,rerank_bge_base,rerank_bge_m3,rerank_medcpt,rerank_llm,rerank_source_aware",
        "supp_new_rerankers_combined.csv",
        "re-ranker family inputs for the audited 78-question view",
    ),
    (
        "p4_expanded_retrieval",
        None,  # filled from run_p4_expanded.RETRIEVAL_MODES at run time
        "p4_expanded_retrieval_combined.csv",
        "expanded-benchmark inputs for the 155-question view",
    ),
    (
        "p4_iso_v2corpus_78q",
        None,  # filled from run_p4_expanded.RETRIEVAL_MODES at run time
        "p4_iso_v2corpus_78q.csv",
        "isolation view (78 audited questions on the expanded corpus)",
    ),
]

# The original 78 audited questions, as shipped with the pre-revision results.
ORIGINAL_VALIDATED = (BASE / "result" / "emnlp_full_results_20260427_gpu_final"
                      / "paper_questions_validated.jsonl")

# The two views, as (stem, env overrides, what it is).
#
# `newrr` starts from the full 100-question pool: its audit summary reports
# 100 -> 78 validated / 20 general / 2 duplicates, so it re-derives the split
# rather than being handed the validated set. `p4` starts from the already
# validated set and sets ASSUME_VALIDATED so the audit does not re-split it
# (its held-out file is legitimately empty -- every expanded question is
# disease-specific by construction).
VIEWS = [
    (
        "newrr",
        {
            "RESULT_DIR": str(REV / "newrr_eval"),
            "RESULTS_FILE": str(REV / "supp_new_rerankers_combined.csv"),
            "QUESTIONS_FILE": str(oncology_path("questions.jsonl", root=BASE)),
            "ANALYSIS_PREFIX": "newrr",
        },
        "re-ranker family on the audited 78-question set",
    ),
    (
        "p4",
        {
            "RESULT_DIR": str(REV / "p4_eval"),
            "RESULTS_FILE": str(REV / "p4_expanded_retrieval_combined.csv"),
            "QUESTIONS_FILE": str(oncology_path("questions_expanded_full_validated.jsonl", root=BASE)),
            "ASSUME_VALIDATED": "1",
            "ANALYSIS_PREFIX": "p4",
        },
        "the expanded 155-question benchmark",
    ),
]


def run(script: str, env_overrides: dict, label: str, dry: bool,
        argv: list | None = None) -> bool:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env.update({k: str(v) for k, v in env_overrides.items()})
    command = [sys.executable, "-m", "legacy." + Path(script).stem]
    cmd = command + [str(a) for a in (argv or [])]
    print(f"\n{'=' * 70}\n>>> {label}\n    {' '.join(cmd[1:])}", flush=True)
    for k, v in env_overrides.items():
        print(f"      {k}={v}", flush=True)
    if dry:
        return True
    r = subprocess.run(cmd, env=env, cwd=BASE)
    ok = r.returncode == 0
    print(f"    -> {'OK' if ok else f'FAILED(exit {r.returncode})'}", flush=True)
    return ok


def p4_retrieval_modes() -> str:
    """The P4 batch's mode list, from its single source of truth."""
    from legacy import run_p4_expanded
    return run_p4_expanded.RETRIEVAL_MODES


def run_combines(dry: bool) -> list:
    """Restitch every combined result file the views are read from."""
    failed = []
    for stem, modes, out_name, what in COMBINES:
        modes = modes or p4_retrieval_modes()
        ok = run(
            "combine_revision_results.py",
            {"RESULT_DIR": str(REV), "COMBINE_MODES": modes},
            f"combine '{stem}' -> {out_name}: {what}",
            dry,
            argv=["--stem", stem, "--out-name", out_name],
        )
        if not ok:
            failed.append(out_name)
    return failed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default=None, help="Run one view only (newrr|p4).")
    args = ap.parse_args()

    views = VIEWS
    if args.only:
        views = [v for v in VIEWS if v[0] == args.only]
        if not views:
            raise SystemExit(f"Unknown view: {args.only} (expected newrr or p4)")

    failed = []
    # The combined files come first: a view read against a stale one scores the
    # wrong mode list and nothing downstream can tell.
    failed += run_combines(args.dry_run)

    for stem, env, what in views:
        if not run("paper_support_analysis.py", env, f"view '{stem}': {what}", args.dry_run):
            failed.append(stem)

    # The revision-only tables read the views, so they only make sense once
    # every view regenerated cleanly.
    if failed:
        print(f"\n!! skipping make_revision_tables.py: view(s) failed: {failed}")
    else:
        if not run("make_revision_tables.py", {}, "revision-only tables (re-ranker/judge/benchmark)", args.dry_run):
            failed.append("make_revision_tables.py")

    print(f"\nDone. Failed: {failed or 'none'}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
