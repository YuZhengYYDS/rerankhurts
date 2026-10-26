"""Build the tables that only exist because of the revision round.

`build_revision_assets.py` regenerates everything the ORIGINAL submission
already had. This script adds the artifacts the reviewers asked for:

  rev_table_rerankers.csv    re-ranker family across three benchmark views
  rev_table_judge.csv        LLM-as-judge answer quality + graded relevance
  rev_table_benchmark.csv    benchmark/corpus scale comparison
  rev_table_subset_split.csv expanded view split by item construction

Three benchmark views are reported, because the revision changed two things at
once (the corpus grew 6,785 -> 7,124 chunks and the question set grew 78 ->
155). Reporting all three separates the two effects:

  orig78   original audited benchmark, original corpus   (continuity with Table 1)
  iso78    same 78 questions, expanded corpus            (corpus effect alone)
  exp155   expanded question set, expanded corpus        (final benchmark)

The expanded view is 155, not the 187 the drafting round produced: the purge
step (`purge_leaky_questions.py`) removed the items whose text named their own
source page, which left the benchmark answerable from the question alone.

Sources are the raw per-question run outputs; every number here is recomputed
from them rather than copied from an intermediate summary.

Usage:
    python -m legacy.make_revision_tables [--dry-run]
"""
import argparse
import os
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from rerankhuts.paths import oncology_path


BASE = Path(__file__).resolve().parents[1]
REV = Path(os.environ.get("RESULT_DIR", BASE / "result_revision")).resolve()
BUNDLE = Path(os.environ.get("BUNDLE_DIR", REV / "bundle")).resolve()
PAPER_RESULT = Path(os.environ.get(
    "PAPER_RESULT_DIR", BASE / "COLING2027_paper" / "result")).resolve()

ORIG_QUESTIONS = (BASE / "result" / "emnlp_full_results_20260427_gpu_final"
                  / "paper_questions_validated.jsonl")
EXPANDED_QUESTIONS = oncology_path("questions_expanded_full_validated.jsonl", root=BASE)

# Order and display names follow the paper's narrative: the non-re-ranked
# reference first, then the re-rankers grouped by family.
#
# The rows are deliberately NOT ordered by parameter count. That reading is the
# one to avoid: the recovery is not monotone in size, and MedCPT (110M,
# biomedical) sits between two larger generic models precisely because it is the
# counterexample -- it recovers more than bge-reranker-base (278M) does. Sorting
# the rows by size would make the table read as a capacity ladder the numbers do
# not support. Read the `params` column and the deltas, not the row order.
#
# No accuracy or delta figures are quoted here on purpose: every number in this
# table is rebuilt each round, and a figure copied into a comment goes stale
# without anything failing.
RERANKER_ROWS = [
    ("baseline", "None (dense Base)", "--", "--"),
    ("rerank", "MiniLM-L6", "22M", "generic"),
    ("rerank_bge_base", "bge-reranker-base", "278M", "generic"),
    ("rerank_medcpt", "MedCPT-Cross-Encoder", "110M", "biomedical"),
    ("rerank_llm", "LLM listwise (DeepSeek)", "--", "general LLM"),
    ("rerank_source_aware", "MiniLM-L6 + NCI source prior", "22M", "source-aware (diagnostic)"),
    ("rerank_bge_m3", "bge-reranker-v2-m3", "568M", "multilingual"),
]

VIEWS = [
    # (key, label, results csv, questions jsonl, pairwise csv)
    ("orig78", "orig78", REV / "supp_new_rerankers_combined.csv", ORIG_QUESTIONS,
     REV / "newrr_eval" / "newrr_pairwise_vs_baseline.csv"),
    ("iso78", "iso78", REV / "p4_iso_v2corpus_78q.csv", ORIG_QUESTIONS, None),
    ("exp155", "exp155", REV / "p4_expanded_retrieval_combined.csv", EXPANDED_QUESTIONS,
     REV / "p4_eval" / "p4_pairwise_vs_baseline.csv"),
]


def read_results(path, usecols):
    """Read a run CSV keeping only the columns the given scorer understands.

    The two scorers want different columns (`score_retrieval` needs the URL
    stages, `analyze_results` needs the answer fields), and a run may not carry
    all of either -- a retrieval-only run has no `insufficient_evidence`.
    """
    return pd.read_csv(path, usecols=lambda c: c in usecols)


