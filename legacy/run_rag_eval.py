import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from scipy import sparse as sp
from sentence_transformers import CrossEncoder, SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from tqdm import tqdm

try:
    import torch
except Exception:  # pragma: no cover - best effort runtime import
    torch = None


from rerankhuts.paths import oncology_path
from legacy.paths import resolve_legacy_path


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
RESULT_DIR = BASE_DIR / "result"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

EMBEDDING_CACHE_DIR = BASE_DIR / ".cache"


def resolve_path(raw_value: Optional[str], default: Path) -> Path:
    if not raw_value:
        return default
    candidate = Path(raw_value)
    return resolve_legacy_path(BASE_DIR, candidate)


def portable_path(path: Path) -> str:
    """A run's input path as recorded in its per-question rows.

    Written relative to the repository when it lives there, because these rows
    are released: an absolute `D:\\Pycharm\\...` path names one machine's
    directory layout, tells a reader nothing about which question set or corpus
    produced the numbers, and makes two runs on different machines look like
    they read different files when they read the same one.
    """
    try:
        return path.relative_to(BASE_DIR).as_posix()
    except ValueError:
        return str(path)


def env_flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes"}


def env_optional_int(name: str) -> Optional[int]:
    raw_value = os.getenv(name, "").strip()
    if not raw_value:
        return None
    return int(raw_value)


DEFAULT_OUTPUT_RESULTS_FILE = RESULT_DIR / "rag_results_experiments.csv"
CORPUS_FILE = resolve_path(os.getenv("CORPUS_FILE"), oncology_path("corpus_chunks_v1.jsonl", root=BASE_DIR))
QUESTIONS_FILE = resolve_path(os.getenv("QUESTIONS_FILE"), oncology_path("questions.jsonl", root=BASE_DIR))
OUTPUT_RESULTS_FILE = resolve_path(os.getenv("OUTPUT_RESULTS_FILE"), DEFAULT_OUTPUT_RESULTS_FILE)
EXPERIMENT_SETTINGS_FILE = resolve_path(os.getenv("EXPERIMENT_SETTINGS_FILE"), RESULT_DIR / "experiment_settings.csv")
EXPERIMENT_OUTPUT_DIR = resolve_path(os.getenv("EXPERIMENT_OUTPUT_DIR"), OUTPUT_RESULTS_FILE.parent)
EXPERIMENT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
EXPERIMENT_SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

if "EXPERIMENT_OUTPUT_PREFIX" in os.environ:
    EXPERIMENT_OUTPUT_PREFIX = os.getenv("EXPERIMENT_OUTPUT_PREFIX", "rag_results").strip() or "rag_results"
elif OUTPUT_RESULTS_FILE == DEFAULT_OUTPUT_RESULTS_FILE:
    EXPERIMENT_OUTPUT_PREFIX = "rag_results"
else:
    EXPERIMENT_OUTPUT_PREFIX = OUTPUT_RESULTS_FILE.stem

EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "BAAI/bge-small-en-v1.5")
RERANK_MODEL_NAME = os.getenv("RERANK_MODEL_NAME", "cross-encoder/ms-marco-MiniLM-L-6-v2")
DEFAULT_SPARSE_BACKEND = os.getenv("SPARSE_BACKEND", "tfidf").strip().lower() or "tfidf"
DEFAULT_FUSION_METHOD = os.getenv("FUSION_METHOD", "linear").strip().lower() or "linear"

DEFAULT_RETRIEVE_POOL = int(os.getenv("TOP_K_RETRIEVE", "24"))
DEFAULT_FINAL_TOP_K = int(os.getenv("TOP_K_RERANK", "4"))
DEFAULT_SMALL_POOL = int(os.getenv("ABLATION_SMALL_POOL_TOP_K", "8"))
DEFAULT_RERANK_DEPTH = env_optional_int("RERANK_DEPTH")
DEFAULT_BM25_POOL = int(os.getenv("BM25_RETRIEVE_POOL", "100"))
DEFAULT_RRF_DEPTH = int(os.getenv("RRF_FUSION_DEPTH", "100"))
MAX_CHUNKS_PER_URL = int(os.getenv("MAX_CHUNKS_PER_URL", "2"))
CORPUS_BATCH_SIZE = int(os.getenv("CORPUS_BATCH_SIZE", "64"))
QUESTION_BATCH_SIZE = int(os.getenv("QUESTION_BATCH_SIZE", "32"))
SAVE_EVIDENCE_TEXTS = env_flag("SAVE_EVIDENCE_TEXTS", "0")
RUN_GENERATION = env_flag("RUN_GENERATION", "1")
RERANK_BATCH_SIZE = int(os.getenv("RERANK_BATCH_SIZE", "32"))

SPARSE_MAX_FEATURES = int(os.getenv("SPARSE_MAX_FEATURES", "50000"))
SPARSE_NGRAM_MAX = int(os.getenv("SPARSE_NGRAM_MAX", "2"))
DEFAULT_HYBRID_ALPHA = float(os.getenv("HYBRID_ALPHA", "0.65"))
# Defaults are the best settings from the BM25 grid search reported in the
# paper (k1 in {0.9, 1.2, 1.5} x b in {0.4, 0.75, 0.9}); every best row used
# b = 0.4. Shipping the tuned value as the default is what makes a plain
# `python -m rerankhuts legacy-eval` reproduce the paper's sparse and hybrid rows --
# with the untuned b = 0.75 the BM25 rows score far lower. The grid sweep
# passes BM25_K1 / BM25_B explicitly, so it is unaffected by this default.
BM25_K1 = float(os.getenv("BM25_K1", "1.2"))
BM25_B = float(os.getenv("BM25_B", "0.4"))
RRF_K = int(os.getenv("RRF_K", "60"))

MODEL_DEVICE = os.getenv("MODEL_DEVICE", "auto").strip().lower() or "auto"
EMBED_MODEL_DEVICE = os.getenv("EMBED_MODEL_DEVICE", MODEL_DEVICE).strip().lower() or MODEL_DEVICE
RERANK_MODEL_DEVICE = os.getenv("RERANK_MODEL_DEVICE", MODEL_DEVICE).strip().lower() or MODEL_DEVICE
USE_FP16 = env_flag("USE_FP16", "1")
LOCAL_MODEL_FILES_ONLY = env_flag("LOCAL_MODEL_FILES_ONLY", "0") or env_flag("HF_HUB_OFFLINE", "0") or env_flag("TRANSFORMERS_OFFLINE", "0")
CORPUS_SOURCE_PRESET = os.getenv("CORPUS_SOURCE_PRESET", "all").strip().lower() or "all"
CORPUS_SOURCE_NAMES = [
    value.strip()
    for value in os.getenv("CORPUS_SOURCE_NAMES", "").split(",")
    if value.strip()
]

