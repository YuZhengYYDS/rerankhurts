"""Reconstruct the paired F4 source data from frozen task-configuration records."""
from pathlib import Path
from collections import defaultdict, Counter
import argparse
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
REL = Path('experiments/strengthening/results/strengthening_v1/per_record.csv')
OFF = 'dense_p64_m3_off_b2048_prefix_prefix512_dprefix512_polnone'
POST = 'dense_p64_m3_post2_b2048_prefix_prefix512_dprefix512_polnone'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/figure_audit')
    output = parser.parse_args().output
    output.mkdir(parents=True, exist_ok=True)
    source = ROOT / REL
    if not source.exists():
        source = ROOT / 'source_data' / REL
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    recorded = json.loads((ROOT / 'MANIFEST.json').read_text())[REL.as_posix()]['sha256']
    if digest != recorded:
        raise ValueError('Frozen per-record bytes differ from the shipped manifest')
    rows = defaultdict(dict)
    with source.open(newline='') as stream:
        for row in csv.DictReader(stream):
            if row['split'] != 'test' or row['config_id'] not in (OFF, POST):
                continue
            key = row['qid']
            name = 'no_cap' if row['config_id'] == OFF else 'post_cap2'
            if name in rows[key]:
                raise ValueError('Duplicate task/configuration')
            rows[key][name] = row
    pairs = []
    for qid, configs in sorted(rows.items()):
        a, b = configs['no_cap'], configs['post_cap2']
        for field in ('group_id', 'seed', 'variant_id'):
            if a[field] != b[field]:
                raise ValueError('Mismatched paired identity')
        pairs.append({'qid': qid, 'group_id': a['group_id'], 'seed': a['seed'],
                      'variant_id': a['variant_id'], 'no_cap_G': int(float(a['G_final'])),
                      'post_cap2_G': int(float(b['G_final'])), 'no_cap_U': int(float(a['U_sim'])),
                      'post_cap2_U': int(float(b['U_sim']))})
    if len(pairs) != 600:
        raise ValueError('Expected 600 matched test tasks')
    transition = Counter()
    worlds = defaultdict(list)
    for row in pairs:
        diff = row['post_cap2_U'] - row['no_cap_U']
        row['U_difference'] = diff
        row['transition'] = 'lost' if diff < 0 else 'gained' if diff > 0 else 'unchanged'
        transition[row['transition']] += 1
        worlds[row['group_id']].append(diff)
    if any(row['no_cap_G'] != row['post_cap2_G'] for row in pairs):
        raise ValueError('Task-level G outcomes differ')
    if transition != {'lost': 63, 'gained': 17, 'unchanged': 520}:
        raise ValueError('Unexpected paired support transitions')
    if len(worlds) != 300 or any(len(values) != 2 for values in worlds.values()):
        raise ValueError('Expected two variants in each of 300 independent test worlds')
    out = output / 'F4_task_pairs.csv'
    with out.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(pairs[0])); writer.writeheader(); writer.writerows(pairs)
    report = {'status': 'PASS', 'source': REL.as_posix(), 'source_bytes': source.stat().st_size,
              'source_sha256': digest, 'task_pairs': 600, 'independent_worlds': 300,
              'no_cap_U_success': sum(r['no_cap_U'] for r in pairs),
              'post_cap2_U_success': sum(r['post_cap2_U'] for r in pairs),
              'no_cap_G_success': sum(r['no_cap_G'] for r in pairs),
              'post_cap2_G_success': sum(r['post_cap2_G'] for r in pairs),
              'G_outcomes_identical_on_every_task': True, 'transitions': dict(transition),
              'difference': sum(r['U_difference'] for r in pairs) / len(pairs),
              'pair_data': 'F4_task_pairs.csv'}
    (output / 'F4_transition_check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
