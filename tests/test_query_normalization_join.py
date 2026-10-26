import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pandas as pd
import pytest

from legacy import generate_normalized_questions
from legacy.generate_normalized_questions import rewrite_question
from legacy.summarize_supplement_results import prepare_results
from validation.audit_metrics import load_normalizer


def frames():
    question = "What is the treatment for NSCLC?"
    labels = pd.DataFrame([{"qid": "q1", "question": question, "gold_url": "https://example.org/gold"}])
    run = pd.DataFrame([{"qid": "q1", "question": rewrite_question(question)[0],
                         "ranking_urls": "https://example.org/gold", "final_urls": "https://example.org/gold"}])
    return run, labels


def test_recognized_rewrite_keeps_gold_annotation():
    run, labels = frames()
    result = prepare_results(run, labels)
    assert result.iloc[0]["ndcg_at_10"] == 1
    assert result.iloc[0]["final_gold_hit"] == 1


def test_unknown_question_id_is_an_error():
    run, labels = frames()
    run.loc[0, "qid"] = "unknown"
    with pytest.raises(ValueError, match="without reference"):
        prepare_results(run, labels)


def test_reused_id_for_unrelated_text_is_an_error():
    run, labels = frames()
    run.loc[0, "question"] = "An unrelated clinical question"
    with pytest.raises(ValueError, match="unrecognized"):
        prepare_results(run, labels)


def test_duplicate_reference_ids_are_an_error():
    run, labels = frames()
    with pytest.raises(ValueError, match="unique"):
        prepare_results(run, pd.concat([labels, labels]))


def test_audit_loads_relocated_normalizer_without_writing_beside_source(tmp_path):
    source = tmp_path / "legacy/generate_normalized_questions.py"
    source.parent.mkdir()
    shutil.copyfile(generate_normalized_questions.__file__, source)
    normalize = load_normalizer(tmp_path)
    assert normalize("What is the treatment for NSCLC?") == rewrite_question("What is the treatment for NSCLC?")
    assert not (tmp_path / "result").exists()
    assert not (tmp_path / "legacy/result").exists()


def test_normalization_dispatcher_writes_requested_outputs(tmp_path):
    input_path, output_path, map_path = [tmp_path / name for name in ("input.jsonl", "normalized.jsonl", "map.csv")]
    row = {"qid": "q1", "question": "Treatment for NSCLC?", "gold_url": "https://example.org/gold"}
    input_path.write_text(json.dumps(row) + "\n")
    env = {**os.environ, "INPUT_FILE": str(input_path), "OUTPUT_FILE": str(output_path), "MAP_FILE": str(map_path)}
    root = Path(generate_normalized_questions.__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, "-m", "rerankhuts", "legacy-normalize"],
                            cwd=root, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    normalized = json.loads(output_path.read_text())
    assert normalized["question"] == rewrite_question(row["question"])[0]
    assert normalized["raw_question"] == row["question"]
    assert normalized["gold_url"] == row["gold_url"]
    assert pd.read_csv(map_path).iloc[0]["qid"] == "q1"