RUN_EXPERIMENTS = [
    name.strip()
    for name in os.getenv(
        "RUN_EXPERIMENTS",
        ",".join([
            "control_dense_only",
            "control_sparse_only",
            "control_hybrid",
            "baseline",
            "rerank",
            "ablation_no_dedup",
            "ablation_small_pool",
            "hybrid_rerank",
        ]),
    ).split(",")
    if name.strip()
]


@dataclass(frozen=True)
class ExperimentConfig:
    name: str
    description: str
    retrieve_pool_size: int
    final_top_k: int
    use_dense: bool
    use_sparse: bool
    use_rerank: bool
    use_dedup: bool
    max_chunks_per_url: Optional[int] = None
    hybrid_alpha: float = DEFAULT_HYBRID_ALPHA
    rerank_depth: Optional[int] = DEFAULT_RERANK_DEPTH
    sparse_backend: str = DEFAULT_SPARSE_BACKEND
    fusion_method: str = DEFAULT_FUSION_METHOD
    fusion_depth: Optional[int] = None
    rerank_model: Optional[str] = None  # None → global RERANK_MODEL_NAME
    rerank_kind: str = "cross_encoder"  # "cross_encoder" | "llm" | "source_aware"


def resolve_rerank_model(config: ExperimentConfig) -> str:
    """Return the human-readable reranker model name used by a config."""
    if config.rerank_kind == "llm":
        return os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    return config.rerank_model or RERANK_MODEL_NAME


@dataclass(frozen=True)
class SparseIndex:
    backend: str
    vectorizer: object
    corpus_matrix: sp.csr_matrix


SOURCE_PRESETS: Dict[str, Optional[Set[str]]] = {
    "all": None,
    "nci_only": {"nci_guidelines"},
    "nci_textbook": {"nci_guidelines", "medrag_textbooks_oncology"},
    "nci_pubmed": {"nci_guidelines", "pubmed_cancer_abstracts"},
    "textbook_only": {"medrag_textbooks_oncology"},
    "pubmed_only": {"pubmed_cancer_abstracts"},
}


