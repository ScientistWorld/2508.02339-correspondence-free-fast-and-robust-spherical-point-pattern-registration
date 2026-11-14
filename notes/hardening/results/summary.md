| attempt | status | robust med | robust succ1 | robust p95 | high med | img med | sparse med | sparse succ5 | rank (valid σ) | rank (all σ) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| reference:spmc_frs | ok | 0.587 | 0.821 | 1.377 | 0.636 | 0.869 | 1.677 | 0.738 | +0.000 | +0.000 |
| v_refine720_1440:spmc_frs_refine720_1440 | ok | 0.425 | 0.808 | 1.853 | 0.512 | 1.632 | 2.822 | 0.600 | -0.259 | -0.287 |
| v_refine1440:spmc_frs_refine1440 | ok | 0.420 | 0.812 | 1.687 | 0.505 | 1.646 | 2.933 | 0.586 | -0.268 | -0.295 |
| baselines:principal_axes | ok | 0.349 | 0.801 | 2.115 | 0.787 | 21.138 | 3.758 | 0.570 | -0.290 | -0.301 |
| stale_artifacts:principal_axes | ok | 0.349 | 0.801 | 2.115 | 0.787 | 21.138 | 3.758 | 0.570 | -0.290 | -0.301 |
| tamper_rotations:principal_axes | ok | 0.349 | 0.801 | 2.115 | 0.787 | 21.138 | 3.758 | 0.570 | -0.290 | -0.301 |
| reference:spmc | ok | 0.572 | 0.660 | 7.676 | 1.103 | 9.320 | 5.674 | 0.480 | -0.429 | -0.449 |
| reference:frs | ok | 0.837 | 0.612 | 166.022 | 0.822 | 0.976 | 3.052 | 0.584 | -1.023 | -1.062 |
| bruteforce:bruteforce_grid | ok | 10.071 | 0.001 | 137.241 | 10.019 | 8.803 | 9.912 | 0.122 | -1.626 | -1.660 |
| shortcuts:public_answer_enumeration | ok | 97.265 | 0.000 | 171.153 | 97.072 | 127.480 | 100.817 | 0.000 | -3.950 | -3.336 |
| baselines:identity | ok | 132.366 | 0.000 | 175.477 | 130.784 | 131.500 | 130.757 | 0.000 | -4.612 | -3.786 |
| shortcuts:read_hidden_seed | ok | 132.366 | 0.000 | 175.477 | 130.784 | 131.500 | 130.757 | 0.000 | -4.612 | -3.786 |
| stale_artifacts:identity | ok | 132.366 | 0.000 | 175.477 | 130.784 | 131.500 | 130.757 | 0.000 | -4.612 | -3.786 |
| tamper_rotations:identity | ok | 132.366 | 0.000 | 175.477 | 130.784 | 131.500 | 130.757 | 0.000 | -4.612 | -3.786 |
| budget:cpu_hog_3s | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -5.763 | -4.565 |
| shortcuts:skip_hard_instances | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -5.763 | -4.565 |
| shortcuts:empty_registry | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -5.763 | -4.565 |
| shortcuts:import_error | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -5.763 | -4.565 |
| shortcuts:nan_matrix | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -5.763 | -4.565 |
| shortcuts:reflection | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -5.763 | -4.565 |
| shortcuts:scaled_identity | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -5.763 | -4.565 |
| shortcuts:wrong_shape | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -5.763 | -4.565 |
| shortcuts:zero_matrix | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -5.763 | -4.565 |
| tamper_template:frs | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -5.763 | -4.565 |
| tamper_template:spmc | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -5.763 | -4.565 |
| tamper_template:spmc_frs | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -5.763 | -4.565 |

Reference rerun identical: True
Paired bootstrap: {
 "reference_self_rank_95pct_halfwidth": 0.04362055183300237,
 "baselines:identity": {
  "rank_vs_reference": -4.612393304827233,
  "paired_bootstrap_95ci": [
   -4.672423183853834,
   -4.5750131059076
  ]
 },
 "baselines:principal_axes": {
  "rank_vs_reference": -0.29041591679606926,
  "paired_bootstrap_95ci": [
   -0.3385345621895839,
   -0.25822926465721485
  ]
 },
 "bruteforce:bruteforce_grid": {
  "rank_vs_reference": -1.6258518564279876,
  "paired_bootstrap_95ci": [
   -1.6829269309298764,
   -1.5858358293720356
  ]
 },
 "reference:frs": {
  "rank_vs_reference": -1.023168434579366,
  "paired_bootstrap_95ci": [
   -1.0748358983503583,
   -0.8912013804419346
  ]
 },
 "reference:spmc": {
  "rank_vs_reference": -0.42947153957160616,
  "paired_bootstrap_95ci": [
   -0.47359763627244733,
   -0.3976288547208292
  ]
 },
 "v_refine1440:spmc_frs_refine1440": {
  "rank_vs_reference": -0.26795210523288515,
  "paired_bootstrap_95ci": [
   -0.31675593586946243,
   -0.16725746804102984
  ]
 },
 "v_refine720_1440:spmc_frs_refine720_1440": {
  "rank_vs_reference": -0.2585963899303504,
  "paired_bootstrap_95ci": [
   -0.3064414816180609,
   -0.16577702317639287
  ]
 }
}
