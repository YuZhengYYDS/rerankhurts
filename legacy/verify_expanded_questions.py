"""Automated answerability screening for the expanded question set.

Reviewer 3 asked how the benchmark audit was performed and whether the gold
labels were independently verified. This script performs a *reproducible,
automatic* screening pass over every expanded question:

  * gather the evidence for the question's gold PDQ page -- by default the
    page's entire excerpt set, optionally just the k chunks most similar to
    the question,
  * ask the LLM judge whether that evidence actually contains enough
    information to answer the question (answerable_from_page),
  * ask whether the question is disease-specific rather than generic
    (disease_specific),
  * and, as a cross-check, record where the gold page ranks when retrieving
    from the FULL v2 corpus (gold_page_rank_in_corpus).

Why the full-page default matters: the benchmark scores retrieval at the
*gold-URL page level*, so an item is valid when the gold PAGE contains the
answer -- not merely when the five chunks most similar to the question happen
to contain it. Showing 5 of a 40-chunk page under-samples the page and yields
false negatives: the judge reports "the excerpts do not mention X" for a page
that does discuss X, in a section the sampler never reached. Pass
`--excerpt-mode topk` to reproduce that narrower, stricter screen.

The output fills the columns of `questions_expanded_review.csv` so a human
reviewer only has to confirm or overturn the automatic verdict rather than
start from an empty checklist.

IMPORTANT: this is automatic LLM-based screening, NOT human annotation. It is
recorded as `annotation_source=llm_screening_automatic` and must be described
as such in the paper.

Usage:
    # Full-page screen. Reuses the gold ranks from an earlier top-k run, so no
    # embedding pass (and no GPU) is required.
    python -m legacy.verify_expanded_questions --excerpt-mode full \
        --rank-source questions_expanded_review_filled.csv \
        --out questions_expanded_review_filled_full.csv
"""
import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "BAAI/bge-small-en-v1.5")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
TOP_K = int(os.getenv("SCREEN_TOP_K", "5"))
MAX_CHUNKS_SHOWN = int(os.getenv("SCREEN_MAX_CHUNKS", "80"))
EXCERPT_CHARS = int(os.getenv("SCREEN_EXCERPT_CHARS", "700"))
SLEEP_BETWEEN = float(os.getenv("SCREEN_SLEEP", "0"))


def load_jsonl(path: Path) -> List[Dict]:
    rows = []
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


# Two strictness settings. "strict" is the acceptance criterion for the
# benchmark; "lenient" reproduces the original wording so the two can be
# compared and the effect of the wording separated from the effect of showing
# the whole page.
STRICT_CLAUSE = (
    "Be strict: if the page genuinely lacks the treatment detail the question "
    "asks for, mark answerable_from_page false. A passing mention, a forward "
    "reference to another section, or a related-but-different clinical setting "
    "does not count as answerable. "
)
LENIENT_CLAUSE = (
    "Be strict: if the excerpts are only tangentially related, mark "
    "answerable_from_page false. "
)

# NOTE: concatenated rather than str.format()-ed -- the literal JSON braces in
# the schema line would otherwise be parsed as format fields and raise KeyError.
SYSTEM_PROMPT_HEAD = (
    "You are auditing an oncology QA benchmark for retrieval evaluation. "
    "You will be shown a question and excerpts taken from ONE NCI/PDQ guideline "
    "page. Judge two things:\n"
    "1. answerable_from_page: does the page contain enough specific treatment "
    "information to answer the question? (true/false)\n"
    "2. disease_specific: is the question specific to this disease and its "
    "treatment, rather than a generic oncology question that any cancer page "
    "could answer? (true/false)\n"
)
SYSTEM_PROMPT_TAIL = (
    "Return ONLY JSON: {\"answerable_from_page\": bool, \"disease_specific\": bool, "
    "\"reason\": \"<one short sentence>\"}"
)


def system_prompt(variant: str) -> str:
    clause = STRICT_CLAUSE if variant == "strict" else LENIENT_CLAUSE
    return SYSTEM_PROMPT_HEAD + clause + SYSTEM_PROMPT_TAIL

EVIDENCE_FRAMING = {
    "full": ("Excerpts covering the question's gold guideline page "
             "(the page's full excerpt set):"),
    "topk": ("Excerpts from the question's gold guideline page "
             "(the chunks most similar to the question):"),
}


