#!/usr/bin/env python3
"""Recreate historical quantitative figures under build/, using frozen archived inputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import xml.etree.ElementTree as ET
from importlib.metadata import version
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
ARCHIVED_FIGURES = ROOT / 'archive/paper_20261022/figures'
OUT = ROOT / 'build/reanalysis/paper_20261022/figures'
CLEAN = OUT / 'source_data'
INPUTS = ARCHIVED_FIGURES / 'source_data/inputs'
INPUT_MANIFEST = INPUTS / 'MANIFEST.json'
VERIFIED_INPUTS = {}
STRENGTH = 'experiments/strengthening/results/strengthening_v1/'
PILOT = 'experiments/simulation/results/pilot_v2/'
TEAL, ORANGE, GREY = '#247ba0', '#d06d28', '#525252'
LIGHT = '#c6ccd0'
NOCAP = 'dense_p64_m3_off_b2048_prefix_prefix512_dprefix512_polnone'
POST = 'dense_p64_m3_post2_b2048_prefix_prefix512_dprefix512_polnone'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_manifest():
    manifest = json.loads(INPUT_MANIFEST.read_text(encoding='utf-8'))
    if manifest.get('schema_version') != 1:
        raise ValueError('Unsupported frozen figure-input manifest')
    return manifest


def input_path(relative: str) -> Path:
    """Resolve one manifest-listed input without requiring the local download cache."""
    relative_path = Path(relative)
    if relative_path.is_absolute() or '..' in relative_path.parts:
        raise ValueError('Source input paths must remain relative to the bundle')
    entry = input_manifest()['files'].get(relative)
    if entry is None:
        raise ValueError(f'Input is not declared in MANIFEST.json: {relative}')
    repository_path = ROOT / relative
    use_repository = relative.startswith('experiments/') and repository_path.is_file()
    resolved = repository_path if use_repository else INPUTS / relative
    if not resolved.is_file():
        raise FileNotFoundError(f'Missing frozen figure input: {relative}')
    actual_sha = sha(resolved)
    if resolved.stat().st_size != entry['bytes'] or actual_sha != entry['sha256']:
        raise ValueError(f'Input SHA-256/size differs from MANIFEST.json: {relative}')
    VERIFIED_INPUTS[relative] = {'path': str(resolved.relative_to(ROOT)),
                               'sha256': actual_sha, 'bytes': entry['bytes'],
                               'resolution': 'repository original' if use_repository else 'frozen release input'}
    return resolved


def csv_rows(relative: str):
    with input_path(relative).open(newline='', encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream))


def one(rows, **selector):
    matched = [row for row in rows if all(row.get(k) == str(v) for k, v in selector.items())]
    if len(matched) != 1:
        raise ValueError(f'Expected one source row for {selector}, found {len(matched)}')
    return matched[0]


def write_csv(name, rows):
    rows = list(rows)
    keys = list(dict.fromkeys(k for row in rows for k in row))
    path = CLEAN / name
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    return str(path.relative_to(ROOT))


def close(a, b, tol=1e-10):
    if not math.isclose(float(a), float(b), abs_tol=tol, rel_tol=tol):
        raise ValueError(f'Inconsistent source values: {a} != {b}')


def style():
    font_manager.findfont('Arial', fallback_to_default=False)
    plt.rcParams.update({
        'font.family': 'Arial', 'font.size': 7.2,
        'axes.labelsize': 7.2, 'axes.titlesize': 7.6,
        'xtick.labelsize': 6.8, 'ytick.labelsize': 7.0,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.linewidth': .65, 'xtick.major.width': .65,
        'ytick.major.width': .65, 'xtick.major.size': 2.6,
        'ytick.major.size': 2.6, 'text.color': GREY,
        'axes.labelcolor': GREY, 'xtick.color': GREY,
        'ytick.color': GREY, 'axes.edgecolor': GREY,
        'figure.facecolor': 'white', 'axes.facecolor': 'white',
        'savefig.facecolor': 'white', 'pdf.fonttype': 42,
        'ps.fonttype': 42, 'svg.fonttype': 'none',
        'mathtext.fontset': 'dejavusans',
    })


def panel(ax, letter, title, offset=-.12, title_y=1.12):
    ax.text(offset, title_y, letter, transform=ax.transAxes, ha='left', va='bottom',
            fontsize=8.4, fontweight='bold', color='black')
    ax.text(0, title_y, title, transform=ax.transAxes, ha='left', va='bottom', fontsize=7.6)


def base_axes(ax, horizontal=True):
    ax.set_axisbelow(True)
    ax.grid(axis='x' if horizontal else 'y', color='#e9e9e9', linewidth=.45)
    if horizontal:
        ax.spines['left'].set_visible(False)
        ax.tick_params(axis='y', length=0)


def save(fig, stem, figure_id, metadata):
    fig.canvas.draw()
    # Keep the exact final physical size; no tight bounding-box resizing.
    exported = {}
    for ext in ('pdf', 'svg', 'png'):
        path = OUT / f'{stem}.{ext}'
        fig.savefig(path, dpi=600 if ext == 'png' else None,
                    metadata={'Creator': 'matplotlib; source-driven manuscript figure'} if ext == 'pdf' else None)
        exported[ext] = {'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'bytes': path.stat().st_size}
    fig.canvas.draw()
    width, height = fig.get_size_inches()
    # Mechanical clipping check complements the visual check of the 600-dpi export.
    renderer = fig.canvas.get_renderer()
    outside = []
    figure_box = fig.bbox
    for text in fig.findobj(matplotlib.text.Text):
        if not text.get_visible() or not text.get_text():
            continue
        box = text.get_window_extent(renderer)
        if box.x0 < -1 or box.y0 < -1 or box.x1 > figure_box.x1 + 1 or box.y1 > figure_box.y1 + 1:
            outside.append(text.get_text())
    plt.close(fig)
    metadata.update({'figure': figure_id, 'width_in': float(width), 'height_in': float(height),
                     'exports': exported, 'qa': {'outside_figure_text': outside,
                     'font': font_manager.findfont('Arial', fallback_to_default=False),
                     'png_dpi': 600, 'pdf_fonttype': 42, 'svg_fonttype': 'none',
                     'visual_review': 'pending'}})
    if outside:
        raise ValueError(f'{figure_id} text outside canvas: {outside}')
    return metadata


def sources(*paths):
    for relative in paths:
        input_path(relative)
    return [dict(source_key=relative, **VERIFIED_INPUTS[relative]) for relative in paths]


def plot_f10():
    source = STRENGTH + 'timing/summary.csv'
    contrast_source = STRENGTH + 'timing_world_contrasts.csv'
    all_rows = csv_rows(source)
    conditions = [('dense_prefix', 'Dense'), ('m3_pre_prefix', 'Pre-cap'),
                  ('m3_post_prefix', 'Post-cap'), ('m3_post_window', 'Window')]
    rows = [one(all_rows, phase='steady', condition=c) for c, _ in conditions]
    contrast = one(csv_rows(contrast_source), name='post_minus_pre_latency')
    means = [float(row['mean_ms']) for row in rows]
    close(means[2] - means[1], contrast['difference'])
    assert {row['worlds'] for row in rows} == {'24'}
    assert {row['requests'] for row in rows} == {'120'}
    clean = [write_csv('f10_steady_means.csv', rows), write_csv('f10_post_minus_pre.csv', [contrast])]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.0, 1.9), gridspec_kw={'width_ratios': [1.9, 1]})
    fig.subplots_adjust(left=.105, right=.975, bottom=.27, top=.78, wspace=.48)
    yy = [3, 2, 1, 0]
    ax.barh(yy, means, height=.56, color=[GREY, TEAL, ORANGE, LIGHT], edgecolor='none')
    ax.set_yticks(yy, [label for _, label in conditions])
    ax.set_xlim(0, 900)
    ax.set_xticks([0, 400, 800])
    ax.set_xlabel('Mean steady request time (ms)', labelpad=3)
    base_axes(ax)
    for y, mean in zip(yy, means):
        ax.text(mean + 12, y, f'{mean:.1f}', ha='left', va='center', fontsize=7.1)
    panel(ax, 'a', 'Steady requests', offset=-.17)
    value, lo, hi = [float(contrast[k]) for k in ('difference', 'ci95_low', 'ci95_high')]
    bx.errorbar(value, .5, xerr=[[value-lo], [hi-value]], fmt='o', color=ORANGE,
                ecolor=GREY, capsize=3, markersize=4.2, elinewidth=1.05, markeredgewidth=.8)
    bx.set_xlim(0, 150)
    bx.set_xticks([0, 50, 100, 150])
    bx.set_ylim(0, 1)
    bx.set_yticks([])
    bx.set_xlabel('Post-cap − Pre-cap (ms)', labelpad=3)
    base_axes(bx)
    bx.text(.5, .88, f'+{value:.2f} ms', transform=bx.transAxes, ha='center', fontsize=8.5, fontweight='bold')
    bx.text(.5, .12, f'95% world CI [{lo:.2f}, {hi:.2f}]', transform=bx.transAxes,
            ha='center', fontsize=6.6)
    panel(bx, 'b', 'Paired-world difference', offset=-.18)
    fig.text(.105, .035, '24 worlds · 120 steady requests per configuration · resident models; loading and generation excluded', fontsize=6.6)
    return save(fig, 'f10_request_cost', 'F10', {
        'source_files': sources(source, contrast_source), 'clean_source_tables': clean,
        'selectors': {'means': {'phase': 'steady', 'conditions': [c for c, _ in conditions]},
                      'contrast': {'name': 'post_minus_pre_latency'}},
        'statistics': {'center': 'mean_ms', 'independent_unit': 'world', 'n_worlds': 24,
                       'steady_requests_per_condition': 120, 'measured_requests_all_phases': sum(int(r['requests']) for r in all_rows),
                       'contrast_interval': contrast['interval_interpretation'],
                       'contrast_analysis': contrast['analysis'], 'marginal_mean_error_bars': 'none'},
        'review_notes': ['p50_ms and p95_ms are not plotted.', 'The interval is on the contrast only.',
                         'Mean pairs: ' + ', '.join(r['mean_rerank_pairs'] for r in rows)]})


def plot_f11():
    oncology_source = 'experiments/runs/e3_m3/first_page_loss.csv'
    summary_source = PILOT + 'summary.csv'
    selection_source = PILOT + 'selection.json'
    oncology = csv_rows(oncology_source)
    counts = Counter()
    for row in oncology:
        counts[row['first_url_loss']] += int(row['n_queries'])
    configs = {r['config_id'] for r in oncology}
    n_records = sum(counts.values())
    assert len(configs) == 20 and n_records == 3100
    assert {sum(int(r['n_queries']) for r in oncology if r['config_id'] == config) for config in configs} == {155}
    primary = json.loads(input_path(selection_source).read_text())['primary']
    assert primary['policy'] == 'open' and primary['budget'] == 512
    n_dev, n_test = primary['n_dev_information_needs'], primary['n_test_information_needs']
    summary = csv_rows(summary_source)
    selected = [('U', primary['dev_selected_by_U_sim']), ('G', primary['dev_selected_by_G'])]
    test_rows = [one(summary, scope='overall', scenario='all', split='test', policy='open', config_id=c) for _, c in selected]
    tie_ids = primary['dev_all_ties']['U_sim']
    dev_rows = [one(summary, scope='overall', scenario='all', split='dev', policy='open', config_id=c) for c in tie_ids]
    dev_values = {float(row['U_sim']) for row in dev_rows}
    assert len(tie_ids) == 10 and len(dev_values) == 1
    dev_u = dev_values.pop()
    close(dev_u, .6)
    for (selector, _), row in zip(selected, test_rows):
        assert int(row['n_information_needs']) == n_test
        close(row['U_sim'], primary['test_selected_config_means']['U_sim' if selector == 'U' else 'G']['U_sim'])
    test_u = [float(row['U_sim']) for row in test_rows]
    delta = test_u[0] - test_u[1]
    close(delta, primary['test_U_sim_delta_U_selected_minus_G_selected'])
    oncology_small = [{'outcome': key, 'count': counts[key], 'n_configuration_records': n_records,
                       'n_questions': 155, 'n_configurations': len(configs)}
                      for key in ('candidate_not_covered', 'budget', 'retained')]
    clean = [write_csv('f11_oncology_outcomes.csv', oncology_small),
             write_csv('f11_pilot_selected_test.csv', [dict(row, selector=selector) for (selector, _), row in zip(selected, test_rows)]),
             write_csv('f11_pilot_development_ties.csv', dev_rows)]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.0, 1.8), gridspec_kw={'width_ratios': [1.3, 1]})
    fig.subplots_adjust(left=.14, right=.975, bottom=.25, top=.79, wspace=.47)
    values = [counts[k] for k in ('candidate_not_covered', 'budget', 'retained')]
    yy = [2, 1, 0]
    ax.barh(yy, values, color=[GREY, ORANGE, TEAL], height=.57, edgecolor='none')
    ax.set_yticks(yy, ['Raw-pool miss', 'Packing loss', 'Retained'])
    ax.set_xlim(0, 3350)
    ax.set_xticks([0, 1000, 2000, 3000])
    ax.set_xlabel('Configuration records', labelpad=3)
    for y, value in zip(yy, values):
        ax.text(value+45, y, f'{value:,}', va='center', ha='left', fontsize=7.1)
    base_axes(ax)
    panel(ax, 'a', 'Oncology page outcomes', offset=-.31)
    bx.bar([0, 1], [u*100 for u in test_u], width=.53, color=[TEAL, ORANGE], edgecolor='none')
    bx.axhline(dev_u*100, color=GREY, linestyle=(0, (3, 2)), linewidth=.9)
    bx.set_ylim(0, 100)
    bx.set_xlim(-.6, 1.6)
    bx.set_yticks([0, 50, 100])
    bx.set_ylabel('Complete coverage (%)', labelpad=3)
    bx.set_xticks([0, 1], ['U-selected', 'G-selected'])
    bx.tick_params(axis='x', length=0)
    for pos, u in enumerate(test_u):
        success = round(u*n_test)
        bx.text(pos, u*100*.48, f'{u*100:.1f}%\n{success}/{n_test}', ha='center', va='center',
                color='white', fontsize=7.3, fontweight='bold', linespacing=1.25)
    base_axes(bx, horizontal=False)
    panel(bx, 'b', 'Pilot test coverage', offset=-.25)
    fig.text(.14, .025, '3,100 records · 155 questions', fontsize=6.6)
    fig.text(.625, .025, '40 test worlds · dashed: dev tie, 10 configs at 60%', fontsize=6.4, ha='center')
    return save(fig, 'f11_complementary_checks', 'F11', {
        'source_files': sources(oncology_source, summary_source, selection_source),
        'clean_source_tables': clean,
        'selectors': {'oncology': 'sum n_queries by first_url_loss',
                      'pilot': {'branch': 'primary', 'policy': 'open', 'budget': 512,
                                'selected_configs': dict(selected), 'split': 'test'}},
        'statistics': {'oncology_unit': 'question-configuration record', 'n_oncology_records': n_records,
                       'n_oncology_questions': 155, 'n_pilot_test_worlds': n_test, 'n_pilot_dev_worlds': n_dev,
                       'pilot_test_difference_U_selected_minus_G_selected': delta,
                       'pilot_test_difference_ci95': primary['paired_test_group_bootstrap_95ci'],
                       'pilot_interval_estimand': primary['interval_estimand'],
                       'pilot_bootstrap_repetitions': primary['bootstrap_repetitions'],
                       'pilot_error_bars': 'none; conditional contrast interval retained in provenance'},
        'review_notes': ['Separate axes and populations.', 'Dashed development reference is not uncertainty.',
                         'Equal test G means do not imply identical per-task G outcomes.',
                         'No marginal confidence intervals are invented.']})


def plot_f4():
    pair_source = 'F4_task_pairs.csv'
    transition_source = 'F4_transition_check.json'
    pairs = csv_rows(pair_source)
    check = json.loads(input_path(transition_source).read_text())
    assert check['status'] == 'PASS'
    assert len(pairs) == 600 and len({r['qid'] for r in pairs}) == 600
    worlds = {r['group_id'] for r in pairs}
    assert len(worlds) == 300
    assert set(Counter(r['group_id'] for r in pairs).values()) == {2}
    assert all(r['no_cap_G'] == r['post_cap2_G'] for r in pairs)
    transitions = Counter()
    for r in pairs:
        delta = int(r['post_cap2_U']) - int(r['no_cap_U'])
        name = 'lost' if delta < 0 else 'gained' if delta > 0 else 'unchanged'
        assert r['transition'] == name and int(r['U_difference']) == delta
        transitions[name] += 1
    assert dict(transitions) == check['transitions']
    summary_source = STRENGTH + 'summary.csv'
    contrast_source = STRENGTH + 'exploratory_contrasts.csv'
    summary = csv_rows(summary_source)
    marginal = [one(summary, split='test', config_id=config) for config in (NOCAP, POST)]
    contrast = one(csv_rows(contrast_source), left_config=POST, right_config=NOCAP,
                   subgroup='all_test', endpoint='U_sim')
    for prefix, row in zip(('no_cap', 'post_cap2'), marginal):
        close(sum(int(r[prefix+'_G']) for r in pairs)/len(pairs), row['G_final'])
        close(sum(int(r[prefix+'_U']) for r in pairs)/len(pairs), row['U_sim'])
    close(float(marginal[1]['U_sim'])-float(marginal[0]['U_sim']), contrast['difference'])
    clean = [write_csv('f04_marginal_endpoints.csv', marginal),
             write_csv('f04_task_transitions.csv', [{'transition': k, 'task_count': transitions[k], 'n_task_pairs':len(pairs)}
                                                    for k in ('lost', 'gained', 'unchanged')]),
             write_csv('f04_paired_world_contrast.csv', [contrast]),
             write_csv('f04_task_pairs.csv', pairs)]
    fig, (ax, bx, cx) = plt.subplots(1, 3, figsize=(7.0, 1.9),
                                   gridspec_kw={'width_ratios': [1.65, 1.05, 1.05]})
    fig.subplots_adjust(left=.069, right=.976, bottom=.27, top=.72, wspace=.58)
    for row, offset, color, label in zip(marginal, (.16,-.16), (TEAL,ORANGE), ('No cap','Post-cap2')):
        values = [float(row['G_final'])*100, float(row['U_sim'])*100]
        positions = [1+offset, 0+offset]
        ax.barh(positions, values, height=.27, color=color, label=label, edgecolor='none')
        for y, value in zip(positions, values):
            ax.text(value+1.8,y,f'{value:.2f}',ha='left',va='center',fontsize=6.5)
    ax.set_yticks([1,0],['G','U_sim'])
    ax.set_ylim(-.4,1.4)
    ax.set_xlim(0,108)
    ax.set_xticks([0,50,100])
    ax.set_xlabel('Tasks (%)',labelpad=3)
    base_axes(ax)
    ax.legend(loc='lower center',bbox_to_anchor=(.5,1.01),ncol=2,frameon=False,fontsize=6.4,
              handlelength=1.1,handletextpad=.5,columnspacing=.9,borderaxespad=0)
    panel(ax,'a','Page vs fact support',offset=-.15,title_y=1.35)
    vals = [transitions[k] for k in ('lost','gained','unchanged')]
    bx.barh([2,1,0],vals,height=.53,color=[ORANGE,TEAL,LIGHT],edgecolor='none')
    bx.set_yticks([2,1,0],['Lost','Gained','Same'])
    bx.set_xlim(0,600)
    bx.set_xticks([0,300,600])
    bx.set_xlabel('Paired tasks',labelpad=3)
    base_axes(bx)
    for y,value in zip([2,1,0],vals):
        bx.text(value+10,y,str(value),ha='left',va='center',fontsize=6.8)
    panel(bx,'b','Coverage transitions',offset=-.31,title_y=1.35)
    value,lo,hi = [float(contrast[k])*100 for k in ('difference','ci95_low','ci95_high')]
    cx.axvline(0,color='#a0a0a0',linewidth=.7)
    cx.errorbar(value,.55,xerr=[[value-lo],[hi-value]],fmt='o',color=ORANGE,ecolor=GREY,
                capsize=3,markersize=4.0,elinewidth=1.0,markeredgewidth=.8)
    cx.set_xlim(-15,1)
    cx.set_xticks([-15,-10,-5,0])
    cx.set_ylim(0,1)
    cx.set_yticks([])
    cx.set_xlabel('Post-cap2 − No cap (pp)',labelpad=3,fontsize=6.8)
    base_axes(cx)
    cx.text(.5,.92,f'{value:.2f} pp',transform=cx.transAxes,ha='center',fontsize=8.2,fontweight='bold')
    cx.text(.5,.10,f'95% world CI\n[{lo:.2f}, {hi:.2f}]',transform=cx.transAxes,
            ha='center',fontsize=6.3,linespacing=1.15)
    panel(cx,'c','Coverage difference',offset=-.17,title_y=1.35)
    fig.text(.069,.032,'300 test worlds · 600 paired tasks · B = 2048 · contrast is exploratory',fontsize=6.6)
    return save(fig,'f04_measurement_gap','F4',{
        'source_files':sources(summary_source,contrast_source,pair_source,transition_source),
        'clean_source_tables':clean,
        'selectors':{'marginals':{'split':'test','config_ids':[NOCAP,POST]},
                     'contrast':{'left_config':POST,'right_config':NOCAP,'subgroup':'all_test','endpoint':'U_sim'},
                     'transitions':'taskwise post_cap2_U minus no_cap_U'},
        'statistics':{'n_independent_worlds':len(worlds),'n_task_pairs':len(pairs),
                      'taskwise_G_equality':True,'transitions':dict(transitions),
                      'marginal_center':'world mean (equivalent to task mean with two variants per world)',
                      'contrast_analysis':contrast['analysis'],
                      'contrast_interval':contrast['interval_interpretation'],
                      'adjusted_q':contrast['q_bh_within_family'],'marginal_mean_error_bars':'none'},
        'review_notes':['G equality verified on every paired task, not inferred from equal means.',
                        'No cap/post-cap comparison remains exploratory.',
                        'The interval is on the paired-world U contrast only.']})


def maintain_visual_qa(results):
    """Carry forward visual review only when regenerated PNG pixels are unchanged."""
    qa_path = CLEAN / 'quantitative_visual_qa.json'
    prior = json.loads(qa_path.read_text()) if qa_path.exists() else {}
    updated = dict(prior)
    for name, metadata in results.items():
        nodes = list(ET.parse(ROOT / metadata['exports']['svg']['path']).getroot().iter())
        text_nodes = sum(node.tag.endswith('}text') for node in nodes)
        image_nodes = sum(node.tag.endswith('}image') for node in nodes)
        font_embedded = b'/FontFile2' in (ROOT / metadata['exports']['pdf']['path']).read_bytes()
        if text_nodes == 0 or image_nodes or not font_embedded:
            raise ValueError(f'{name} failed editable-vector/font checks')
        previous = prior.get(name, {})
        prior_png_sha = previous.get('reviewed_exports', {}).get('png', {}).get('sha256')
        unchanged = prior_png_sha == metadata['exports']['png']['sha256']
        reviewed = previous.get('status') == 'PASS' and unchanged
        metadata['qa'].update({'svg_editable_text_nodes': text_nodes,
                               'svg_embedded_images': image_nodes,
                               'pdf_embedded_truetype': font_embedded,
                               'visual_review': 'PASS; reviewed PNG unchanged' if reviewed else 'pending'})
        updated[name] = {'status': 'PASS' if reviewed else 'pending visual review',
                         'visual_review': previous.get('visual_review', '') if reviewed else 'Inspect final-size PNG before accepting this redraw.',
                         'review_basis': 'same SHA-256 as the previously inspected PNG' if reviewed else 'new or unreviewed PNG',
                         'outside_figure_text': metadata['qa']['outside_figure_text'],
                         'svg_editable_text_nodes': text_nodes, 'svg_embedded_images': image_nodes,
                         'pdf_embedded_truetype': font_embedded, 'reviewed_exports': metadata['exports']}
    qa_path.write_text(json.dumps(updated, indent=2, ensure_ascii=False)+'\n')
    return {name: updated[name]['status'] for name in results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--figures', nargs='+', choices=['F4', 'F10', 'F11'], default=['F4', 'F10', 'F11'])
    args = parser.parse_args()
    if not INPUT_MANIFEST.is_file():
        raise FileNotFoundError(f'Missing frozen archived figure inputs: {INPUT_MANIFEST}')
    OUT.mkdir(parents=True, exist_ok=True)
    CLEAN.mkdir(parents=True, exist_ok=True)
    style()
    for relative in input_manifest()['files']:
        input_path(relative)
    source_report = input_path('evidence_check_report.json')
    report = json.loads(source_report.read_text())
    provenance_path = OUT / 'quantitative_provenance.json'
    provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else {}
    provenance.update({'backend': 'Python / matplotlib', 'source_repository': report['repository'],
                       'source_commit': report['commit'], 'source_evidence_check_sha256': sha(source_report),
                       'script': 'scripts/plot_completed_results.py', 'script_sha256': sha(Path(__file__)),
                       'input_manifest': {'path': str(INPUT_MANIFEST.relative_to(ROOT)), 'sha256': sha(INPUT_MANIFEST)},
                       'verified_inputs': VERIFIED_INPUTS,
                       'runtime': {'python': sys.version.split()[0], 'matplotlib': version('matplotlib'), 'numpy': version('numpy')},
                       'requirements_file': {'path': 'scripts/requirements_figures.txt', 'sha256': sha(ROOT / 'scripts/requirements_figures.txt')},
                       'palette': {'teal': TEAL, 'orange': ORANGE, 'grey': GREY}})
    results = {}
    for name in args.figures:
        results[name] = {'F4': plot_f4, 'F10': plot_f10, 'F11': plot_f11}[name]()
    visual_qa = maintain_visual_qa(results)
    provenance.setdefault('figures', {}).update(results)
    provenance_path.write_text(json.dumps(provenance, indent=2, ensure_ascii=False)+'\n')
    summary = {'figures_run': args.figures, 'script_sha256': provenance['script_sha256'],
               'input_manifest_sha256': sha(INPUT_MANIFEST), 'verified_input_count': len(VERIFIED_INPUTS),
               'visual_review': visual_qa,
               'outputs': {name: result['exports'] for name, result in results.items()},
               'clipping_checks': {name: result['qa']['outside_figure_text'] for name, result in results.items()}}
    (CLEAN / 'quantitative_run_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({'completed': args.figures, 'provenance': str(provenance_path.relative_to(ROOT)),
                      'clipping_checks': summary['clipping_checks']}, indent=2))


if __name__ == '__main__':
    main()
