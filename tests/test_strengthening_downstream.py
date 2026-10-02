from experiments.strengthening.downstream import build_messages, fixed_world_sample, score_answer
from experiments.strengthening.timing import request_schedule


FACTS = [{"fact_id": "r", "key": "route", "value": "Aster-47"}]


def claim(**changes):
    return {"key": "route", "value": "Aster-47", "status": "valid", "admissible": True,
            "source_index": 1, **changes}


def test_correct_answer_requires_a_valid_matching_citation_to_be_grounded():
    valid = '{"route":{"value":"Aster-47","source":"S1"}}'
    result = score_answer(valid, FACTS, [claim()], 1)
    assert result["complete_correct"] == result["complete_grounded_correct"] == 1
    assert score_answer(valid.replace('S1', 'S2'), FACTS, [claim()], 1)["complete_grounded_correct"] == 0


def test_stale_disallowed_and_absent_support_do_not_count_as_grounding():
    text = '{"route":{"value":"Aster-47","source":"S1"}}'
    for claims in ([], [claim(status="obsolete")], [claim(admissible=False)]):
        scored = score_answer(text, FACTS, claims, 1)
        assert scored["complete_correct"] == 1
        assert scored["complete_grounded_correct"] == 0
        assert scored["unsupported_fields"] == 1


def test_abstention_is_reported_separately_from_truth_accuracy():
    text = '{"route":{"value":"unknown","source":"none"}}'
    scored = score_answer(text, FACTS, [], 0)
    assert scored["complete_correct"] == 0
    assert scored["unsupported_abstentions"] == 1
    assert scored["unsupported_answers"] == 0


def test_complete_multifragment_citation_requires_both_source_labels():
    supporting = claim(source_index=None, source_indices=[1, 2])
    text = '{"route":{"value":"Aster-47","source":["S1","S2"]}}'
    assert score_answer(text, FACTS, [supporting], 2)["complete_grounded_correct"] == 1
    partial = '{"route":{"value":"Aster-47","source":"S1"}}'
    assert score_answer(partial, FACTS, [supporting], 2)["complete_grounded_correct"] == 0


def test_malformed_or_extra_fields_do_not_receive_complete_credit():
    for text in ('not json', '{"route":"Aster-47"}',
                 '{"route":{"value":"Aster-47","source":"S1"},"extra":7}'):
        assert score_answer(text, FACTS, [claim()], 1)["complete_correct"] == 0


def test_prompt_has_no_oracle_parameter_and_preserves_exact_evidence():
    chunks = [{"url": "https://registry.invalid/disputed-current-label", "text": "Visible fictional evidence."}]
    messages = build_messages("Current route?", ["route"], chunks)
    assert "Aster-47" not in str(messages)
    assert "Visible fictional evidence." in messages[1]["content"]
    assert "https://registry.invalid/" in messages[1]["content"]
    assert "disputed-current-label" not in str(messages)


def test_sample_is_world_grouped_and_ignores_order_and_outcomes():
    metadata = [{"group_id": f"g{s}-{i}", "qid": f"q{s}-{i}-{v}", "seed": s, "split": "test",
                 "template_family": "prose", "scenario": str(i % 2), "policy": "open", "U_sim": v}
                for s in (1, 2, 3) for i in range(6) for v in range(2)]
    sample = fixed_world_sample(metadata, 3)
    assert len(sample) == len(set(sample)) == 9
    assert sample == fixed_world_sample(list(reversed(metadata)), 3)


def test_timing_schedule_balances_every_query_config_repeat():
    schedule = request_schedule(["b", "a"], ["pre", "post"], 5, 3)
    assert len(schedule) == len(set(schedule)) == 20
    assert schedule == request_schedule(["a", "b"], ["pre", "post"], 5, 3)
    assert set(schedule) == {(q, c, r) for q in ("a", "b") for c in ("pre", "post") for r in range(5)}
