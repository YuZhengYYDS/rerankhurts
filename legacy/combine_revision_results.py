"""Combine the per-mode result CSVs into the single file downstream expects.

`run_rag_eval.py` normally writes one combined `rag_results_experiments.csv`,
but under the driver scripts it writes one file per mode
(`<stem>_<mode>.csv`). `score_retrieval.py`, `analyze_results.py` and
`paper_support_analysis.py` all read the combined file, so this script stitches
the per-mode pieces back together.

The default mode list is exactly the eight configurations in the paper's main
results table, in table order:

    Base, Dense, Hybrid-BM25, RRF, Rerank, RRF+Rerank, BM25+Dedup, BM25

All eight carry generation output in the `supp_strong_baselines_validated`
batch, which is what the answer-level figure needs.

Usage:
    python -m legacy.combine_revision_results                      # main table, 78-question run
    python -m legacy.combine_revision_results --stem supp_strong_baselines_full100 \
        --questions questions.jsonl --out-name rag_results_expanded.csv
"""
import argparse
import os
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RESULT_DIR = Path(os.getenv("RESULT_DIR", str(BASE_DIR / "result_revision")))
if not RESULT_DIR.is_absolute():
    RESULT_DIR = BASE_DIR / RESULT_DIR

# Paper Table 1 order. `--modes` must name these files as <stem>_<mode>.csv.
MAIN_TABLE_MODES = [
    "baseline",           # Base
    "control_dense_only",  # Dense
    "hybrid_bm25",        # Hybrid-BM25
    "rrf_hybrid",         # RRF
    "rerank",             # Rerank
    "rrf_hybrid_rerank",  # RRF+Rerank
    "bm25_base",          # BM25+Dedup
    "bm25_only",          # BM25
    # Ablations cited by the appendix stage-retention, rank-transition and
    # case-study tables. Consumers that care about a subset (the main table and
    # the re-ranker figure) filter by an explicit mode list, so carrying these
    # here cannot leak into a table that did not ask for them.
    "ablation_no_dedup",    # NoDedup  (from the dedup sweep's c=inf batch)
    "ablation_small_pool",  # SmallPool
]

REQUIRED_COLS = {"qid", "question", "mode"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default="supp_strong_baselines_validated",
                    help="Batch stem whose per-mode files should be combined.")
    ap.add_argument("--also-stem", default=os.getenv("COMBINE_ALSO_STEMS", ""),
                    help="Extra batch stems, comma-separated. Each mode is looked "
                         "up in --stem first and then in these, so a mode that "
                         "belongs to a different sweep (the no-dedup ablation "
                         "lives in the dedup sweep, small-pool in its own batch) "
                         "still lands in the same combined file.")
    ap.add_argument("--modes", default=os.getenv("COMBINE_MODES", ",".join(MAIN_TABLE_MODES)),
                    help="Comma-separated mode names, in output order.")
    ap.add_argument("--out-name", default="rag_results_experiments.csv")
    ap.add_argument("--result-dir", default=None)
    args = ap.parse_args()

    result_dir = Path(args.result_dir) if args.result_dir else RESULT_DIR
    if not result_dir.is_absolute():
        result_dir = BASE_DIR / result_dir

    stems = [args.stem] + [s.strip() for s in args.also_stem.split(",") if s.strip()]

    def locate(mode: str) -> Path | None:
        for stem in stems:
            cand = result_dir / f"{stem}_{mode}.csv"
            if cand.exists() and cand.stat().st_size > 0:
                return cand
        return None

    modes = [m.strip() for m in args.modes.split(",") if m.strip()]
    frames, missing = [], []
    for mode in modes:
        path = locate(mode)
        if path is None:
            missing.append(f"{mode} (no per-mode file in: {', '.join(stems)})")
            continue
        df = pd.read_csv(path)
        if not REQUIRED_COLS.issubset(df.columns):
            missing.append(f"{path.name} (missing {REQUIRED_COLS - set(df.columns)})")
            continue
        df["mode"] = mode
        frames.append(df)

    if missing:
        raise SystemExit(
            "Cannot combine - these per-mode files are absent or malformed:\n  "
            + "\n  ".join(missing)
        )

    combined = pd.concat(frames, ignore_index=True)
    out_path = result_dir / args.out_name
    combined.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"Combined {len(frames)} modes x {len(combined) // len(frames)} questions "
          f"= {len(combined)} rows")
    print(f"  modes: {', '.join(modes)}")
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