EXPERIMENT_REGISTRY = {
    "control_dense_only": ExperimentConfig(
        name="control_dense_only",
        description="Dense retrieval only with no diversity cap and no reranking.",
        retrieve_pool_size=DEFAULT_FINAL_TOP_K,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=False,
        use_rerank=False,
        use_dedup=False,
        max_chunks_per_url=None,
    ),
    "control_sparse_only": ExperimentConfig(
        name="control_sparse_only",
        description="Sparse lexical retrieval only with no diversity cap and no reranking.",
        retrieve_pool_size=DEFAULT_FINAL_TOP_K,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=False,
        use_sparse=True,
        use_rerank=False,
        use_dedup=False,
        max_chunks_per_url=None,
        sparse_backend="tfidf",
    ),
    "control_hybrid": ExperimentConfig(
        name="control_hybrid",
        description="Dense plus sparse hybrid retrieval with URL diversity cap, no reranking.",
        retrieve_pool_size=DEFAULT_RETRIEVE_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=True,
        use_rerank=False,
        use_dedup=True,
        max_chunks_per_url=MAX_CHUNKS_PER_URL,
        sparse_backend="tfidf",
        fusion_method="linear",
    ),
    "baseline": ExperimentConfig(
        name="baseline",
        description="Dense retrieval with larger candidate pool plus URL diversity cap.",
        retrieve_pool_size=DEFAULT_RETRIEVE_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=False,
        use_rerank=False,
        use_dedup=True,
        max_chunks_per_url=MAX_CHUNKS_PER_URL,
    ),
    "rerank": ExperimentConfig(
        name="rerank",
        description="Dense retrieval plus reranking and URL diversity cap.",
        retrieve_pool_size=DEFAULT_RETRIEVE_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=False,
        use_rerank=True,
        use_dedup=True,
        max_chunks_per_url=MAX_CHUNKS_PER_URL,
    ),
    "ablation_base_no_dedup": ExperimentConfig(
        name="ablation_base_no_dedup",
        description="Remove the URL diversity cap while keeping the Base retrieval design.",
        retrieve_pool_size=DEFAULT_RETRIEVE_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=False,
        use_rerank=False,
        use_dedup=False,
        max_chunks_per_url=None,
    ),
    "ablation_base_small_pool": ExperimentConfig(
        name="ablation_base_small_pool",
        description="Use the Base retrieval design but limit the first-stage dense retrieval pool.",
        retrieve_pool_size=DEFAULT_SMALL_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=False,
        use_rerank=False,
        use_dedup=True,
        max_chunks_per_url=MAX_CHUNKS_PER_URL,
    ),
    "ablation_no_dedup": ExperimentConfig(
        name="ablation_no_dedup",
        description="Remove the URL diversity cap while keeping dense retrieval and reranking.",
        retrieve_pool_size=DEFAULT_RETRIEVE_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=False,
        use_rerank=True,
        use_dedup=False,
        max_chunks_per_url=None,
    ),
    "ablation_small_pool": ExperimentConfig(
        name="ablation_small_pool",
        description="Use reranking but limit the first-stage dense retrieval pool.",
        retrieve_pool_size=DEFAULT_SMALL_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=False,
        use_rerank=True,
        use_dedup=True,
        max_chunks_per_url=MAX_CHUNKS_PER_URL,
    ),
    "hybrid_rerank": ExperimentConfig(
        name="hybrid_rerank",
        description="Dense plus sparse hybrid retrieval followed by reranking and URL diversity cap.",
        retrieve_pool_size=DEFAULT_RETRIEVE_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=True,
        use_rerank=True,
        use_dedup=True,
        max_chunks_per_url=MAX_CHUNKS_PER_URL,
        sparse_backend="tfidf",
        fusion_method="linear",
    ),
    "bm25_only": ExperimentConfig(
        name="bm25_only",
        description="BM25 sparse retrieval only with no diversity cap and no reranking.",
        retrieve_pool_size=DEFAULT_BM25_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=False,
        use_sparse=True,
        use_rerank=False,
        use_dedup=False,
        max_chunks_per_url=None,
        sparse_backend="bm25",
    ),
    "bm25_base": ExperimentConfig(
        name="bm25_base",
        description="BM25 sparse retrieval with larger candidate pool plus URL diversity cap.",
        retrieve_pool_size=DEFAULT_BM25_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=False,
        use_sparse=True,
        use_rerank=False,
        use_dedup=True,
        max_chunks_per_url=MAX_CHUNKS_PER_URL,
        sparse_backend="bm25",
    ),
    "hybrid_bm25": ExperimentConfig(
        name="hybrid_bm25",
        description="Dense plus BM25 linear hybrid retrieval with URL diversity cap, no reranking.",
        retrieve_pool_size=DEFAULT_RETRIEVE_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=True,
        use_rerank=False,
        use_dedup=True,
        max_chunks_per_url=MAX_CHUNKS_PER_URL,
        sparse_backend="bm25",
        fusion_method="linear",
    ),
    "rrf_hybrid": ExperimentConfig(
        name="rrf_hybrid",
        description="Dense plus BM25 RRF hybrid retrieval with URL diversity cap, no reranking.",
        retrieve_pool_size=DEFAULT_RETRIEVE_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=True,
        use_rerank=False,
        use_dedup=True,
        max_chunks_per_url=MAX_CHUNKS_PER_URL,
        sparse_backend="bm25",
        fusion_method="rrf",
        fusion_depth=DEFAULT_RRF_DEPTH,
    ),
    "rrf_hybrid_rerank": ExperimentConfig(
        name="rrf_hybrid_rerank",
        description="Dense plus BM25 RRF hybrid retrieval followed by reranking and URL diversity cap.",
        retrieve_pool_size=DEFAULT_RETRIEVE_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=True,
        use_rerank=True,
        use_dedup=True,
        max_chunks_per_url=MAX_CHUNKS_PER_URL,
        sparse_backend="bm25",
        fusion_method="rrf",
        fusion_depth=DEFAULT_RRF_DEPTH,
    ),
    "rerank_bge_base": ExperimentConfig(
        name="rerank_bge_base",
        description="Dense retrieval plus BGE-reranker-base cross-encoder reranking and URL diversity cap.",
        retrieve_pool_size=DEFAULT_RETRIEVE_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=False,
        use_rerank=True,
        use_dedup=True,
        max_chunks_per_url=MAX_CHUNKS_PER_URL,
        rerank_model="BAAI/bge-reranker-base",
    ),
    "rerank_bge_m3": ExperimentConfig(
        name="rerank_bge_m3",
        description="Dense retrieval plus BGE-reranker-v2-m3 cross-encoder reranking and URL diversity cap.",
        retrieve_pool_size=DEFAULT_RETRIEVE_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=False,
        use_rerank=True,
        use_dedup=True,
        max_chunks_per_url=MAX_CHUNKS_PER_URL,
        rerank_model="BAAI/bge-reranker-v2-m3",
    ),
    "rerank_medcpt": ExperimentConfig(
        name="rerank_medcpt",
        description="Dense retrieval plus MedCPT biomedical cross-encoder reranking and URL diversity cap.",
        retrieve_pool_size=DEFAULT_RETRIEVE_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=False,
        use_rerank=True,
        use_dedup=True,
        max_chunks_per_url=MAX_CHUNKS_PER_URL,
        rerank_model="ncbi/MedCPT-Cross-Encoder",
    ),
    "rerank_llm": ExperimentConfig(
        name="rerank_llm",
        description="Dense retrieval plus LLM-based listwise reranking and URL diversity cap.",
        retrieve_pool_size=DEFAULT_RETRIEVE_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=False,
        use_rerank=True,
        use_dedup=True,
        max_chunks_per_url=MAX_CHUNKS_PER_URL,
        rerank_kind="llm",
    ),
    "rerank_source_aware": ExperimentConfig(
        name="rerank_source_aware",
        description="Dense retrieval plus source-aware reranking (NCI/PDQ source prior) and URL diversity cap.",
        retrieve_pool_size=DEFAULT_RETRIEVE_POOL,
        final_top_k=DEFAULT_FINAL_TOP_K,
        use_dense=True,
        use_sparse=False,
        use_rerank=True,
        use_dedup=True,
        max_chunks_per_url=MAX_CHUNKS_PER_URL,
        rerank_kind="source_aware",
    ),
}


def load_jsonl(path: Path) -> List[Dict]:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    return items


def resolve_device(requested: str) -> str:
    normalized = requested.strip().lower()
    if normalized != "auto":
        return normalized
    if torch is not None and torch.cuda.is_available():
        return "cuda"
    return "cpu"


def configure_torch_runtime(device: str) -> None:
    if torch is None or not device.startswith("cuda"):
        return
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    if hasattr(torch, "set_float32_matmul_precision"):
        torch.set_float32_matmul_precision("high")


def describe_runtime(device: str) -> str:
    if torch is None:
        return f"device={device} (torch unavailable)"
    if device.startswith("cuda") and torch.cuda.is_available():
        gpu_idx = 0
        if ":" in device:
            try:
                gpu_idx = int(device.split(":", 1)[1])
            except Exception:
                gpu_idx = 0
        return f"device={device} ({torch.cuda.get_device_name(gpu_idx)})"
    return f"device={device}"


def get_source_name_filter() -> Optional[Set[str]]:
    if CORPUS_SOURCE_NAMES:
        return set(CORPUS_SOURCE_NAMES)
    if CORPUS_SOURCE_PRESET not in SOURCE_PRESETS:
        valid = ", ".join(sorted(SOURCE_PRESETS))
        raise ValueError(f"Unsupported CORPUS_SOURCE_PRESET={CORPUS_SOURCE_PRESET!r}. Valid options: {valid}")
    return SOURCE_PRESETS[CORPUS_SOURCE_PRESET]


def filter_corpus_by_source(corpus: List[Dict]) -> List[Dict]:
    allowed_sources = get_source_name_filter()
    if not allowed_sources:
        return corpus

    filtered = [item for item in corpus if item.get("source_name") in allowed_sources]
    if not filtered:
        raise ValueError(f"No corpus rows matched selected sources: {sorted(allowed_sources)}")
    return filtered


