"""Recreate current Fig. 11 from final Oncology and frozen pilot results."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ONCOLOGY='experiments/supplements/oncology_coverage_v1/results/per_question_coverage.csv'
PILOT='experiments/simulation/results/pilot_v2/'


def load_data(root=ROOT):
    root=Path(root)
    with (root/ONCOLOGY).open(encoding='utf-8-sig',newline='') as stream:rows=list(csv.DictReader(stream))
    assert len(rows)==3100 and len({r['qid'] for r in rows})==155
    assert len({(r['qid'],r['config_id']) for r in rows})==3100
    assert set(Counter(r['config_id'] for r in rows).values())=={155}
    counts=Counter()
    for row in rows:
        raw,final=int(row['G_raw']),int(row['G_final'])
        assert not final or raw
        counts['Raw-pool miss' if not raw else 'Packing loss' if not final else 'Retained']+=1
    assert [counts[k] for k in ['Raw-pool miss','Packing loss','Retained']]==[20,167,2913]
    selection=json.loads((root/(PILOT+'selection.json')).read_text(encoding='utf-8'))['primary']
    assert selection['policy']=='open' and selection['budget']==512
    with (root/(PILOT+'summary.csv')).open(encoding='utf-8-sig',newline='') as stream:summary=list(csv.DictReader(stream))
    chosen=[]
    for criterion in ['U_sim','G']:
        cid=selection['dev_selected_by_'+criterion]
        rr=[r for r in summary if r['scope']=='overall' and r['scenario']=='all' and r['split']=='test' and r['policy']=='open' and r['config_id']==cid]
        assert len(rr)==1
        chosen.append({'criterion':criterion,'config_id':cid,'coverage':float(rr[0]['U_sim']),
                       'test_worlds':int(rr[0]['n_information_needs'])})
    assert [r['coverage'] for r in chosen]==[.55,.675]
    assert all(r['test_worlds']==40 for r in chosen)
    tied=selection['dev_all_ties']['U_sim'];assert len(tied)==10
    dev=[r for r in summary if r['scope']=='overall' and r['scenario']=='all' and r['split']=='dev' and r['policy']=='open' and r['config_id'] in tied]
    assert len(dev)==10 and {float(r['U_sim']) for r in dev}=={.6}
    return counts,chosen


def plot(root,output):
    root,output=Path(root).resolve(),Path(output).resolve()
    if not output.is_relative_to(root/'build'):raise ValueError('Output must be under build/')
    if output.exists():raise FileExistsError(output)
    counts,chosen=load_data(root)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42})
    fig,(ax,bx)=plt.subplots(1,2,figsize=(8.0,2.35),gridspec_kw={'width_ratios':[1.3,1]})
    fig.subplots_adjust(left=.16,right=.985,bottom=.30,top=.78,wspace=.50)
    teal,orange,gray='#14b3d9','#ff681d','#a4afbb'
    labels=['Raw-pool miss','Packing loss','Retained'];values=[counts[k] for k in labels]
    ax.barh([2,1,0],values,color=[gray,orange,teal],height=.48)
    ax.set_yticks([2,1,0],labels);ax.set_xlim(0,3350);ax.set_xticks([0,1000,2000,3000])
    ax.set_xlabel('Question-configuration records',labelpad=9)
    for y,value in zip([2,1,0],values):ax.text(value+50,y,f'{value:,}',va='center',fontsize=8)
    coverage=[r['coverage']*100 for r in chosen]
    bx.bar([0,1],coverage,width=.60,color=[teal,orange])
    bx.axhline(60,color=gray,linestyle=(0,(5,3)),linewidth=1)
    bx.text(-.55,65,'Development tie: 60%',fontsize=7.7)
    bx.set_ylim(0,100);bx.set_xlim(-.60,1.60);bx.set_yticks([0,50,100])
    bx.set_ylabel('Full fact coverage (%)',labelpad=7)
    bx.set_xticks([0,1],['Selected by\nfull fact coverage','Selected by\npage retention'])
    bx.tick_params(axis='x',pad=15)
    for x,r in enumerate(chosen):bx.text(x,r['coverage']*50,f"{r['coverage']*100:.1f}%\n{round(r['coverage']*40)}/40",ha='center',va='center',fontsize=8)
    for axis,title,letter in [(ax,'Oncology page outcomes','a'),(bx,'Pilot test coverage','b')]:
        axis.spines[['top','right']].set_visible(False)
        axis.grid(axis='y' if axis is bx else 'x',color='#edf0f3',linewidth=.8)
        axis.set_axisbelow(True);axis.tick_params(length=2)
        axis.text(0,1.20,letter,transform=axis.transAxes,fontweight='bold',fontsize=9)
        axis.text(.08,1.20,title,transform=axis.transAxes,fontweight='bold',fontsize=9)
    output.mkdir(parents=True)
    fig.savefig(output/'f11_complementary_checks-v3.pdf',bbox_inches='tight',pad_inches=.06)
    fig.savefig(output/'f11_complementary_checks-v3.png',dpi=200,bbox_inches='tight',pad_inches=.06)
    plt.close(fig)
    sources={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in [ONCOLOGY,PILOT+'summary.csv',PILOT+'selection.json']}
    report=dict(figure=11,version='v25',oncology_counts=dict(counts),pilot=chosen,
                source_sha256=sources,development_reference_percent=60,
                uncertainty='No marginal error bars; dashed line is the development tie, not a confidence interval',
                paper_assets_overwritten=False,model_inference=False)
    (output/'source_data.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project',type=Path,default=ROOT)
    ap.add_argument('--output',type=Path,default=ROOT/'build/reanalysis/v25_fig11')
    args=ap.parse_args();print(json.dumps(plot(args.project,args.output),indent=2))


if __name__=='__main__':main()
