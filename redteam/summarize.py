"""Apply the specified ranking rule to a declared audit cohort.

Future cohort standard deviations cannot be known. Pareto domination and
missing-metric ties are also reported because they do not depend on that cohort.
Coefficient sign is intentionally ignored; direction comes from higher_is_better.
"""
import json
import math
import statistics
from pathlib import Path

ROOT = Path('/home/user/redteam')
SPEC = json.loads((ROOT/'ranking_reference.json').read_text())['experiments']
CHECKED = json.loads((ROOT/'reference_scores_test.json').read_text())


def values(scores):
    return { (exp, metric): result.get(metric)
            for exp, bundle in scores.get('experiments', {}).items()
            for method, result in bundle.get('results', {}).items() if method == 'spmc_frs'
            for metric in SPEC.get(exp, {}).get('metrics', {}) }


attempts = {}
statuses = {}
for p in sorted(ROOT.glob('*/status.json')):
    name = p.parent.name
    statuses[name] = json.loads(p.read_text())
    scores = p.parent/'scores_test.json'
    if statuses[name]['test_exit'] == 0 and scores.exists():
        attempts[name] = json.loads(scores.read_text())

flat = {name: values(scores) for name, scores in attempts.items()}
flat['checked_reference'] = values(CHECKED)
scales = {}
for exp, spec in SPEC.items():
    for metric in spec['metrics']:
        k = exp, metric
        vals = [v[k] for v in flat.values() if isinstance(v.get(k), (int, float)) and math.isfinite(v[k])]
        scales[k] = statistics.pstdev(vals) if len(vals)>1 else 0.0


def rank(vals, anchor):
    total, contributions = 0., {}
    for exp, spec in SPEC.items():
        for metric, desc in spec['metrics'].items():
            k = exp, metric
            a, b = vals.get(k), anchor.get(k)
            if a is None or b is None or not scales[k]:
                continue
            if not math.isfinite(a) or not math.isfinite(b):
                continue
            improvement = (a-b) if desc['higher_is_better'] else (b-a)
            delta = spec['weight']*abs(desc['coefficient'])*improvement/scales[k]
            total += delta
            contributions[exp+'/'+metric] = delta
    return total, contributions


summary = {'normalization': 'population standard deviation across successful audit attempts plus checked reference; NaNs excluded',
           'cohort': list(flat), 'standard_deviations': {'/'.join(k):v for k,v in scales.items()},
           'attempts': {}}
for name in statuses:
    entry = dict(statuses[name])
    if name in flat:
        entry['rank_vs_checked_reference'], entry['contributions_vs_checked_reference'] = rank(flat[name], flat['checked_reference'])
        entry['rank_vs_fresh_reference'], entry['contributions_vs_fresh_reference'] = rank(flat[name], flat.get('reference_seed0', flat['checked_reference']))
        entry['metrics'] = {'/'.join(k): v for k,v in flat[name].items()}
        entry['missing_metrics'] = ['/'.join((exp,metric)) for exp,spec in SPEC.items() for metric in spec['metrics'] if (exp,metric) not in flat[name]]
    summary['attempts'][name] = entry
seeds = [flat.get(f'reference_seed{i}', {}) for i in range(3)]
spread = {}
for k in set().union(*seeds):
    vals = [s[k] for s in seeds if k in s]
    spread['/'.join(k)] = {'min': min(vals), 'max': max(vals), 'range': max(vals)-min(vals)}
summary['seed_spread'] = spread
seed_ranks = [summary['attempts'][f'reference_seed{i}']['rank_vs_fresh_reference'] for i in range(3) if f'reference_seed{i}' in summary['attempts']]
summary['seed_rank_spread'] = max(seed_ranks)-min(seed_ranks) if seed_ranks else None
(ROOT/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
cols = [('robust_alignment_all','median_rotation_error_deg'), ('robust_alignment_all','mean_rotation_error_deg'),
        ('robust_alignment_all','success_rate_1deg'), ('robust_alignment_all','median_time_s'),
        ('robust_alignment_high_outliers','median_rotation_error_deg'),
        ('computational_complexity','time_at_1e7_points_s')]
table = ['| Run | all median ° | all mean ° | success ≤1° | time s | high median ° | 10⁷ time s | rank vs fresh | rank vs checked |',
         '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for name in ['checked_reference', *flat]:
    if name == 'checked_reference' and len(table)>2:
        continue
    def fmt(v):
        return 'missing' if v is None else f'{v:.6g}'
    vals = flat[name]
    table.append('| '+name+' | '+' | '.join(fmt(vals.get(k)) for k in cols)+' | '+fmt(rank(vals, flat.get('reference_seed0', flat['checked_reference']))[0])+' | '+fmt(rank(vals, flat['checked_reference'])[0])+' |')
(ROOT/'report_tables.md').write_text('\n'.join(table)+'\n')
print('\n'.join(table))
print('Seed rank range:', summary['seed_rank_spread'])