def get_corpus_signature(corpus: List[Dict]) -> str:
    digest = hashlib.md5()
    digest.update(str(CORPUS_FILE.resolve()).encode("utf-8"))
    digest.update(f"::{CORPUS_SOURCE_PRESET}::{','.join(sorted(get_source_name_filter() or []))}".encode("utf-8"))
    digest.update(f"::rows={len(corpus)}".encode("utf-8"))
    for item in corpus:
        digest.update(str(item.get("chunk_id", "")).encode("utf-8"))
        digest.update(b"|")
        digest.update(str(item.get("url", "")).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()[:12]


def build_client() -> OpenAI:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    if not api_key:
        raise ValueError("Missing DEEPSEEK_API_KEY in .env")

    return OpenAI(api_key=api_key, base_url=base_url)


def get_experiments() -> List[ExperimentConfig]:
    missing = [name for name in RUN_EXPERIMENTS if name not in EXPERIMENT_REGISTRY]
    if missing:
        valid = ", ".join(EXPERIMENT_REGISTRY.keys())
        raise ValueError(f"Unknown experiments: {missing}. Valid options: {valid}")
    return [EXPERIMENT_REGISTRY[name] for name in RUN_EXPERIMENTS]


def get_embedding_cache_path(corpus_signature: str, model_name: str) -> Path:
    cache_key = f"{corpus_signature}::{model_name}"
    digest = hashlib.md5(cache_key.encode("utf-8")).hexdigest()[:12]
    return EMBEDDING_CACHE_DIR / f"corpus_embeddings_{digest}.npy"


def load_or_encode_corpus_embeddings(
    corpus: List[Dict],
    embed_model: SentenceTransformer,
    corpus_signature: str,
) -> np.ndarray:
    EMBEDDING_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = get_embedding_cache_path(corpus_signature, EMBED_MODEL_NAME)

    if cache_path.exists():
        print(f"Loading cached corpus embeddings: {cache_path.name}")
        return np.load(cache_path).astype(np.float32, copy=False)

    print("Encoding corpus embeddings...")
    corpus_texts = [item["text"] for item in corpus]
    embeddings = embed_model.encode(
        corpus_texts,
        batch_size=CORPUS_BATCH_SIZE,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    ).astype(np.float32, copy=False)

    np.save(cache_path, embeddings)
    print(f"Saved corpus embedding cache: {cache_path.name}")
    return embeddings


def encode_question_embeddings(questions: List[Dict], embed_model: SentenceTransformer) -> np.ndarray:
    texts = [item["question"] for item in questions]
    return embed_model.encode(
        texts,
        batch_size=QUESTION_BATCH_SIZE,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    ).astype(np.float32, copy=False)


def build_sparse_index(corpus: List[Dict], backend: str) -> SparseIndex:
    corpus_texts = [item["text"] for item in corpus]
    backend = backend.strip().lower()

    if backend == "tfidf":
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, SPARSE_NGRAM_MAX),
            max_features=SPARSE_MAX_FEATURES,
        )
        corpus_matrix = vectorizer.fit_transform(corpus_texts).tocsr()
        return SparseIndex(backend=backend, vectorizer=vectorizer, corpus_matrix=corpus_matrix)

    if backend == "bm25":
        vectorizer = CountVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, SPARSE_NGRAM_MAX),
            max_features=SPARSE_MAX_FEATURES,
        )
        count_matrix = vectorizer.fit_transform(corpus_texts).tocsr().astype(np.float32)
        doc_lengths = np.asarray(count_matrix.sum(axis=1)).ravel().astype(np.float32, copy=False)
        avg_doc_length = float(doc_lengths.mean()) if len(doc_lengths) else 0.0
        avg_doc_length = avg_doc_length if avg_doc_length > 0 else 1.0
        df = np.bincount(count_matrix.indices, minlength=count_matrix.shape[1]).astype(np.float32, copy=False)
        num_docs = float(count_matrix.shape[0])
        idf = np.log1p((num_docs - df + 0.5) / (df + 0.5)).astype(np.float32, copy=False)

        weights = count_matrix.tocoo(copy=True)
        norm = BM25_K1 * (1.0 - BM25_B + BM25_B * (doc_lengths / avg_doc_length))
        numerators = weights.data * (BM25_K1 + 1.0)
        denominators = weights.data + norm[weights.row]
        weights.data = (idf[weights.col] * (numerators / denominators)).astype(np.float32, copy=False)
        corpus_matrix = weights.tocsr()
        return SparseIndex(backend=backend, vectorizer=vectorizer, corpus_matrix=corpus_matrix)

    raise ValueError(f"Unsupported sparse backend: {backend}")


def encode_sparse_questions(questions: List[Dict], sparse_index: SparseIndex):
    return sparse_index.vectorizer.transform([item["question"] for item in questions])


def top_k_indices(scores: np.ndarray, top_k: int) -> np.ndarray:
    top_k = min(top_k, len(scores))
    if top_k <= 0:
        return np.array([], dtype=np.int64)
    if top_k == len(scores):
        return np.argsort(scores)[::-1]

    idx = np.argpartition(scores, -top_k)[-top_k:]
    return idx[np.argsort(scores[idx])[::-1]]


def min_max_normalize(scores: np.ndarray) -> np.ndarray:
    if scores.size == 0:
        return scores
    min_val = float(scores.min())
    max_val = float(scores.max())
    if max_val <= min_val:
        return np.zeros_like(scores, dtype=np.float32)
    return ((scores - min_val) / (max_val - min_val)).astype(np.float32, copy=False)


def compute_rrf_scores(
    dense_scores: np.ndarray,
    sparse_scores: np.ndarray,
    fusion_depth: int,
) -> np.ndarray:
    if fusion_depth <= 0:
        raise ValueError("fusion_depth must be positive for RRF.")

    fused = np.zeros_like(dense_scores, dtype=np.float32)
    for scores in [dense_scores, sparse_scores]:
        top_idx = top_k_indices(scores, fusion_depth)
        if len(top_idx) == 0:
            continue
        ranks = np.arange(1, len(top_idx) + 1, dtype=np.float32)
        fused[top_idx] += 1.0 / (RRF_K + ranks)
    return fused


