"""LLM-as-judge evaluation for the oncology RAG paper.

Scores model-generated answers (faithfulness / citation-support / helpfulness /
abstention-appropriateness) and graded evidence relevance (0/1/2) using the
DeepSeek chat model configured in `.env`.

IMPORTANT: the output is *automatic* LLM-based evaluation. It is NOT human
annotation and must be labeled as such in the paper (`annotation_source`
is set to `llm_judge_automatic` and `valid_for_human_eval_claim=False`).

Two subcommands:
    python -m legacy.llm_judge answer     --input results.csv --methods base,rr \
        --out answer_eval.csv [--sample N --seed 42]
    python -m legacy.llm_judge relevance  --input results.csv --methods base,rr \
        --out relevance_eval.csv [--sample N --seed 42 --top-k 4]

`--input` is a `run_rag_eval.py` combined output CSV. It must contain, per row:
    mode, qid, question, answer, insufficient_evidence,
    final_urls, final_titles, and (for `answer`) final_evidence_texts.
`final_evidence_texts` is only populated when the run set SAVE_EVIDENCE_TEXTS=1.
"""
import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI


def pmap(fn, items, workers):
    """Map `fn` over `items`, optionally concurrently.

    The judge issues one API call per judgement (200 for answers, ~800 for
    top-4 relevance), which is ~50 minutes sequentially. The OpenAI client is
    thread-safe, so a small pool is enough. Order is preserved so the output
    rows stay aligned with the input.
    """
    items = list(items)
    if workers <= 1:
        return [fn(item) for item in items]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(fn, items))

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


def build_client() -> OpenAI:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    if not api_key:
        raise ValueError("Missing DEEPSEEK_API_KEY in .env")
    return OpenAI(api_key=api_key, base_url=base_url)


MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def _chat(client, system, user):
    resp = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        temperature=0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content


def _parse_json(content):
    try:
        return json.loads(content)
    except Exception:
        return {}


ANSWER_SYSTEM = (
    "You are a clinical evaluator judging the quality of an oncology QA answer "
    "against the evidence actually provided to the model. Return ONLY a JSON "
    "object with integer keys: faithfulness (1-5), citation_support (1-5), "
    "helpfulness (1-5), abstention_ok (0 or 1), and a short string rationale. "
    "Score strictly: faithfulness = every clinical claim is supported by the "
    "evidence; citation_support = the answer aligns with the cited evidence; "
    "helpfulness = the answer addresses the question; abstention_ok = 1 if the "
    "model abstained when evidence was insufficient, or correctly answered when "
    "it was sufficient."
)


# How `run_rag_eval.py` joins the per-chunk evidence texts into one CSV cell.
# It is a module constant here because `stability` reverses the list, which
# means splitting on the same separator the writer used -- an inline literal in
# two files is how the two silently drift apart.
EVIDENCE_SEPARATOR = "\n\n====================\n\n"

# Characters of evidence the judge prompt carries. Chunks are 1500 chars each
# and a top-4 list runs to ~4.9k, so this is active on almost every row: the
# real judged prompts are already truncated, and anything past this is
# invisible to the judge. Kept as a constant because the stability check has to
# apply the same cut to both of its arms or it measures the cut, not the order.
EVIDENCE_CHAR_BUDGET = 4000


def reorder_evidence(evidence_text: str, order: str,
                     budget: int = EVIDENCE_CHAR_BUDGET) -> str:
    """Present the same evidence chunks in a different order.

    This is what makes a stability check mean something. The judge runs at
    temperature 0, so asking it the same question twice in the same words must
    return the same grades -- that re-run checks the pipeline is deterministic,
    not that the grades are robust. What a reader has to worry about is the
    converse: that the score depends on incidental presentation, and the
    evidence list is the part of the prompt the pipeline reorders freely (the
    re-rankers exist to reorder it). Reversing it keeps the information
    identical and changes only the order, so any grade that moves is
    order-sensitivity, which is a property of the judge and worth disclosing.

    The budget is applied *before* reversing, not after. That order matters:
    with it the other way round the reversed arm would show the reader the
    chunks the forward arm had already cut, and a grade that moved would be
    telling us about the truncation and not about the order at all. Cut first
    and both arms carry exactly the same characters -- the last chunk may be
    clipped mid-sentence either way -- so the only difference between them is
    where each block sits.
    """
    clipped = evidence_text[:budget]
    if order == "as_given":
        return clipped
    if order == "reversed":
        return EVIDENCE_SEPARATOR.join(reversed(clipped.split(EVIDENCE_SEPARATOR)))
    raise ValueError(f"Unknown evidence order: {order}")


