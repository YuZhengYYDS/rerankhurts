"""Reproduce within-question stage transitions from frozen evaluated records."""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if not output.is_relative_to(root / 'build'):
        raise ValueError('Output must be a new directory under repository build/')
    if output.exists():
        raise FileExistsError(output)
    source = root/'experiments/strengthening/results/strengthening_v1/per_record.csv'
    selected = defaultdict(dict)
    source_rows = 0
    with source.open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream):
            source_rows += 1
            if (row['split'] == 'test' and row['retriever'] == 'dense'
                    and row['pool'] == '64' and row['reranker'] == 'm3'
                    and row['cap'] == '2' and row['cap_stage'] in ('pre', 'post')
                    and row['dense_view'] == row['score_view'] == 'prefix512'
                    and row['packing'] == 'prefix' and row['refill'] == 'False'
                    and row['policy_stage'] == 'none' and row['budget'] in ('512', '2048')):
                key = (row['budget'], row['cap_stage'])
                if row['qid'] in selected[key]:
                    raise ValueError('Duplicate matched task')
                selected[key][row['qid']] = row
    assert source_rows == 89280
    pairs, counts = [], Counter()
    for budget in ('512', '2048'):
        pre, post = selected[budget, 'pre'], selected[budget, 'post']
        assert len(pre) == len(post) == 600 and pre.keys() == post.keys()
        worlds=Counter(r['group_id'] for r in pre.values())
        assert len(worlds)==300 and set(worlds.values())=={2}
        for qid, a in sorted(pre.items()):
            b = post[qid]
            assert a['group_id'] == b['group_id']
            values = tuple(int(float(r[k])) for r,k in ((a,'post_policy_U_sim'),(b,'post_policy_U_sim'),(a,'U_sim'),(b,'U_sim')))
            counts[(budget, *values)] += 1
            pairs.append(dict(budget=budget,qid=qid,group_id=a['group_id'],
                pre_upstream_full=values[0],post_upstream_full=values[1],
                pre_final_full=values[2],post_final_full=values[3]))
    table = []
    states = [(1,1,'both'),(0,1,'post_only'),(1,0,'pre_only'),(0,0,'neither')]
    for p,z,label in states:
        row = {'packing_input_support':label,
               'tasks':sum(counts[('512',p,z,x,y)] for x,y,_ in states)}
        assert row['tasks'] == sum(counts[('2048',p,z,x,y)] for x,y,_ in states)
        for budget in ('512','2048'):
            for x,y,name in states:
                row['final_'+budget+'_'+name] = counts[(budget,p,z,x,y)]
        table.append(row)
    with (HERE/'results/paired_transition_summary.csv').open(encoding='utf-8-sig',newline='') as stream:
        saved = list(csv.DictReader(stream))
    assert [{k:str(v) for k,v in r.items()} for r in table] == saved
    # Verify the two published execution examples against exact corpus text and
    # unchanged traces; all four settings are checked for each example.
    corpus_path = root/'experiments/strengthening/data/strengthening_v1/corpus.jsonl'
    examples = json.loads((HERE/'results/case_evidence.json').read_text(encoding='utf-8'))
    wanted = {loc['chunk_id'] for ex in examples for c in ex['configurations']
              for group in c['full_text_support_locations'].values() for loc in group}
    corpus = {}
    with corpus_path.open(encoding='utf-8') as stream:
        for line in stream:
            c = json.loads(line)
            if c['chunk_id'] in wanted: corpus[c['chunk_id']] = c['text']
    checked = 0
    for ex in examples:
        name = hashlib.sha256(json.dumps(ex['qid'],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()[:24]+'.json.gz'
        with gzip.open(root/'experiments/runs/strengthening_v1/traces'/name,'rt',encoding='utf-8') as stream:
            trace = json.load(stream)
        records = {r['configuration']['config_id']:r for r in trace['configurations']}
        assert trace['qid'] == ex['qid']
        for c in ex['configurations']:
            original = records[c['configuration']['config_id']]
            for stage, locations in c['full_text_support_locations'].items():
                stage_ids = [r['chunk_id'] for r in original['stages'][stage]]
                for loc in locations:
                    assert stage_ids[loc['rank']-1] == loc['chunk_id']
                    assert corpus[loc['chunk_id']][loc['start']:loc['end']] == loc['quote']
            assert original['final_context']['used_tokens'] == c['used_tokens']
            delivered = original['final_context']['chunks']
            assert len(delivered) == len(c['delivered_intervals'])
            for a,b in zip(delivered,c['delivered_intervals']):
                assert a['chunk_id'] == b['chunk_id'] and a['text'] == b['text']
                assert a['char_start'] == b['start'] and a['char_end'] == b['end']
            checked += 1
    output.mkdir(parents=True)
    for name, rows in [('paired_transition_summary.csv',table),('paired_records.csv',pairs)]:
        with (output/name).open('w',encoding='utf-8',newline='') as stream:
            w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    report = dict(status='PASS',source_sha256=digest(source),source_rows=source_rows,
                  paired_records=len(pairs),tasks_per_budget=600,worlds_per_budget=300,
                  example_configurations_verified=checked,models_rerun=False)
    (output/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path,default=ROOT/'build/reanalysis/stage_v1')
    args=parser.parse_args()
    print(json.dumps(analyze(args.project,args.output),indent=2))


if __name__ == '__main__': main()
