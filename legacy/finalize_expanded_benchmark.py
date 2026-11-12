"""Turn the automatic screening verdicts into the locked expanded benchmark.

The expanded questions were drafted from the cancer type and the gold page URL,
without showing the model the page text -- so some of them ask about treatment
details the assigned page does not actually cover. The screening pass in
`verify_expanded_questions.py` finds those; this script applies its verdict and
writes the benchmark files the experiment drivers consume.

Acceptance criterion (`--criterion`, default `strict`): a question enters the
benchmark only if the full-page screen judged it answerable_from_page. The
stricter wording is deliberate -- a false negative merely drops a usable
question, while a false positive puts an item in the benchmark whose gold page
cannot support it, which corrupts every retrieval number computed on top.

Outputs:
    questions_expanded_validated.jsonl        accepted new questions only
    questions_expanded_full_validated.jsonl   78 audited + accepted new
    questions_judge_sample_validated.jsonl    stratified answer-eval sample
    questions_expanded_review_final.csv       human checklist w/ auto verdicts

The checklist records the question-answerability screening verdicts.
The completed expert review of the 155-question fact and source-evidence
annotation rubric is delivered in experiments/supplements/oncology_coverage_v1/reviews/.

Usage:
    python -m legacy.finalize_expanded_benchmark --criterion strict
    python -m legacy.finalize_expanded_benchmark --criterion lenient --judge-sample 40
"""
import argparse
import json
import random
from pathlib import Path
from typing import Dict, List

import pandas as pd

# One definition of "this question names its own gold document", shared with the
# standalone audit tool, so the benchmark and its checker cannot drift apart.
from legacy.purge_leaky_questions import LEAK_PATTERN

from rerankhuts.paths import oncology_path


BASE_DIR = Path(__file__).resolve().parents[1]

AUDITED78 = BASE_DIR / "result/emnlp_full_results_20260427_gpu_final/paper_questions_validated.jsonl"

# Two question-drafting rounds feed the expanded benchmark, each screened by its
# own run of verify_expanded_questions.py:
#   v1 -- drafted from the cancer type + gold URL only (the model never saw the
#         page text), so the screen rejects a large share of it.
#   v2 -- drafted with the full gold page in the prompt (build_grounded_questions.py),
#         which is the fix for v1's root cause.
# Both are screened with the same full-page protocol before entering the pool.
SOURCES = [
    (oncology_path("questions_expanded.jsonl", root=BASE_DIR), {
        "strict": oncology_path("questions_expanded_review_filled_full.csv", root=BASE_DIR),
        "lenient": oncology_path("questions_expanded_review_filled_full_lenient.csv", root=BASE_DIR),
        "topk": oncology_path("questions_expanded_review_filled.csv", root=BASE_DIR),
    }),
    (oncology_path("questions_expanded_v2.jsonl", root=BASE_DIR), {
        "strict": oncology_path("questions_expanded_v2_screening.csv", root=BASE_DIR),
        "lenient": oncology_path("questions_expanded_v2_screening.csv", root=BASE_DIR),
        "topk": oncology_path("questions_expanded_v2_screening.csv", root=BASE_DIR),
    }),
]
ACCEPT_COLUMN = "answerable_from_page"


