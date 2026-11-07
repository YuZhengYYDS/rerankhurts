"""Check supplied model-based review records against the frozen 60-world sample."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
DATA='experiments/strengthening/data/strengthening_v1'
CITATION=re.compile(r'chunk `([^`]+)`, claim `([^`]+)`, Character span `\[(\d+), (\d+)\)`; Source `([^`]+)`\.')


def quoted_text_equal(display,source):
    return ' '.join(display.split())==' '.join(source.split())


def verify(root=ROOT):
    root=Path(root)
    data=root/DATA
    packet=[json.loads(s) for s in (data/'audit/human_audit_packet.jsonl').read_text(encoding='utf-8').splitlines()]
    packet={x['group_id']:x for x in packet}
    reviews=[];wanted=set()
    for label in ['A','B']:
        path=data/'audit/reviews'/f'WORLD_REVIEW_RESULTS_{label}.md'
        text=path.read_text(encoding='utf-8-sig')
        if 'Result source: model-based review.' not in text:
            raise ValueError('Missing original review-source label')
        sections=re.split(r'^## World \d+: ',text,flags=re.M)[1:]
        seen=set();citations=[]
        for section in sections:
            world=section.splitlines()[0].strip()
            if world not in packet or world in seen:raise ValueError('Unknown/duplicate world')
            seen.add(world)
            qline=re.search(r'^Question IDs: (.+)$',section,re.M)
            cline=re.search(r'^Collection IDs: (.+)$',section,re.M)
            assert qline and cline
            assert set(re.findall(r'`([^`]+)`',qline.group(1)))==set(packet[world]['qids'])
            assert set(re.findall(r'`([^`]+)`',cline.group(1)))==set(packet[world]['collection_ids'])
            fact_line=re.search(r'^Required facts: (.+)$',section,re.M)
            assert fact_line
            stated=dict(tuple(x.strip() for x in field.split('=',1))
                        for field in fact_line.group(1).rstrip('.').split(';'))
            truth=packet[world]['truth']
            required={f['key']:str(f['value']) for f in truth['facts']
                      if f['fact_id'] in truth['required_fact_ids']}
            assert stated==required
            headings=re.findall(r'^\*\*D([1-4]) [^\n]+: pass\*\*',section,re.M)
            assert headings==['1','2','3','4']
            for match in CITATION.finditer(section):
                quote=section[match.end():].lstrip().splitlines()[0]
                assert quote.startswith('> ')
                citation=(*match.groups(),quote[2:])
                citations.append(citation);wanted.add(citation[0])
        assert seen==set(packet) and len(seen)==60
        reviews.append((label,path,citations))
    corpus={};claims={}
    for filename,key,out in [('corpus.jsonl','chunk_id',corpus),('claims.jsonl','claim_id',claims)]:
        with (data/filename).open(encoding='utf-8') as stream:
            for line in stream:
                row=json.loads(line)
                if row['chunk_id'] in wanted:out[row[key]]=row
    reports=[]
    for label,path,citations in reviews:
        normalized=0
        for cid,claimid,left,right,url,quote in citations:
            a,b=int(left),int(right);chunk=corpus[cid];claim=claims[claimid]
            assert (claim['chunk_id'],claim['start_char'],claim['end_char'])==(cid,a,b)
            assert chunk['url']==url
            original=chunk['text'][a:b]
            assert quoted_text_equal(quote,original)
            normalized+=quote!=original
        reports.append(dict(review=label,worlds=60,dimension_judgments=240,
            evidence_citations=len(citations),whitespace_display_normalizations=normalized,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    return dict(status='PASS',record_source='model-based review',worlds=60,
                paired_questions=120,required_facts=183,reviews=reports,
                checks='World/sample membership, identical required facts, all four dimension entries, source claim bindings, exact offsets/URLs and whitespace-normalized displayed quotes')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=ROOT)
    ap.add_argument('--output',type=Path)
    args=ap.parse_args();result=verify(args.root)
    if args.output:
        path=args.output.resolve();base=(args.root/'build').resolve()
        if not path.is_relative_to(base):raise ValueError('Output must be under build/')
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