def score_answer(client, question, answer, insufficient, evidence_text,
                 evidence_order: str = "as_given"):
    user = (
        f"Question:\n{question}\n\n"
        f"Evidence provided to the model:\n"
        f"{reorder_evidence(evidence_text, evidence_order)}\n\n"
        f"Model's answer:\n{answer or '(empty)'}\n\n"
        f"Model declared insufficient_evidence: {insufficient}\n\n"
        'Return JSON: {"faithfulness": int, "citation_support": int, '
        '"helpfulness": int, "abstention_ok": int, "rationale": str}'
    )
    parsed = _parse_json(_chat(client, ANSWER_SYSTEM, user))
    return {
        "faithfulness": parsed.get("faithfulness"),
        "citation_support": parsed.get("citation_support"),
        "helpfulness": parsed.get("helpfulness"),
        "abstention_ok": parsed.get("abstention_ok"),
        "rationale": parsed.get("rationale", ""),
    }


RELEVANCE_SYSTEM = (
    "You are a retrieval relevance judge for oncology treatment QA. Given a "
    "question and one evidence chunk (URL + title + text), rate relevance: "
    "2 = authoritative/directly relevant, 1 = partially or background relevant, "
    "0 = irrelevant. Return ONLY JSON with keys \"score\" (int) and \"rationale\" (str)."
)


def score_relevance(client, question, url, title, text):
    user = (
        f"Question:\n{question}\n\n"
        f"Chunk URL:\n{url}\n"
        f"Chunk title:\n{title}\n"
        f"Chunk text:\n{text[:1500]}\n\n"
        'Return JSON: {"score": int, "rationale": str}'
    )
    parsed = _parse_json(_chat(client, RELEVANCE_SYSTEM, user))
    return {
        "score": parsed.get("score"),
        "rationale": parsed.get("rationale", ""),
    }


