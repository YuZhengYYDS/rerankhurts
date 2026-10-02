"""Driver for the P3 experiment matrix (78-question audited set + new rerankers).

Runs each batch of `run_rag_eval.py` sequentially with the correct env-var
combination, writing all outputs under `result_revision/`. Continues past a
failing batch so one bad model download does not stall the whole matrix.

Usage:
    python -m legacy.run_p3_matrix --dry-run     # print the plan only
    python -m legacy.run_p3_matrix               # execute everything
    python -m legacy.run_p3_matrix --only <stem> # execute a single batch by stem
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "result_revision"
OUT.mkdir(exist_ok=True)

VALIDATED78 = "result/emnlp_full_results_20260427_gpu_final/paper_questions_validated.jsonl"
NORMALIZED78 = "result/emnlp_full_results_20260427_gpu_final/paper_questions_validated_normalized.jsonl"
FULL100 = "questions.jsonl"

NINE_MODES = ",".join([
    "control_dense_only", "control_hybrid", "bm25_only", "bm25_base",
    "hybrid_bm25", "rrf_hybrid", "rrf_hybrid_rerank", "baseline", "rerank",
])
NEW_RERANK_MODES = "baseline,rerank,rerank_bge_base,rerank_bge_m3,rerank_medcpt,rerank_llm,rerank_source_aware"

# Batches that run a BM25-backed mode (bm25_only / bm25_base / hybrid_bm25 /
# rrf_hybrid / rrf_hybrid_rerank) but do not sweep BM25 must state k1 and b
# explicitly. Otherwise they silently inherit whatever the defaults happen to be
# on the day they run, and a later change to those defaults leaves a batch
# scored with a different function than the rest of the result set -- which is
# exactly how `supp_strong_baselines_full100` came to disagree with the validated
# batch on every BM25 row. Sweeps pass their own values and must not be pinned.
TUNED_BM25 = {"BM25_K1": "1.2", "BM25_B": "0.4"}


def _batches():
    b = []
    # (stem, questions_file, modes, run_generation, extra_env)
    b.append(("supp_strong_baselines_validated", VALIDATED78, NINE_MODES, True, dict(TUNED_BM25)))
    b.append(("supp_strong_baselines_full100", FULL100, NINE_MODES, False, dict(TUNED_BM25)))
    # Strong dense retrievers
    b.append(("supp_strong_dense_BAAI__bge_base_en_v1_5", VALIDATED78, "baseline,rerank", False,
              {"EMBED_MODEL_NAME": "BAAI/bge-base-en-v1.5"}))
    b.append(("supp_strong_dense_intfloat__e5_base_v2", VALIDATED78, "baseline,rerank", False,
              {"EMBED_MODEL_NAME": "intfloat/e5-base-v2"}))
    # Strong cross-encoder (MiniLM-L12) across rerank depths (pool fixed at 100)
    for d in (10, 24, 50, 100):
        b.append((f"supp_strong_reranker_minilm_l12_d{d:03d}", VALIDATED78, "baseline,rerank", False,
                  {"RERANK_MODEL_NAME": "cross-encoder/ms-marco-MiniLM-L-12-v2",
                   "RERANK_DEPTH": d, "TOP_K_RETRIEVE": 100}))
    # NEW rerankers for this revision (bge-reranker-base / v2-m3 / MedCPT / LLM)
    b.append(("supp_new_rerankers", VALIDATED78, NEW_RERANK_MODES, False, {}))
    # Pool-size sweep
    for p in (4, 8, 16, 24, 40, 80):
        b.append((f"supp_pool_sweep_p{p:02d}", VALIDATED78, "baseline,rerank", False,
                  {"TOP_K_RETRIEVE": p}))
    # URL dedup-cap sweep (c1, c2, c3, cinf)
    for c in (1, 2, 3):
        b.append((f"supp_dedup_sweep_c{c}", VALIDATED78,
                  "baseline,ablation_base_no_dedup,rerank,ablation_no_dedup", False,
                  {"MAX_CHUNKS_PER_URL": c}))
    b.append(("supp_dedup_sweep_cinf", VALIDATED78,
              "baseline,ablation_base_no_dedup,rerank,ablation_no_dedup", False, {}))
    # Small-pool ablation: the same pipeline with an 8-chunk candidate pool.
    # This was present in the pre-revision round but never added here, so the
    # appendix's SmallPool rows had no source in the current result set.
    b.append(("supp_ablation_small_pool", VALIDATED78,
              "ablation_base_small_pool,ablation_small_pool", False, {}))
    # Rerank-depth sweep (pool fixed at 100). `rrf_hybrid_rerank` fuses a BM25
    # ranking, so the tuned k1/b must be pinned here too (see TUNED_BM25).
    for d in (10, 24, 50, 100):
        b.append((f"supp_rerank_depth_d{d:03d}", VALIDATED78, "rerank,rrf_hybrid_rerank", False,
                  {"TOP_K_RETRIEVE": 100, "RERANK_DEPTH": d, **TUNED_BM25}))
    # Final evidence count sweep
    for k in (2, 4, 6, 8):
        b.append((f"supp_finalk_sweep_k{k}", VALIDATED78, "baseline,rerank", False,
                  {"TOP_K_RERANK": k}))
    # Source-mixture ablation
    for p in ("all", "nci_only", "nci_textbook", "nci_pubmed", "textbook_only", "pubmed_only"):
        b.append((f"supp_source_ablation_{p}", VALIDATED78, "baseline,rerank", False,
                  {"CORPUS_SOURCE_PRESET": p}))
    # Query-normalization check (re-run the same pipeline on normalized wording).
    b.append(("supp_query_normalization", NORMALIZED78, "control_dense_only,baseline,rerank",
              False, {}))
    # BM25 grid search
    for k1 in ("0.9", "1.2", "1.5"):
        for bb in ("0.4", "0.75", "0.9"):
            # `bm25_base` carries the URL diversity cap, `bm25_only` does not --
            # the appendix grid reports both, and previously only the capped
            # variant was produced, leaving the no-dedup rows unsourced.
            b.append((f"supp_bm25_grid_k{k1.replace('.', '')}b{bb.replace('.', '')}",
                      VALIDATED78, "bm25_base,bm25_only", False,
                      {"BM25_K1": k1, "BM25_B": bb}))
    return b


def batch_complete(stem: str, modes: str) -> bool:
    """A batch is complete only when every per-mode output file exists and is non-empty."""
    mode_list = [m.strip() for m in modes.split(",") if m.strip()]
    for mode in mode_list:
        path = OUT / f"{stem}_{mode}.csv"
        if not path.exists() or path.stat().st_size == 0:
            return False
    return True


def run_batch(stem, questions, modes, generation, extra):
    out_file = OUT / f"{stem}.csv"
    settings = OUT / f"{stem}_settings.csv"
    base = {
        "QUESTIONS_FILE": questions,
        "RUN_EXPERIMENTS": modes,
        "RUN_GENERATION": "1" if generation else "0",
        "OUTPUT_RESULTS_FILE": str(out_file),
        "EXPERIMENT_SETTINGS_FILE": str(settings),
        "EXPERIMENT_OUTPUT_DIR": str(OUT),
        "EXPERIMENT_OUTPUT_PREFIX": stem,
    }
    base.update({k: str(v) for k, v in extra.items()})
    env = os.environ.copy()
    env.update(base)
    print(f"\n{'=' * 70}\n=== {stem} ===\n  questions={questions}\n  modes={modes}\n  generation={generation}\n  extra={extra}", flush=True)
    t0 = time.time()
    r = subprocess.run([sys.executable, str(BASE / "run_rag_eval.py")], env=env, cwd=BASE)
    dt = time.time() - t0
    status = "OK" if r.returncode == 0 else f"FAILED(exit {r.returncode})"
    print(f"  -> {status} in {dt:.0f}s", flush=True)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", type=str, default=None)
    ap.add_argument("--no-skip", action="store_true",
                    help="Re-run batches whose outputs already exist.")
    args = ap.parse_args()

    batches = _batches()
    if args.only:
        batches = [b for b in batches if b[0] == args.only]
        if not batches:
            print(f"Unknown batch stem: {args.only}")
            sys.exit(1)

    print(f"Total batches: {len(batches)}")
    failed = []
    for (stem, questions, modes, generation, extra) in batches:
        if args.dry_run:
            print(f"  {stem}: QUESTIONS={questions} MODES={modes} GEN={generation} EXTRA={extra}")
            continue
        if not args.no_skip and batch_complete(stem, modes):
            print(f"\n=== {stem} ===\n  -> SKIP (already complete)", flush=True)
            continue
        ok = run_batch(stem, questions, modes, generation, extra)
        if not ok:
            failed.append(stem)

    print(f"\nDone. Failed batches: {failed or 'none'}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
