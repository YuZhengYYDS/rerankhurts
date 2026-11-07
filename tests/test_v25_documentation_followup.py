"""Review sample coverage, token-boundary guards and current figure data."""
import importlib.util
from pathlib import Path
import re
import pytest
from scripts.check_world_review_records import quoted_text_equal
from scripts.plot_v25_complementary import load_data

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('oncology_tokenizer_check',
    ROOT/'experiments/supplements/oncology_coverage_v1/verify_tokenizer_intervals.py')
tok=importlib.util.module_from_spec(spec);spec.loader.exec_module(tok)


def test_review_display_allows_whitespace_only_changes():
    assert quoted_text_equal('Q: current revision? A: R3.','Q: current revision?\nA: R3.')
    assert not quoted_text_equal('Q: current revision? A: R2.','Q: current revision?\nA: R3.')


def test_original_token_prefix_maps_to_complete_last_token_endpoint():
    chunk={'delivered_tokens':2,'token_ids':[4,5],'chunk_tokens':3,'partial':True}
    assert tok.check_prefix(chunk,[4,5,6],[(0,2),(3,6),(7,10)])==6


@pytest.mark.parametrize('override',[{'token_ids':[4,6]},{'partial':False},{'chunk_tokens':4},{'delivered_tokens':0}])
def test_token_verifier_rejects_inconsistent_prefix_or_boundary_metadata(override):
    chunk={'delivered_tokens':2,'token_ids':[4,5],'chunk_tokens':3,'partial':True,**override}
    with pytest.raises(ValueError):tok.check_prefix(chunk,[4,5,6],[(0,2),(3,6),(7,10)])


def test_current_figure_uses_final_snapshot_and_frozen_pilot():
    counts,chosen=load_data()
    assert [counts[k] for k in ['Raw-pool miss','Packing loss','Retained']]==[20,167,2913]
    assert [r['coverage'] for r in chosen]==[.55,.675]


@pytest.mark.parametrize('name',['guide.md','docs/CODE_GUIDE.md','docs/RESULTS_GUIDE.md','docs/STRENGTHENING_GUIDE.md'])
def test_maintained_usage_guides_are_english(name):
    assert not re.search(r'[\u4e00-\u9fff]',(ROOT/name).read_text(encoding='utf-8'))


def test_detailed_reviews_cover_all_60_worlds():
    base=ROOT/'experiments/strengthening/data/strengthening_v1/audit/reviews'
    for label in ['A','B']:
        text=(base/f'WORLD_REVIEW_RESULTS_{label}.md').read_text(encoding='utf-8-sig')
        assert len(re.findall(r'^## World \d+: ',text,re.M))==60
