"""Drop benchmark questions whose text names their own gold document.

A retrieval benchmark item is only informative if finding the right page is the
task. Items like

    "For patients with resected stage III melanoma and a BRAF V600E/K mutation,
     what adjuvant systemic therapy options are recommended in the NCI PDQ
     melanoma treatment summary?"

hand the retriever the answer document inside the query: a keyword system that
matches "NCI PDQ melanoma treatment summary" wins the item without doing any
retrieval. All 32 items that leaked this way belong to the expanded batch (0 of
the original 78 audited questions do this), and on them the plain dense baseline
scores 0.988 nDCG@10 against 0.880 on the rest of the expanded set -- they are
near-trivially retrievable and inflate the expanded benchmark.

They are removed rather than reworded. A rule-based strip leaves broken grammar
("...treatment options are?"), and having a model rewrite them would edit the
benchmark's content, which is not something a reader could verify from the
released artifact.

The removal is recorded item by item in a report, so the drop is auditable
rather than silent.

Usage:
    python -m legacy.purge_leaky_questions --dry-run
    python -m legacy.purge_leaky_questions
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

# Input and output are different files on purpose. They were briefly the same
# one -- the purge was run in place and `questions_expanded_full_validated.jsonl`
# came to hold the purged set -- which quietly turned this step into a no-op: a
# re-run read its own output, reported "Leaky: none", and left no way to tell
# that 32 items had ever been dropped. The pre-purge set is kept under its own
# name so the 187 -> 155 step is visible and re-checkable.
SOURCE = BASE / "questions_expanded_full_prepurge.jsonl"
OUT = BASE / "questions_expanded_full_validated.jsonl"
REPORT = BASE / "questions_expanded_leakfree_report.csv"

# Every way an item can name its own source document. Word boundaries matter:
# unanchored, "nci" matches "sequencing" and reports a false leak.
#
#   "the NCI PDQ <disease> treatment summary"
#   "the NCI PDQ health-professional treatment summary"
#   "according to this page" / "does this page describe"
#
# The last form leaks by presupposition -- it tells the reader there is exactly
# one page in play, and it is the gold one -- so it is matched too.
LEAK_PATTERN = re.compile(
    r"\bpdq\b|treatment\s+summary|\bnci\b|\bthis\s+(?:page|document|summary)\b",
    re.I,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=str(SOURCE))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--report", default=str(REPORT))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src = Path(args.source)
    if not src.exists():
        raise SystemExit(f"Question set not found: {src}")

    questions = [json.loads(line) for line in src.read_text(encoding="utf-8").splitlines() if line.strip()]

    kept, dropped = [], []
    for q in questions:
        text = q.get("question", "") or ""
        match = LEAK_PATTERN.search(text)
        if match:
            dropped.append((q, match.group(0)))
        else:
            kept.append(q)

    # A silent drop is indistinguishable from a question set that was always this
    # size, so anything removed has to be reported.
    if dropped:
        by_source = {}
        for q, _ in dropped:
            key = q.get("construction_source", "?")
            by_source[key] = by_source.get(key, 0) + 1
        print(f"Source      : {src.name} ({len(questions)} questions)")
        print(f"Leaky       : {len(dropped)} removed")
        for key, n in sorted(by_source.items()):
            print(f"                {key}: {n}")
        print(f"Clean       : {len(kept)} kept -> {Path(args.out).name}")
    else:
        print(f"Source      : {src.name} ({len(questions)} questions)")
        print("Leaky       : none")

    if not args.dry_run:
        out = Path(args.out)
        with out.open("w", encoding="utf-8") as fh:
            for q in kept:
                fh.write(json.dumps(q, ensure_ascii=False) + "\n")

        with Path(args.report).open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["qid", "topic", "construction_source", "matched_span", "question"])
            for q, span in dropped:
                writer.writerow([q.get("qid", ""), q.get("topic", ""),
                                 q.get("construction_source", ""), span,
                                 q.get("question", "")])
        print(f"\nWrote {out}")
        print(f"Wrote {Path(args.report)}")

    if not kept:
        sys.exit("Refusing to write an empty question set.")


if __name__ == "__main__":
    main()