def compute_retrieval_scores(
    config: ExperimentConfig,
    query_dense_embedding: Optional[np.ndarray],
    query_sparse_vector,
    corpus_embeddings: Optional[np.ndarray],
    sparse_index: Optional[SparseIndex],
) -> Dict[str, np.ndarray]:
    dense_scores = None
    sparse_scores = None

    if config.use_dense:
        if query_dense_embedding is None or corpus_embeddings is None:
            raise ValueError(f"Experiment {config.name} requires dense embeddings.")
        dense_scores = corpus_embeddings @ query_dense_embedding

    if config.use_sparse:
        if query_sparse_vector is None or sparse_index is None:
            raise ValueError(f"Experiment {config.name} requires sparse retrieval inputs.")
        sparse_scores = (sparse_index.corpus_matrix @ query_sparse_vector.T).toarray().ravel().astype(np.float32, copy=False)

    if config.use_dense and config.use_sparse:
        if config.fusion_method == "linear":
            dense_norm = min_max_normalize(dense_scores)
            sparse_norm = min_max_normalize(sparse_scores)
            retrieve_scores = (config.hybrid_alpha * dense_norm) + ((1.0 - config.hybrid_alpha) * sparse_norm)
        elif config.fusion_method == "rrf":
            fusion_depth = config.fusion_depth or max(config.retrieve_pool_size, DEFAULT_RRF_DEPTH)
            retrieve_scores = compute_rrf_scores(
                dense_scores=dense_scores,
                sparse_scores=sparse_scores,
                fusion_depth=fusion_depth,
            )
        else:
            raise ValueError(f"Unsupported fusion method: {config.fusion_method}")
    elif config.use_dense:
        retrieve_scores = dense_scores.astype(np.float32, copy=False)
    elif config.use_sparse:
        retrieve_scores = sparse_scores.astype(np.float32, copy=False)
    else:
        raise ValueError(f"Experiment {config.name} must enable dense or sparse retrieval.")

    return {
        "retrieve_scores": retrieve_scores,
        "dense_scores": dense_scores if dense_scores is not None else np.zeros_like(retrieve_scores),
        "sparse_scores": sparse_scores if sparse_scores is not None else np.zeros_like(retrieve_scores),
    }


def retrieve_candidates(
    config: ExperimentConfig,
    corpus: List[Dict],
    query_dense_embedding: Optional[np.ndarray],
    query_sparse_vector,
    corpus_embeddings: Optional[np.ndarray],
    sparse_index: Optional[SparseIndex],
) -> List[Dict]:
    score_pack = compute_retrieval_scores(
        config=config,
        query_dense_embedding=query_dense_embedding,
        query_sparse_vector=query_sparse_vector,
        corpus_embeddings=corpus_embeddings,
        sparse_index=sparse_index,
    )

    top_idx = top_k_indices(score_pack["retrieve_scores"], config.retrieve_pool_size)

    results = []
    for idx in top_idx:
        item = corpus[int(idx)].copy()
        item["retrieve_score"] = float(score_pack["retrieve_scores"][int(idx)])
        item["dense_score"] = float(score_pack["dense_scores"][int(idx)])
        item["sparse_score"] = float(score_pack["sparse_scores"][int(idx)])
        results.append(item)
    return results


def deduplicate_by_url(candidates: List[Dict], max_per_url: Optional[int]) -> List[Dict]:
    if not max_per_url:
        return list(candidates)

    url_counter = {}
    filtered = []

    for item in candidates:
        url = item["url"]
        url_counter.setdefault(url, 0)

        if url_counter[url] < max_per_url:
            filtered.append(item)
            url_counter[url] += 1

    return filtered


def rerank_candidates(
    query: str,
    candidates: List[Dict],
    reranker: CrossEncoder,
    rerank_depth: Optional[int] = None,
) -> List[Dict]:
    if not candidates:
        return []

    if rerank_depth is None or rerank_depth <= 0:
        rerank_depth = len(candidates)
    rerank_depth = min(rerank_depth, len(candidates))

    rerank_pool = candidates[:rerank_depth]
    tail = [item.copy() for item in candidates[rerank_depth:]]
    pairs = [(query, item["text"]) for item in rerank_pool]
    scores = reranker.predict(
        pairs,
        batch_size=RERANK_BATCH_SIZE,
        show_progress_bar=False,
    )

    ranked = []
    for item, score in zip(rerank_pool, scores):
        scored = item.copy()
        scored["rerank_score"] = float(score)
        ranked.append(scored)

    ranked.sort(key=lambda x: x["rerank_score"], reverse=True)
    return ranked + tail


def source_aware_rerank_candidates(
    query: str,
    candidates: List[Dict],
    reranker: CrossEncoder,
    rerank_depth: Optional[int] = None,
) -> List[Dict]:
    """Re-rank with a source-authority prior: NCI/PDQ guideline chunks first.

    A "source-aware" re-ranker is one that knows the benchmark's authoritative
    source (NCI/PDQ treatment guidelines) and prioritises it. This is the
    positive control for the paper's central claim: off-the-shelf semantic
    re-rankers hurt because their training objective is misaligned with the
    benchmark's authoritative-source target, so a re-ranker that is told the
    source should recover the loss. The semantic score still breaks ties WITHIN
    each source tier (the re-ranker is not a pure filter); the source tier just
    sorts first.

    It is deliberately reported as a diagnostic, not a leaderboard entry: on a
    benchmark whose gold URLs are all NCI/PDQ, prioritising NCI chunks is close
    to tautological, which is exactly the point -- it isolates source-misalignment
    from any other cause of the semantic re-rankers' drop.
    """
    if not candidates:
        return []

    if rerank_depth is None or rerank_depth <= 0:
        rerank_depth = len(candidates)
    rerank_depth = min(rerank_depth, len(candidates))

    rerank_pool = candidates[:rerank_depth]
    tail = [item.copy() for item in candidates[rerank_depth:]]
    pairs = [(query, item["text"]) for item in rerank_pool]
    scores = reranker.predict(
        pairs,
        batch_size=RERANK_BATCH_SIZE,
        show_progress_bar=False,
    )

    ranked = []
    for item, score in zip(rerank_pool, scores):
        scored = item.copy()
        scored["rerank_score"] = float(score)
        scored["_source_authoritative"] = int(
            scored.get("source_name") == "nci_guidelines")
        ranked.append(scored)

    ranked.sort(key=lambda x: (x["_source_authoritative"], x["rerank_score"]),
                reverse=True)
    return ranked + tail


