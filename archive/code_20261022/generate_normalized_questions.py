import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


BASE_DIR = Path(__file__).resolve().parent
RESULT_DIR = BASE_DIR / "result"
RESULT_DIR.mkdir(parents=True, exist_ok=True)


def resolve_path(raw_value: str, default: Path) -> Path:
    if not raw_value:
        return default
    candidate = Path(raw_value)
    return candidate if candidate.is_absolute() else BASE_DIR / candidate


INPUT_FILE = resolve_path(
    os.getenv("INPUT_FILE", ""),
    RESULT_DIR / "paper_questions_validated.jsonl",
)
OUTPUT_FILE = resolve_path(
    os.getenv("OUTPUT_FILE", ""),
    RESULT_DIR / "paper_questions_validated_normalized.jsonl",
)
MAP_FILE = resolve_path(
    os.getenv("MAP_FILE", ""),
    RESULT_DIR / "paper_questions_validated_normalization_map.csv",
)


REWRITE_RULES: List[Tuple[re.Pattern, str, str]] = [
    (re.compile(r"\bnsclc\b", flags=re.IGNORECASE), "non-small cell lung cancer (NSCLC)", "expand_nsclc"),
    (re.compile(r"\bsclc\b", flags=re.IGNORECASE), "small cell lung cancer (SCLC)", "expand_sclc"),
    (re.compile(r"\baml\b", flags=re.IGNORECASE), "acute myeloid leukemia (AML)", "expand_aml"),
    (re.compile(r"\bcll\b", flags=re.IGNORECASE), "chronic lymphocytic leukemia (CLL)", "expand_cll"),
    (re.compile(r"\begfr\b", flags=re.IGNORECASE), "epidermal growth factor receptor (EGFR)", "expand_egfr"),
    (re.compile(r"\balk\b", flags=re.IGNORECASE), "ALK rearrangement", "expand_alk"),
    (re.compile(r"\bher2\b", flags=re.IGNORECASE), "HER2 (ERBB2)", "expand_her2"),
    (re.compile(r"\bpd-l1\b", flags=re.IGNORECASE), "programmed death-ligand 1 (PD-L1)", "expand_pdl1"),
    (re.compile(r"\ber\+\b", flags=re.IGNORECASE), "estrogen receptor-positive (ER+)", "expand_er_positive"),
    (re.compile(r"\bhr\+\b", flags=re.IGNORECASE), "hormone receptor-positive (HR+)", "expand_hr_positive"),
    (re.compile(r"\bher2-negative\b", flags=re.IGNORECASE), "HER2-negative", "normalize_her2_negative"),
    (re.compile(r"\btriple negative\b", flags=re.IGNORECASE), "triple-negative", "normalize_triple_negative"),
    (re.compile(r"\bpd 1\b", flags=re.IGNORECASE), "PD-1", "normalize_pd1"),
    (re.compile(r"\bpd l1\b", flags=re.IGNORECASE), "PD-L1", "normalize_pdl1_spacing"),
]


def load_jsonl(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def normalize_spacing(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,?.:;])", r"\1", text)
    return text


def rewrite_question(question: str) -> Tuple[str, List[str]]:
    updated = question
    applied: List[str] = []

    for pattern, replacement, label in REWRITE_RULES:
        next_text, count = pattern.subn(replacement, updated)
        if count > 0:
            applied.append(label)
            updated = next_text

    updated = normalize_spacing(updated)
    return updated, applied


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"{INPUT_FILE} not found")

    rows = load_jsonl(INPUT_FILE)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    MAP_FILE.parent.mkdir(parents=True, exist_ok=True)

    map_rows: List[Dict] = []
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_handle:
        for row in rows:
            question = str(row.get("question", ""))
            normalized_question, applied_rules = rewrite_question(question)

            payload = dict(row)
            payload["raw_question"] = question
            payload["question"] = normalized_question
            payload["normalization_applied"] = bool(applied_rules)
            payload["normalization_rules"] = applied_rules
            out_handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

            map_rows.append(
                {
                    "qid": row.get("qid", ""),
                    "topic": row.get("topic", ""),
                    "normalization_applied": bool(applied_rules),
                    "normalization_rule_count": len(applied_rules),
                    "normalization_rules": "|".join(applied_rules),
                    "raw_question": question,
                    "normalized_question": normalized_question,
                }
            )

    import pandas as pd

    pd.DataFrame(map_rows).to_csv(MAP_FILE, index=False, encoding="utf-8-sig")
    print(f"Saved normalized questions: {OUTPUT_FILE}")
    print(f"Saved normalization map: {MAP_FILE}")


if __name__ == "__main__":
    main()
