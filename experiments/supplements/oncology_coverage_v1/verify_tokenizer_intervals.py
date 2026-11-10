"""Reconstruct saved Oncology character intervals from the pinned fast tokenizer.

Only tokenizer.json is loaded; no neural model or network call is used. Pass a
local JSON file or snapshot directory. Outputs require a new build/ destination.
"""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
TOKENIZER_SHA256='ce64fce797c24f68df90b40a3f74f579b336a493db14bd583fd520ea0d8c9a98'


def check_prefix(chunk,ids,offsets):
    n=chunk['delivered_tokens']
    if n<=0 or n>len(ids) or chunk['token_ids']!=ids[:n]:
        raise ValueError('Delivered tokens are not the original token prefix')
    if chunk['chunk_tokens']!=len(ids) or bool(chunk['partial'])!=(n<len(ids)):
        raise ValueError('Chunk length/partial flag differs from tokenizer')
    return int(offsets[n-1][1])


def verify(tokenizer_path,output,root=ROOT):
    from tokenizers import Tokenizer
    root,output=Path(root).resolve(),Path(output).resolve()
    if not output.is_relative_to(root/'build'):raise ValueError('Output must be under build/')
    if output.exists():raise FileExistsError(output)
    tokenizer_path=Path(tokenizer_path)
    if tokenizer_path.is_dir():tokenizer_path=tokenizer_path/'tokenizer.json'
    if hashlib.sha256(tokenizer_path.read_bytes()).hexdigest()!=TOKENIZER_SHA256:
        raise ValueError('Tokenizer bytes do not match the frozen original snapshot')
    tokenizer=Tokenizer.from_file(str(tokenizer_path));tokenizer.no_truncation();tokenizer.no_padding()
    corpus_path=root/'data/oncology/corpus/corpus_chunks_v2.jsonl'
    freeze=json.loads((HERE/'annotations/rubric_freeze.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(corpus_path.read_bytes()).hexdigest()==freeze['corpus_sha256']
    corpus=[json.loads(line) for line in corpus_path.read_text(encoding='utf-8').splitlines()]
    encoded=tokenizer.encode_batch([r['text'] for r in corpus],add_special_tokens=False)
    with (HERE/'inputs/delivered_original_intervals.csv').open(encoding='utf-8-sig',newline='') as stream:
        rows=list(csv.DictReader(stream))
    intervals={(r['qid'],r['config_id']):json.loads(r['original_intervals']) for r in rows}
    assert len(intervals)==len(rows)==3100
    trace_index=json.loads((HERE/'inputs/trace_index.json').read_text(encoding='utf-8'))['records']
    assert len(trace_index)==155
    sep=tokenizer.token_to_id('[SEP]');assert sep is not None
    checked=0;chunks=0;seen=set()
    for source in trace_index:
        path=root/source['repository_path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==source['sha256']
        with gzip.open(path,'rt',encoding='utf-8') as stream:trace=json.load(stream)
        assert trace['qid']==source['qid']
        for record in trace['configurations']:
            key=(trace['qid'],record['configuration']['config_id']);assert key not in seen;seen.add(key)
            ctx=record['final_context'];parts=intervals[key];assert len(parts)==len(ctx['chunks'])
            stream=[]
            for chunk,part in zip(ctx['chunks'],parts):
                row=chunk['corpus_row'];entry=encoded[row]
                end=check_prefix(chunk,entry.ids,entry.offsets)
                assert part['corpus_row']==row and part['start_char']==0 and part['end_char']==end
                assert part['delivered_tokens']==chunk['delivered_tokens']
                if stream:stream.append(sep)
                stream.extend(chunk['token_ids']);chunks+=1
            assert stream==ctx['token_ids'] and len(stream)==ctx['used_tokens']<=record['configuration']['budget']
            checked+=1
    assert seen==set(intervals)
    report=dict(status='PASS',tokenizer_sha256=TOKENIZER_SHA256,corpus_rows=len(corpus),
        question_configuration_records=checked,delivered_chunks=chunks,
        character_intervals_reconstructed=True,token_streams_reconstructed=True,
        model_inference=False,network_access=False)
    output.mkdir(parents=True)
    (output/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tokenizer',type=Path,required=True)
    ap.add_argument('--project',type=Path,default=ROOT)
    ap.add_argument('--output',type=Path,default=ROOT/'build/verification/oncology_tokenizer')
    args=ap.parse_args();print(json.dumps(verify(args.tokenizer,args.output,args.project),indent=2))


if __name__=='__main__':main()