def retrieval_table(path, questions_path):
    from legacy import score_retrieval as sr
    from legacy import analyze_results as ar
    questions = sr.load_questions_jsonl(str(questions_path))

    metrics = sr.summarize_metrics(
        sr.prepare_result_df(read_results(path, sr.RESULT_USECOLS), questions), ["mode"])

    raw = read_results(path, ar.RESULT_USECOLS)
    if "insufficient_evidence" not in raw.columns:
        raw = raw.assign(insufficient_evidence=False)
    hits = (ar.prepare_result_df(raw, questions)
            .groupby("mode", as_index=False)["gold_url_hit"].mean()
            .rename(columns={"gold_url_hit": "final_top4_hit"}))
    return metrics.merge(hits, on="mode", how="left")


def rerank_cost(path):
    """Mean re-ranking latency per mode, in ms, from the run's timing column.

    The re-rankers in this table differ by two orders of magnitude in cost: a 22M
    cross-encoder scores a candidate list in milliseconds while an LLM listwise
    call takes about a second per question. The table reported accuracy with no
    cost column at all, so a reader deciding whether re-ranking is worth it could
    see that the bigger models recover accuracy but not what they charge for it.
    Cost is measured on the same run as the accuracy numbers beside it, rather
    than quoted from a separate timing experiment.
    """
    raw = pd.read_csv(path, usecols=lambda c: c in {"mode", "rerank_ms"})
    if "rerank_ms" not in raw.columns:
        return {}
    return raw.groupby("mode")["rerank_ms"].mean().round(1).to_dict()


def deltas_from_pairwise(path):
    if path is None or not Path(path).exists():
        return {}
    pw = pd.read_csv(path)
    nd = pw[pw["metric"] == "ndcg_at_10"].set_index("candidate_mode")
    return {mode: (row["delta_candidate_minus_baseline"], row["p_value_bootstrap"])
            for mode, row in nd.iterrows()}


def build_reranker_table():
    rows = []
    per_view = {}
    for key, _label, results, questions, pairwise in VIEWS:
        if not Path(results).exists():
            print(f"  !! missing {results.name}; skipping view {key}")
            continue
        per_view[key] = retrieval_table(results, questions)
        per_view[key + "_pw"] = deltas_from_pairwise(pairwise)
        per_view[key + "_cost"] = rerank_cost(results)

    for mode, name, params, domain in RERANKER_ROWS:
        row = {"method": name, "params": params, "domain": domain}
        for key, _label, _r, _q, _p in VIEWS:
            if key not in per_view:
                continue
            t = per_view[key]
            hit = t[t["mode"] == mode]
            if hit.empty:
                continue
            hit = hit.iloc[0]
            row[f"{key}_ndcg"] = round(float(hit["ndcg_at_10"]), 4)
            row[f"{key}_mrr"] = round(float(hit["mrr"]), 4)
            row[f"{key}_r10"] = round(float(hit["recall_at_10"]), 4)
            row[f"{key}_hit"] = round(float(hit["final_top4_hit"]), 4)
            row[f"{key}_rerank_ms"] = per_view[key + "_cost"].get(mode)
            delta, p = per_view[key + "_pw"].get(mode, (None, None))
            if delta is not None:
                row[f"{key}_delta"] = round(float(delta), 4)
                row[f"{key}_p"] = round(float(p), 4)
        rows.append(row)
    return pd.DataFrame(rows)


def build_benchmark_table():
    rows = []
    for key, label, results, questions, _p in VIEWS:
        if not Path(results).exists():
            continue
        from legacy import score_retrieval as sr
        df = read_results(results, sr.RESULT_USECOLS | {"corpus_chunk_count"})
        qs = sr.load_questions_jsonl(str(questions))
        rows.append({
            "view": label,
            "questions": len(qs),
            "topics": qs["topic"].nunique() if "topic" in qs.columns else None,
            "corpus_chunks": int(df["corpus_chunk_count"].iloc[0]),
            "modes": df["mode"].nunique(),
        })
    return pd.DataFrame(rows)


