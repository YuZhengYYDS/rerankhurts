"""Oracle-free operators for the new workload; no imports from frozen runners."""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, replace
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit


SCHEMA_VERSION = "strengthening-traces-v1"


def canonical_json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_hash(path):
    hasher = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def read_jsonl(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def load_json(path):
    path = Path(path)
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (canonical_json(value) + "\n").encode("utf-8")
    if path.suffix == ".gz":
        payload = gzip.compress(payload, mtime=0)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


@dataclass(frozen=True)
class Config:
    retriever: str = "dense"
    dense_view: str = "prefix512"
    pool: int = 64
    reranker: str = "m3"
    cap: int = 0
    cap_stage: str = "off"
    refill: bool = False
    budget: int = 512
    packing: str = "prefix"
    score_view: str = "prefix512"
    policy_stage: str = "none"
    mmr_lambda: float | None = None

    def __post_init__(self):
        choices = {"retriever": {"dense", "bm25", "fusion"},
                   "dense_view": {"prefix128", "prefix512", "window512"},
                   "reranker": {"none", "m3", "minilm"},
                   "cap_stage": {"off", "pre", "post"},
                   "packing": {"prefix", "whole", "window"},
                   "score_view": {"prefix128", "prefix512", "window512"},
                   "policy_stage": {"none", "pre_retrieve", "post_retrieve", "post_rerank"}}
        for field, allowed in choices.items():
            if getattr(self, field) not in allowed:
                raise ValueError(f"Invalid {field}: {getattr(self, field)}")
        if self.pool < 1 or self.budget < 1 or self.cap not in (0, 1, 2, 4):
            raise ValueError("Positive pool/budget and cap in {0,1,2,4} required")
        if (self.cap == 0) != (self.cap_stage == "off") or (self.refill and not self.cap):
            raise ValueError("An off cap has no location/refill; active caps need pre/post")
        if self.mmr_lambda is not None and not 0 <= self.mmr_lambda <= 1:
            raise ValueError("MMR lambda must lie in [0,1]")
        if self.mmr_lambda is not None and self.dense_view != "prefix512":
            raise ValueError("The frozen MMR baseline uses prefix512 query/document cosine")

    @property
    def config_id(self):
        cap = "off" if not self.cap else f"{self.cap_stage}{self.cap}"
        return (f"{self.retriever}_p{self.pool}_{self.reranker}_{cap}"
                f"{'_refill' if self.refill else ''}_b{self.budget}_{self.packing}"
                f"_{self.score_view}_d{self.dense_view}_pol{self.policy_stage}"
                f"{'' if self.mmr_lambda is None else '_mmr' + str(self.mmr_lambda)}")

    def record(self):
        return {"config_id": self.config_id, **asdict(self)}

    @classmethod
    def from_record(cls, record):
        return cls(**{key: value for key, value in record.items() if key != "config_id"})


def build_configurations():
    """Main 28 cells plus fixed, limited mechanism/robustness submatrices."""
    base = Config()
    configs = []
    caps = [(0, "off"), *[(cap, place) for cap in (1, 2, 4) for place in ("pre", "post")]]
    for budget in (256, 512, 1024, 2048):
        configs.extend(replace(base, budget=budget, cap=cap, cap_stage=place) for cap, place in caps)
    for budget in (512, 2048):
        configs.extend(replace(base, budget=budget, cap=cap, cap_stage=place, refill=True)
                       for cap in (1, 2) for place in ("pre", "post"))
        configs.extend(replace(base, budget=budget, retriever=retriever, reranker=reranker)
                       for retriever in ("dense", "bm25", "fusion")
                       for reranker in ("none", "m3", "minilm"))
        configs.extend(replace(base, budget=budget, reranker="minilm", cap=2, cap_stage=place)
                       for place in ("pre", "post"))
        configs.extend(replace(base, budget=budget, retriever=retriever, cap=2, cap_stage=place)
                       for retriever in ("bm25", "fusion") for place in ("pre", "post"))
        selected_caps = ((0, "off"), (2, "pre"), (2, "post"))
        for cap, place in selected_caps:
            anchor = replace(base, budget=budget, cap=cap, cap_stage=place)
            configs.extend(replace(anchor, packing=packing) for packing in ("whole", "window"))
            configs.extend(replace(anchor, score_view=view) for view in ("prefix128", "window512"))
            configs.extend(replace(anchor, policy_stage=stage)
                           for stage in ("pre_retrieve", "post_retrieve", "post_rerank"))
            configs.append(replace(anchor, pool=16))
        configs.extend(replace(base, budget=budget, retriever=retriever, reranker="none", mmr_lambda=0.5)
                       for retriever in ("dense", "fusion"))
        configs.extend(replace(base, budget=budget, dense_view=view, reranker=reranker)
                       for view in ("prefix128", "window512") for reranker in ("none", "m3"))
    return list({config.config_id: config for config in configs}.values())


def normalize_url(url):
    parts = urlsplit(url)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), parts.query, ""))


