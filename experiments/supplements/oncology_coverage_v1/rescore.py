"""Offline annotated-support rescoring on saved original-character intervals.

The interval input was verified against the pinned tokenizer in the source run.
This command checks file identities, exact quotes, stage membership and delivered
token streams. It uses that saved boundary map, without downloading a tokenizer.
"""
import argparse
from collections import defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def read_jsonl(path):
    with path.open(encoding='utf-8-sig') as stream:
        return [json.loads(line) for line in stream if line.strip()]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def present(fact, intervals):
    return any(all(any(o['corpus_row'] in intervals
                       and o['end_char'] <= intervals[o['corpus_row']]
                       for o in ref['alternative_occurrences'])
                   for ref in support['required_references'])
               for support in fact['support_sets'])


def rescore(root, output):
    root,output=Path(root).resolve(),Path(output).resolve()
    if not output.is_relative_to(root/'build'):
        raise ValueError('Output must be a new directory under repository build/')
    if output.exists(): raise FileExistsError(output)
    corpus_path=root/'data/oncology/corpus/corpus_chunks_v2.jsonl'
    freeze=read_json(HERE/'annotations/rubric_freeze.json')
    for path,key in [(corpus_path,'corpus_sha256'),
                     (HERE/'inputs/questions_revised.jsonl','questions_sha256'),
                     (HERE/'annotations/truth.jsonl','truth_sha256'),
                     (HERE/'annotations/claims.jsonl','claims_sha256')]:
        assert sha(path)==freeze[key], (path,'Frozen input changed')
    corpus=read_jsonl(corpus_path)
    truths={r['qid']:r for r in read_jsonl(HERE/'annotations/truth.jsonl')}
    questions={r['qid']:r for r in read_jsonl(HERE/'inputs/questions_revised.jsonl')}
    assert len(truths)==len(questions)==155 and truths.keys()==questions.keys()
    quotes=0
    for truth in truths.values():
        assert truth['facts'] and not truth['unresolved_component_ids']
        for fact in truth['facts']:
            assert fact['support_sets']
            for support in fact['support_sets']:
                assert support['required_references']
                for ref in support['required_references']:
                    assert ref['alternative_occurrences']
                    for o in ref['alternative_occurrences']:
                        assert corpus[o['corpus_row']]['text'][o['start_char']:o['end_char']]==o['exact_quote']
                        quotes+=1
    with (HERE/'inputs/delivered_original_intervals.csv').open(encoding='utf-8-sig',newline='') as stream:
        rows=list(csv.DictReader(stream))
    bounds={(r['qid'],r['config_id']):r for r in rows}
    assert len(bounds)==len(rows)==3100
    with (HERE/'results/per_question_coverage.csv').open(encoding='utf-8-sig',newline='') as stream:
        rows=list(csv.DictReader(stream))
    saved={(r['qid'],r['config_id']):r for r in rows}
    assert len(saved)==len(rows)==3100
    seen=set();records=[];stage_records=[];fact_records=[]
    trace_index=read_json(HERE/'inputs/trace_index.json')['records']
    assert len(trace_index)==155 and len({r['qid'] for r in trace_index})==155
    for item in trace_index:
        path=(root/item['repository_path']).resolve()
        assert path.is_relative_to(root) and sha(path)==item['sha256']
        with gzip.open(path,'rt',encoding='utf-8') as stream: trace=json.load(stream)
        qid=item['qid'];truth=truths[qid]
        assert trace['qid']==qid and trace['identity_hash']==item['run_identity_hash']
        assert trace['question']==questions[qid]['question']==truth['question']
        assert len(trace['configurations'])==20
        for record in trace['configurations']:
            c=record['configuration'];ctx=record['final_context'];key=(qid,c['config_id'])
            assert key not in seen;seen.add(key)
            parts=json.loads(bounds[key]['original_intervals'])
            assert len(parts)==len(ctx['chunks'])
            intervals={};token_count=0
            for chunk,part in zip(ctx['chunks'],parts):
                row=chunk['corpus_row'];end=part['end_char']
                assert part['corpus_row']==row and part['start_char']==0
                assert part['delivered_tokens']==chunk['delivered_tokens']==len(chunk['token_ids'])
                assert part['partial']==chunk['partial'] and 0<end<=len(corpus[row]['text'])
                assert part['url']==corpus[row]['url']
                token_count+=len(chunk['token_ids'])
                intervals[row]=max(end,intervals.get(row,0))
            assert token_count+max(0,len(parts)-1)==ctx['used_tokens']<=c['budget']
            # Final stream contains the exact chunk tokens plus one separator.
            cursor=0
            for chunk in ctx['chunks']:
                n=len(chunk['token_ids'])
                assert ctx['token_ids'][cursor:cursor+n]==chunk['token_ids']
                cursor+=n+1
            ff=[present(f,intervals) for f in truth['facts']]
            stages={}
            for stage in ['raw','pre_cap','rerank','post_cap']:
                membership={x['corpus_row']:len(corpus[x['corpus_row']]['text']) for x in record['stages'][stage]}
                stages[stage]=[present(f,membership) for f in truth['facts']]
            assert stages['pre_cap']==stages['rerank']
            assert all(not y or x for x,y in zip(stages['post_cap'],ff))
            baseline=saved[key]
            assert int(all(ff))==int(baseline['annotated_full_support'])
            assert sum(ff)==int(baseline['supported_annotated_facts'])
            assert abs(sum(ff)/len(ff)-float(baseline['annotated_fact_fraction']))<1e-12
            assert int(record['metrics']['G_final'])==int(baseline['G_final'])
            output_row=dict(qid=qid,config_id=c['config_id'],required_fact_count=len(ff),
                supported_annotated_facts=sum(ff),annotated_fact_fraction=sum(ff)/len(ff),
                annotated_full_support=int(all(ff)),G_final=record['metrics']['G_final'])
            records.append(output_row)
            for stage,flags in [*stages.items(),('packing',ff)]:
                stage_records.append(dict(qid=qid,config_id=c['config_id'],stage=stage,
                    supported_facts=sum(flags),required_facts=len(flags),annotated_full_support=int(all(flags))))
            for fact,flag in zip(truth['facts'],ff):
                fact_records.append(dict(qid=qid,config_id=c['config_id'],fact_id=fact['fact_id'],delivered_supported=int(flag)))
    assert seen==set(bounds)==set(saved)
    groups=defaultdict(list)
    for row in records:groups[row['config_id']].append(row)
    summary=[]
    expected={r['config_id']:r for r in csv.DictReader((HERE/'results/configuration_summary.csv').open(encoding='utf-8-sig',newline=''))}
    for cid,rr in sorted(groups.items()):
        n=len(rr);assert n==155
        row=dict(config_id=cid,questions=n,complete_questions=sum(r['annotated_full_support'] for r in rr),
            page_retention=sum(r['G_final'] for r in rr)/n,
            annotated_fact_fraction_macro=sum(r['annotated_fact_fraction'] for r in rr)/n,
            annotated_full_support=sum(r['annotated_full_support'] for r in rr)/n)
        for k in ('complete_questions','page_retention','annotated_fact_fraction_macro','annotated_full_support'):
            assert abs(float(row[k])-float(expected[cid][k]))<1e-12,(cid,k)
        summary.append(row)
    output.mkdir(parents=True)
    for name,rr in [('per_question_coverage.csv',records),('configuration_summary.csv',summary),
                    ('per_stage_coverage.csv',stage_records),('per_fact_coverage.csv',fact_records)]:
        with (output/name).open('w',encoding='utf-8',newline='') as stream:
            w=csv.DictWriter(stream,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
    report=dict(status='PASS',questions=155,configurations=20,records=len(records),
        facts=sum(len(t['facts']) for t in truths.values()),exact_quotes_verified=quotes,
        trace_files_verified=len(trace_index),all_saved_coverage_outcomes_reproduced=True,
        tokenizer_boundary_map='Saved original-character intervals; no tokenizer rerun',models_rerun=False)
    (output/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project',type=Path,default=ROOT)
    ap.add_argument('--output',type=Path,default=ROOT/'build/reanalysis/oncology_coverage_v1')
    args=ap.parse_args()
    print(json.dumps(rescore(args.project,args.output),indent=2))


if __name__=='__main__': main()