def build_subset_table():
    """nDCG@10 per mode on the expanded benchmark, split by how items were built.

    The expanded view's headline scores every system over all its items at once,
    but the set is not homogeneous. Some items are the original audited
    questions; the rest were written for this revision and admitted by an
    automatic screen. Reported as one number, an easier profile among the added
    items can carry a conclusion the original items do not support -- a system
    can be ahead overall while behind on the audited subset it was meant to
    improve on. The split is therefore shown rather than assumed away, and the
    delta column says which subset is doing the work.

    The two added groups are kept apart rather than pooled into one "added"
    column. They are not interchangeable: a `grounded_in_gold_page` item was
    written by reading the very page the item is scored against, while a
    `drafted_from_topic_and_url` item was written from the topic and then given
    a gold page. If the grounded items score higher, that is as likely to be a
    property of how they were written as of the system being measured, and a
    single pooled column would hide it. The pooled delta is still reported,
    because orig-vs-added is the comparison the scale claim turns on.
    """
    results = REV / "p4_expanded_retrieval_combined.csv"
    if not Path(results).exists():
        print(f"  !! missing {results.name}; skipping subset split")
        return None

    from legacy import score_retrieval as sr
    questions = sr.load_questions_jsonl(str(EXPANDED_QUESTIONS))
    prepared = sr.prepare_result_df(read_results(results, sr.RESULT_USECOLS), questions)

    source = {str(row["qid"]): str(row.get("construction_source", "") or "")
              for _, row in questions.iterrows()}
    prepared["construction"] = prepared["qid"].map(lambda q: source.get(str(q), ""))

    # A question in the results that is not in the question file means the two
    # inputs are from different rounds -- typically a combined results file that
    # was not refreshed after the question set changed. Left alone it silently
    # grows an unlabelled group whose scores are averaged in with the rest, and
    # the table still looks well-formed.
    unmatched = sorted(set(prepared.loc[prepared["construction"] == "", "qid"].astype(str)))
    if unmatched:
        raise SystemExit(
            f"{Path(results).name} holds {len(unmatched)} questions absent from "
            f"{Path(EXPANDED_QUESTIONS).name} (e.g. {', '.join(unmatched[:5])}). "
            f"Refusing to split by construction: the results and the question set "
            f"are from different rounds. Re-run run_view_analyses.py to refresh "
            f"the combined file."
        )
    prepared["subset"] = prepared["construction"].map(
        lambda s: "original" if s == "audited_subset_original" else "added")

    wide = (sr.summarize_metrics(prepared, ["mode", "construction"])
            .pivot(index="mode", columns="construction", values="ndcg_at_10"))

    pooled = sr.summarize_metrics(prepared, ["mode", "subset"]).pivot(
        index="mode", columns="subset", values="ndcg_at_10")
    wide["ndcg_original"] = pooled.get("original")
    wide["ndcg_added"] = pooled.get("added")

    counts = prepared.groupby("subset")["qid"].nunique().to_dict()
    wide.insert(0, "n_original", int(counts.get("original", 0)))
    wide.insert(1, "n_added", int(counts.get("added", 0)))

    if {"ndcg_original", "ndcg_added"} <= set(wide.columns):
        wide["delta_added_minus_original"] = (wide["ndcg_added"] - wide["ndcg_original"]).round(4)
        return wide.sort_values("ndcg_added", ascending=False).reset_index()
    # A run whose questions carry no construction_source yields one subset; sort
    # on whatever survived rather than raising on a column that is not there.
    return wide.sort_values(wide.columns[0], ascending=False).reset_index()


JUDGE_DIMENSIONS = ("faithfulness", "citation_support", "helpfulness")