def judge(client: OpenAI, question: str, excerpts: str, mode: str, variant: str) -> Dict:
    user_prompt = (
        f"Question:\n{question}\n\n"
        f"{EVIDENCE_FRAMING[mode]}\n{excerpts}\n\n"
        "Return the JSON verdict."
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            response_format={"type": "json_object"},
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt(variant)},
                {"role": "user", "content": user_prompt},
            ],
        )
        parsed = json.loads(resp.choices[0].message.content)
        return {
            "answerable_from_page": bool(parsed.get("answerable_from_page")),
            "disease_specific": bool(parsed.get("disease_specific")),
            "reason": str(parsed.get("reason", ""))[:300],
        }
    except Exception as exc:  # pragma: no cover - network best effort
        return {
            "answerable_from_page": None,
            "disease_specific": None,
            "reason": f"judge_error: {type(exc).__name__}",
        }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="corpus_chunks_v2.jsonl")
    ap.add_argument("--questions", default="questions_expanded.jsonl")
    ap.add_argument("--out", default="questions_expanded_review_filled.csv")
    ap.add_argument("--excerpt-mode", choices=["full", "topk"], default="full",
                    help="'full' shows the gold page's entire excerpt set (default; "
                         "correct for a page-level gold standard). 'topk' shows only "
                         "the k chunks most similar to the question.")
    ap.add_argument("--rank-source", default=None,
                    help="CSV from an earlier screening run whose "
                         "gold_page_rank_in_corpus / gold_page_chunks columns should "
                         "be reused, so no embedding pass (and no GPU) is needed.")
    ap.add_argument("--prompt-variant", choices=["strict", "lenient"], default="strict",
                    help="'strict' (default) is the benchmark acceptance criterion; "
                         "'lenient' reproduces the original wording for comparison.")
    args = ap.parse_args()

    corpus = load_jsonl(BASE_DIR / args.corpus)
    questions = load_jsonl(BASE_DIR / args.questions)
    print(f"Corpus chunks: {len(corpus)} | questions: {len(questions)} | "
          f"excerpt_mode: {args.excerpt_mode}")

    by_url: Dict[str, List[int]] = {}
    for i, c in enumerate(corpus):
        by_url.setdefault(c.get("url", ""), []).append(i)

    cached: Dict[str, pd.Series] = {}
    if args.rank_source:
        src = BASE_DIR / args.rank_source
        if src.exists():
            prev = pd.read_csv(src)
            cached = {str(r["qid"]): r for _, r in prev.iterrows()}
            print(f"Reusing gold ranks for {len(cached)} questions from {src.name}")
        else:
            print(f"!! --rank-source {args.rank_source} not found; will embed instead")

    need_embed = not cached
    emb = q_emb = None
    if need_embed:
        from sentence_transformers import SentenceTransformer
        embed = SentenceTransformer(EMBED_MODEL_NAME, device="cuda")
        texts = [c["text"] for c in corpus]
        emb = embed.encode(texts, batch_size=64, normalize_embeddings=True,
                           convert_to_numpy=True, show_progress_bar=True)
        q_emb = embed.encode([q["question"] for q in questions], batch_size=32,
                             normalize_embeddings=True, convert_to_numpy=True)

    client = build_client()
    rows = []
    for qi, q in enumerate(tqdm(questions, desc="screening")):
        gold = q.get("gold_url", "")
        gold_idx = by_url.get(gold, [])

        # Cross-check: rank of the gold page in the FULL corpus.
        if need_embed:
            sims = emb @ q_emb[qi]
            gold_rank: Optional[int] = None
            for rank, idx in enumerate(np.argsort(-sims), start=1):
                if corpus[int(idx)].get("url") == gold:
                    gold_rank = rank
                    break
        else:
            sims = None
            prev = cached.get(str(q.get("qid")))
            gold_rank = None
            if prev is not None and pd.notna(prev.get("gold_page_rank_in_corpus")):
                gold_rank = int(prev["gold_page_rank_in_corpus"])

        if gold_idx:
            if need_embed:
                order = np.argsort(-sims[gold_idx])
            else:
                order = np.arange(len(gold_idx))
            order = order[:TOP_K] if args.excerpt_mode == "topk" else order[:MAX_CHUNKS_SHOWN]
            picked = [gold_idx[int(o)] for o in order]
            excerpts = "\n\n".join(f"[{n+1}] {corpus[i]['text'][:EXCERPT_CHARS]}"
                                   for n, i in enumerate(picked))
        else:
            picked = []
            excerpts = "(no chunks found for the gold URL)"

        verdict = judge(client, q["question"], excerpts, args.excerpt_mode,
                        args.prompt_variant)

        rows.append({
            "qid": q.get("qid"),
            "topic": q.get("topic"),
            "question": q.get("question"),
            "gold_url": gold,
            "gold_page_chunks": len(gold_idx),
            "gold_page_chunks_shown": len(picked),
            "gold_page_rank_in_corpus": gold_rank,
            "answerable_from_page": verdict["answerable_from_page"],
            "disease_specific": verdict["disease_specific"],
            "screening_reason": verdict["reason"],
            "excerpt_mode": args.excerpt_mode,
            "prompt_variant": args.prompt_variant,
            "annotation_source": "llm_screening_automatic",
            "human_verified": False,
        })
        if SLEEP_BETWEEN:
            time.sleep(SLEEP_BETWEEN)

    out_df = pd.DataFrame(rows)
    out_path = BASE_DIR / args.out
    out_df.to_csv(out_path, index=False, encoding="utf-8-sig")

    n_ans = int((out_df["answerable_from_page"] == True).sum())  # noqa: E712
    n_dis = int((out_df["disease_specific"] == True).sum())  # noqa: E712
    print(f"\nSaved: {out_path}")
    print(f"  excerpt_mode         : {args.excerpt_mode}")
    print(f"  answerable_from_page : {n_ans}/{len(out_df)}")
    print(f"  disease_specific     : {n_dis}/{len(out_df)}")
    print("  NOTE: automatic screening only - NOT human annotation.")


if __name__ == "__main__":
    main()
