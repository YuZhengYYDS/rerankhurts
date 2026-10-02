"""Draft expanded-benchmark questions that are grounded in the gold page text.

The first expansion round asked the model for questions given only the cancer
type and the gold page URL -- it never saw the page. The automatic answerability
screen then rejected a large share of those questions, because models happily
invent plausible treatment questions for details the assigned page does not
cover (e.g. asking about desmoid tumors on a general soft-tissue-sarcoma page).

This script fixes the construction step rather than only filtering its output:
it places the full text of the target PDQ page in the prompt and requires each
question to be answerable from that text alone. Existing questions for the
cancer type are passed in as a do-not-repeat list.

Output is a candidate set that still has to pass the same full-page screen in
`verify_expanded_questions.py` before it can enter the benchmark -- generation
grounding and verification stay separate steps on purpose.

Usage:
    python -m legacy.build_grounded_questions --per-cancer 8
    python -m legacy.build_grounded_questions --topics Prostate,Sarcoma
"""
import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

CORPUS = BASE_DIR / "corpus_chunks_v2.jsonl"
EXISTING = BASE_DIR / "questions_expanded.jsonl"
OUT_QUESTIONS = BASE_DIR / "questions_expanded_v2.jsonl"

MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
MAX_PAGE_CHARS = int(os.getenv("GROUNDED_MAX_PAGE_CHARS", "60000"))

NEW_CANCERS: List[tuple] = [
    ("Prostate", "https://www.cancer.gov/types/prostate/hp/prostate-treatment-pdq"),
    ("Ovarian", "https://www.cancer.gov/types/ovarian/hp/ovarian-epithelial-treatment-pdq"),
    ("Pancreatic", "https://www.cancer.gov/types/pancreatic/hp/pancreatic-treatment-pdq"),
    ("Melanoma", "https://www.cancer.gov/types/skin/hp/melanoma-treatment-pdq"),
    ("Kidney", "https://www.cancer.gov/types/kidney/hp/kidney-treatment-pdq"),
    ("Bladder", "https://www.cancer.gov/types/bladder/hp/bladder-treatment-pdq"),
    ("Gastric", "https://www.cancer.gov/types/stomach/hp/stomach-treatment-pdq"),
    ("Esophageal", "https://www.cancer.gov/types/esophageal/hp/esophageal-treatment-pdq"),
    ("Cervical", "https://www.cancer.gov/types/cervical/hp/cervical-treatment-pdq"),
    ("Endometrial", "https://www.cancer.gov/types/uterine/hp/endometrial-treatment-pdq"),
    ("Liver", "https://www.cancer.gov/types/liver/hp/adult-liver-treatment-pdq"),
    ("Brain", "https://www.cancer.gov/types/brain/hp/adult-brain-treatment-pdq"),
    ("Thyroid", "https://www.cancer.gov/types/thyroid/hp/thyroid-treatment-pdq"),
    ("Myeloma", "https://www.cancer.gov/types/myeloma/hp/myeloma-treatment-pdq"),
    ("Lymphoma", "https://www.cancer.gov/types/lymphoma/hp/adult-nhl-treatment-pdq"),
    ("Sarcoma", "https://www.cancer.gov/types/soft-tissue-sarcoma/hp/adult-soft-tissue-treatment-pdq"),
]

SYSTEM = (
    "You are building a disease-specific oncology treatment question benchmark. "
    "You will be given the full text of ONE NCI/PDQ health-professional treatment "
    "page. Write questions that a clinician could answer using ONLY this page.\n"
    "Rules:\n"
    "- Every question must target treatment detail the page actually states: a "
    "regimen, a sequencing decision, a biomarker-directed option, a stage-specific "
    "recommendation, or the role of surgery/radiation.\n"
    "- Name the clinical setting precisely (line of therapy, stage, biomarker "
    "status) so the answer is unambiguous.\n"
    "- Do NOT ask about a different disease or a different PDQ page. If the page "
    "only forward-references another topic, do not ask about that topic.\n"
    "- Do NOT repeat any question in the do-not-repeat list (paraphrases count).\n"
    "Return ONLY JSON: {\"questions\": [<string>, ...]}"
)