def build_judge_ci_table():
    """Judge scores with intervals, and whether the differences survive re-grading.

    A bootstrap over questions is not enough on its own here. It treats each
    grade as a fixed measurement, so it measures how much the *question sample*
    could have moved the mean -- not how much the judge would have moved it.
    `llm_judge.py stability` shows the judge does move: it reproduces only
    ~92-96% of its own grades when asked the same question twice, and ~84-94%
    when the evidence blocks are reordered. An interval that ignores that
    understates the uncertainty around exactly the claim this table is used to
    make, which is which systems differ.

    The headline columns are therefore the production grades, and beside them
    sit the same difference recomputed from two independent re-grades of the
    same answers: `delta_reask` (identical prompt, so any movement is judge
    noise) and `delta_reordered` (evidence blocks reversed, so movement is
    order-sensitivity). `same_sign_all_passes` is the honest summary -- a
    difference that points the same way in all three is one the conclusion can
    rest on; one that changes sign is the judge talking.

    Every number in a row comes from the same measurement as the others in that
    row, so `delta_vs_baseline` is the gap between the two `composite_mean`
    values printed beside it.
    """
    path = REV / "p4_judge_answer_eval.csv"
    if not path.exists():
        print(f"  !! missing {path.name}; skipping judge intervals")
        return None

    raw = pd.read_csv(path)
    missing = [d for d in JUDGE_DIMENSIONS if d not in raw.columns]
    if missing or "mode" not in raw.columns or "qid" not in raw.columns:
        print(f"  !! {path.name} lacks {missing or 'mode/qid'}; skipping judge intervals")
        return None

    for d in JUDGE_DIMENSIONS:
        raw[d] = pd.to_numeric(raw[d], errors="coerce")
    raw["composite"] = raw[list(JUDGE_DIMENSIONS)].mean(axis=1)
    wide = raw.pivot_table(index="qid", columns="mode", values="composite", aggfunc="mean")

    # The re-grades, reshaped onto the same (qid x mode) layout so each can be
    # put through the identical comparison. They are keyed on the same cells --
    # if they were not, the "re-grade" would be of different answers and would
    # measure the sample rather than the judge.
    regrades = {}
    stab_path = REV / "p4_judge_stability.csv"
    if stab_path.exists():
        s = pd.read_csv(stab_path)
        for label, pass_name in (("reask", "pass2"), ("reordered", "reversed")):
            cols = [f"{d}_{pass_name}" for d in JUDGE_DIMENSIONS]
            if not set(cols) <= set(s.columns):
                print(f"  !! {stab_path.name} lacks {cols[0]}; "
                      f"skipping the {label} re-grade")
                continue
            frame = s[["qid", "mode"] + cols].copy()
            for c in cols:
                frame[c] = pd.to_numeric(frame[c], errors="coerce")
            frame["_c"] = frame[cols].mean(axis=1)
            regrades[label] = frame.pivot_table(
                index="qid", columns="mode", values="_c", aggfunc="mean")

    from legacy import paper_support_analysis as psa
    rounds = getattr(psa, "BOOTSTRAP_ROUNDS", 2000)
    seed = getattr(psa, "RNG_SEED", 42)
    base_mode = "baseline"

    def paired_delta(frame, mode, idx):
        """Bootstrap the paired difference on `frame`, or None if unavailable."""
        if frame is None or base_mode not in frame.columns or mode not in frame.columns:
            return None
        paired = frame[[base_mode, mode]].dropna()
        if paired.empty:
            return None
        return psa.bootstrap_delta(
            base_values=paired[base_mode].to_numpy(dtype=np.float64),
            candidate_values=paired[mode].to_numpy(dtype=np.float64),
            rounds=rounds, seed=seed + idx * 97,
        )

    rows = []
    for idx, mode in enumerate(sorted(wide.columns)):
        values = wide[mode].dropna().to_numpy(dtype=np.float64)
        if values.size == 0:
            continue
        rng = np.random.default_rng(seed + idx * 131)
        draws = np.array([values[rng.integers(0, values.size, values.size)].mean()
                          for _ in range(rounds)])
        row = {
            "mode": mode,
            "num_questions": int(values.size),
            "composite_mean": round(float(values.mean()), 4),
            "ci_low": round(float(np.quantile(draws, 0.025)), 4),
            "ci_high": round(float(np.quantile(draws, 0.975)), 4),
            "annotation_source": "llm_judge_automatic",
            "valid_for_human_eval_claim": False,
        }
        stats = paired_delta(wide, mode, idx) if mode != base_mode else None
        if stats is not None:
            row.update({
                "delta_vs_baseline": round(stats["delta"], 4),
                "delta_ci_low": round(stats["ci_low"], 4),
                "delta_ci_high": round(stats["ci_high"], 4),
                "p_value_bootstrap": round(stats["p_value"], 4),
                "separated_from_baseline_95ci": bool(
                    stats["ci_low"] > 0 or stats["ci_high"] < 0),
            })
            signs = [np.sign(stats["delta"])]
            for label in ("reask", "reordered"):
                other = paired_delta(regrades.get(label), mode, idx)
                if other is None:
                    continue
                row[f"delta_{label}"] = round(other["delta"], 4)
                signs.append(np.sign(other["delta"]))
            if len(signs) > 1:
                row["same_sign_all_passes"] = bool(
                    all(s == signs[0] for s in signs) and signs[0] != 0)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("composite_mean", ascending=False).reset_index(drop=True)


