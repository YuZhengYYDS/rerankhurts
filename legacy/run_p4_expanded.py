"""Driver for the P4 (expanded benchmark) experiment batches.

P4a re-runs the retrieval comparison on the EXPANDED 159-question benchmark
over the expanded v2 corpus (23 NCI/PDQ pages instead of 6). P4b produces
generated answers on the 40-question judge sample so that `llm_judge.py` can
score answer quality and graded evidence relevance.

Everything is written under `result_revision/`, so P3 and P4 artifacts sit
side by side and can be summarised together.

Usage:
    python -m legacy.run_p4_expanded --dry-run
    python -m legacy.run_p4_expanded                 # run all batches (skips complete)
    python -m legacy.run_p4_expanded --only <stem>
    python -m legacy.run_p4_expanded --no-skip       # force re-run
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

# The BM25 function every batch here must be scored with. These batches run
# BM25-backed modes (`bm25_only`, `bm25_base`, `hybrid_bm25`, `rrf_hybrid`,
# `rrf_hybrid_rerank`) but never sweep k1/b, so without this they inherit
# whatever `run_rag_eval.py`'s defaults happen to be on the day they run. That
# is not hypothetical: it is how `supp_strong_baselines_full100` came to
# disagree with the validated batch on every BM25 row, and the disagreement was
# invisible because each batch is internally consistent. Imported rather than
# restated so a tuning change moves both drivers at once.
from legacy.run_p3_matrix import TUNED_BM25

EXPANDED_CORPUS = "corpus_chunks_v2.jsonl"
# Written by finalize_expanded_benchmark.py: the 78 audited questions plus the
# expanded questions whose gold page passed the automatic answerability screen.
EXPANDED_QUESTIONS = "questions_expanded_full_validated.jsonl"
# The judge now runs on ALL 155 validated questions, not the 40-question sample
# the first pass used. R1 asked for end-to-end answer quality with and without
# the re-ranker; a 40-question sample put the answer-quality noise floor at the
# same size as the between-system gaps, so the scale-up is what turns "the judge
# says something" into "the judge says something with enough questions to matter".
# The 40-question sample file is kept (finalize_expanded_benchmark.py still
# writes it) as the stratum the stability check re-grades; the answer/relevance
# judge reads the full set below.
JUDGE_QUESTIONS = EXPANDED_QUESTIONS
# The original 78 audited questions, kept as an isolation view: running them on
# the expanded v2 corpus separates "the expanded corpus changed the result" from
# "the expanded question set changed the result". Neither the corpus expansion
# nor the question expansion on its own should be able to explain a shift in the
# re-ranking ordering.
ORIGINAL_VALIDATED = str(BASE / "result" / "emnlp_full_results_20260427_gpu_final"
                         / "paper_questions_validated.jsonl")

# Modes for the expanded retrieval comparison (no generation: fast, GPU only).
# `rerank_llm` belongs here: the paper's contributions paragraph describes the
# re-ranker family as spanning "two benchmark scales (78 and 155 questions)",
# and the re-ranker table (`rev_table_rerankers.csv`) has a column per view for
# every other re-ranker. Leaving the LLM arm out of this batch left its
# expanded-benchmark and corpus-isolation cells empty, so the one claim the
# family is introduced for -- that capacity and domain alignment recover the
# loss -- could not be read off it at either scale.
RETRIEVAL_MODES = ",".join([
    "control_dense_only", "bm25_only", "bm25_base",
    "hybrid_bm25", "rrf_hybrid", "rrf_hybrid_rerank",
    "baseline", "rerank",
    "rerank_bge_base", "rerank_bge_m3", "rerank_medcpt", "rerank_llm",
    "rerank_source_aware",
])

# Modes for the answer-level LLM judgement (generation on, evidence saved).
# `rerank_bge_m3` is here because it is the configuration the retrieval results
# single out: it is the one re-ranker that does not lose to the non-re-ranked
# baseline on the expanded benchmark, and the paper's positive claim rests on it.
# Leaving it out of the answer-level evaluation meant the judged set could not
# speak to the system the retrieval half of the paper argues for -- every other
# judged arm is one the retrieval results already show to be worse.
JUDGE_MODES = ("baseline,rerank,rrf_hybrid,rerank_bge_base,rerank_medcpt,"
               "rerank_bge_m3,rerank_source_aware")


def _batches():
    b = []
    # (stem, corpus, questions, modes, generation, extra_env)
    b.append(("p4_expanded_retrieval", EXPANDED_CORPUS, EXPANDED_QUESTIONS,
              RETRIEVAL_MODES, False, dict(TUNED_BM25)))
    b.append(("p4_iso_v2corpus_78q", EXPANDED_CORPUS, ORIGINAL_VALIDATED,
              RETRIEVAL_MODES, False, dict(TUNED_BM25)))
    b.append(("p4_expanded_judge_answers", EXPANDED_CORPUS, JUDGE_QUESTIONS,
              JUDGE_MODES, True, {"SAVE_EVIDENCE_TEXTS": "1", **TUNED_BM25}))
    return b


def batch_complete(stem: str, modes: str) -> bool:
    """A batch is complete only when every per-mode output file exists and is non-empty."""
    for mode in [m.strip() for m in modes.split(",") if m.strip()]:
        path = OUT / f"{stem}_{mode}.csv"
        if not path.exists() or path.stat().st_size == 0:
            return False
    return True


def run_batch(stem, corpus, questions, modes, generation, extra):
    out_file = OUT / f"{stem}.csv"
    settings = OUT / f"{stem}_settings.csv"
    env_overrides = {
        "CORPUS_FILE": corpus,
        "QUESTIONS_FILE": questions,
        "RUN_EXPERIMENTS": modes,
        "RUN_GENERATION": "1" if generation else "0",
        "OUTPUT_RESULTS_FILE": str(out_file),
        "EXPERIMENT_SETTINGS_FILE": str(settings),
        "EXPERIMENT_OUTPUT_DIR": str(OUT),
        "EXPERIMENT_OUTPUT_PREFIX": stem,
    }
    env_overrides.update({k: str(v) for k, v in extra.items()})
    env = os.environ.copy()
    env.update(env_overrides)
    print(f"\n{'=' * 70}\n=== {stem} ===\n  corpus={corpus}\n  questions={questions}\n"
          f"  modes={modes}\n  generation={generation}\n  extra={extra}", flush=True)
    t0 = time.time()
    r = subprocess.run([sys.executable, str(BASE / "run_rag_eval.py")], env=env, cwd=BASE)
    dt = time.time() - t0
    ok = r.returncode == 0
    print(f"  -> {'OK' if ok else f'FAILED(exit {r.returncode})'} in {dt:.0f}s", flush=True)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", type=str, default=None)
    ap.add_argument("--no-skip", action="store_true")
    args = ap.parse_args()

    batches = _batches()
    if args.only:
        batches = [b for b in batches if b[0] == args.only]
        if not batches:
            print(f"Unknown batch stem: {args.only}")
            sys.exit(1)

    print(f"Total batches: {len(batches)}")
    failed = []
    for (stem, corpus, questions, modes, generation, extra) in batches:
        if args.dry_run:
            print(f"  {stem}: CORPUS={corpus} QUESTIONS={questions} "
                  f"MODES={modes} GEN={generation} EXTRA={extra}")
            continue
        if not args.no_skip and batch_complete(stem, modes):
            print(f"\n=== {stem} ===\n  -> SKIP (already complete)", flush=True)
            continue
        if not run_batch(stem, corpus, questions, modes, generation, extra):
            failed.append(stem)

    print(f"\nDone. Failed batches: {failed or 'none'}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