def allowed_source(url, prefixes):
    # Prefixes are explicit public task parameters, never inferred from labels.
    return not prefixes or any(url.startswith(prefix) for prefix in prefixes)


def url_cap(items, cap):
    if not cap:
        return list(items)
    seen, selected = Counter(), []
    for item in items:
        url = normalize_url(item["url"])
        if seen[url] < cap:
            selected.append(item)
            seen[url] += 1
    return selected


def lexical_tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25:
    """Collection-local BM25: positive Robertson IDF, k1=1.2 and b=0.75."""
    def __init__(self, texts, k1=1.2, b=0.75):
        self.rows = [Counter(lexical_tokens(text)) for text in texts]
        self.lengths = [sum(row.values()) for row in self.rows]
        self.average = sum(self.lengths) / max(len(self.rows), 1)
        df = Counter(token for row in self.rows for token in row)
        self.idf = {token: math.log(1 + (len(self.rows) - n + .5) / (n + .5)) for token, n in df.items()}
        self.k1, self.b = k1, b

    def scores(self, query):
        terms = set(lexical_tokens(query))
        output = []
        for row, length in zip(self.rows, self.lengths):
            normalizer = self.k1 * (1 - self.b + self.b * length / max(self.average, 1))
            output.append(sum(self.idf.get(term, 0) * row[term] * (self.k1 + 1) / (row[term] + normalizer)
                              for term in terms if row[term]))
        return output


def reciprocal_rank_fusion(rankings, constant=60):
    scores = Counter()
    for ranking in rankings:
        for rank, item_id in enumerate(ranking, 1):
            scores[item_id] += 1 / (constant + rank)
    return dict(scores)


def mmr_order(items, similarities, relevance, weight=0.5):
    """Reorder the complete candidate set; deterministic ties keep input order.

    similarities is candidate cosine similarity; relevance is query cosine,
    avoiding incompatible BM25/logit scales in the MMR objective.
    """
    remaining, selected = list(range(len(items))), []
    while remaining:
        def objective(index):
            redundancy = max((float(similarities[index][j]) for j in selected), default=0.0)
            return weight * float(relevance[index]) - (1 - weight) * redundancy
        best = max(remaining, key=objective)
        selected.append(best)
        remaining.remove(best)
    return [items[index] for index in selected]


def stage(items, scores=None):
    return [{"chunk_id": item["chunk_id"], "url": item["url"], "rank": rank,
             "raw_rank": item.get("raw_rank"), "retrieval_score": item.get("retrieval_score"),
             "rerank_score": scores.get(item["chunk_id"]) if scores else None,
             "chunk_tokens": len(item["token_ids"]), "dense_view": item.get("dense_view"),
             "dense_visible_char_start": item.get("dense_visible_char_start"),
             "dense_visible_char_end": item.get("dense_visible_char_end")}
            for rank, item in enumerate(items, 1)]


