import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RESULT_DIR = BASE_DIR / "result"


def resolve_path(raw_value: str, default: Path) -> Path:
    if not raw_value:
        return default
    candidate = Path(raw_value)
    return candidate if candidate.is_absolute() else BASE_DIR / candidate


QUESTIONS_FILE = resolve_path(
    os.getenv("QUESTIONS_FILE", ""),
    RESULT_DIR / "paper_questions_validated.jsonl",
)
OUTPUT_DIR = resolve_path(
    os.getenv("OUTPUT_DIR", ""),
    RESULT_DIR / "human_eval_packets",
)
SAMPLE_SIZE = int(os.getenv("SAMPLE_SIZE", "48"))
SEED = int(os.getenv("SEED", "42"))

RETRIEVAL_METHOD_SPECS = os.getenv(
    "RETRIEVAL_METHOD_SPECS",
    ";".join(
        [
            "baseline=result/supp_strong_baselines_validated_baseline.csv",
            "rerank=result/supp_strong_baselines_validated_rerank.csv",
            "rrf_hybrid=result/supp_strong_baselines_validated_rrf_hybrid.csv",
            "strong_reranker=result/supp_strong_reranker_minilm_l12_d024_rerank.csv",
        ]
    ),
)
ANSWER_METHOD_SPECS = os.getenv("ANSWER_METHOD_SPECS", "")


def parse_method_specs(spec_text: str) -> List[Tuple[str, Path]]:
    items: List[Tuple[str, Path]] = []
    for part in spec_text.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise ValueError(f"Invalid method spec: {part}")
        alias, raw_path = part.split("=", 1)
        items.append((alias.strip(), resolve_path(raw_path.strip(), BASE_DIR / raw_path.strip())))
    return items


def load_jsonl(path: Path) -> pd.DataFrame:
    rows: List[Dict] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return pd.DataFrame(rows)


def split_pipe(value) -> List[str]:
    if pd.isna(value):
        return []
    return [item.strip() for item in str(value).split("|") if item.strip()]


def normalize_gold_urls(value, fallback_gold_url) -> List[str]:
    if isinstance(value, list):
        urls = [str(item).strip() for item in value if str(item).strip()]
    elif pd.isna(value):
        urls = []
    else:
        try:
            parsed = json.loads(value) if isinstance(value, str) else value
            if isinstance(parsed, list):
                urls = [str(item).strip() for item in parsed if str(item).strip()]
            else:
                urls = []
        except Exception:
            urls = []
    if not urls and pd.notna(fallback_gold_url) and str(fallback_gold_url).strip():
        urls = [str(fallback_gold_url).strip()]
    return urls


def get_rank_of_gold(urls: Iterable[str], gold_urls: Iterable[str]) -> Optional[int]:
    gold_set = set(gold_urls)
    if not gold_set:
        return None
    for index, url in enumerate(urls, start=1):
        if url in gold_set:
            return index
    return None


def choose_ranking_urls(row: pd.Series) -> List[str]:
    for col in ["ranking_urls", "final_urls", "deduped_urls", "retrieved_urls"]:
        if col in row and pd.notna(row[col]) and str(row[col]).strip():
            return split_pipe(row[col])
    return []


def choose_ranking_titles(row: pd.Series) -> List[str]:
    for col in ["ranking_titles", "final_titles", "deduped_titles", "retrieved_titles"]:
        if col in row and pd.notna(row[col]) and str(row[col]).strip():
            return split_pipe(row[col])
    return []


def build_topic_quotas(questions_df: pd.DataFrame, sample_size: int) -> Dict[str, int]:
    counts = questions_df["topic"].value_counts().sort_index()
    total = int(counts.sum())
    if sample_size >= total:
        return {topic: int(count) for topic, count in counts.items()}

    exact = {
        topic: (count / total) * sample_size
        for topic, count in counts.items()
    }
    base = {
        topic: min(int(np.floor(value)), int(counts[topic]))
        for topic, value in exact.items()
    }

    for topic, count in counts.items():
        if count > 0 and base[topic] == 0:
            base[topic] = 1

    assigned = sum(base.values())
    remainders = sorted(
        [
            (exact[topic] - base[topic], topic)
            for topic in counts.index
            if base[topic] < int(counts[topic])
        ],
        reverse=True,
    )

    while assigned < sample_size and remainders:
        _, topic = remainders.pop(0)
        if base[topic] < int(counts[topic]):
            base[topic] += 1
            assigned += 1

    while assigned > sample_size:
        removable = [
            topic
            for topic in counts.index
            if base[topic] > 1
        ]
        if not removable:
            break
        topic = removable[-1]
        base[topic] -= 1
        assigned -= 1

    return base


