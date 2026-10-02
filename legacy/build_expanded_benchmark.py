"""Expand the oncology benchmark: new NCI/PDQ pages + new treatment questions.

Two steps, run in order:
    python -m legacy.build_expanded_benchmark --fetch
        Fetch new NCI treatment PDQ pages, chunk them with the SAME logic as
        build_corpus.py, and append to corpus_chunks_v2.jsonl (a copy of v1
        plus the new pages, all under source_name "nci_guidelines").

    python -m legacy.build_expanded_benchmark --questions
        Use DeepSeek to draft disease-specific treatment questions per new
        cancer type, write questions_expanded.jsonl, and emit a human-review
        checklist (questions_expanded_review.csv) for gold-URL verification.

The review checklist is the human-in-the-loop step: an expert must confirm each
question is answerable from its gold PDQ page before the expanded set is locked.
"""
import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

from legacy import build_corpus  # reuse fetch_html / extract_paragraphs / make_chunk_records

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

ORIGINAL_CORPUS = BASE_DIR / "corpus_chunks_v1.jsonl"
EXPANDED_CORPUS = BASE_DIR / "corpus_chunks_v2.jsonl"
ORIGINAL_QUESTIONS = BASE_DIR / "questions.jsonl"
EXPANDED_QUESTIONS = BASE_DIR / "questions_expanded.jsonl"
REVIEW_CHECKLIST = BASE_DIR / "questions_expanded_review.csv"

# (topic_label, url_slug, pdq_url, question keyword hints)
NEW_CANCERS: List[Tuple[str, str, str]] = [
    ("Prostate", "prostate", "https://www.cancer.gov/types/prostate/hp/prostate-treatment-pdq"),
    ("Ovarian", "ovarian", "https://www.cancer.gov/types/ovarian/hp/ovarian-epithelial-treatment-pdq"),
    ("Pancreatic", "pancreatic", "https://www.cancer.gov/types/pancreatic/hp/pancreatic-treatment-pdq"),
    ("Melanoma", "melanoma", "https://www.cancer.gov/types/skin/hp/melanoma-treatment-pdq"),
    ("Kidney", "kidney", "https://www.cancer.gov/types/kidney/hp/kidney-treatment-pdq"),
    ("Bladder", "bladder", "https://www.cancer.gov/types/bladder/hp/bladder-treatment-pdq"),
    ("Gastric", "gastric", "https://www.cancer.gov/types/stomach/hp/stomach-treatment-pdq"),
    ("Esophageal", "esophageal", "https://www.cancer.gov/types/esophageal/hp/esophageal-treatment-pdq"),
    ("Cervical", "cervical", "https://www.cancer.gov/types/cervical/hp/cervical-treatment-pdq"),
    ("Endometrial", "endometrial", "https://www.cancer.gov/types/uterine/hp/endometrial-treatment-pdq"),
    ("Liver", "liver", "https://www.cancer.gov/types/liver/hp/adult-liver-treatment-pdq"),
    ("Brain", "brain", "https://www.cancer.gov/types/brain/hp/adult-brain-treatment-pdq"),
    ("Thyroid", "thyroid", "https://www.cancer.gov/types/thyroid/hp/thyroid-treatment-pdq"),
    ("Myeloma", "myeloma", "https://www.cancer.gov/types/myeloma/hp/myeloma-treatment-pdq"),
    ("Lymphoma", "lymphoma", "https://www.cancer.gov/types/lymphoma/hp/adult-nhl-treatment-pdq"),
    ("Sarcoma", "sarcoma", "https://www.cancer.gov/types/soft-tissue-sarcoma/hp/adult-soft-tissue-treatment-pdq"),
]

NCI_SOURCE = {
    "name": "nci_guidelines",
    "role": "corpus",
    "type": "web_url_list",
    "license": "public_web",
    "notes": "Expanded NCI/PDQ treatment pages for the extended benchmark.",
}

QUESTIONS_PER_CANCER = 5


def build_client() -> OpenAI:
    import os
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    if not api_key:
        raise ValueError("Missing DEEPSEEK_API_KEY in .env")
    return OpenAI(api_key=api_key, base_url=base_url)


MODEL = "deepseek-chat"