def token_windows(length, width=192, overlap=32):
    if width < 1 or overlap < 0 or overlap >= width:
        raise ValueError("Window width must exceed nonnegative overlap")
    start = 0
    while start < length:
        end = min(start + width, length)
        yield start, end
        if end == length:
            break
        start = end - overlap


def segment(item, start, end):
    if not 0 <= start < end <= len(item["token_ids"]):
        raise ValueError("Invalid delivered token interval")
    char_start, char_end = item["offsets"][start][0], item["offsets"][end - 1][1]
    if not 0 <= char_start < char_end <= len(item["text"]):
        raise ValueError("Invalid tokenizer character offsets")
    return {"chunk_id": item["chunk_id"], "url": item["url"],
            "source_token_start": start, "source_token_end": end,
            "char_start": char_start, "char_end": char_end,
            "text": item["text"][char_start:char_end], "token_ids": item["token_ids"][start:end],
            "partial": start > 0 or end < len(item["token_ids"]),
            "chunk_tokens": len(item["token_ids"]), "delivered_tokens": end - start}


def pack(items, budget, separator_id, strategy="prefix", query="", window_width=192):
    """Pack original-text spans using an explicit evidence-token budget.

    prefix: truncate the final ranked chunk. whole: skip chunks that do not fit.
    window: BM25-rank disjoint fixed windows within each ranked chunk, retaining
    chunk order and then window score order. A final window can be truncated.
    No tokenizer decoding, oracle IDs, truth spans, or required facts are read.
    """
    if budget < 1 or strategy not in {"prefix", "whole", "window"}:
        raise ValueError("Invalid packing configuration")
    candidates = []
    for item in items:
        if strategy == "window":
            ranges = list(token_windows(len(item["token_ids"]), window_width, 0))
            texts = [segment(item, start, end)["text"] for start, end in ranges]
            scores = BM25(texts).scores(query)
            ranges = [ranges[i] for i in sorted(range(len(ranges)), key=lambda i: (-scores[i], i))]
        else:
            ranges = [(0, len(item["token_ids"]))] if item["token_ids"] else []
        candidates.extend((item, start, end) for start, end in ranges)
    tokens, selected = [], []
    for item, start, end in candidates:
        remaining = budget - len(tokens) - bool(selected)
        if remaining <= 0:
            break
        if strategy == "whole" and end - start > remaining:
            continue
        take_end = min(end, start + remaining)
        delivered = segment(item, start, take_end)
        delivered["rank"] = len(selected) + 1
        if selected:
            tokens.append(separator_id)
        tokens.extend(delivered["token_ids"])
        selected.append(delivered)
        if take_end < end:
            break
    return {"chunks": selected, "token_ids": tokens, "used_tokens": len(tokens),
            "budget": budget, "separator_tokens": max(0, len(selected) - 1), "packing": strategy}


def validate_inputs(corpus, questions):
    cfields = {"chunk_id", "collection_id", "url", "text"}
    qfields = {"qid", "collection_id", "question", "allowed_url_prefixes"}
    if not corpus or not questions or any(set(row) != cfields for row in corpus) or any(set(row) != qfields for row in questions):
        raise ValueError("Only the declared public corpus/question projection is accepted")
    if len({row["chunk_id"] for row in corpus}) != len(corpus) or len({row["qid"] for row in questions}) != len(questions):
        raise ValueError("Duplicate public IDs")
    collections = {row["collection_id"] for row in corpus}
    if any(q["collection_id"] not in collections for q in questions):
        raise ValueError("Question refers to a missing collection")
    for row in corpus:
        if any(not isinstance(row[key], str) or not row[key] for key in cfields):
            raise ValueError("Corpus fields must be nonempty strings")
    for row in questions:
        if any(not isinstance(row[key], str) or not row[key] for key in qfields - {"allowed_url_prefixes"}):
            raise ValueError("Question text and IDs must be nonempty strings")
        if not isinstance(row["allowed_url_prefixes"], list) or any(not isinstance(x, str) or not x for x in row["allowed_url_prefixes"]):
            raise ValueError("Allowed source prefixes must be an explicit list of nonempty strings")
