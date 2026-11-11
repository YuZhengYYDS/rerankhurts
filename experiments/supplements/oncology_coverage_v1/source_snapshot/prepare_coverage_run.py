import gzip,hashlib,json,shutil
from pathlib import Path
BASE=Path('/data/L202500309/JIELI/RAG')
ROOT=BASE/'oncology_coverage_run_20261103'
PROJECT=BASE/'github files/rerankhurts-main/rerankhurts-main'
ANN=BASE/'oncology_question_revision_20261103'
assert ROOT.is_dir() and not (ROOT/'protocol.json').exists()
for n in ['inputs','inputs/reused_traces','inputs/old_changed_query_traces','annotations','results','models','logs','run_three']:
 (ROOT/n).mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sources={}
def cp(src,dst):
 shutil.copyfile(src,dst);assert sha(src)==sha(dst);sources[str(src)]=sha(src)
cp(ANN/'questions_revised.jsonl',ROOT/'inputs/questions_revised.jsonl')
cp(ANN/'annotations/truth.jsonl',ROOT/'annotations/truth.jsonl')
cp(ANN/'annotations/claims.jsonl',ROOT/'annotations/claims.jsonl')
cp(ANN/'annotations/rubric_freeze.json',ROOT/'annotations/rubric_freeze.json')
cp(BASE/'oncology_full_annotation_20261102/backup/corpus_chunks_v2.jsonl',ROOT/'inputs/corpus_chunks_v2.jsonl')
cp(BASE/'oncology_fact_validation_20261102/results/delivered_original_intervals.csv',ROOT/'inputs/old_delivered_intervals.csv')
cp(PROJECT/'experiments/runs/e3_m3/manifest.json',ROOT/'inputs/original_run_manifest.json')
cp(ANN/'inputs/original_questions.jsonl',ROOT/'inputs/original_questions.jsonl')
qs=[json.loads(s) for s in (ROOT/'inputs/questions_revised.jsonl').open()]
changed=[q for q in qs if q['qid'] in ['q124','q141','q297']]
(ROOT/'inputs/three_revised_questions.jsonl').write_text(''.join(json.dumps(q,ensure_ascii=False)+'\n' for q in changed),encoding='utf-8')
(ROOT/'code/experiments').mkdir()
for name in ['__init__.py','protocol.py','run_factorial.py']:
 cp(PROJECT/'experiments'/name,ROOT/'code/experiments'/name)
(ROOT/'inputs/original_model_files').mkdir()
for p in (PROJECT/'experiments/runs/e3_m3/model_files').glob('*.json'):cp(p,ROOT/'inputs/original_model_files'/p.name)
ids=[]
for p in (PROJECT/'experiments/runs/e3_m3/traces').glob('*.json.gz'):
 with gzip.open(p,'rt') as f:t=json.load(f)
 q=next(q for q in qs if q['qid']==t['qid']);ids.append(t['qid'])
 folder='old_changed_query_traces' if t['qid'] in ['q124','q141','q297'] else 'reused_traces'
 if folder=='reused_traces':assert t['question']==q['question']
 cp(p,ROOT/'inputs'/folder/p.name)
assert len(ids)==len(set(ids))==155
# Find a matching existing BERT tokenizer by content, not directory name.
mf=json.loads((ROOT/'inputs/original_model_files/google-bert--bert-base-uncased.json').read_text())
tok=ROOT/'models/bert-base-uncased';tok.mkdir()
for name,digest in mf['files'].items():
 if '\\' in name or '/' in name:continue
 candidates=list((PROJECT/'.cache/models/google-bert--bert-base-uncased').glob('*/'+name))+[Path('/data/share/bert-base-uncased')/name,Path('/data/share/bert-base-uncased-pytorch')/name]
 match=next((p for p in candidates if p.exists() and sha(p)==digest),None)
 assert match is not None, name
 cp(match,tok/name)
protected=json.loads((BASE/'oncology_full_annotation_20261102/inputs/previous_protocol.json').read_text())['original_source_files']
for p,h in sources.items():protected[p]=h
save(ROOT/'protected_files.json',protected)
protocol={'status':'frozen_before_new_query_inference_and_full_cohort_scoring','questions':155,'reused_question_count':152,
 'new_query_ids':['q124','q141','q297'],'configurations_per_question':20,'expected_records':3100,
 'annotation_snapshot_sha256':sha(ROOT/'annotations/truth.jsonl'),'corpus_sha256':sha(ROOT/'inputs/corpus_chunks_v2.jsonl'),
 'questions_sha256':sha(ROOT/'inputs/questions_revised.jsonl'),'original_files_must_remain_unchanged':True,
 'main_comparisons':['p64_off_m3 vs p64_post_m3','p64_pre_m3 vs p64_post_m3'],
 'budgets':[512,2048],'no_answer_generation':True,'no_RAGChecker_or_RAGAS_experiment':True,
 'coverage_definition':'OR over annotated support sets; AND over required references; a reference is present only when a complete annotated original-character span is delivered.',
 'limitation':'Annotated-support coverage only, not exhaustive semantic absence, current clinical correctness, or human-adjudicated utility. Prior pilot outcomes known; exploratory.',
 'mixed_hardware_timing':'Old traces were generated on RTX5060 Windows; new three on RTX5090 Linux. Do not pool latencies as same-environment measurements.',
 'independent_external_information_needs':False,'protected_files':len(protected)}
save(ROOT/'protocol.json',protocol)
save(ROOT/'preparation_validation.json',{'original_files_changed':[p for p,h in protected.items() if sha(Path(p))!=h],
 'reused_traces':len(list((ROOT/'inputs/reused_traces').glob('*'))),'changed_original_traces_archived':3})
print(json.dumps(protocol,indent=2))