def load_jsonl(path: Path) -> List[Dict]:
    rows = []
    if not path.exists():
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def build_client() -> OpenAI:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    if not api_key:
        raise ValueError("Missing DEEPSEEK_API_KEY in .env")
    return OpenAI(api_key=api_key, base_url=base_url)


def page_text(chunks: List[Dict]) -> str:
    """Full page text in chunk order, truncated to the model's workable budget."""
    joined = "\n\n".join(c["text"] for c in chunks)
    if len(joined) > MAX_PAGE_CHARS:
        joined = joined[:MAX_PAGE_CHARS]
    return joined


def draft(client: OpenAI, topic: str, text: str, avoid: List[str], n: int) -> List[str]:
    avoid_block = "\n".join(f"- {q}" for q in avoid) if avoid else "(none)"
    user = (
        f"Cancer type: {topic}\n\n"
        f"Full text of the gold NCI/PDQ treatment page:\n{text}\n\n"
        f"Do-not-repeat list of existing questions for this cancer type:\n{avoid_block}\n\n"
        f"Write {n} new distinct treatment questions that this page can answer. "
        f"Return JSON: {{\"questions\": [...]}}"
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            response_format={"type": "json_object"},
            temperature=0.7,
            messages=[{"role": "system", "content": SYSTEM},
                      {"role": "user", "content": user}],
        )
        return json.loads(resp.choices[0].message.content).get("questions", [])
    except Exception as exc:
        print(f"  !! {topic}: {type(exc).__name__}: {exc}")
        return []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-cancer", type=int, default=8)
    ap.add_argument("--topics", default=None,
                    help="Comma-separated topic subset; default is all new cancer types.")
    args = ap.parse_args()

    corpus = load_jsonl(CORPUS)
    existing = load_jsonl(EXISTING)
    by_url: Dict[str, List[Dict]] = {}
    for c in corpus:
        by_url.setdefault(c.get("url", ""), []).append(c)

    existing_by_topic: Dict[str, List[str]] = {}
    for q in existing:
        existing_by_topic.setdefault(q.get("topic", ""), []).append(q["question"])

    start_num = max((int(str(q["qid"]).lstrip("q"))
                     for q in existing if str(q["qid"]).lstrip("q").isdigit()),
                    default=181) + 1

    wanted = {t.strip() for t in args.topics.split(",")} if args.topics else None
    targets = [(t, u) for t, u in NEW_CANCERS if wanted is None or t in wanted]
    if not targets:
        raise SystemExit("No matching cancer types.")

    client = build_client()
    rows, report = [], []
    next_num = start_num

    for topic, url in tqdm(targets, desc="drafting grounded questions"):
        chunks = by_url.get(url, [])
        if not chunks:
            print(f"  !! {topic}: no chunks in corpus for {url}")
            report.append({"topic": topic, "url": url, "chunks": 0, "drafted": 0})
            continue
        qs = draft(client, topic, page_text(chunks),
                   existing_by_topic.get(topic, []), args.per_cancer)
        kept = 0
        for q in qs:
            q = str(q).strip()
            if not q:
                continue
            q = q.rstrip("?") + "?"
            rows.append({"qid": f"q{next_num}", "question": q, "topic": topic,
                         "gold_url": url, "gold_urls": [url],
                         "construction_source": "grounded_in_gold_page"})
            next_num += 1
            kept += 1
        report.append({"topic": topic, "url": url, "chunks": len(chunks),
                       "page_chars": len(page_text(chunks)), "drafted": kept})
        print(f"  {topic}: {kept} questions from {len(chunks)} chunks "
              f"({len(page_text(chunks))} chars)")
        time.sleep(0.3)

    with open(OUT_QUESTIONS, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"\nDrafted {len(rows)} grounded questions -> {OUT_QUESTIONS.name}")
    print(f"qids q{start_num}..q{next_num - 1}")
    print("\nNext: screen them with")
    print(f"  python -m legacy.verify_expanded_questions --questions {OUT_QUESTIONS.name} "
          f"--corpus corpus_chunks_v2.jsonl --excerpt-mode full --prompt-variant strict "
          f"--out questions_expanded_v2_screening.csv")
    print("(No --rank-source here: these are new qids, so the gold-page rank "
          "cross-check has to be computed by embedding.)")


if __name__ == "__main__":
    main()
