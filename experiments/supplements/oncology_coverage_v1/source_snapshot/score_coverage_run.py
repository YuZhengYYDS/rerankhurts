"""Recompute annotated source-span coverage; preserve original traces and labels."""
import collections,csv,gzip,hashlib,html,json,os,sys,zipfile
from pathlib import Path
ROOT=Path('/data/L202500309/JIELI/RAG/oncology_coverage_run_20261103')
os.environ.update(PYTHONDONTWRITEBYTECODE='1',TOKENIZERS_PARALLELISM='false',MPLCONFIGDIR=str(ROOT/'runtime_cache/matplotlib'),OMP_NUM_THREADS='8')
sys.path.insert(0,str(ROOT/'code'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def readjl(p):return [json.loads(s) for s in p.open(encoding='utf-8')]
def save(p,x):
 with p.open('x',encoding='utf-8') as f:f.write(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def csvout(p,rows):
 with p.open('x',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def loadtrace(p):
 with gzip.open(p,'rt') as f:return json.load(f)
def software_checks():
 def ref(row,a,b):return {'alternative_occurrences':[{'corpus_row':row,'start_char':a,'end_char':b}]}
 fact={'support_sets':[{'required_references':[ref(1,2,10),ref(2,3,20)]},{'required_references':[ref(3,0,15)]}]}
 checks={'AND_requires_all_parts':not present(fact,{1:10}),
 'OR_accepts_alternative_set':present(fact,{3:15}),'AND_support_across_rows':present(fact,{1:10,2:20}),
 'cut_reference_rejected':not present(fact,{3:14}),'same_offset_wrong_row_rejected':not present(fact,{4:20}),
 'unknown_token_overlap_rejected':not present(fact,{3:15},{3:[(3,5)]})}
 assert all(checks.values());return checks
def present(f,intervals,unknown=None):
 def match(ref):
  return any(o['corpus_row'] in intervals and o['end_char']<=intervals[o['corpus_row']] and
   (unknown is None or not any(a<o['end_char'] and b>o['start_char'] for a,b in unknown.get(o['corpus_row'],[])))
   for o in ref['alternative_occurrences'])
 return any(all(match(ref) for ref in s['required_references']) for s in f['support_sets'])
def flags(tr,ints,unknown=None):return [present(f,ints,unknown) for f in tr['facts']]
def main():
 import numpy as np
 from transformers import AutoTokenizer
 from experiments.protocol import gold_urls,url_metrics,identify_corpus
 assert (ROOT/'inference_completion.json').exists(),'Wait for successful three-question inference'
 assert not (ROOT/'results/per_question_coverage.csv').exists(),'Preserve existing scores; choose a new result version'
 protocol=json.loads((ROOT/'protocol.json').read_text())
 truths={q['qid']:q for q in readjl(ROOT/'annotations/truth.jsonl')}
 questions={q['qid']:q for q in readjl(ROOT/'inputs/questions_revised.jsonl')}
 corpus,identity=identify_corpus(readjl(ROOT/'inputs/corpus_chunks_v2.jsonl'))
 tokenizer=AutoTokenizer.from_pretrained(str(ROOT/'models/bert-base-uncased'),local_files_only=True,use_fast=True)
 encoded=tokenizer([c['text'] for c in corpus],add_special_tokens=False,truncation=False,return_offsets_mapping=True,verbose=False)
 ids,offsets=encoded['input_ids'],encoded['offset_mapping']
 unk={i:[(a,b) for tok,(a,b) in zip(tokens,offsets[i]) if tok==tokenizer.unk_token_id] for i,tokens in enumerate(ids)}
 with (ROOT/'inputs/old_delivered_intervals.csv').open(encoding='utf-8-sig',newline='') as f:
  oldmaps={(r['qid'],r['config_id']):r for r in csv.DictReader(f)}
 traces={};sources={};trace_manifest=[]
 oldmanifest=json.loads((ROOT/'inputs/original_run_manifest.json').read_text())
 newmanifest=json.loads((ROOT/'run_three/manifest.json').read_text())
 assert oldmanifest['identity']['corpus_sha256']==newmanifest['identity']['corpus_sha256']==sha(ROOT/'inputs/corpus_chunks_v2.jsonl')
 assert oldmanifest['identity']['models']==newmanifest['identity']['models']
 for folder,origin,m in [('inputs/reused_traces','reused_original_unchanged_query',oldmanifest),('run_three/traces','newly_run_revised_query',newmanifest)]:
  for p in sorted((ROOT/folder).glob('*.json.gz')):
   tr=loadtrace(p);qid=tr['qid'];assert qid not in traces
   assert tr['question']==questions[qid]['question']==truths[qid]['question']
   assert tr['identity_hash']==m['identity_hash'];assert len(tr['configurations'])==20
   traces[qid]=tr;sources[qid]=origin
   trace_manifest.append({'qid':qid,'path':str(p.relative_to(ROOT)),'sha256':sha(p),'origin':origin,'run_identity_hash':tr['identity_hash']})
 assert set(traces)==set(questions)==set(truths) and len(traces)==155
 save(ROOT/'results/trace_provenance.json',{'records':trace_manifest,'old_unchanged_questions':152,'new_revised_questions':3,'timings_not_aggregated_across_hardware':True})
 checks=software_checks();per=[];facts=[];stages=[];bindings=[];chunks_checked=0;exact_quotes=0
 for t in truths.values():
  assert t['facts'] and not t['unresolved_component_ids']
  for f in t['facts']:
   for ss in f['support_sets']:
    for ref in ss['required_references']:
     for o in ref['alternative_occurrences']:
      assert corpus[o['corpus_row']]['text'][o['start_char']:o['end_char']]==o['exact_quote'];exact_quotes+=1
 print('Annotation source-span checks passed:',exact_quotes,flush=True)
 for qid,tr in sorted(traces.items(),key=lambda kv:int(kv[0][1:])):
  truth=truths[qid];nf=len(truth['facts'])
  for rec in tr['configurations']:
   c=rec['configuration'];ctx=rec['final_context'];ints={};parts=[];stream=[];unknowns=0
   for chunk in ctx['chunks']:
    row=chunk['corpus_row'];n=chunk['delivered_tokens'];given=chunk['token_ids']
    assert given==ids[row][:n] and len(ids[row])==chunk['chunk_tokens']
    assert n>0 and chunk['partial']==(n<len(ids[row]))
    if stream:stream.append(tokenizer.sep_token_id)
    stream.extend(given);end=int(offsets[row][n-1][1]);ints[row]=max(end,ints.get(row,0))
    unknowns+=given.count(tokenizer.unk_token_id);chunks_checked+=1
    parts.append({'corpus_row':row,'start_char':0,'end_char':end,'delivered_tokens':n,'partial':chunk['partial'],'url':corpus[row]['url']})
   assert stream==ctx['token_ids'] and len(stream)==ctx['used_tokens']<=c['budget']
   if sources[qid]=='reused_original_unchanged_query':
    prev=oldmaps[(qid,c['config_id'])]
    assert json.loads(prev['original_intervals'])==parts,(qid,c['config_id'],'old interval differs')
   final=flags(truth,ints);strict=flags(truth,ints,unk)
   bystage={}
   for stage in ['raw','pre_cap','rerank','post_cap']:
    membership={x['corpus_row']:len(corpus[x['corpus_row']]['text']) for x in rec['stages'][stage]}
    bystage[stage]=flags(truth,membership)
   assert bystage['pre_cap']==bystage['rerank'],'Pure rerank cannot delete membership'
   assert all(not z or a for a,z in zip(bystage['raw'],bystage['pre_cap']))
   assert all(not z or a for a,z in zip(bystage['rerank'],bystage['post_cap']))
   assert all(not z or a for a,z in zip(bystage['post_cap'],final))
   gold=gold_urls(questions[qid]);assert rec['metrics']['G_final']==url_metrics(ctx['chunks'],gold)['G']
   first='retained'
   for name,ff in [('candidate_not_covered',bystage['raw']),('pre_cap',bystage['pre_cap']),('rerank_membership',bystage['rerank']),('post_cap',bystage['post_cap']),('packing',final)]:
    if not all(ff):first=name;break
   row={'qid':qid,'question':tr['question'],'topic':tr['topic'],'source_group':truth['source_url'],
    'construction_source':truth['construction_source'],'trace_origin':sources[qid],**c,
    'required_fact_count':nf,'supported_annotated_facts':sum(final),'annotated_fact_fraction':sum(final)/nf,
    'annotated_full_support':int(all(final)),'full_support_without_unknown_overlap':int(all(strict)),
    'G_final':rec['metrics']['G_final'],'G_raw':rec['metrics']['G_raw'],'candidate_full_support':int(all(bystage['raw'])),
    'post_cap_full_support':int(all(bystage['post_cap'])),'first_annotated_support_loss':first,
    'context_tokens':ctx['used_tokens'],'unknown_context_tokens':unknowns,
    'supported_fact_ids':json.dumps([f['fact_id'] for f,z in zip(truth['facts'],final) if z]),
    'human_review_completed':False}
   per.append(row)
   bindings.append({'qid':qid,'config_id':c['config_id'],'trace_origin':sources[qid],'token_prefix_verified':True,
    'original_intervals':json.dumps(parts),'unknown_tokens':unknowns})
   for name,ff in list(bystage.items())+[('packing',final)]:
    stages.append({'qid':qid,'config_id':c['config_id'],'budget':c['budget'],'stage':name,
     'supported_facts':sum(ff),'required_facts':nf,'annotated_fact_fraction':sum(ff)/nf,
     'annotated_full_support':int(all(ff)),'trace_origin':sources[qid]})
   for i,(f,z) in enumerate(zip(truth['facts'],final)):
    facts.append({'qid':qid,'config_id':c['config_id'],'fact_id':f['fact_id'],'fact_value':str(f['value']),
     'candidate_supported':int(bystage['raw'][i]),'pre_cap_supported':int(bystage['pre_cap'][i]),
     'post_cap_supported':int(bystage['post_cap'][i]),'delivered_supported':int(z),
     'delivered_supported_without_unknown_overlap':int(strict[i]),'human_review_completed':False})
 assert len(per)==3100 and len(facts)==377*20
 csvout(ROOT/'results/per_question_coverage.csv',per);csvout(ROOT/'results/per_fact_coverage.csv',facts)
 csvout(ROOT/'results/per_stage_coverage.csv',stages);csvout(ROOT/'results/delivered_original_intervals.csv',bindings)
 def config_summary(rows):
  out=[]
  for cid in sorted({r['config_id'] for r in rows}):
   rr=[r for r in rows if r['config_id']==cid];n=len(rr)
   mean=lambda k:sum(r[k] for r in rr)/n
   out.append({'config_id':cid,'questions':n,'source_groups':len({r['source_group'] for r in rr}),
    **{k:rr[0][k] for k in ['pool','cap','reranker','budget']},'page_retention':mean('G_final'),
    'annotated_fact_fraction_macro':mean('annotated_fact_fraction'),
    'annotated_full_support':mean('annotated_full_support'),
    'complete_questions':sum(r['annotated_full_support'] for r in rr),
    'candidate_full_support':mean('candidate_full_support'),
    'complete_without_unknown_overlap':mean('full_support_without_unknown_overlap'),
    'reused_questions':sum(r['trace_origin']=='reused_original_unchanged_query' for r in rr),
    'newly_run_questions':sum(r['trace_origin']=='newly_run_revised_query' for r in rr),'human_review_completed':False})
  return out
 summary=config_summary(per);csvout(ROOT/'results/configuration_summary.csv',summary)
 unchanged=[r for r in per if r['trace_origin']=='reused_original_unchanged_query']
 csvout(ROOT/'results/configuration_summary_unchanged_152.csv',config_summary(unchanged))
 lookup={(r['qid'],r['config_id']):r for r in per};contrasts=[];cases=[]
 for cohort,qids in [('revised_all_155',list(traces)),('unchanged_only_152',[q for q in traces if sources[q]=='reused_original_unchanged_query'])]:
  for b in [512,2048]:
   for label,cap0,cap1 in [('no_cap_vs_post','off','post'),('pre_vs_post','pre','post')]:
    cc=collections.Counter();fraction=0;gdelta=0;groups={}
    for qid in qids:
     a,z=[lookup[(qid,f'p64_{cap}_m3_b{b}')] for cap in [cap0,cap1]]
     x,y=a['annotated_full_support'],z['annotated_full_support'];cc['n']+=1
     cc['gain']+=x==0 and y==1;cc['loss']+=x==1 and y==0;cc['both']+=x==1 and y==1;cc['neither']+=x==0 and y==0
     same=a['G_final']==z['G_final'];cc['same_G']+=same
     cc['same_G_full_diff']+=same and x!=y;cc['same_G_facts_diff']+=same and a['supported_fact_ids']!=z['supported_fact_ids']
     fraction+=z['annotated_fact_fraction']-a['annotated_fact_fraction'];gdelta+=z['G_final']-a['G_final']
     groups.setdefault(a['source_group'],[]).append(y-x)
     if cohort=='revised_all_155' and same and a['supported_fact_ids']!=z['supported_fact_ids']:
      cases.append({'qid':qid,'budget':b,'contrast':label,'trace_origin':sources[qid],
       'G_a':a['G_final'],'G_b':z['G_final'],'complete_a':x,'complete_b':y,'facts_a':a['supported_fact_ids'],'facts_b':z['supported_fact_ids'],
       'interpretation':'Divergence in annotated supports, not proof that all unannotated paraphrases are absent.'})
    sums=np.array([sum(v) for v in groups.values()]);sizes=np.array([len(v) for v in groups.values()]);ng=len(sums)
    rng=np.random.default_rng(20260924);ind=rng.integers(0,ng,size=(5000,ng));boot=sums[ind].sum(1)/sizes[ind].sum(1)*100
    lo,hi=np.quantile(boot,[.025,.975])
    contrasts.append({'cohort':cohort,'budget':b,'contrast':label,'questions':cc['n'],'source_groups':ng,
     'complete_gains':cc['gain'],'complete_losses':cc['loss'],'both_complete':cc['both'],'neither_complete':cc['neither'],
     'complete_difference_pp':100*(cc['gain']-cc['loss'])/cc['n'],
     'exploratory_group_bootstrap_ci_low_pp':float(lo),'exploratory_group_bootstrap_ci_high_pp':float(hi),
     'macro_fact_fraction_difference_pp':100*fraction/cc['n'],'page_retention_difference_pp':100*gdelta/cc['n'],
     'same_G_questions':cc['same_G'],'same_G_different_complete_support':cc['same_G_full_diff'],
     'same_G_different_supported_fact_set':cc['same_G_facts_diff'],'human_review_completed':False})
 csvout(ROOT/'results/paired_contrasts.csv',contrasts)
 if cases:csvout(ROOT/'results/same_page_different_fact_cases.csv',cases)
 save(ROOT/'results/divergence_cases.json',cases)
 stage_summary=[]
 for cid in sorted({r['config_id'] for r in per}):
  for name in ['raw','pre_cap','rerank','post_cap','packing']:
   rr=[r for r in stages if r['config_id']==cid and r['stage']==name]
   stage_summary.append({'config_id':cid,'stage':name,'questions':len(rr),
    'complete_questions':sum(r['annotated_full_support'] for r in rr),
    'complete_fraction':sum(r['annotated_full_support'] for r in rr)/len(rr),
    'macro_fact_fraction':sum(r['annotated_fact_fraction'] for r in rr)/len(rr)})
 csvout(ROOT/'results/stage_summary.csv',stage_summary)
 # Readable evidence review for the principal paired divergence cases.
 review=ROOT/'review';review.mkdir()
 links=[];header='<!doctype html><meta charset="utf-8"><style>body{font:16px Arial;max-width:1100px;margin:24px auto;line-height:1.6}pre{white-space:pre-wrap;background:#eee;padding:12px}td,th{border:1px solid #bbb;padding:8px}table{border-collapse:collapse}</style>'
 for qid in sorted({r['qid'] for r in cases},key=lambda q:int(q[1:])):
  tr=truths[qid];s=header+'<h1>'+qid+'</h1><p>'+html.escape(tr['question'])+'</p><p>Assistant source-span annotations; domain review pending. Unannotated semantic alternatives may exist.</p>'
  for f in tr['facts']:
   s+='<h3>'+html.escape(f['fact_id'])+'</h3><p>'+html.escape(str(f['value']))+'</p>'
   scores=[r for r in facts if r['qid']==qid and r['fact_id']==f['fact_id'] and r['config_id'].startswith('p64_') and '_m3_' in r['config_id']]
   s+='<table><tr><th>Configuration</th><th>Candidate</th><th>After cap</th><th>Delivered</th></tr>'+''.join('<tr><td>'+r['config_id']+'</td><td>'+str(r['candidate_supported'])+'</td><td>'+str(r['post_cap_supported'])+'</td><td>'+str(r['delivered_supported'])+'</td></tr>' for r in scores)+'</table>'
   for ss in f['support_sets']:
    s+='<details><summary>Alternative support set (all parts required)</summary>'
    for ref in ss['required_references']:
     o=ref['alternative_occurrences'][0];s+='<pre>'+html.escape(o['exact_quote'])+'</pre><p>'+html.escape(o['url'])+'</p>'
    s+='</details>'
  (review/(qid+'.html')).write_text(s,encoding='utf-8');links.append('<li><a href="'+qid+'.html">'+qid+'</a>: '+html.escape(tr['question'])+'</li>')
 (review/'index.html').write_text(header+'<h1>Annotated-support divergence cases</h1><ul>'+''.join(links)+'</ul>',encoding='utf-8')
 # Descriptive figure; uncertainty is reported for paired effects in the CSV.
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,2,figsize=(10,4.2),sharey=True)
 for ax,b in zip(axes,[512,2048]):
  rr=[next(r for r in summary if r['config_id']==f'p64_{cap}_m3_b{b}') for cap in ['off','pre','post']]
  x=np.arange(3)
  for i,(key,label,color) in enumerate([('page_retention','Page retained','#4878a8'),('annotated_fact_fraction_macro','Annotated fact fraction','#e49444'),('annotated_full_support','Complete annotated support','#5f9e6e')]):
   bars=ax.bar(x+(i-1)*.24,[r[key]*100 for r in rr],width=.23,label=label,color=color)
   ax.bar_label(bars,fmt='%.1f',fontsize=7,padding=2)
  ax.set_xticks(x,['No cap','Pre-cap','Post-cap']);ax.set_title(f'{b}-token budget');ax.set_ylim(0,110);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
 axes[0].set_ylabel('Questions / mean annotated facts (%)')
 fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=3,fontsize=8)
 fig.suptitle('Oncology: 155 revised questions, fixed pool 64 and M3',fontsize=12)
 fig.text(.5,.02,'Exploratory assistant annotations; domain adjudication pending. 152 reused traces + 3 rerun queries.',ha='center',fontsize=8)
 fig.tight_layout(rect=[0,.1,1,.94]);fig.savefig(ROOT/'results/oncology_coverage.png',dpi=190);plt.close(fig)
 protection=json.loads((ROOT/'protected_files.json').read_text())
 changed=[p for p,h in protection.items() if sha(Path(p))!=h];assert not changed
 status={'status':'complete_exploratory_annotated_support_scoring','questions':155,'facts':377,'configurations_per_question':20,
  'records':len(per),'per_fact_records':len(facts),'reused_queries':152,'rerun_queries':3,'rerun_configurations':60,
  'exact_source_spans_verified':exact_quotes,'token_streams_verified':3100,'selected_chunks_verified':chunks_checked,
  'old_interval_mappings_reproduced':3040,'unknown_overlap_changes_full_support':sum(r['annotated_full_support']!=r['full_support_without_unknown_overlap'] for r in per),
  'protected_files_checked':len(protection),'original_files_changed':changed,
  'no_answer_generation':True,'no_RAGChecker_RAGAS_experiments':True,'mixed_hardware_latency_not_aggregated':True,
  'human_review_completed':False,'semantic_absence_established':False,'independent_external_validation_established':False}
 save(ROOT/'status.json',status);save(ROOT/'results/validation.json',dict(status,software_checks=checks))
 lines=['Oncology 新标注覆盖计算（2026-11-03）','',
 '本次复用152道未修改问题的原始轨迹；使用与原实验文件哈希相同的 BGE-small、BGE-reranker-v2-m3 和 BERT 分词器，重新运行 q124、q141、q297 的20组配置，共60条新记录。',
 '合计155题×20配置=3100条；377条候选必需事实。原始项目和前期标注文件均未修改。',
 '主要是基于标注的原文支持区间覆盖：逐题事实比例、全部标注事实是否齐全、页面命中、逐阶段支持。不是回答准确率、医学建议正确率或经真人裁决的U。',
 '未穷尽全语料中的所有语义改写和替代支持，故未命中已标注区间不等于事实语义必然不存在。当前参考范围由问题限定，所有候选标注仍需领域复核。',
 '三题新运行的模型字节与原实验一致，平台/GPU不同。未将新旧延迟混合成统一延迟结果；本次不运行回答生成、不运行RAGChecker/RAGAS。','',
 '主表（pool64，M3）：预算 | cap | 页面保留 | 平均标注事实覆盖 | 完整标注支持问题数']
 for b in [512,2048]:
  for cap in ['off','pre','post']:
   r=next(r for r in summary if r['config_id']==f'p64_{cap}_m3_b{b}')
   lines.append(f"{b} | {cap} | {r['page_retention']:.2%} | {r['annotated_fact_fraction_macro']:.2%} | {r['complete_questions']}/155 ({r['annotated_full_support']:.2%})")
 lines+=['','配对变化：正值表示post优于比较项。']
 for r in contrasts:
  if r['cohort']!='revised_all_155':continue
  lines.append(f"{r['budget']} {r['contrast']}: 完整支持净变化 {r['complete_difference_pp']:+.2f}pp，增加{r['complete_gains']}题，减少{r['complete_losses']}题；页面命中相同但完整支持不同{r['same_G_different_complete_support']}题。")
 lines+=['','文件入口：results/configuration_summary.csv（20配置总表）；results/paired_contrasts.csv（两组配对及152题敏感性分析）；results/per_question_coverage.csv（逐题）；results/per_fact_coverage.csv（逐事实）；results/per_stage_coverage.csv（逐阶段）；results/oncology_coverage.png（描述图）；review/index.html（分歧案例）。',
 '配对区间按指定来源页面整组bootstrap，5000次，seed20260924，为探索性逐项95%区间，未做多重比较确认性检验；页面分组不是事实独立性的保证。阶段结果定位丢失位置，不自动建立原因。',
 '没有基于这些结果继续改题或调标注。本版含3题问题范围修订，应如实报告，不能当作原155题完全不变的外部复现。','',json.dumps(status,ensure_ascii=False,indent=2)]
 (ROOT/'REPORT_CN.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 # Compact delivery omits 2.4GB model weights and offline embeddings.
 include=[]
 for folder in ['code','annotations','results','review','inputs','run_three/traces','run_three/model_files']:
  include.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 include += [ROOT/f for f in ['REPORT_CN.txt','status.json','protocol.json','protected_files.json','preparation_validation.json','inference_completion.json','run_three/manifest.json','run_three/status.json','run_three/per_question.csv','run_three/summary.csv','models/download_verification.json']]
 include=sorted(set(include));manifest=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in include]
 save(ROOT/'artifact_manifest.json',{'files':manifest,'weights_and_embeddings_omitted':True})
 archive=ROOT/'coverage_results_bundle.zip'
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for p in include+[ROOT/'artifact_manifest.json']:z.write(p,str(p.relative_to(ROOT)))
 print(json.dumps({'status':status,'main_contrasts':[r for r in contrasts if r['cohort']=='revised_all_155'],'archive':str(archive),'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size},ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
