"""Verify recovered raw answers, the frozen sample and saved endpoint summaries."""
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
if __package__ in (None, ''):
    sys.path.insert(0,str(ROOT))
from scripts.check_strengthening_files import recorded_source


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def verify():
    raw=HERE/'raw'
    manifest=json.loads((raw/'manifest.json').read_text(encoding='utf-8'))
    status=json.loads((raw/'status.json').read_text(encoding='utf-8'))
    assert digest(manifest['identity'])==manifest['identity_hash']==status['identity_hash']
    assert status['status']=='complete' and status['observed_answers']==status['expected_answers']==240
    baseline=json.loads((ROOT/'experiments/strengthening/results/strengthening_v1/answers/manifest.json').read_text(encoding='utf-8'))
    assert set(manifest['identity']['questions'])==set(baseline['identity']['questions'])
    assert len(manifest['identity']['questions'])==120
    paths=status['response_sha256'];assert len(paths)==240
    assert {p.name for p in (raw/'responses').glob('*.json')}=={Path(p).name for p in paths}
    endpoints=('complete_correct','complete_grounded_correct','field_accuracy','grounded_field_accuracy')
    grouped=defaultdict(list);seen=set()
    rows={}
    with (HERE/'results/per_answer.csv').open(encoding='utf-8-sig',newline='') as stream:
        for row in csv.DictReader(stream):
            key=(row['qid'],row['condition']);assert key not in rows;rows[key]=row
    for name,expected in paths.items():
        p=(raw/name).resolve();assert p.is_relative_to(raw.resolve())
        payload=p.read_bytes();assert hashlib.sha256(payload).hexdigest()==expected
        r=json.loads(payload);assert r['identity_hash']==manifest['identity_hash']
        key=(r['qid'],r['condition']);assert key not in seen;seen.add(key)
        assert r['qid'] in manifest['identity']['questions']
        for data,hash_key in [('messages','messages_sha256'),('prompt_token_ids','prompt_tokens_sha256'),('generated_token_ids','generated_tokens_sha256')]:
            assert digest(r[data])==r[hash_key]
        for endpoint in endpoints:
            assert abs(float(rows[key][endpoint])-float(r['evaluation'][endpoint]))<1e-12
        grouped[r['condition']].append(r)
    assert seen==set(rows) and len(seen)==240
    summaries=list(csv.DictReader((HERE/'results/summary.csv').open(encoding='utf-8-sig',newline='')))
    for row in summaries:
        rr=grouped[row['condition']];assert len(rr)==120 and len({r['group_id'] for r in rr})==60
        for endpoint in endpoints:
            assert abs(sum(r['evaluation'][endpoint] for r in rr)/120-float(row[endpoint+'_world_mean']))<1e-12
    for name,h in status['generation_code_sha256'].items():
        p=recorded_source(ROOT/'experiments/strengthening',name,h)
        if p.exists(): assert hashlib.sha256(p.read_bytes()).hexdigest()==h
    return dict(status='PASS',raw_response_hashes_verified=240,questions=120,worlds=60,
                saved_endpoint_means_reconciled=True,models_rerun=False)


if __name__=='__main__': print(json.dumps(verify(),indent=2))
