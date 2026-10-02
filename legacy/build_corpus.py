import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


BASE_DIR = Path(__file__).resolve().parents[1]
SOURCES_FILE = BASE_DIR / "data_sources.json"
OUTPUT_FILE = BASE_DIR / "corpus_chunks_v1.jsonl"

TARGET_CHUNK_CHARS = int(os.getenv("TARGET_CHUNK_CHARS", "2200"))
CHUNK_OVERLAP_PARAGRAPHS = int(os.getenv("CHUNK_OVERLAP_PARAGRAPHS", "1"))
MIN_PARAGRAPH_CHARS = int(os.getenv("MIN_PARAGRAPH_CHARS", "100"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

DEFAULT_SOURCE_LIMIT = int(os.getenv("DEFAULT_SOURCE_LIMIT", "5000"))
DATASET_DOWNLOAD_MODE = os.getenv("HF_DATASET_DOWNLOAD_MODE", "reuse_dataset_if_exists")

ONCOLOGY_KEYWORDS = [
    "oncology",
    "cancer",
    "tumor",
    "tumour",
    "malignancy",
    "carcinoma",
    "adenocarcinoma",
    "sarcoma",
    "lymphoma",
    "leukemia",
    "leukaemia",
    "melanoma",
    "glioblastoma",
    "myeloma",
]

TREATMENT_HEADING_KEYWORDS = [
    "treatment",
    "therapy",
    "therapies",
    "systemic",
    "chemotherapy",
    "immunotherapy",
    "targeted",
    "targeted therapy",
    "radiation",
    "radiotherapy",
    "surgery",
    "surgical",
    "management",
    "stage information",
    "treatment option overview",
    "option overview",
    "recurrent",
    "relapsed",
    "refractory",
    "metastatic",
    "advanced",
    "localized",
    "unresectable",
    "resectable",
    "consolidation",
    "induction",
    "maintenance",
    "transplant",
    "watchful waiting",
    "supportive care",
    "hormone",
    "endocrine",
    "her2",
    "egfr",
    "alk",
    "pd-l1",
    "biomarker",
]

NON_TREATMENT_HEADING_KEYWORDS = [
    "anatomy",
    "incidence",
    "mortality",
    "risk factors",
    "etiology",
    "pathogenesis",
    "cellular classification",
    "histopathology",
    "screening",
    "prevention",
    "diagnostic evaluation",
    "diagnosis",
    "clinical presentation",
    "general information",
    "prognosis and prognostic factors",
    "statistics",
]


def load_source_config() -> List[Dict]:
    if not SOURCES_FILE.exists():
        raise FileNotFoundError(f"{SOURCES_FILE} not found")

    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    if not isinstance(config, list):
        raise ValueError("data_sources.json must contain a list of source objects")

    return config


def fetch_html(url: str, timeout: int = REQUEST_TIMEOUT) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; OncologyRAGBot/2.0)"
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def normalize_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\[[0-9,\-\s]+\]", "", text)
    return text.strip()


def normalize_multiline_text(text: str) -> str:
    lines = [normalize_text(line) for line in str(text).splitlines()]
    lines = [line for line in lines if line]
    return "\n\n".join(lines)


def preprocess_dom(soup: BeautifulSoup):
    for tag in soup([
        "script", "style", "nav", "footer", "header", "aside",
        "form", "noscript", "svg", "button"
    ]):
        tag.decompose()


def extract_title(soup: BeautifulSoup) -> str:
    if soup.title:
        return normalize_text(soup.title.get_text(" ", strip=True))
    return "untitled"


def get_main_container(soup: BeautifulSoup):
    main = soup.find("main")
    if main is not None:
        return main

    article = soup.find("article")
    if article is not None:
        return article

    return soup.body


def is_noise(text: str) -> bool:
    t = text.lower()

    bad_patterns = [
        "on this page",
        "email this page",
        "print this page",
        "table of contents",
        "more information",
        "board of editors",
        "about this pdq summary",
        "patient version",
        "health professional version",
        "permission to use",
        "related resources",
        "nci information",
        "last revised",
    ]

    if len(text) < MIN_PARAGRAPH_CHARS:
        return True

    if len(text.split()) < 10:
        return True

    if any(pattern in t for pattern in bad_patterns):
        return True

    return False


def heading_is_treatment_related(heading: str) -> bool:
    h = heading.lower()

    if any(x in h for x in NON_TREATMENT_HEADING_KEYWORDS):
        return False

    if any(x in h for x in TREATMENT_HEADING_KEYWORDS):
        return True

    return False


def paragraph_is_treatment_related(text: str) -> bool:
    t = text.lower()

    strong_keywords = [
        "treatment",
        "therapy",
        "therapies",
        "systemic",
        "chemotherapy",
        "immunotherapy",
        "targeted",
        "radiation",
        "radiotherapy",
        "surgery",
        "management",
        "watchful waiting",
        "transplant",
        "induction",
        "consolidation",
        "maintenance",
        "metastatic",
        "recurrent",
        "relapsed",
        "refractory",
        "advanced disease",
        "stage i",
        "stage ii",
        "stage iii",
        "stage iv",
        "her2",
        "egfr",
        "alk",
        "pd-l1",
        "endocrine",
        "hormone therapy",
    ]

    weak_negative = [
        "incidence",
        "mortality",
        "risk factor",
        "anatomy",
        "screening",
        "prevention",
    ]

    if any(x in t for x in strong_keywords):
        return True

    if any(x in t for x in weak_negative):
        return False

    return False


def extract_paragraphs(html: str) -> Tuple[str, List[str]]:
    soup = BeautifulSoup(html, "lxml")
    preprocess_dom(soup)

    title = extract_title(soup)
    container = get_main_container(soup)

    if container is None:
        return title, []

    paragraphs = []
    current_heading = ""
    keep_current_section = False

    for elem in container.find_all(["h1", "h2", "h3", "h4", "p"], recursive=True):
        text = normalize_text(elem.get_text(" ", strip=True))
        if not text:
            continue

        if elem.name in ["h1", "h2", "h3", "h4"]:
            current_heading = text
            keep_current_section = heading_is_treatment_related(current_heading)
            continue

        if is_noise(text):
            continue

        if not keep_current_section and not paragraph_is_treatment_related(text):
            continue

        if current_heading:
            text = f"{current_heading}. {text}"

        paragraphs.append(text)

    seen = set()
    deduped = []
    for paragraph in paragraphs:
        if paragraph not in seen:
            deduped.append(paragraph)
            seen.add(paragraph)

    return title, deduped


def split_text_to_paragraphs(text: str) -> List[str]:
    raw_parts = re.split(r"\n{2,}", normalize_multiline_text(text))
    paragraphs = []

    for part in raw_parts:
        part = normalize_text(part)
        if not part:
            continue

        if len(part) <= TARGET_CHUNK_CHARS:
            paragraphs.append(part)
            continue

        sentences = re.split(r"(?<=[.!?])\s+", part)
        current = []
        current_len = 0

        for sentence in sentences:
            sentence = normalize_text(sentence)
            if not sentence:
                continue

            if current_len + len(sentence) + 1 <= TARGET_CHUNK_CHARS:
                current.append(sentence)
                current_len += len(sentence) + 1
            else:
                if current:
                    paragraphs.append(" ".join(current).strip())
                current = [sentence]
                current_len = len(sentence)

        if current:
            paragraphs.append(" ".join(current).strip())

    return paragraphs


def chunk_paragraphs(paragraphs: List[str], title: str) -> List[str]:
    if not paragraphs:
        return []

    chunks = []
    current = []
    current_len = 0

    for para in paragraphs:
        para_len = len(para)

        if current_len + para_len + 2 <= TARGET_CHUNK_CHARS:
            current.append(para)
            current_len += para_len + 2
        else:
            if current:
                chunk_text = "\n\n".join(current).strip()
                chunk_text = f"DOCUMENT TITLE: {title}\n\n{chunk_text}"
                chunks.append(chunk_text)

            overlap = current[-CHUNK_OVERLAP_PARAGRAPHS:] if current else []
            current = overlap + [para]
            current_len = sum(len(x) + 2 for x in current)

    if current:
        chunk_text = "\n\n".join(current).strip()
        chunk_text = f"DOCUMENT TITLE: {title}\n\n{chunk_text}"
        chunks.append(chunk_text)

    return chunks


def stable_id(*parts: str) -> str:
    joined = "||".join([str(part) for part in parts])
    return hashlib.md5(joined.encode("utf-8")).hexdigest()[:16]


def make_chunk_records(
    source: Dict,
    canonical_id: str,
    title: str,
    url: str,
    paragraphs: List[str],
) -> List[Dict]:
    chunks = chunk_paragraphs(paragraphs, title)
    records = []

    for idx, chunk in enumerate(chunks):
        records.append({
            "chunk_id": f"{stable_id(source['name'], canonical_id)}_{idx}",
            "source_name": source["name"],
            "source_type": source["type"],
            "license": source.get("license", ""),
            "url": url,
            "title": title,
            "chunk_index": idx,
            "text": chunk,
        })

    return records


def keyword_match(text: str, keywords: Optional[List[str]]) -> bool:
    if not keywords:
        return True
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def keyword_reject(text: str, keywords: Optional[List[str]]) -> bool:
    if not keywords:
        return False
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def hf_row_to_text(row: Dict, source: Dict) -> Tuple[str, str, str]:
    title_field = source.get("title_field")
    text_fields = source.get("text_fields", [])
    prefix_fields = source.get("prefix_fields", [])
    id_field = source.get("id_field", "id")

    title = normalize_text(str(row.get(title_field, source["name"]))) if title_field else source["name"]

    pieces = []
    for field in prefix_fields:
        value = row.get(field)
        if value not in (None, ""):
            pieces.append(f"{field}: {normalize_text(str(value))}")

    for field in text_fields:
        value = row.get(field)
        if value not in (None, ""):
            pieces.append(normalize_multiline_text(str(value)))

    body = "\n\n".join([piece for piece in pieces if piece]).strip()
    canonical_id = str(row.get(id_field, stable_id(source["name"], title, body[:120])))

    url_template = source.get("url_template")
    if url_template:
        safe_row = {key: str(value) for key, value in row.items()}
        url = url_template.format(**safe_row)
    else:
        url = f"hf://{source['dataset']}/{canonical_id}"

    return title, body, url


def load_hf_dataset(source: Dict) -> Iterable[Dict]:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise ImportError(
            "datasets is required for Hugging Face sources. "
            "Please install it with `pip install datasets`."
        ) from exc

    split = source.get("split", "train")
    download_mode = DATASET_DOWNLOAD_MODE
    dataset = load_dataset(
        source["dataset"],
        split=split,
        download_mode=download_mode,
    )

    if source.get("shuffle"):
        dataset = dataset.shuffle(seed=int(source.get("seed", 42)))

    return dataset


def build_records_from_hf_source(source: Dict) -> List[Dict]:
    dataset = load_hf_dataset(source)
    max_records = int(source.get("max_records", DEFAULT_SOURCE_LIMIT))
    include_any = source.get("include_any_keywords")
    exclude_any = source.get("exclude_any_keywords")

    records = []
    accepted = 0

    for row in tqdm(dataset, desc=f"HF source: {source['name']}"):
        title, body, url = hf_row_to_text(dict(row), source)
        searchable_text = f"{title}\n{body}"

        if not body:
            continue

        if not keyword_match(searchable_text, include_any):
            continue

        if keyword_reject(searchable_text, exclude_any):
            continue

        paragraphs = split_text_to_paragraphs(body)
        if not paragraphs:
            continue

        canonical_id = str(row.get(source.get("id_field", "id"), stable_id(source["name"], title, url)))
        records.extend(make_chunk_records(source, canonical_id, title, url, paragraphs))
        accepted += 1

        if accepted >= max_records:
            break

    return records


def iter_web_urls(source: Dict) -> List[str]:
    if source["type"] == "web_urls_file":
        path = BASE_DIR / source["path"]
        if not path.exists():
            raise FileNotFoundError(f"{path} not found")
        return [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    if source["type"] == "web_url_list":
        return [url.strip() for url in source.get("urls", []) if url.strip()]

    raise ValueError(f"Unsupported web source type: {source['type']}")


def build_records_from_web_source(source: Dict) -> List[Dict]:
    urls = iter_web_urls(source)
    records = []

    for url in tqdm(urls, desc=f"Web source: {source['name']}"):
        try:
            html = fetch_html(url)
            title, paragraphs = extract_paragraphs(html)
            canonical_id = url
            records.extend(make_chunk_records(source, canonical_id, title, url, paragraphs))
            time.sleep(1)
        except Exception as exc:
            print(f"[WARN] Failed to process {url}: {exc}")

    return records


def main():
    sources = load_source_config()
    enabled_sources = [source for source in sources if source.get("enabled") and source.get("role") == "corpus"]

    if not enabled_sources:
        raise ValueError("No enabled corpus sources found in data_sources.json")

    all_records = []

    for source in enabled_sources:
        source_type = source.get("type")
        print(f"Building source: {source['name']} ({source_type})")

        if source_type in {"web_urls_file", "web_url_list"}:
            records = build_records_from_web_source(source)
        elif source_type == "hf_dataset":
            records = build_records_from_hf_source(source)
        else:
            print(f"[WARN] Skipping unsupported source type: {source_type}")
            continue

        print(f"Collected {len(records)} chunks from {source['name']}")
        all_records.extend(records)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for record in all_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Saved {len(all_records)} chunks to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