def build_judge_table():
    out = []
    ans = REV / "p4_judge_answer_eval_summary.csv"
    rel = REV / "p4_judge_relevance_eval.csv"
    if ans.exists():
        a = pd.read_csv(ans)
        a.insert(0, "judge", "answer_quality_1to5")
        out.append(a)
    if rel.exists():
        raw = pd.read_csv(rel)
        raw["rel"] = pd.to_numeric(
            raw["relevance_score_0_1_2"], errors="coerce")
        raw["rel2"] = raw["rel"].eq(2)
        per_question = raw.groupby(["mode", "qid"], as_index=False).agg(
            distinct_source_mean_relevance=("rel", "mean"),
            distinct_source_rel2_rate=("rel2", "mean"),
            num_distinct_sources=("url", "nunique"),
        )
        r = per_question.groupby("mode", as_index=False).agg(
            num_questions=("qid", "nunique"),
            num_distinct_sources=("num_distinct_sources", "sum"),
            mean_distinct_sources_per_question=("num_distinct_sources", "mean"),
            distinct_source_mean_relevance=(
                "distinct_source_mean_relevance", "mean"),
            distinct_source_rel2_rate=("distinct_source_rel2_rate", "mean"),
        )
        r["annotation_source"] = "llm_judge_automatic"
        r["valid_for_human_eval_claim"] = False
        r.insert(0, "judge", "graded_relevance_0to2")
        out.append(r)
    if not out:
        return None
    return pd.concat(out, ignore_index=True)


# The judged question set. The judge originally ran on a 40-question stratified
# sample; the R1-driven scale-up now judges ALL 155 validated questions, so the
# gold-URL map used by the inversion and by-source tables must read the full set
# (a 40-question map left 115 questions with no gold URL and silently zeroed
# their hit/relevance-by-source split).
JUDGE_SAMPLE = EXPANDED_QUESTIONS


def _bootstrap_mean(values, rounds, seed):
    """Bootstrap 95% CI of a mean over question-level `values`."""
    rng = np.random.default_rng(seed)
    draws = np.array([values[rng.integers(0, values.size, values.size)].mean()
                      for _ in range(rounds)])
    return round(float(draws.mean()), 4), round(float(np.quantile(draws, 0.025)), 4), \
        round(float(np.quantile(draws, 0.975)), 4)


def build_inversion_table():
    """Retrieval, graded relevance and answer quality on the SAME judged questions.

    The retrieval and answer columns are meaningful only if they cover the same
    items.  All three are therefore computed on the identical 155 questions.

    Every column is recomputed from raw per-question outputs, not copied from an
    intermediate summary, and every row is `llm_judge_automatic`.
    """
    frames = []
    for f in sorted(REV.glob("p4_expanded_judge_answers_*.csv")):
        if "settings" in f.name:
            continue
        frames.append(pd.read_csv(f))
    if not frames:
        print("  !! no per-mode judge answer files; skipping inversion table")
        return None
    results = pd.concat(frames, ignore_index=True)

    from legacy import analyze_results as ar
    jq = ar.load_questions_jsonl(str(JUDGE_SAMPLE))
    prep = ar.prepare_result_df(results, jq)
    gold_hit = (prep.groupby("mode")["gold_url_hit"].mean()
                .rename("gold_url_hit_top4"))

    ans = pd.read_csv(REV / "p4_judge_answer_eval.csv")
    for d in JUDGE_DIMENSIONS:
        ans[d] = pd.to_numeric(ans[d], errors="coerce")
    ans["composite"] = ans[list(JUDGE_DIMENSIONS)].mean(axis=1)
    composite = ans.groupby("mode")["composite"].mean().rename("answer_composite_1to5")
    n = ans.groupby("mode")["qid"].nunique().rename("num_questions")

    rel = pd.read_csv(REV / "p4_judge_relevance_eval.csv")
    rel["rel"] = pd.to_numeric(rel["relevance_score_0_1_2"], errors="coerce")
    # The judge scores one excerpt per distinct final URL.  Average those source
    # scores within each question first so that every benchmark item, rather than
    # every delivered URL, has equal weight in the system comparison.
    per_question_rel = rel.groupby(["mode", "qid"])["rel"].mean()
    relevance = (per_question_rel.groupby("mode").mean()
                 .rename("graded_relevance_0to2"))

    out = pd.concat([n, gold_hit, relevance, composite], axis=1).reset_index()
    out["annotation_source"] = "llm_judge_automatic"
    out["valid_for_human_eval_claim"] = False
    return out.sort_values("answer_composite_1to5", ascending=False).reset_index(drop=True)


