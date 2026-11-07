"""Dependency-light, explicit protocol primitives for the ICDE factorial audit."""
from __future__ import annotations

import gzip
import hashlib
import json
import math
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

PROTOCOL_VERSION = "icde-e3-v1"


def canonical_json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def read_jsonl(path):
    with Path(path).open(encoding="utf-8-sig") as f:
        return [json.loads(line) for line in f if line.strip()]


def save_json(path, obj):
    """Atomic write; a killed process never leaves a successful-looking checkpoint."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (canonical_json(obj) + "\n").encode("utf-8")
    if path.suffix == ".gz":
        data = gzip.compress(data, mtime=0)
    temp = path.with_name(path.name + ".tmp")
    temp.write_bytes(data)
    temp.replace(path)


def load_json(path):
    path = Path(path)
    data = path.read_bytes()
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    return json.loads(data)


def normalize_url(url):
    """Lower-case scheme/host, remove fragment and trailing slash; retain query."""
    parts = urlsplit(str(url).strip())
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(),
                       parts.path.rstrip("/"), parts.query, ""))


def gold_urls(question):
    values = question.get("gold_urls") or [question.get("gold_url", "")]
    if isinstance(values, str):
        values = [values]
    return sorted({normalize_url(v) for v in values if v})


def identify_corpus(corpus):
    """Preserve every input row; disambiguate legacy ID collisions by frozen row index."""
    counts = Counter(c["chunk_id"] for c in corpus)
    exact = Counter((c["chunk_id"], c["url"], c["text"]) for c in corpus)
    rows = []
    for index, item in enumerate(corpus):
        original = item["chunk_id"]
        rows.append({**item, "original_chunk_id": original, "corpus_row": index,
                     "chunk_id": f"{original}::row{index:06d}" if counts[original] > 1 else original})
    if len({r["chunk_id"] for r in rows}) != len(rows):
        raise ValueError("Canonical corpus row ID collision.")
    return rows, {"input_rows": len(rows), "unique_legacy_ids": len(counts),
                  "colliding_legacy_ids": sum(v > 1 for v in counts.values()),
                  "extra_rows_with_colliding_id": sum(v - 1 for v in counts.values()),
                  "exact_duplicate_extra_rows": sum(v - 1 for v in exact.values()),
                  "policy": "Retain every row; collided IDs receive ::row plus zero-based frozen corpus row index. No content deduplication."}


@dataclass(frozen=True)
class Configuration:
    pool: int
    cap: str
    reranker: str
    budget: int

    @property
    def config_id(self):
        return f"p{self.pool}_{self.cap}_{self.reranker}_b{self.budget}"

    def record(self):
        return {"config_id": self.config_id, **asdict(self)}


def configurations(reranker="m3"):
    return [Configuration(pool, cap, ranker, budget)
            for pool in (16, 64)
            for ranker in ("none", reranker)
            for cap in (("off", "pre") if ranker == "none" else ("off", "pre", "post"))
            for budget in (512, 2048)]


def url_cap(items, cap=2):
    """Stable removal within the raw pool, with no replenishment outside the pool."""
    seen = Counter()
    result = []
    for item in items:
        url = normalize_url(item["url"])
        if seen[url] < cap:
            result.append(item)
            seen[url] += 1
    return result


def rerank(items, scores):
    # An exact score tie keeps first-stage order, never corpus or hash-map order.
    return sorted(items, key=lambda x: (-float(scores[x["chunk_id"]]), x["raw_rank"]))


def stage(items, scores=None):
    return [{"chunk_id": item["chunk_id"], "url": item["url"],
             "original_chunk_id": item.get("original_chunk_id", item["chunk_id"]),
             "corpus_row": item.get("corpus_row"),
             "normalized_url": normalize_url(item["url"]), "rank": i,
             "raw_rank": item["raw_rank"], "chunk_tokens": len(item["token_ids"]),
             "retrieval_score": item["retrieval_score"],
             "rerank_score": None if scores is None else float(scores[item["chunk_id"]])}
            for i, item in enumerate(items, 1)]


def pack_prefix(items, budget, separator_id, decode):
    """Concatenate chunk token IDs with one separator; truncate only the last chunk.

    Budget counts this exact evidence token stream. No question, metadata, answer
    prompt or special start/end tokens are included. A partial chunk is explicitly
    distinguished from full delivery. No skipping of longer chunks is permitted.
    """
    if budget < 1:
        raise ValueError("budget must be positive")
    tokens, selected = [], []
    for item in items:
        if not item["token_ids"]:
            continue
        overhead = 1 if selected else 0
        remaining = budget - len(tokens) - overhead
        if remaining <= 0:
            break
        take = item["token_ids"][:remaining]
        if overhead:
            tokens.append(separator_id)
        tokens.extend(take)
        selected.append({"chunk_id": item["chunk_id"], "url": item["url"],
                         "original_chunk_id": item.get("original_chunk_id", item["chunk_id"]),
                         "corpus_row": item.get("corpus_row"),
                         "rank": len(selected) + 1, "raw_rank": item["raw_rank"],
                         "chunk_tokens": len(item["token_ids"]),
                         "delivered_tokens": len(take), "partial": len(take) < len(item["token_ids"]),
                         "text": decode(take), "token_ids": take})
        if len(take) < len(item["token_ids"]):
            break
    return {"chunks": selected, "token_ids": tokens, "used_tokens": len(tokens),
            "separator_tokens": max(len(selected) - 1, 0), "budget": budget}


def url_metrics(items, gold, k=10):
    """Binary URL nDCG after stable URL collapse; IDCG uses ALL gold URLs."""
    gold = set(map(normalize_url, gold))
    urls = list(dict.fromkeys(normalize_url(x["url"]) for x in items))
    ranks = [i for i, u in enumerate(urls, 1) if u in gold]
    dcg = sum(1 / math.log2(r + 1) for r in ranks if r <= k)
    idcg = sum(1 / math.log2(r + 1) for r in range(1, min(k, len(gold)) + 1))
    return {"G": int(bool(ranks)), "url_mrr": 1 / min(ranks) if ranks else 0.0,
            "url_ndcg_at_10": dcg / idcg if idcg else None,
            "gold_url_recall": len(ranks) / len(gold) if gold else None}


def first_url_loss(raw, pre, ordered, post, final, gold):
    """Mutually exclusive source-retention diagnostic, never a support-loss label."""
    for name, rows in (("candidate_not_covered", raw), ("pre_cap", pre),
                       ("rerank_membership", ordered), ("post_cap", post), ("budget", final)):
        if not url_metrics(rows, gold)["G"]:
            return name
    return "retained"


def freeze_manifest(path, manifest):
    path = Path(path)
    if path.exists():
        previous = load_json(path)
        if previous["identity_hash"] != manifest["identity_hash"]:
            raise ValueError("Output directory belongs to a different protocol/data/model/argument hash; use a new output directory.")
        return previous
    save_json(path, manifest)
    return manifest


def require_human_utility(rows):
    if not rows:
        raise ValueError("E2 requires independent human utility labels; none were supplied.")
    for row in rows:
        if row.get("annotation_source") != "human_adjudicated" or row.get("U") not in (0, 1, 2):
            raise ValueError("E2 requires adjudicated human U in {0,1,2}; URL hits/automatic judges cannot substitute.")