def score_chunks_listwise(client: OpenAI, model_name: str, query: str, texts: List[str]) -> List[float]:
    """Ask an LLM to score each candidate chunk 0-2 for relevance to the query.

    Returns one float score per text, in the same order. On any failure, returns
    zeros so the caller can fall back to the original order without crashing.
    """
    if not texts:
        return []

    numbered = []
    for idx, text in enumerate(texts, start=1):
        numbered.append(f"[{idx}] {text[:500]}")
    joined = "\n\n".join(numbered)

    system_prompt = (
        "You are a retrieval relevance judge for oncology treatment QA. "
        "For each numbered evidence chunk, rate how well it supports a specific "
        "answer to the question: 2 = directly relevant/authoritative, "
        "1 = partially or background relevant, 0 = irrelevant. "
        "Return ONLY a JSON object with a single key \"scores\" mapping to a list "
        "of integers, one per chunk, in the same order."
    )
    user_prompt = (
        f"Question:\n{query}\n\n"
        f"Candidate chunks:\n{joined}\n\n"
        f"Return JSON: {{\"scores\": [<int for [1]>, <int for [2]>, ...]}} with exactly {len(texts)} integers."
    )

    try:
        response = client.chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content
        parsed = json.loads(content)
        raw_scores = parsed.get("scores", [])
        scores = []
        for value in raw_scores[: len(texts)]:
            try:
                scores.append(float(value))
            except Exception:
                scores.append(0.0)
        while len(scores) < len(texts):
            scores.append(0.0)
        return scores
    except Exception:
        return [0.0] * len(texts)


def llm_rerank_candidates(
    query: str,
    candidates: List[Dict],
    client: OpenAI,
    model_name: str,
    rerank_depth: Optional[int] = None,
) -> List[Dict]:
    if not candidates:
        return []

    if rerank_depth is None or rerank_depth <= 0:
        rerank_depth = len(candidates)
    rerank_depth = min(rerank_depth, len(candidates))

    rerank_pool = candidates[:rerank_depth]
    tail = [item.copy() for item in candidates[rerank_depth:]]
    scores = score_chunks_listwise(client, model_name, query, [item["text"] for item in rerank_pool])

    ranked = []
    for item, score in zip(rerank_pool, scores):
        scored = item.copy()
        scored["rerank_score"] = float(score)
        ranked.append(scored)

    ranked.sort(key=lambda x: x["rerank_score"], reverse=True)
    return ranked + tail


def build_prompt(question: str, evidence: List[Dict]):
    evidence_text = []
    for idx, item in enumerate(evidence, start=1):
        snippet = item["text"][:1200]
        evidence_text.append(
            f"[{idx}] CHUNK_ID: {item['chunk_id']}\n"
            f"TITLE: {item['title']}\n"
            f"URL: {item['url']}\n"
            f"TEXT: {snippet}"
        )

    joined_evidence = "\n\n".join(evidence_text)

    system_prompt = (
        "You are an oncology RAG assistant. "
        "Answer only with information supported by the provided evidence. "
        "If the evidence is incomplete, ambiguous, or missing key treatment details, set insufficient_evidence to true. "
        "Return concise clinical-style JSON and do not invent unsupported details."
    )

    user_prompt = (
        f"Question:\n{question}\n\n"
        f"Evidence:\n{joined_evidence}\n\n"
        "Return JSON with keys:\n"
        "- answer: string\n"
        "- evidence_ids: list of CHUNK_ID strings actually used\n"
        "- insufficient_evidence: true or false\n"
    )

    return system_prompt, user_prompt