def load_method_frame(alias: str, path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found for method {alias}")
    frame = pd.read_csv(path)
    frame["method_alias"] = alias
    return frame


def build_selection_frame(
    questions_df: pd.DataFrame,
    method_specs: Sequence[Tuple[str, Path]],
) -> pd.DataFrame:
    per_method: List[pd.DataFrame] = []

    for alias, path in method_specs:
        frame = load_method_frame(alias, path)
        keep_cols = [col for col in ["qid", "question", "ranking_urls", "ranking_titles", "final_urls", "final_titles"] if col in frame.columns]
        keep_cols.extend(["method_alias"])
        method_df = frame[keep_cols].copy()
        per_method.append(method_df)

    merged = questions_df.copy()
    merged["gold_urls_norm"] = merged.apply(
        lambda row: normalize_gold_urls(row.get("gold_urls"), row.get("gold_url")),
        axis=1,
    )

    score_rows: List[Dict] = []
    for _, qrow in merged.iterrows():
        qid = qrow["qid"]
        gold_urls = qrow["gold_urls_norm"]
        method_ranks: Dict[str, int] = {}
        final_hits: Dict[str, int] = {}

        for method_df in per_method:
            alias = method_df.iloc[0]["method_alias"]
            row_match = method_df[method_df["qid"] == qid]
            if row_match.empty:
                method_ranks[alias] = 99
                final_hits[alias] = 0
                continue

            row = row_match.iloc[0]
            ranking_urls = choose_ranking_urls(row)
            final_urls = split_pipe(row["final_urls"]) if "final_urls" in row else []
            gold_rank = get_rank_of_gold(ranking_urls, gold_urls)
            final_hit = get_rank_of_gold(final_urls, gold_urls)

            method_ranks[alias] = int(gold_rank) if gold_rank is not None else 99
            final_hits[alias] = 1 if final_hit is not None else 0

        rank_values = np.array(list(method_ranks.values()), dtype=np.float64)
        hit_values = np.array(list(final_hits.values()), dtype=np.float64)
        score_rows.append(
            {
                "qid": qid,
                "topic": qrow["topic"],
                "question": qrow["question"],
                "gold_url": qrow.get("gold_url", ""),
                "rank_range": float(rank_values.max() - rank_values.min()),
                "rank_std": float(rank_values.std()),
                "hit_disagreement": float(hit_values.max() - hit_values.min()),
                "selection_score": float(rank_values.std() + 2.0 * (hit_values.max() - hit_values.min())),
                "method_ranks_json": json.dumps(method_ranks, ensure_ascii=False, sort_keys=True),
                "final_hits_json": json.dumps(final_hits, ensure_ascii=False, sort_keys=True),
            }
        )

    return pd.DataFrame(score_rows)


def select_sample_questions(
    questions_df: pd.DataFrame,
    selection_df: pd.DataFrame,
    sample_size: int,
) -> pd.DataFrame:
    quotas = build_topic_quotas(questions_df, sample_size)
    selected_parts: List[pd.DataFrame] = []

    for topic, quota in quotas.items():
        sub = selection_df[selection_df["topic"] == topic].copy()
        if sub.empty:
            continue
        sub = sub.sort_values(
            by=["selection_score", "rank_range", "rank_std", "qid"],
            ascending=[False, False, False, True],
        )
        selected_parts.append(sub.head(quota))

    selected = pd.concat(selected_parts, ignore_index=True)
    selected = selected.sort_values(["topic", "qid"]).reset_index(drop=True)
    return selected


def write_sample_questions(sample_df: pd.DataFrame, questions_df: pd.DataFrame, output_dir: Path) -> Path:
    sample_qids = set(sample_df["qid"].tolist())
    selected_questions = questions_df[questions_df["qid"].isin(sample_qids)].copy()
    selected_questions = selected_questions.sort_values(["topic", "qid"]).reset_index(drop=True)

    output_path = output_dir / "answer_eval_sample_questions.jsonl"
    with open(output_path, "w", encoding="utf-8") as handle:
        for _, row in selected_questions.iterrows():
            payload = {
                key: row[key]
                for key in ["qid", "question", "topic", "gold_url", "gold_urls"]
                if key in row and pd.notna(row[key])
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return output_path


def build_answer_packet(
    sample_df: pd.DataFrame,
    answer_method_specs: Sequence[Tuple[str, Path]],
    output_dir: Path,
    seed: int,
) -> None:
    if not answer_method_specs:
        return

    answer_frames = {
        alias: load_method_frame(alias, path)
        for alias, path in answer_method_specs
    }

    required_aliases = [alias for alias, _ in answer_method_specs]
    slots = [chr(ord("A") + idx) for idx in range(len(required_aliases))]
    rng = np.random.default_rng(seed)

    packet_rows: List[Dict] = []
    key_rows: List[Dict] = []

    for _, sample_row in sample_df.iterrows():
        qid = sample_row["qid"]
        system_payloads: List[Dict] = []
        for alias in required_aliases:
            frame = answer_frames[alias]
            row_match = frame[frame["qid"] == qid]
            if row_match.empty:
                continue
            row = row_match.iloc[0]
            system_payloads.append(
                {
                    "alias": alias,
                    "answer": row.get("answer", ""),
                    "insufficient_evidence": row.get("insufficient_evidence", ""),
                    "final_urls": row.get("final_urls", ""),
                    "final_titles": row.get("final_titles", ""),
                }
            )

        if len(system_payloads) != len(required_aliases):
            continue

        order = rng.permutation(len(system_payloads))
        shuffled = [system_payloads[idx] for idx in order]
        packet_row = {
            "qid": qid,
            "topic": sample_row["topic"],
            "question": sample_row["question"],
        }

        for slot, payload in zip(slots, shuffled):
            packet_row[f"slot_{slot}_answer"] = payload["answer"]
            packet_row[f"slot_{slot}_insufficient_evidence"] = payload["insufficient_evidence"]
            packet_row[f"slot_{slot}_final_urls"] = payload["final_urls"]
            packet_row[f"slot_{slot}_final_titles"] = payload["final_titles"]
            packet_row[f"slot_{slot}_faithfulness_1to5"] = ""
            packet_row[f"slot_{slot}_citation_support_1to5"] = ""
            packet_row[f"slot_{slot}_helpfulness_1to5"] = ""
            packet_row[f"slot_{slot}_abstention_ok_0or1"] = ""
            packet_row[f"slot_{slot}_notes"] = ""
            key_rows.append(
                {
                    "qid": qid,
                    "slot": slot,
                    "method_alias": payload["alias"],
                }
            )

        packet_rows.append(packet_row)

    if packet_rows:
        pd.DataFrame(packet_rows).to_csv(
            output_dir / "answer_level_blind_eval.csv",
            index=False,
            encoding="utf-8-sig",
        )
        pd.DataFrame(key_rows).to_csv(
            output_dir / "answer_level_blind_eval_key.csv",
            index=False,
            encoding="utf-8-sig",
        )


def build_relevance_packet(
    sample_df: pd.DataFrame,
    retrieval_method_specs: Sequence[Tuple[str, Path]],
    output_dir: Path,
) -> None:
    retrieval_frames = {
        alias: load_method_frame(alias, path)
        for alias, path in retrieval_method_specs
    }

    packet_rows: List[Dict] = []
    key_rows: List[Dict] = []

    for _, sample_row in sample_df.iterrows():
        qid = sample_row["qid"]
        question = sample_row["question"]
        topic = sample_row["topic"]
        gold_urls = normalize_gold_urls(sample_row.get("gold_urls"), sample_row.get("gold_url"))
        url_table: Dict[str, Dict] = {}

        for alias, frame in retrieval_frames.items():
            row_match = frame[frame["qid"] == qid]
            if row_match.empty:
                continue
            row = row_match.iloc[0]
            urls = choose_ranking_urls(row)[:10]
            titles = choose_ranking_titles(row)[:10]

            for rank, url in enumerate(urls, start=1):
                record = url_table.setdefault(
                    url,
                    {
                        "qid": qid,
                        "topic": topic,
                        "question": question,
                        "url": url,
                        "title": titles[rank - 1] if rank - 1 < len(titles) else "",
                        "appears_in_methods": [],
                        "ranks_by_method": {},
                    },
                )
                if alias not in record["appears_in_methods"]:
                    record["appears_in_methods"].append(alias)
                record["ranks_by_method"][alias] = rank

        for url, record in sorted(
            url_table.items(),
            key=lambda item: (len(item[1]["appears_in_methods"]) * -1, min(item[1]["ranks_by_method"].values()), item[0]),
        ):
            packet_rows.append(
                {
                    "qid": record["qid"],
                    "topic": record["topic"],
                    "question": record["question"],
                    "url": record["url"],
                    "title": record["title"],
                    "appears_in_methods": "|".join(sorted(record["appears_in_methods"])),
                    "ranks_by_method": json.dumps(record["ranks_by_method"], ensure_ascii=False, sort_keys=True),
                    "relevance_score_0_1_2": "",
                    "review_notes": "",
                }
            )
            key_rows.append(
                {
                    "qid": record["qid"],
                    "url": record["url"],
                    "is_reference_gold": int(url in set(gold_urls)),
                    "gold_urls": json.dumps(gold_urls, ensure_ascii=False),
                    "ranks_by_method": json.dumps(record["ranks_by_method"], ensure_ascii=False, sort_keys=True),
                }
            )

    if packet_rows:
        pd.DataFrame(packet_rows).to_csv(
            output_dir / "graded_relevance_packet.csv",
            index=False,
            encoding="utf-8-sig",
        )
        pd.DataFrame(key_rows).to_csv(
            output_dir / "graded_relevance_packet_key.csv",
            index=False,
            encoding="utf-8-sig",
        )


def main() -> None:
    if not QUESTIONS_FILE.exists():
        raise FileNotFoundError(f"{QUESTIONS_FILE} not found")

    retrieval_specs = parse_method_specs(RETRIEVAL_METHOD_SPECS)
    answer_specs = parse_method_specs(ANSWER_METHOD_SPECS) if ANSWER_METHOD_SPECS.strip() else []

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    questions_df = load_jsonl(QUESTIONS_FILE)
    selection_df = build_selection_frame(questions_df, retrieval_specs)
    sample_df = select_sample_questions(questions_df, selection_df, SAMPLE_SIZE)

    selection_df.to_csv(OUTPUT_DIR / "sample_selection_scores.csv", index=False, encoding="utf-8-sig")
    sample_df.to_csv(OUTPUT_DIR / "sample_selection.csv", index=False, encoding="utf-8-sig")
    sample_questions_path = write_sample_questions(sample_df, questions_df, OUTPUT_DIR)

    build_answer_packet(sample_df, answer_specs, OUTPUT_DIR, seed=SEED)
    build_relevance_packet(sample_df, retrieval_specs, OUTPUT_DIR)

    print(f"Saved: {OUTPUT_DIR / 'sample_selection_scores.csv'}")
    print(f"Saved: {OUTPUT_DIR / 'sample_selection.csv'}")
    print(f"Saved: {sample_questions_path}")
    print(f"Saved: {OUTPUT_DIR / 'graded_relevance_packet.csv'}")
    print(f"Saved: {OUTPUT_DIR / 'graded_relevance_packet_key.csv'}")
    if answer_specs:
        print(f"Saved: {OUTPUT_DIR / 'answer_level_blind_eval.csv'}")
        print(f"Saved: {OUTPUT_DIR / 'answer_level_blind_eval_key.csv'}")


if __name__ == "__main__":
    main()