def load_jsonl(path: Path) -> List[Dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def save_jsonl(path: Path, rows: List[Dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def cmd_fetch(args) -> None:
    original = load_jsonl(ORIGINAL_CORPUS)
    seen_urls = {row.get("url") for row in original}
    new_records: List[Dict] = []
    report: List[Dict] = []

    for topic, slug, url in NEW_CANCERS:
        if url in seen_urls:
            print(f"[SKIP] already in corpus: {url}")
            continue
        try:
            html = build_corpus.fetch_html(url)
            title, paragraphs = build_corpus.extract_paragraphs(html)
            if not paragraphs:
                raise ValueError("no treatment paragraphs extracted")
            records = build_corpus.make_chunk_records(NCI_SOURCE, url, title, url, paragraphs)
            new_records.extend(records)
            report.append({"topic": topic, "url": url, "status": "ok", "chunks": len(records), "title": title})
            print(f"[OK] {topic}: {len(records)} chunks from {url}")
        except Exception as exc:
            report.append({"topic": topic, "url": url, "status": f"fail: {type(exc).__name__}: {str(exc)[:120]}", "chunks": 0, "title": ""})
            print(f"[FAIL] {topic} {url}: {type(exc).__name__} {exc}")
        time.sleep(1.5)

    combined = original + new_records
    save_jsonl(EXPANDED_CORPUS, combined)
    pd.DataFrame(report).to_csv(BASE_DIR / "corpus_expansion_report.csv", index=False, encoding="utf-8-sig")
    print(f"\nTotal original chunks: {len(original)}")
    print(f"Total new chunks: {len(new_records)}")
    print(f"Expanded corpus: {len(combined)} -> {EXPANDED_CORPUS.name}")


def _generate_questions(client: OpenAI, topic: str, url: str, n: int) -> List[str]:
    system = (
        "You are building a disease-specific oncology treatment question benchmark. "
        "Generate clinical treatment questions that are answerable ONLY from the "
        "corresponding NCI PDQ health-professional treatment summary. Each question "
        "must be treatment-focused (regimens, sequencing, biomarkers, staging, "
        "refractory/recurrent management) and disease-specific — not a general "
        "oncology question. Return ONLY JSON: {\"questions\": [<string>, ...]}."
    )
    user = (
        f"Cancer type: {topic}\n"
        f"Gold source page: {url}\n\n"
        f"Generate {n} distinct treatment questions. Vary the treatment dimension "
        f"(first-line, second-line/refractory, biomarker-guided, stage-specific, "
        f"role of surgery/radiation)."
    )
    resp = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        temperature=0.7,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    try:
        return json.loads(resp.choices[0].message.content).get("questions", [])
    except Exception:
        return []


def cmd_questions(args) -> None:
    client = build_client()
    original = load_jsonl(ORIGINAL_QUESTIONS)
    used_qids = {row["qid"] for row in original}
    next_num = max(int(row["qid"][1:]) for row in original if row["qid"][1:].isdigit()) + 1

    new_rows: List[Dict] = []
    review_rows: List[Dict] = []

    for topic, slug, url in tqdm(NEW_CANCERS, desc="Generating questions"):
        qs = _generate_questions(client, topic, url, QUESTIONS_PER_CANCER)
        for q in qs:
            q = q.strip().rstrip("?") + "?"
            qid = f"q{next_num}"
            next_num += 1
            new_rows.append({"qid": qid, "question": q, "topic": topic, "gold_url": url, "gold_urls": [url]})
            review_rows.append({"qid": qid, "topic": topic, "question": q, "gold_url": url,
                                "answerable_from_page": "", "disease_specific": "", "reviewer_notes": ""})
        time.sleep(0.3)

    save_jsonl(EXPANDED_QUESTIONS, new_rows)
    pd.DataFrame(review_rows).to_csv(REVIEW_CHECKLIST, index=False, encoding="utf-8-sig")
    print(f"\nGenerated {len(new_rows)} questions -> {EXPANDED_QUESTIONS.name}")
    print(f"Review checklist -> {REVIEW_CHECKLIST.name}")
    print(f"New qids start at q{next_num - len(new_rows)}; {len(used_qids)} original questions kept separate.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--questions", action="store_true")
    args = ap.parse_args()

    if not args.fetch and not args.questions:
        ap.error("Pass --fetch and/or --questions")
    if args.fetch:
        cmd_fetch(args)
    if args.questions:
        cmd_questions(args)


if __name__ == "__main__":
    main()