def generate_answer(client: OpenAI, model_name: str, question: str, evidence: List[Dict]) -> Dict:
    system_prompt, user_prompt = build_prompt(question, evidence)

    response = client.chat.completions.create(
        model=model_name,
        response_format={"type": "json_object"},
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = response.choices[0].message.content

    try:
        parsed = json.loads(content)
    except Exception:
        parsed = {
            "answer": content,
            "evidence_ids": [],
            "insufficient_evidence": None,
        }

    return parsed


def pack_candidates(candidates: List[Dict]) -> Dict[str, str]:
    texts = ""
    if SAVE_EVIDENCE_TEXTS:
        texts = "\n\n====================\n\n".join([item["text"][:1500] for item in candidates])

    return {
        "chunk_ids": " | ".join([item["chunk_id"] for item in candidates]),
        "urls": " | ".join([item["url"] for item in candidates]),
        "titles": " | ".join([item["title"] for item in candidates]),
        "retrieve_scores": " | ".join([str(round(item.get("retrieve_score", 0.0), 6)) for item in candidates]),
        "dense_scores": " | ".join([str(round(item.get("dense_score", 0.0), 6)) for item in candidates]),
        "sparse_scores": " | ".join([str(round(item.get("sparse_score", 0.0), 6)) for item in candidates]),
        "rerank_scores": " | ".join([str(round(item.get("rerank_score", 0.0), 6)) for item in candidates]),
        "texts": texts,
    }


def run_experiment(
    config: ExperimentConfig,
    questions: List[Dict],
    question_embeddings: Optional[np.ndarray],
    sparse_question_vectors_by_backend: Dict[str, object],
    corpus: List[Dict],
    corpus_embeddings: Optional[np.ndarray],
    sparse_indexes: Dict[str, SparseIndex],
    rerankers: Dict[str, object],
    client: Optional[OpenAI],
    model_name: str,
    run_generation: bool,
) -> pd.DataFrame:
    rows = []

    for idx, question_obj in enumerate(tqdm(questions, desc=f"Running {config.name}")):
        started_at = time.perf_counter()
        query = question_obj["question"]
        query_dense_embedding = question_embeddings[idx] if question_embeddings is not None else None
        sparse_index = sparse_indexes.get(config.sparse_backend) if config.use_sparse else None
        sparse_question_vectors = sparse_question_vectors_by_backend.get(config.sparse_backend)
        query_sparse_vector = sparse_question_vectors[idx] if sparse_question_vectors is not None else None

        retrieval_started_at = time.perf_counter()
        retrieved = retrieve_candidates(
            config=config,
            corpus=corpus,
            query_dense_embedding=query_dense_embedding,
            query_sparse_vector=query_sparse_vector,
            corpus_embeddings=corpus_embeddings,
            sparse_index=sparse_index,
        )
        retrieval_ms = (time.perf_counter() - retrieval_started_at) * 1000.0

        candidates = deduplicate_by_url(
            retrieved,
            max_per_url=config.max_chunks_per_url if config.use_dedup else None,
        )

        rerank_ms = 0.0
        if config.use_rerank:
            rerank_started_at = time.perf_counter()
            if config.rerank_kind == "llm":
                if client is None:
                    raise ValueError(f"Experiment {config.name} uses an LLM reranker but no client is available.")
                ranking = llm_rerank_candidates(
                    query=query,
                    candidates=candidates,
                    client=client,
                    model_name=model_name,
                    rerank_depth=config.rerank_depth,
                )
            elif config.rerank_kind == "source_aware":
                reranker = rerankers.get((config.rerank_kind, resolve_rerank_model(config)))
                if reranker is None:
                    raise ValueError(f"Experiment {config.name} requires reranker {resolve_rerank_model(config)!r}.")
                ranking = source_aware_rerank_candidates(
                    query=query,
                    candidates=candidates,
                    reranker=reranker,
                    rerank_depth=config.rerank_depth,
                )
            else:
                reranker = rerankers.get((config.rerank_kind, resolve_rerank_model(config)))
                if reranker is None:
                    raise ValueError(f"Experiment {config.name} requires reranker {resolve_rerank_model(config)!r}.")
                ranking = rerank_candidates(
                    query=query,
                    candidates=candidates,
                    reranker=reranker,
                    rerank_depth=config.rerank_depth,
                )
            rerank_ms = (time.perf_counter() - rerank_started_at) * 1000.0
        else:
            ranking = list(candidates)

        final_evidence = ranking[:config.final_top_k]
        generation_ms = 0.0
        if run_generation:
            if client is None:
                raise ValueError("Generation is enabled but no OpenAI client is available.")
            generation_started_at = time.perf_counter()
            answer_obj = generate_answer(
                client=client,
                model_name=model_name,
                question=query,
                evidence=final_evidence,
            )
            generation_ms = (time.perf_counter() - generation_started_at) * 1000.0
        else:
            answer_obj = {
                "answer": None,
                "evidence_ids": [],
                "insufficient_evidence": None,
            }

        retrieved_pack = pack_candidates(retrieved)
        candidate_pack = pack_candidates(candidates)
        ranking_pack = pack_candidates(ranking)
        final_pack = pack_candidates(final_evidence)

        rows.append({
            **asdict(config),
            "embed_model_name": EMBED_MODEL_NAME,
            "rerank_model_name": resolve_rerank_model(config) if config.use_rerank else "",
            "generation_model_name": model_name if run_generation else "",
            "run_generation": run_generation,
            "question_file": portable_path(QUESTIONS_FILE),
            "corpus_file": portable_path(CORPUS_FILE),
            "corpus_source_preset": CORPUS_SOURCE_PRESET,
            "corpus_source_names": ",".join(sorted(get_source_name_filter() or [])) or "all",
            "corpus_chunk_count": len(corpus),
            "embed_device": resolve_device(EMBED_MODEL_DEVICE) if config.use_dense else "",
            "rerank_device": resolve_device(RERANK_MODEL_DEVICE) if config.use_rerank else "",
            "mode": config.name,
            "qid": question_obj.get("qid"),
            "question": query,
            "retrieval_ms": round(retrieval_ms, 3),
            "rerank_ms": round(rerank_ms, 3),
            "generation_ms": round(generation_ms, 3),
            "total_ms": round((time.perf_counter() - started_at) * 1000.0, 3),
            "retrieved_count": len(retrieved),
            "candidate_count": len(candidates),
            "ranking_count": len(ranking),
            "final_count": len(final_evidence),
            "retrieved_chunk_ids": retrieved_pack["chunk_ids"],
            "retrieved_urls": retrieved_pack["urls"],
            "retrieved_titles": retrieved_pack["titles"],
            "retrieved_scores": retrieved_pack["retrieve_scores"],
            "retrieved_dense_scores": retrieved_pack["dense_scores"],
            "retrieved_sparse_scores": retrieved_pack["sparse_scores"],
            "candidate_chunk_ids": candidate_pack["chunk_ids"],
            "candidate_urls": candidate_pack["urls"],
            "candidate_titles": candidate_pack["titles"],
            "candidate_retrieve_scores": candidate_pack["retrieve_scores"],
            "candidate_dense_scores": candidate_pack["dense_scores"],
            "candidate_sparse_scores": candidate_pack["sparse_scores"],
            "deduped_chunk_ids": candidate_pack["chunk_ids"],
            "deduped_urls": candidate_pack["urls"],
            "deduped_titles": candidate_pack["titles"],
            "deduped_scores": candidate_pack["retrieve_scores"],
            "ranking_chunk_ids": ranking_pack["chunk_ids"],
            "ranking_urls": ranking_pack["urls"],
            "ranking_titles": ranking_pack["titles"],
            "ranking_retrieve_scores": ranking_pack["retrieve_scores"],
            "ranking_dense_scores": ranking_pack["dense_scores"],
            "ranking_sparse_scores": ranking_pack["sparse_scores"],
            "ranking_rerank_scores": ranking_pack["rerank_scores"],
            "final_chunk_ids": final_pack["chunk_ids"],
            "final_urls": final_pack["urls"],
            "final_titles": final_pack["titles"],
            "final_retrieve_scores": final_pack["retrieve_scores"],
            "final_dense_scores": final_pack["dense_scores"],
            "final_sparse_scores": final_pack["sparse_scores"],
            "final_rerank_scores": final_pack["rerank_scores"],
            "final_evidence_texts": final_pack["texts"],
            "answer": answer_obj.get("answer"),
            "evidence_ids": json.dumps(answer_obj.get("evidence_ids", []), ensure_ascii=False),
            "insufficient_evidence": answer_obj.get("insufficient_evidence"),
        })

    return pd.DataFrame(rows)


def experiment_output_path(name: str) -> Path:
    return EXPERIMENT_OUTPUT_DIR / f"{EXPERIMENT_OUTPUT_PREFIX}_{name}.csv"


def guard_combined_write(path: Path, modes_this_run: list) -> None:
    """Refuse to shrink a combined file by writing a subset of its modes.

    A combined file is the union of the modes its batch ran. When a corrective
    run re-runs only some of them -- the BM25-backed modes, say, after the
    default `b` changed -- and is pointed at the batch's combined path, the
    write below replaces a nine-mode file with a four-mode one. Nothing
    downstream can tell: `combine_revision_results.py` and the Pareto builder
    just read fewer rows, so a figure quietly loses the systems it should
    compare, and the modes left out keep numbers from the run being corrected.

    That is exactly how `supp_strong_baselines_validated.csv` came to hold four
    of its nine modes, so the check is a hard stop: a partial re-run has to name
    its own output file.
    """
    if not path.exists():
        return
    try:
        existing = set(pd.read_csv(path, usecols=["mode"])["mode"].astype(str))
    except Exception:
        # An unreadable or modeless file is not evidence of a shrink; overwrite it.
        return
    dropped = sorted(existing - {str(m) for m in modes_this_run})
    if dropped:
        raise SystemExit(
            f"Refusing to overwrite {path.name}: it holds {len(existing)} modes and "
            f"this run produced {len(modes_this_run)}, dropping {', '.join(dropped)}.\n"
            f"A partial re-run must write to its own OUTPUT_RESULTS_FILE. To rebuild "
            f"the full file, re-run every mode of the batch; to stitch the existing "
            f"per-mode files instead, use combine_revision_results.py."
        )


def main():
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    if not CORPUS_FILE.exists():
        raise FileNotFoundError(f"{CORPUS_FILE} not found.")

    if not QUESTIONS_FILE.exists():
        raise FileNotFoundError(f"{QUESTIONS_FILE} not found.")

    experiments = get_experiments()
    settings_df = pd.DataFrame([asdict(exp) for exp in experiments])
    # The BM25 hyperparameters are module-level globals, not ExperimentConfig
    # fields, so `asdict` alone would leave them out of the settings record. That
    # gap is not cosmetic: a run made before the BM25_B default changed left no
    # trace of which b it used, and the mismatch only surfaced later as two
    # batches disagreeing on the same questions. Record them explicitly so every
    # batch states the scoring function it was actually run with.
    settings_df["bm25_k1"] = BM25_K1
    settings_df["bm25_b"] = BM25_B
    settings_df.to_csv(
        EXPERIMENT_SETTINGS_FILE,
        index=False,
        encoding="utf-8-sig",
    )
    print(f"Saved experiment settings: {EXPERIMENT_SETTINGS_FILE.name}")

    print(f"Using corpus file: {CORPUS_FILE}")
    print(f"Using questions file: {QUESTIONS_FILE}")
    print(f"Experiments: {[exp.name for exp in experiments]}")
    print(f"Run generation: {RUN_GENERATION}")
    print(f"Corpus source preset: {CORPUS_SOURCE_PRESET}")

    embed_device = resolve_device(EMBED_MODEL_DEVICE)
    rerank_device = resolve_device(RERANK_MODEL_DEVICE)
    configure_torch_runtime(embed_device)
    configure_torch_runtime(rerank_device)
    print(f"Embedding runtime: {describe_runtime(embed_device)}")
    print(f"Rerank runtime: {describe_runtime(rerank_device)}")

    corpus = load_jsonl(CORPUS_FILE)
    corpus = filter_corpus_by_source(corpus)
    corpus_signature = get_corpus_signature(corpus)
    selected_sources = sorted({item.get('source_name', '') for item in corpus})
    print(f"Selected corpus sources: {selected_sources}")
    print(f"Selected corpus chunks: {len(corpus)}")
    questions = load_jsonl(QUESTIONS_FILE)

    needs_dense = any(exp.use_dense for exp in experiments)
    needs_sparse = any(exp.use_sparse for exp in experiments)
    needs_rerank = any(exp.use_rerank for exp in experiments)

    embed_model = None
    corpus_embeddings = None
    question_embeddings = None
    if needs_dense:
        print("Loading embedding model...")
        embed_model = SentenceTransformer(
            EMBED_MODEL_NAME,
            device=embed_device,
            local_files_only=LOCAL_MODEL_FILES_ONLY,
        )
        if USE_FP16 and embed_device.startswith("cuda"):
            embed_model.half()
        corpus_embeddings = load_or_encode_corpus_embeddings(
            corpus=corpus,
            embed_model=embed_model,
            corpus_signature=corpus_signature,
        )
        print("Encoding question embeddings...")
        question_embeddings = encode_question_embeddings(questions=questions, embed_model=embed_model)

    sparse_indexes: Dict[str, SparseIndex] = {}
    sparse_question_vectors_by_backend: Dict[str, object] = {}
    if needs_sparse:
        sparse_backends = sorted({exp.sparse_backend for exp in experiments if exp.use_sparse})
        for backend in sparse_backends:
            print(f"Building sparse index: {backend}")
            sparse_index = build_sparse_index(corpus=corpus, backend=backend)
            sparse_indexes[backend] = sparse_index
            sparse_question_vectors_by_backend[backend] = encode_sparse_questions(
                questions=questions,
                sparse_index=sparse_index,
            )

    rerankers: Dict[str, object] = {}
    if needs_rerank:
        for exp in experiments:
            if not exp.use_rerank or exp.rerank_kind not in ("cross_encoder", "source_aware"):
                continue
            model = resolve_rerank_model(exp)
            key = (exp.rerank_kind, model)
            if key in rerankers:
                continue
            print(f"Loading reranker: {model}")
            reranker = CrossEncoder(
                model,
                device=rerank_device,
                local_files_only=LOCAL_MODEL_FILES_ONLY,
                trust_remote_code=True,
            )
            if USE_FP16 and rerank_device.startswith("cuda") and hasattr(reranker, "model"):
                reranker.model.half()
            rerankers[key] = reranker

    needs_client = RUN_GENERATION or any(exp.rerank_kind == "llm" for exp in experiments)
    client = None
    if needs_client:
        print("Building DeepSeek client...")
        client = build_client()
    else:
        print("Skipping answer generation; retrieval-only mode is enabled.")

    all_results = []
    for config in experiments:
        result_df = run_experiment(
            config=config,
            questions=questions,
            question_embeddings=question_embeddings,
            sparse_question_vectors_by_backend=sparse_question_vectors_by_backend,
            corpus=corpus,
            corpus_embeddings=corpus_embeddings,
            sparse_indexes=sparse_indexes,
            rerankers=rerankers,
            client=client,
            model_name=model_name,
            run_generation=RUN_GENERATION,
        )
        result_df.to_csv(experiment_output_path(config.name), index=False, encoding="utf-8-sig")
        print(f"Saved experiment results: {experiment_output_path(config.name).name}")
        all_results.append(result_df)

    combined_df = pd.concat(all_results, ignore_index=True)
    guard_combined_write(OUTPUT_RESULTS_FILE, [exp.name for exp in experiments])
    combined_df.to_csv(OUTPUT_RESULTS_FILE, index=False, encoding="utf-8-sig")
    print(f"Saved combined results: {OUTPUT_RESULTS_FILE.name}")


if __name__ == "__main__":
    main()