def _spearman(xs, ys):
    """Spearman rho with average ranks for ties."""
    def ranks(values):
        order = sorted(range(len(values)), key=lambda i: values[i])
        out = [0.0] * len(values)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                out[order[k]] = avg
            i = j + 1
        return out

    def pearson(a, b):
        ma, mb = sum(a) / len(a), sum(b) / len(b)
        num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        da = sum((x - ma) ** 2 for x in a) ** 0.5
        db = sum((y - mb) ** 2 for y in b) ** 0.5
        return num / (da * db)

    return pearson(ranks(xs), ranks(ys))


def build_spearman_table(inversion=None):
    """Rank agreement among gold hit, distinct-source relevance and answers."""
    if inversion is None:
        path = REV / "rev_table_inversion.csv"
        if not path.exists():
            print("  !! rev_table_inversion.csv missing; skipping Spearman table")
            return None
        inversion = pd.read_csv(path)
    pairs = [
        ("gold_url_hit_top4", "graded_relevance_0to2"),
        ("gold_url_hit_top4", "answer_composite_1to5"),
        ("graded_relevance_0to2", "answer_composite_1to5"),
    ]
    rows = []
    for a, b in pairs:
        xs = pd.to_numeric(inversion[a], errors="coerce").tolist()
        ys = pd.to_numeric(inversion[b], errors="coerce").tolist()
        rows.append({"metric_a": a, "metric_b": b,
                     "spearman_rho": round(_spearman(xs, ys), 6),
                     "num_systems": len(inversion)})
    return pd.DataFrame(rows)


def build_relevance_by_source_table():
    """Graded relevance split by the distinct source page the judge scored.

    The input has already been de-duplicated by (question, system, URL), so each
    row represents one delivered source page rather than one of four chunks.
    """
    path = REV / "p4_judge_relevance_eval.csv"
    if not path.exists():
        print(f"  !! missing {path.name}; skipping relevance-by-source")
        return None
    rel = pd.read_csv(path)
    rel["rel"] = pd.to_numeric(rel["relevance_score_0_1_2"], errors="coerce")

    from legacy import analyze_results as ar
    jq = ar.load_questions_jsonl(str(JUDGE_SAMPLE))
    qgold = {str(r["qid"]): str(r.get("gold_url", "")) for _, r in jq.iterrows()}
    rel["gold"] = rel["qid"].astype(str).map(qgold)

    def classify(r):
        u = str(r["url"])
        g = str(r.get("gold") or "")
        if "cancer.gov" in u:
            return "nci_gold" if (g and g in u) else "nci_non_gold"
        if "pubmed" in u:
            return "pubmed"
        if "medrag" in u.lower() or "textbook" in u.lower():
            return "textbook"
        return "other"

    rel["source"] = rel.apply(classify, axis=1)
    out = rel.groupby("source").agg(
        n_distinct_sources=("rel", "size"),
        mean_relevance=("rel", "mean"),
        scored_0=("rel", lambda s: int((s == 0).sum())),
        scored_1=("rel", lambda s: int((s == 1).sum())),
        scored_2=("rel", lambda s: int((s == 2).sum())),
    ).reset_index()
    out["mean_relevance"] = out["mean_relevance"].round(4)
    out["annotation_source"] = "llm_judge_automatic"
    out["valid_for_human_eval_claim"] = False
    return out.sort_values("mean_relevance", ascending=False).reset_index(drop=True)


