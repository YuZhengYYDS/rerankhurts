"""Fix plot footer layout before delivery; do not change any numeric results."""
import csv,hashlib,json,os,zipfile
from pathlib import Path
ROOT=Path('/data/L202500309/JIELI/RAG/oncology_coverage_run_20261103')
os.environ['MPLCONFIGDIR']=str(ROOT/'runtime_cache/matplotlib')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((ROOT/'artifact_manifest.json').read_text())
protected={str(ROOT/r['path']):r['sha256'] for r in old['files'] if r['path']!='results/oncology_coverage.png'}
with (ROOT/'results/configuration_summary.csv').open(encoding='utf-8-sig') as f:summary=list(csv.DictReader(f))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
fig,axes=plt.subplots(1,2,figsize=(10.5,4.8),sharey=True)
for ax,b in zip(axes,[512,2048]):
 rr=[next(r for r in summary if r['config_id']==f'p64_{cap}_m3_b{b}') for cap in ['off','pre','post']]
 x=np.arange(3)
 for i,(key,label,color) in enumerate([('page_retention','Page retained','#4878a8'),('annotated_fact_fraction_macro','Annotated fact fraction','#e49444'),('annotated_full_support','Complete annotated support','#5f9e6e')]):
  bars=ax.bar(x+(i-1)*.24,[float(r[key])*100 for r in rr],width=.23,label=label,color=color)
  ax.bar_label(bars,fmt='%.1f',fontsize=7,padding=2)
 ax.set_xticks(x,['No cap','Pre-cap','Post-cap']);ax.set_title(f'{b}-token budget');ax.set_ylim(0,110)
 ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
axes[0].set_ylabel('Percent (%)')
legend=fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',bbox_to_anchor=(.5,.075),ncol=3,fontsize=8)
fig.suptitle('Oncology: 155 questions (3 revised), pool 64 and M3',fontsize=12)
footer=fig.text(.5,.025,'152 reused traces + 3 rerun queries.',ha='center',fontsize=8)
fig.tight_layout(rect=[0,.15,1,.94]);fig.canvas.draw()
assert not legend.get_window_extent().overlaps(footer.get_window_extent())
fig.savefig(ROOT/'results/oncology_coverage.png',dpi=190);plt.close(fig)
assert all(sha(Path(p))==h for p,h in protected.items()),'Numerical results and previous files must remain unchanged'
assert all(sha(Path(p))==h for p,h in json.loads((ROOT/'protected_files.json').read_text()).items())
include=[ROOT/r['path'] for r in old['files']]+[Path(__file__)]
include=sorted(set(include))
manifest={'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in include],
 'weights_and_embeddings_omitted':True,'plot_footer_layout_corrected_before_delivery':True,
 'all_numeric_result_files_unchanged':True}
(ROOT/'artifact_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
archive=ROOT/'coverage_results_bundle.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for p in include+[ROOT/'artifact_manifest.json']:z.write(p,str(p.relative_to(ROOT)))
print(json.dumps({'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'verified_files':len(include),'numeric_results_changed':False},indent=2))
