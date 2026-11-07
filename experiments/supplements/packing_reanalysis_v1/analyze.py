"""Reanalyse frozen packing results without rerunning models or editing sources."""
import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def dump_csv(path, rows):
    assert rows
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[3])
    ap.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[3]/'build/reanalysis/packing_v1')
    args = ap.parse_args()
    root, out = args.project, args.output
    root, out = root.resolve(), out.resolve()
    if not out.is_relative_to(root / 'build'):
        raise ValueError('Output must be a new directory under repository build/')
    out.mkdir(parents=True, exist_ok=False)
    source = root / 'experiments/strengthening/results/strengthening_v1/per_record.csv'
    summary_path = root / 'experiments/strengthening/results/strengthening_v1/summary.csv'
    manifest_path = root / 'experiments/runs/strengthening_v1/manifest.json'
    audit_path = root / 'experiments/strengthening/data/strengthening_v1/audit/report.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    configs = {}
    for c in manifest['configurations']:
        if (c['retriever'] == 'dense' and c['pool'] == 64 and c['reranker'] == 'm3'
                and c['cap'] == 2 and c['cap_stage'] == 'post'
                and c['dense_view'] == 'prefix512' and c['score_view'] == 'prefix512'
                and not c['refill'] and c['policy_stage'] == 'none'
                and c['budget'] in (512, 2048) and c['packing'] in ('prefix', 'whole', 'window')):
            configs[c['config_id']] = c
    assert len(configs) == 6
    rows = defaultdict(dict)
    total_source_rows = 0
    with source.open(encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            total_source_rows += 1
            if r['split'] != 'test' or r['config_id'] not in configs:
                continue
            c = configs[r['config_id']]
            for key, value in c.items():
                if value is not None:
                    assert r[key] == str(value), (key, r[key], value)
            k = (int(r['budget']), r['packing'])
            assert r['qid'] not in rows[k]
            s = set(json.loads(r['supported_fact_ids']))
            lost = set(json.loads(r['budget_lost_last_support_ids']))
            assert not (s & lost)
            upstream = s | lost
            assert len(s) == int(r['supported_fact_count'])
            assert len(upstream) == int(r['post_policy_supported_fact_count'])
            assert int(r['U_sim']) == int(len(s) == int(r['required_fact_count']))
            assert int(r['post_policy_U_sim']) == int(len(upstream) == int(r['required_fact_count']))
            assert abs(float(r['fact_coverage']) - len(s) / int(r['required_fact_count'])) < 1e-12
            assert int(r['budget_lost_last_support_count']) == len(lost)
            r['_support'], r['_upstream'] = s, upstream
            rows[k][r['qid']] = r
    assert total_source_rows == manifest['expected_records'] == 89280
    conditional, overall, details, marginals = [], [], [], []
    for budget in (512, 2048):
        base = rows[(budget, 'prefix')]
        assert len(base) == 600
        worlds = Counter(r['group_id'] for r in base.values())
        assert len(worlds) == 300 and set(worlds.values()) == {2}
        assert sorted(Counter(r['seed'] for r in base.values()).values()) == [200, 200, 200]
        for policy in ('prefix', 'whole', 'window'):
            rr = list(rows[(budget, policy)].values())
            assert len(rr) == 600
            marginals.append(dict(budget=budget, packing=policy, tasks=600, worlds=300,
                                  full_support_tasks=sum(int(r['U_sim']) for r in rr),
                                  full_coverage=mean(int(r['U_sim']) for r in rr),
                                  partial_fact_coverage=mean(float(r['fact_coverage']) for r in rr),
                                  page_retention=mean(int(r['G_final']) for r in rr)))
        for policy in ('whole', 'window'):
            alt = rows[(budget, policy)]
            assert base.keys() == alt.keys()
            c = Counter()
            base_cov, alt_cov = [], []
            for qid, a in base.items():
                b = alt[qid]
                for key in ('group_id', 'seed', 'variant_id', 'required_fact_count'):
                    assert a[key] == b[key]
                # Every pre-packing stage score and transition is invariant to packing.
                for key in a:
                    if key.startswith(('raw_', 'after_retrieval_policy_', 'pre_cap_', 'rerank_', 'post_cap_', 'post_policy_', 'score_visible_', 'score_single_call_')):
                        assert a[key] == b[key], (budget, policy, qid, key)
                assert a['_upstream'] == b['_upstream']
                s0, s1 = a['_support'], b['_support']
                upstream = a['_upstream']
                assert s0 <= upstream and s1 <= upstream
                originally_lost = upstream - s0
                restored = originally_lost & s1
                new_lost = s0 - s1
                eligible = a['post_policy_U_sim'] == '1' and a['U_sim'] == '0'
                u0, u1 = int(a['U_sim']), int(b['U_sim'])
                base_cov.append(float(a['fact_coverage']))
                alt_cov.append(float(b['fact_coverage']))
                c['n'] += 1
                c['base_full'] += u0
                c['alt_full'] += u1
                c['gained_full'] += int(u0 == 0 and u1 == 1)
                c['lost_full'] += int(u0 == 1 and u1 == 0)
                c['both_full'] += int(u0 == u1 == 1)
                c['neither_full'] += int(u0 == u1 == 0)
                if eligible:
                    assert a['first_support_loss_stage'] == 'budget'
                    c['eligible'] += 1
                    c['any_restore'] += bool(restored)
                    c['new_other_loss'] += bool(new_lost)
                    c['full_restore'] += u1
                    c['restored_fact_instances'] += len(restored)
                    c['new_lost_fact_instances'] += len(new_lost)
                    c['originally_lost_fact_instances'] += len(originally_lost)
                    c['restore_and_lose'] += bool(restored and new_lost)
                    c['fact_count_increase'] += len(s1) > len(s0)
                    c['fact_count_decrease'] += len(s1) < len(s0)
                    c['fact_count_equal'] += len(s1) == len(s0)
                details.append(dict(budget=budget, alternative=policy, qid=qid,
                                    group_id=a['group_id'], seed=a['seed'], variant_id=a['variant_id'],
                                    prefix_config_id=a['config_id'], alternative_config_id=b['config_id'],
                                    required_fact_count=int(a['required_fact_count']),
                                    prepacking_full=int(a['post_policy_U_sim']),
                                    prefix_full=u0, alternative_full=u1,
                                    eligible_packing_loss=int(eligible),
                                    restored_fact_count=len(restored), new_lost_fact_count=len(new_lost),
                                    prefix_fact_count=len(s0), alternative_fact_count=len(s1),
                                    prefix_partial_coverage=float(a['fact_coverage']),
                                    alternative_partial_coverage=float(b['fact_coverage']),
                                    prepacking_supported_fact_ids=json.dumps(sorted(upstream)),
                                    prefix_supported_fact_ids=json.dumps(sorted(s0)),
                                    alternative_supported_fact_ids=json.dumps(sorted(s1)),
                                    restored_fact_ids=json.dumps(sorted(restored)),
                                    new_lost_fact_ids=json.dumps(sorted(new_lost)),
                                    annotation_source=a['annotation_source'],
                                    valid_for_human_eval_claim=a['valid_for_human_eval_claim']))
            assert sum(c[k] for k in ('gained_full','lost_full','both_full','neither_full')) == 600
            assert c['alt_full'] - c['base_full'] == c['gained_full'] - c['lost_full']
            assert c['eligible'] == (243 if budget == 512 else 73)
            assert c['full_restore'] == c['gained_full']  # Upstream-incomplete cases cannot become complete here.
            conditional.append(dict(budget=budget, alternative=policy, total_tasks=600,
                                    eligible_tasks=c['eligible'], eligible_fraction=c['eligible']/600,
                                    any_fact_restored_tasks=c['any_restore'],
                                    any_fact_restored_fraction=c['any_restore']/c['eligible'],
                                    newly_lost_other_fact_tasks=c['new_other_loss'],
                                    newly_lost_other_fact_fraction=c['new_other_loss']/c['eligible'],
                                    full_coverage_restored_tasks=c['full_restore'],
                                    full_coverage_restored_fraction=c['full_restore']/c['eligible'],
                                    originally_lost_fact_instances=c['originally_lost_fact_instances'],
                                    restored_fact_instances=c['restored_fact_instances'],
                                    newly_lost_fact_instances=c['new_lost_fact_instances'],
                                    restored_and_newly_lost_tasks=c['restore_and_lose'],
                                    fact_count_increase_tasks=c['fact_count_increase'],
                                    fact_count_decrease_tasks=c['fact_count_decrease'],
                                    fact_count_equal_tasks=c['fact_count_equal']))
            overall.append(dict(budget=budget, alternative=policy, tasks=600, worlds=300,
                                prefix_full_support_tasks=c['base_full'],
                                alternative_full_support_tasks=c['alt_full'],
                                gained_full_support_tasks=c['gained_full'], lost_full_support_tasks=c['lost_full'],
                                both_full_support_tasks=c['both_full'], neither_full_support_tasks=c['neither_full'],
                                prefix_full_coverage=c['base_full']/600,
                                alternative_full_coverage=c['alt_full']/600,
                                full_coverage_difference_pp=(c['alt_full']-c['base_full'])/6,
                                prefix_partial_coverage=mean(base_cov),
                                alternative_partial_coverage=mean(alt_cov),
                                partial_coverage_difference_pp=100*(mean(alt_cov)-mean(base_cov))))
    # Cross-check against the frozen published aggregate file, not only this calculation.
    with summary_path.open(encoding='utf-8', newline='') as f:
        published = {r['config_id']:r for r in csv.DictReader(f) if r['split'] == 'test' and r['config_id'] in configs}
    assert len(published) == 6
    for r in marginals:
        cid = next(cid for cid,c in configs.items() if c['budget'] == r['budget'] and c['packing'] == r['packing'])
        old = published[cid]
        assert int(old['n_worlds']) == 300
        for new_key, old_key in [('full_coverage','U_sim'),('partial_fact_coverage','fact_coverage'),('page_retention','G_final')]:
            assert abs(r[new_key] - float(old[old_key])) < 1e-12
    by_key = {(r['budget'],r['packing']):r for r in marginals}
    assert abs(by_key[(512,'prefix')]['partial_fact_coverage'] - .4128) < .00005
    assert abs(by_key[(512,'window')]['partial_fact_coverage'] - .4256) < .00005
    dump_csv(out/'packing_loss_recovery.csv', conditional)
    dump_csv(out/'packing_all_test_transitions.csv', overall)
    dump_csv(out/'packing_marginals.csv', marginals)
    dump_csv(out/'packing_paired_records.csv', details)
    trace_checks = []
    for budget, policy, gain in [(512,'window',True),(2048,'window',True),(512,'whole',False)]:
        r = next(r for r in details if r['budget'] == budget and r['alternative'] == policy
                 and (r['prefix_full'],r['alternative_full']) == ((0,1) if gain else (1,0)))
        name = hashlib.sha256(json.dumps(r['qid'],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()[:24] + '.json.gz'
        trace_path = root / 'experiments/runs/strengthening_v1/traces' / name
        with gzip.open(trace_path,'rt',encoding='utf-8') as f:
            trace = json.load(f)
        records = {x['configuration']['config_id']:x for x in trace['configurations']}
        a,b = (records[r[key]] for key in ('prefix_config_id','alternative_config_id'))
        assert trace['qid'] == r['qid']
        assert a['stages'] == b['stages']
        assert a['final_context']['budget'] == b['final_context']['budget'] == budget
        trace_checks.append(dict(qid=r['qid'],budget=budget,alternative=policy,
                                 trace_file=str(trace_path),trace_sha256=sha256(trace_path),
                                 upstream_stage_records_identical=True,
                                 prefix_full=r['prefix_full'],alternative_full=r['alternative_full']))
    (out/'trace_spot_checks.json').write_text(json.dumps(trace_checks,indent=2),encoding='utf-8')
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    provenance = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                      source_project=str(root), source_csv=str(source),
                      source_csv_sha256=sha256(source), source_rows=total_source_rows,
                      frozen_aggregate_sha256=sha256(summary_path),
                      run_manifest_sha256=sha256(manifest_path),
                      script_sha256=sha256(Path(__file__)),
                      configs=configs, matched_tasks=600, matched_worlds=300,
                      human_audit_completed=audit['human_audit_completed'],
                      analysis_status='exploratory reanalysis of existing parser-scored results',
                      selection='All test tasks. Conditional subset: post_policy_U_sim=1 and prefix U_sim=0.',
                      pairing='qid within each fixed budget. group_id identifies dependent paired variants.',
                      support_reconstruction='prepacking support = prefix supported_fact_ids union budget_lost_last_support_ids; checked against alternative and stage counts.',
                      inference='Descriptive counts and empirical differences only. No new confidence intervals or significance tests.',
                      raw_trace_verification='Three paired gain/loss examples checked against frozen compressed traces; all upstream stage records identical.',
                      interpretation='Restoration is defined by the existing parser, not independently human-validated. Packing changes can alter chunk selection as well as truncation. No proof of unique causal explanation or generic tuning benefit.')
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    print(json.dumps({'status':'PASS','conditional':conditional,'overall':overall}, indent=2))


if __name__ == '__main__':
    main()