def load_results(path, methods):
    df = pd.read_csv(path)
    required = {"mode", "qid", "question"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Input missing columns: {missing}")
    if methods:
        df = df[df["mode"].isin(methods)]
    return df


def _cell(value) -> str:
    """CSV cell -> str, treating None/NaN as empty.

    Needed because `float('nan') or ""` evaluates to nan (NaN is truthy), so a
    plain `or` would stringify missing evidence as the literal "nan".
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value)


def _sample_questions(df, n, seed):
    if n is None or n >= df["qid"].nunique():
        return df["qid"].unique().tolist()
    return df["qid"].drop_duplicates().sample(n, random_state=seed).tolist()


def cmd_answer(args):
    client = build_client()
    df = load_results(args.input, args.methods)
    qids = _sample_questions(df, args.sample, args.seed)
    df = df[df["qid"].isin(qids)].copy()

    def judge(r):
        s = score_answer(
            client,
            r["question"],
            r.get("answer"),
            r.get("insufficient_evidence"),
            _cell(r.get("final_evidence_texts")),
            args.evidence_order,
        )
        return {
            "qid": r["qid"],
            "mode": r["mode"],
            "question": r["question"],
            "answer": r.get("answer"),
            "insufficient_evidence": r.get("insufficient_evidence"),
            "annotation_source": "llm_judge_automatic",
            "valid_for_human_eval_claim": False,
            "evidence_order": args.evidence_order,
            **s,
        }

    rows = pmap(judge, [r for _, r in df.iterrows()], args.workers)

    out = pd.DataFrame(rows)
    out.to_csv(args.out, index=False, encoding="utf-8-sig")
    summary = build_answer_summary(out)
    summary_path = str(Path(args.out).with_suffix("")) + "_summary.csv"
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(out)} answer judgements -> {args.out}")
    print(f"Wrote per-method summary -> {summary_path}")
    print(summary.to_string(index=False))


def build_answer_summary(judged):
    for c in ("faithfulness", "citation_support", "helpfulness", "abstention_ok"):
        if c in judged.columns:
            judged[c] = pd.to_numeric(judged[c], errors="coerce")
    g = judged.groupby("mode", as_index=False).agg(
        num_questions=("qid", "nunique"),
        faithfulness_mean=("faithfulness", "mean"),
        citation_support_mean=("citation_support", "mean"),
        helpfulness_mean=("helpfulness", "mean"),
        abstention_ok_rate=("abstention_ok", "mean"),
    )
    g["composite_mean"] = g[["faithfulness_mean", "citation_support_mean", "helpfulness_mean"]].mean(axis=1)
    g["annotation_source"] = "llm_judge_automatic"
    g["valid_for_human_eval_claim"] = False
    return g.sort_values("composite_mean", ascending=False).reset_index(drop=True)


STABILITY_DIMENSIONS = ("faithfulness", "citation_support", "helpfulness", "abstention_ok")


def cmd_stability(args):
    """Grade every answer three times to separate noise from order-sensitivity.

    Three passes over the same rows: the production prompt twice (which, at
    temperature 0, tells us whether the judge is reproducible at all) and once
    with the evidence blocks reversed but carrying the same characters. The
    first pair answers "would a second run have said the same thing"; the first
    and third answer "does the grade depend on how the evidence was arranged",
    which is the part a reader cannot check for themselves.
    """
    client = build_client()
    df = load_results(args.input, args.methods)
    qids = _sample_questions(df, args.sample, args.seed)
    df = df[df["qid"].isin(qids)].copy()

    def run(r):
        evidence = _cell(r.get("final_evidence_texts"))
        kwargs = dict(
            question=r["question"],
            answer=r.get("answer"),
            insufficient=r.get("insufficient_evidence"),
            evidence_text=evidence,
        )
        first = score_answer(client, evidence_order="as_given", **kwargs)
        second = score_answer(client, evidence_order="as_given", **kwargs)
        flipped = score_answer(client, evidence_order="reversed", **kwargs)
        row = {
            "qid": r["qid"],
            "mode": r["mode"],
            "question": r["question"],
            "evidence_chars": len(evidence),
            "evidence_truncated": len(evidence) > EVIDENCE_CHAR_BUDGET,
            "evidence_chunks": evidence.count(EVIDENCE_SEPARATOR) + 1,
            "annotation_source": "llm_judge_automatic",
            "valid_for_human_eval_claim": False,
        }
        for dim in STABILITY_DIMENSIONS:
            a, b, c = first.get(dim), second.get(dim), flipped.get(dim)
            row[f"{dim}_pass1"] = a
            row[f"{dim}_pass2"] = b
            row[f"{dim}_reversed"] = c
            row[f"{dim}_deterministic"] = int(a == b)
            row[f"{dim}_order_stable"] = int(a == c)
            try:
                row[f"{dim}_order_within_1"] = int(abs(float(a) - float(c)) <= 1)
            except (TypeError, ValueError):
                row[f"{dim}_order_within_1"] = None
        return row

    rows = pmap(run, [r for _, r in df.iterrows()], args.workers)
    out = pd.DataFrame(rows)
    out.to_csv(args.out, index=False, encoding="utf-8-sig")

    summary = build_stability_summary(out)
    summary_path = str(Path(args.out).with_suffix("")) + "_summary.csv"
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(out)} stability rows -> {args.out}")
    print(f"Wrote stability summary -> {summary_path}")
    print(summary.to_string(index=False))


def build_stability_summary(rows):
    """Agreement rates per method, plus an ALL row over every graded answer.

    The ALL row is the one that goes in the paper: the question a limitation
    paragraph has to answer is how reliable the judge is in general, not how it
    behaved on the four systems the sample happened to cover.
    """
    def aggregate(frame, label):
        entry = {"mode": label, "num_questions": int(frame["qid"].nunique())}
        for dim in STABILITY_DIMENSIONS:
            det = pd.to_numeric(frame[f"{dim}_deterministic"], errors="coerce")
            stable = pd.to_numeric(frame[f"{dim}_order_stable"], errors="coerce")
            near = pd.to_numeric(frame[f"{dim}_order_within_1"], errors="coerce")
            entry[f"{dim}_deterministic_rate"] = round(float(det.mean()), 4)
            entry[f"{dim}_order_stable_rate"] = round(float(stable.mean()), 4)
            entry[f"{dim}_order_within_1_rate"] = round(float(near.mean()), 4)
        entry["rows"] = len(frame)
        entry["rows_truncated"] = int(frame["evidence_truncated"].sum())
        entry["annotation_source"] = "llm_judge_automatic"
        entry["valid_for_human_eval_claim"] = False
        return entry

    summary = [aggregate(rows, "ALL")]
    for mode, frame in rows.groupby("mode"):
        summary.append(aggregate(frame, mode))
    return pd.DataFrame(summary)


def cmd_relevance(args):
    client = build_client()
    df = load_results(args.input, args.methods)
    qids = _sample_questions(df, args.sample, args.seed)
    df = df[df["qid"].isin(qids)].copy()

    # Collect distinct final evidence sources per (qid, mode).  A final window
    # can contain two chunks from the same URL, but the task below deliberately
    # de-duplicates by URL and grades the first associated excerpt.  The output
    # is therefore source-page level, not a four-chunk evaluation.
    top_k = args.top_k
    tasks = []
    seen = set()
    for _, r in df.iterrows():
        urls = _cell(r.get("final_urls")).split(" | ")
        titles = _cell(r.get("final_titles")).split(" | ")
        texts = _cell(r.get("final_evidence_texts")).split(EVIDENCE_SEPARATOR)
        for i in range(min(top_k, len(urls))):
            url = urls[i].strip()
            if not url:
                continue
            key = (r["qid"], r["mode"], url)
            if key in seen:
                continue
            seen.add(key)
            tasks.append({
                "qid": r["qid"],
                "mode": r["mode"],
                "question": r["question"],
                "url": url,
                "title": titles[i] if i < len(titles) else "",
                "text": texts[i] if i < len(texts) else "",
            })

    def judge(t):
        s = score_relevance(client, t["question"], t["url"], t["title"], t["text"])
        return {
            "qid": t["qid"],
            "mode": t["mode"],
            "question": t["question"],
            "url": t["url"],
            "title": t["title"],
            "annotation_source": "llm_judge_automatic",
            "valid_for_human_eval_claim": False,
            "relevance_score_0_1_2": s["score"],
            "review_notes": s["rationale"],
        }

    rows = pmap(judge, tasks, args.workers)

    out = pd.DataFrame(rows)
    out.to_csv(args.out, index=False, encoding="utf-8-sig")
    summary = build_relevance_summary(out)
    summary_path = str(Path(args.out).with_suffix("")) + "_summary.csv"
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(out)} distinct-source relevance judgements -> {args.out}")
    print(f"Wrote per-method summary -> {summary_path}")
    print(summary.to_string(index=False))


def build_relevance_summary(judged):
    """Summarize distinct-source scores with every question weighted equally."""
    judged = judged.copy()
    judged["relevance_score_0_1_2"] = pd.to_numeric(
        judged["relevance_score_0_1_2"], errors="coerce")
    judged["is_fully_authoritative"] = judged["relevance_score_0_1_2"].eq(2)
    per_question = judged.groupby(["mode", "qid"], as_index=False).agg(
        distinct_source_mean_relevance=("relevance_score_0_1_2", "mean"),
        distinct_source_rel2_rate=("is_fully_authoritative", "mean"),
        num_distinct_sources=("url", "nunique"),
    )
    g = per_question.groupby("mode", as_index=False).agg(
        num_questions=("qid", "nunique"),
        num_distinct_sources=("num_distinct_sources", "sum"),
        mean_distinct_sources_per_question=("num_distinct_sources", "mean"),
        distinct_source_mean_relevance=("distinct_source_mean_relevance", "mean"),
        distinct_source_rel2_rate=("distinct_source_rel2_rate", "mean"),
    )
    g["annotation_source"] = "llm_judge_automatic"
    g["valid_for_human_eval_claim"] = False
    return g.sort_values(
        "distinct_source_mean_relevance", ascending=False).reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("answer")
    pa.add_argument("--input", required=True)
    pa.add_argument("--methods", type=str, default=None, help="comma-separated modes")
    pa.add_argument("--out", required=True)
    pa.add_argument("--sample", type=int, default=None)
    pa.add_argument("--seed", type=int, default=42)
    pa.add_argument("--workers", type=int, default=1)
    pa.add_argument("--evidence-order", choices=["as_given", "reversed"],
                    default="as_given",
                    help="the paper's grades use the default; `reversed` exists "
                         "so the stability check can re-grade the same rows")
    pa.set_defaults(func=cmd_answer)

    ps = sub.add_parser("stability")
    ps.add_argument("--input", required=True)
    ps.add_argument("--methods", type=str, default=None)
    ps.add_argument("--out", required=True)
    ps.add_argument("--sample", type=int, default=None)
    ps.add_argument("--seed", type=int, default=42)
    ps.add_argument("--workers", type=int, default=1)
    ps.set_defaults(func=cmd_stability)

    pr = sub.add_parser("relevance")
    pr.add_argument("--input", required=True)
    pr.add_argument("--methods", type=str, default=None)
    pr.add_argument("--out", required=True)
    pr.add_argument("--sample", type=int, default=None)
    pr.add_argument("--seed", type=int, default=42)
    pr.add_argument("--top-k", type=int, default=4)
    pr.add_argument("--workers", type=int, default=1)
    pr.set_defaults(func=cmd_relevance)

    args = ap.parse_args()
    args.methods = [m.strip() for m in args.methods.split(",")] if args.methods else None
    args.func(args)


if __name__ == "__main__":
    main()