def load_jsonl(path: Path) -> List[Dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def save_jsonl(path: Path, rows: List[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_judge_sample(rows: List[Dict], n: int, seed: int) -> List[Dict]:
    """Stratified draw across topics, so no cancer type dominates the sample."""
    by_topic: Dict[str, List[Dict]] = {}
    for row in rows:
        by_topic.setdefault(row["topic"], []).append(row)

    rng = random.Random(seed)
    topics = sorted(by_topic)
    for t in topics:
        rng.shuffle(by_topic[t])

    # Largest-remainder allocation proportional to topic size.
    total = len(rows)
    quota = {t: n * len(by_topic[t]) / total for t in topics}
    take = {t: min(int(quota[t]), len(by_topic[t])) for t in topics}
    remainder = sorted(topics, key=lambda t: quota[t] - take[t], reverse=True)
    i = 0
    while sum(take.values()) < n and remainder:
        t = remainder[i % len(remainder)]
        if take[t] < len(by_topic[t]):
            take[t] += 1
        i += 1
        if i > 10 * len(remainder):
            break

    sample = []
    for t in topics:
        sample.extend(by_topic[t][: take[t]])
    sample.sort(key=lambda r: (r["topic"], r["qid"]))
    return sample


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--criterion", choices=["strict", "lenient", "topk"],
                    default="strict")
    ap.add_argument("--judge-sample", type=int, default=40)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    oncology_path("questions_expanded_review_final.csv", root=BASE_DIR).parent.mkdir(parents=True, exist_ok=True)

    expanded: Dict[str, Dict] = {}
    accepted: set = set()
    screens: List[pd.DataFrame] = []
    for qfile, screen_files in SOURCES:
        screen_path = screen_files[args.criterion]
        if not qfile.exists():
            print(f"  -- source not found, skipping: {qfile.name}")
            continue
        if not screen_path.exists():
            raise SystemExit(
                f"Screening file not found for {qfile.name}: {screen_path}\n"
                f"Run verify_expanded_questions.py on it first "
                f"(criterion '{args.criterion}').")
        screen = pd.read_csv(screen_path)
        take = set(screen.loc[screen[ACCEPT_COLUMN] == True, "qid"].astype(str))  # noqa: E712
        print(f"Criterion '{args.criterion}' ({screen_path.name}): "
              f"{len(take)}/{len(screen)} questions accepted")
        accepted |= take
        screens.append(screen)
        for row in load_jsonl(qfile):
            expanded[str(row["qid"])] = row

    screen = pd.concat(screens, ignore_index=True)
    audited = load_jsonl(AUDITED78)

    kept = [expanded[q] for q in expanded if q in accepted]
    # Stamp each question with how it was built and what accepted it, so the
    # released benchmark explains its own provenance instead of relying on this
    # script being at hand.
    for row in kept:
        row.setdefault("construction_source", "drafted_from_topic_and_url")
        row["screening_protocol"] = (
            "full_gold_page_excerpts; strict prompt; "
            "automatic LLM screen (not human annotation)")
        row["screening_criterion"] = args.criterion
        row["screening_answerable_from_page"] = True
    for row in audited:
        row.setdefault("construction_source", "audited_subset_original")
    dropped = [expanded[q] for q in expanded if q not in accepted]

    # A question that names its own gold document is not a retrieval item: the
    # query text hands the retriever the page it is meant to find, so a keyword
    # system wins it without retrieving anything. The `grounded_in_gold_page`
    # round drafted with the page in the prompt, and the habit it fell into was
    # to write the source into the question ("...according to the NCI PDQ
    # melanoma treatment summary?"); "according to this page" leaks the same way
    # by presupposition. Those items are dropped, not reworded -- see
    # purge_leaky_questions.py -- and every drop is recorded below.
    leaky = [r for r in audited + kept if LEAK_PATTERN.search(r.get("question", "") or "")]
    if leaky:
        audited = [r for r in audited if not LEAK_PATTERN.search(r.get("question", "") or "")]
        kept = [r for r in kept if not LEAK_PATTERN.search(r.get("question", "") or "")]
        pd.DataFrame([{
            "qid": r.get("qid", ""),
            "topic": r.get("topic", ""),
            "construction_source": r.get("construction_source", ""),
            "question": r.get("question", ""),
        } for r in leaky]).to_csv(
            oncology_path("questions_expanded_leakfree_report.csv", root=BASE_DIR),
            index=False, encoding="utf-8-sig")
        print(f"  source-naming items dropped: {len(leaky)} "
              f"-> report in questions_expanded_leakfree_report.csv")

    # Keep file order stable (qid ascending) regardless of screening order.
    kept.sort(key=lambda r: int(str(r["qid"]).lstrip("q")))

    pool = audited + kept
    sample = build_judge_sample(pool, args.judge_sample, args.seed)

    save_jsonl(oncology_path("questions_expanded_validated.jsonl", root=BASE_DIR), kept)
    save_jsonl(oncology_path("questions_expanded_full_validated.jsonl", root=BASE_DIR), pool)
    save_jsonl(oncology_path("questions_judge_sample_validated.jsonl", root=BASE_DIR), sample)

    review = screen.copy()
    review["included_in_benchmark"] = review["qid"].astype(str).isin(accepted)
    review.to_csv(oncology_path("questions_expanded_review_final.csv", root=BASE_DIR),
                  index=False, encoding="utf-8-sig")

    print(f"  accepted new questions : {len(kept)}")
    print(f"  dropped (auto-rejected): {len(dropped)}")
    print(f"  benchmark pool         : {len(pool)}  (78 audited + {len(kept)} new)")
    print(f"  judge sample           : {len(sample)} across "
          f"{len({r['topic'] for r in sample})} topics")
    print()
    print(f"  dropped qids: {', '.join(str(r['qid']) for r in dropped) or 'none'}")
    print()
    print("  Question-answerability screening records have been written. "
          "questions_expanded_review_final.csv is the checklist for expert review.")


if __name__ == "__main__":
    main()
