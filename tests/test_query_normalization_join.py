import pandas as pd
import pytest

from generate_normalized_questions import rewrite_question
from summarize_supplement_results import prepare_results


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
