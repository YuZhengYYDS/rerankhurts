"""Support semantics, output protection and inclusion of the v25 supplement."""
import importlib.util
from pathlib import Path
import pytest
from rerankhuts.cli import commands_for
from scripts.package_release import is_result, is_code

ROOT=Path(__file__).resolve().parents[1]


def load(name, path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


onc=load('oncology_rescore','experiments/supplements/oncology_coverage_v1/rescore.py')
stage=load('stage_reanalysis','experiments/supplements/stage_reanalysis_v1/analyze.py')


def reference(row,start,end):
    return {'alternative_occurrences':[{'corpus_row':row,'start_char':start,'end_char':end}]}


def test_conjunctive_and_alternative_support_and_complete_spans():
    fact={'support_sets':[
        {'required_references':[reference(1,2,10),reference(2,0,15)]},
        {'required_references':[reference(3,5,20)]}]}
    assert not onc.present(fact,{1:10})
    assert onc.present(fact,{1:10,2:15})
    assert onc.present(fact,{3:20})
    assert not onc.present(fact,{3:19})
    assert not onc.present(fact,{4:20})


@pytest.mark.parametrize('module',[onc,stage])
def test_analysis_cannot_write_to_frozen_source_directory(tmp_path,module):
    method=getattr(module,'rescore',None) or module.analyze
    with pytest.raises(ValueError,match='build'):
        method(tmp_path,tmp_path/'experiments/results')


@pytest.mark.parametrize('module',[onc,stage])
def test_analysis_refuses_existing_output(tmp_path,module):
    output=tmp_path/'build/reanalysis/existing';output.mkdir(parents=True)
    method=getattr(module,'rescore',None) or module.analyze
    with pytest.raises(FileExistsError):method(tmp_path,output)


@pytest.mark.parametrize('name',['stage-reanalysis','packing-reanalysis','oncology-coverage'])
def test_offline_cli_dispatches_to_supplement(name):
    plan=commands_for(name,['--output','build/reanalysis/check'])
    assert len(plan)==1 and plan[0][0].startswith('experiments/supplements/')
    assert plan[0][-2:]==['--output','build/reanalysis/check']


@pytest.mark.parametrize('path',[
    'experiments/supplements/oncology_coverage_v1/annotations/truth.jsonl',
    'experiments/supplements/oncology_coverage_v1/run_three/traces/one.json.gz',
    'experiments/supplements/stage_reanalysis_v1/results/paired_transition_summary.csv',
    'experiments/supplements/answers_2048_120_v1/raw/responses/one.json'])
def test_results_archive_includes_supplement_inputs_and_traces(path):
    assert is_result(path)


def test_code_archive_keeps_supplement_analysis_but_omits_input_data():
    assert is_code('experiments/supplements/oncology_coverage_v1/rescore.py')
    assert not is_code('experiments/supplements/oncology_coverage_v1/annotations/truth.jsonl')
