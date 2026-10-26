import json
import re
from collections import Counter, defaultdict
from pathlib import Path


from rerankhuts.paths import oncology_path


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = oncology_path("questions.jsonl", root=BASE_DIR)
OUTPUT_FILE = oncology_path("questions_annotated.jsonl", root=BASE_DIR)

URLS = {
    "NSCLC": "https://www.cancer.gov/types/lung/hp/non-small-cell-lung-treatment-pdq",
    "SCLC": "https://www.cancer.gov/types/lung/hp/small-cell-lung-treatment-pdq",
    "Breast": "https://www.cancer.gov/types/breast/hp/breast-treatment-pdq",
    "Colon": "https://www.cancer.gov/types/colorectal/hp/colon-treatment-pdq",
    "AML": "https://www.cancer.gov/types/leukemia/hp/adult-aml-treatment-pdq",
    "CLL": "https://www.cancer.gov/types/leukemia/hp/cll-treatment-pdq",
    "General": "https://www.cancer.gov/publications/pdq/information-summaries/genetics",
}

TOPIC_PATTERNS = [
    ("NSCLC", [
        r"non-small cell lung cancer",
        r"\bnsclc\b",
        r"\begfr\b",
        r"\balk\b",
        r"pd-l1",
    ]),
    ("SCLC", [
        r"small cell lung cancer",
        r"\bsclc\b",
    ]),
    ("Breast", [
        r"breast cancer",
        r"\bher2\b",
        r"triple-negative",
        r"hormone receptor-positive",
        r"endocrine therapy",
    ]),
    ("Colon", [
        r"colon cancer",
        r"colorectal",
    ]),
    ("AML", [
        r"acute myeloid leukemia",
        r"\baml\b",
    ]),
    ("CLL", [
        r"chronic lymphocytic leukemia",
        r"\bcll\b",
    ]),
]


def normalize_question(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def infer_topic(question: str) -> str:
    text = str(question).strip().lower()
    matched_topics = [
        topic
        for topic, patterns in TOPIC_PATTERNS
        if any(re.search(pattern, text) for pattern in patterns)
    ]

    if len(matched_topics) == 1:
        return matched_topics[0]
    if not matched_topics:
        return "General"
    return matched_topics[0]


def main():
    annotated = []
    topic_counter = Counter()
    duplicates = defaultdict(list)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)

            topic = infer_topic(item.get("question", ""))
            item["topic"] = topic
            item["gold_url"] = URLS[topic]
            item["gold_urls"] = [URLS[topic]]

            topic_counter[topic] += 1
            duplicates[normalize_question(item.get("question", ""))].append(item.get("qid", ""))
            annotated.append(item)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for item in annotated:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    duplicate_groups = {
        question: qids
        for question, qids in duplicates.items()
        if len(qids) > 1
    }

    print(f"Saved annotated questions to {OUTPUT_FILE}")
    print("Topic counts:", dict(topic_counter))
    print(f"Duplicate question groups: {len(duplicate_groups)}")
    for qids in duplicate_groups.values():
        print(" -", ", ".join(qids))


if __name__ == "__main__":
    main()