def build_judge_rates_table():
    """Unsupported-answer and abstention rates per mode, from the 1-5 judge.

    The reviewer asked for a hallucination/safety signal with and without the
    re-ranker, not just a bounded composite. The judge already emits a 1-5
    faithfulness grade and an abstention-appropriateness flag; reporting the
    share of answers scored at or below 2 (unsupported/hallucinated) and the
    abstention-appropriateness rate turns those into the rate the reviewer asked
    for. These are automatic LLM grades, so the label is carried alongside.
    """
    path = REV / "p4_judge_answer_eval.csv"
    if not path.exists():
        print(f"  !! missing {path.name}; skipping judge rates")
        return None
    ans = pd.read_csv(path)
    ans["faith"] = pd.to_numeric(ans["faithfulness"], errors="coerce")
    ans["abst"] = pd.to_numeric(ans["abstention_ok"], errors="coerce")
    out = ans.groupby("mode").agg(
        num_questions=("qid", "nunique"),
        mean_faithfulness=("faith", "mean"),
        rate_faithfulness_le2=("faith", lambda s: (s <= 2).mean()),
        rate_faithfulness_lt5=("faith", lambda s: (s < 5).mean()),
        abstention_ok_rate=("abst", "mean"),
    ).reset_index()
    for c in ("mean_faithfulness", "rate_faithfulness_le2",
              "rate_faithfulness_lt5", "abstention_ok_rate"):
        out[c] = out[c].round(4)
    out["annotation_source"] = "llm_judge_automatic"
    out["valid_for_human_eval_claim"] = False
    return out.sort_values("mean_faithfulness", ascending=False).reset_index(drop=True)


def build_source_ablation_ci_table():
    """Bootstrap 95% CI for each source-composition preset.

    `supp_source_ablation_summary.csv` reports a point nDCG@10 per preset with no
    uncertainty, even though every preset scores only 78 questions and several
    are definitionally saturated (all 78 gold URLs are cancer.gov, so
    pubmed_only / textbook_only can only ever score 0.0). A point number without
    an interval invites the saturation reading to be mistaken for a measured
    ceiling. The CI is bootstrapped over the 78 questions per preset per mode.
    """
    from legacy import score_retrieval as sr
    from legacy import paper_support_analysis as psa
    rounds = getattr(psa, "BOOTSTRAP_ROUNDS", 2000)
    seed = getattr(psa, "RNG_SEED", 42)
    qs = sr.load_questions_jsonl(str(ORIG_QUESTIONS))

    presets = ["all", "nci_only", "nci_textbook", "nci_pubmed",
               "pubmed_only", "textbook_only"]
    rows = []
    for pi, preset in enumerate(presets):
        path = REV / f"supp_source_ablation_{preset}.csv"
        if not Path(path).exists():
            print(f"  !! missing {path.name}; skipping preset {preset}")
            continue
        prep = sr.prepare_result_df(
            read_results(path, sr.RESULT_USECOLS), qs)
        per_q = sr.summarize_metrics(prep, ["mode", "qid"])
        for mi, mode in enumerate(sorted(per_q["mode"].unique())):
            sub = per_q[per_q["mode"] == mode]
            values = sub["ndcg_at_10"].to_numpy(dtype=np.float64)
            mean, lo, hi = _bootstrap_mean(values, rounds, seed + pi * 47 + mi * 11)
            rows.append({
                "preset": preset,
                "mode": mode,
                "n_questions": int(values.size),
                "ndcg_at_10": round(float(values.mean()), 4),
                "ci_low": lo,
                "ci_high": hi,
            })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    targets = [REV, BUNDLE, PAPER_RESULT]

    inversion = build_inversion_table()
    tables = {
        "rev_table_rerankers.csv": build_reranker_table(),
        "rev_table_benchmark.csv": build_benchmark_table(),
        "rev_table_subset_split.csv": build_subset_table(),
        "rev_table_judge.csv": build_judge_table(),
        "rev_table_judge_ci.csv": build_judge_ci_table(),
        "rev_table_inversion.csv": inversion,
        "rev_table_spearman.csv": build_spearman_table(inversion),
        "rev_table_relevance_by_source.csv": build_relevance_by_source_table(),
        "rev_table_judge_rates.csv": build_judge_rates_table(),
        "rev_table_source_ablation_ci.csv": build_source_ablation_ci_table(),
    }

    for name, df in tables.items():
        if df is None or df.empty:
            print(f"!! {name}: nothing to write")
            continue
        print(f"\n=== {name} ===")
        print(df.to_string(index=False))
        if args.dry_run:
            continue
        for d in targets:
            d.mkdir(parents=True, exist_ok=True)
            df.to_csv(d / name, index=False, encoding="utf-8-sig")
        print(f"  -> written to {len(targets)} locations")

    if not args.dry_run:
        for d in (BUNDLE, PAPER_RESULT):
            d.mkdir(parents=True, exist_ok=True)
        print(f"\nDone. Tables in {BUNDLE} and {PAPER_RESULT}")


if __name__ == "__main__":
    main()
