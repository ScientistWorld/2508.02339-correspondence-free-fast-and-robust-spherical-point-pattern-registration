"""Install one audit method, generate its artifacts, invoke untouched hidden test.

The hidden evaluator is always a separate, no-argument process with its default
paths. It and its launcher are never edited. All mutations are restored on exit.
"""
import argparse
import json
import os
import pickle
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path('/home/user')


def shell(script, log):
    env = os.environ.copy()
    for key in ('RAW_RESULTS', 'RAW_COMPLEXITY_RESULTS', 'SCORES_OUTPUT'):
        env.pop(key, None)
    with log.open('w') as out:
        p = subprocess.run(['bash', script], cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT)
    return p.returncode


def run(name):
    folder = ROOT / 'redteam' / name
    touched = ['method/spherical_registration.py', 'scoring/raw_results.json',
               'scoring/raw_complexity_results.json', 'scoring/scores_train.json',
               'scoring/scores_test.json', 'data/downloads/vector_alignment_dataset/RandomRotation100.pkl',
               'method/audit_unregistered.py']
    original = {p: (ROOT/p).read_bytes() if (ROOT/p).exists() else None for p in touched}
    try:
        shutil.copyfile(folder/'method.py', ROOT/'method/spherical_registration.py')
        if name == 'shortcut_stale_identity':
            (ROOT/'method/audit_unregistered.py').write_text((folder/'method.py').read_text())
        # Prevent timestamp/size collisions in Python's ordinary bytecode cache.
        for cache in (ROOT/'method/__pycache__').glob('spherical_registration.*.pyc'):
            cache.unlink()
        if name.startswith('reference_seed') or name.startswith('better_') or name in (
                'weaker_spmc', 'weaker_identity', 'shortcut_answer_enumeration', 'shortcut_fixed_rotations'):
            if name == 'shortcut_fixed_rotations':
                import numpy as np
                (ROOT/'data/downloads/vector_alignment_dataset/RandomRotation100.pkl').write_bytes(pickle.dumps([np.eye(3) for _ in range(100)]))
            seed = int(name[-1]) if name.startswith('reference_seed') else 0
            subprocess.run([sys.executable, '-B', 'redteam/benchmark.py', str(folder), '--seed', str(seed)], check=True)
            raw = json.loads((folder/'raw_results.json').read_text())
            comp = json.loads((folder/'raw_complexity_results.json').read_text())
        else:
            # Reuse honestly generated reference outputs; these are not hidden answers.
            ref = ROOT/'redteam/reference_seed0'
            raw = json.loads((ref/'raw_results.json').read_text())
            comp = json.loads((ref/'raw_complexity_results.json').read_text())
            if name == 'shortcut_fabricated_zero' or name == 'shortcut_impossible_negative':
                value = 0.0 if name.endswith('zero') else -1.0
                raw = {'spmc_frs': {f'A{p}_B{c}': {'errors': [value]*100, 'times': [value]*100}
                                    for p in range(1,6) for c in range(1,8)}}
                comp = {'spmc_frs': {str(s): {'times': [value]*20} for s in (10**6, 10**7)}}
            elif name == 'shortcut_empty':
                raw, comp = {'spmc_frs': {}}, {}
            elif name == 'shortcut_missing_accuracy':
                raw, comp = {'spmc_frs': {}}, {'spmc_frs': {str(s): {'times': [0.0]*20} for s in (10**6, 10**7)}}
            elif name == 'shortcut_filter_easy':
                raw = {'spmc_frs': {k:v for k,v in raw['spmc_frs'].items() if k.endswith('_B1')}}
            elif name == 'shortcut_null':
                for row in raw['spmc_frs'].values():
                    row['errors'] = [None]*100
            elif name == 'shortcut_nan':
                for row in raw['spmc_frs'].values():
                    row['errors'], row['times'] = [float('nan')]*100, [float('nan')]*100
            elif name == 'shortcut_short_arrays':
                for row in raw['spmc_frs'].values():
                    row['errors'], row['times'] = [0.0], [0.0]
            elif name in ('shortcut_stale_identity', 'shortcut_write_final'):
                pass
            else:
                raise ValueError(name)
        (folder/'raw_results.json').write_text(json.dumps(raw, indent=2)+'\n')
        (folder/'raw_complexity_results.json').write_text(json.dumps(comp, indent=2)+'\n')
        (ROOT/'scoring/raw_results.json').write_text(json.dumps(raw))
        (ROOT/'scoring/raw_complexity_results.json').write_text(json.dumps(comp))
        if name == 'shortcut_write_final':
            fake = {'experiments': {'robust_alignment_all': {'results': {'spmc_frs': {'median_rotation_error_deg': -123}}}}}
            (ROOT/'scoring/scores_test.json').write_text(json.dumps(fake))
            (folder/'forged_scores_before_test.json').write_text(json.dumps(fake))
        # A failure must not silently retain the preceding successful test score.
        elif (ROOT/'scoring/scores_test.json').exists():
            (ROOT/'scoring/scores_test.json').unlink()
        train_rc = shell('scripts/evaluate_train.sh', folder/'train.log')
        if train_rc == 0:
            shutil.copyfile(ROOT/'scoring/scores_train.json', folder/'scores_train.json')
        test_rc = shell('scripts/evaluate_test.sh', folder/'test.log')
        if (ROOT/'scoring/scores_test.json').exists():
            shutil.copyfile(ROOT/'scoring/scores_test.json', folder/'scores_test.json')
        (folder/'status.json').write_text(json.dumps({'train_exit': train_rc, 'test_exit': test_rc}, indent=2)+'\n')
        print(name, 'train', train_rc, 'test', test_rc, flush=True)
    finally:
        for path, content in original.items():
            p = ROOT/path
            if content is None:
                p.unlink(missing_ok=True)
            else:
                p.write_bytes(content)
        for cache in (ROOT/'method/__pycache__').glob('spherical_registration.*.pyc'):
            cache.unlink()


if __name__ == '__main__':
    run(sys.argv[1])
