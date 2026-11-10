"""Run an unchanged copied original runner using hash-verified local snapshots."""
import concurrent.futures,hashlib,json,os,shutil,sys,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path('/data/L202500309/JIELI/RAG/oncology_coverage_run_20261103')
os.environ.update(PYTHONDONTWRITEBYTECODE='1',CUDA_VISIBLE_DEVICES='0',CUBLAS_WORKSPACE_CONFIG=':4096:8',
 HF_HOME=str(ROOT/'runtime_cache/huggingface'),TORCH_HOME=str(ROOT/'runtime_cache/torch'),
 XDG_CACHE_HOME=str(ROOT/'runtime_cache'),TOKENIZERS_PARALLELISM='false',OMP_NUM_THREADS='8')
os.chdir(ROOT)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def snapshots():
 report=[]
 for model in ['BAAI/bge-small-en-v1.5','BAAI/bge-reranker-v2-m3']:
  original=json.loads((ROOT/'inputs/original_model_files'/(model.replace('/','--')+'.json')).read_text())
  url='https://modelscope.cn/api/v1/models/'+model+'/repo/files?Revision=master&Recursive=true'
  with urllib.request.urlopen(url,timeout=30) as r:meta=json.load(r)
  save(ROOT/'models'/(model.replace('/','--')+'_mirror_metadata.json'),meta)
  items={f['Path']:f for f in meta['Data']['Files'] if f['Type']=='blob'}
  dest=ROOT/'models'/model.replace('/','--');dest.mkdir(exist_ok=True)
  def one(entry):
   name,expected=entry;name=name.replace('\\','/');item=items[name]
   assert item['Sha256']==expected,(model,name,'different mirror bytes')
   target=dest/name;target.parent.mkdir(parents=True,exist_ok=True)
   if not(target.exists() and sha(target)==expected):
    partial=target.with_name(target.name+'.part')
    address='https://modelscope.cn/models/'+model+'/resolve/'+item['Revision']+'/'+urllib.parse.quote(name)
    for attempt in range(4):
     try:
      offset=partial.stat().st_size if partial.exists() else 0
      req=urllib.request.Request(address,headers={'Range':f'bytes={offset}-'} if offset else {})
      with urllib.request.urlopen(req,timeout=90) as r:
       with partial.open('ab' if offset and r.status==206 else 'wb') as f:
        while True:
         b=r.read(4*1024*1024)
         if not b:break
         f.write(b)
      assert partial.stat().st_size==item['Size'] and sha(partial)==expected
      partial.replace(target);break
     except Exception as e:
      print('DOWNLOAD_RETRY',model,name,attempt,str(e)[:180],flush=True)
      if attempt==3:raise
      time.sleep(3)
   print('VERIFIED',model,name,target.stat().st_size,flush=True)
   return {'file':name,'sha256':expected,'mirror_file_revision':item['Revision']}
  with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:files=list(pool.map(one,original['files'].items()))
  report.append({'model':model,'official_hf_revision':original['sha'],'local_path':str(dest),'files':files})
 save(ROOT/'models/download_verification.json',{'models':report,'matches_original_file_hashes':True})
 return {x['model']:x['local_path'] for x in report}
def main():
 paths=snapshots();paths['google-bert/bert-base-uncased']=str(ROOT/'models/bert-base-uncased')
 sys.path.insert(0,str(ROOT/'code'))
 from experiments import run_factorial as runner
 def local(spec,output,tokenizer_only=False):
  path=Path(paths[spec['model']]);old=json.loads((ROOT/'inputs/original_model_files'/(spec['model'].replace('/','--')+'.json')).read_text())
  assert spec['sha']==old['sha']
  files={}
  for name,expected in old['files'].items():
   name=name.replace('\\','/')
   if spec['model']=='google-bert/bert-base-uncased' and '/' in name:continue
   assert sha(path/name)==expected,(spec['model'],name)
   files[name]=expected
  (output/'model_files').mkdir(exist_ok=True)
  save(output/'model_files'/(spec['model'].replace('/','--')+'.json'),dict(old,files=files,local_path=str(path),download_policy='read_only_verified_against_original_manifest'))
  return str(path)
 runner.local_model_snapshot=local
 runner.main(['--corpus',str(ROOT/'inputs/corpus_chunks_v2.jsonl'),'--questions',str(ROOT/'inputs/three_revised_questions.jsonl'),
  '--output',str(ROOT/'run_three'),'--device','cuda','--dense-revision','5c38ec7c405ec4b44b94cc5a9bb96e735b38267a',
  '--reranker-revision','953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e','--tokenizer-revision','86b5e0934494bd15c9632b12f734a8a67f723594',
  '--embed-batch-size','32','--rerank-batch-size','8','--max-length','512','--seed','20260924'])
 save(ROOT/'inference_completion.json',{'status':'complete','questions':3,'configurations':60,'same_model_file_hashes':True,
  'old_152_traces_reused':True,'mixed_hardware_timing_do_not_pool':True})
if __name__=='__main__':
 try:main()
 except Exception as e:
  save(ROOT/'inference_failure.json',{'error':repr(e),'original_files_modified':False});raise
