| attempt | status | robust med | robust succ1 | robust p95 | high med | img med | sparse med | sparse succ5 | rank (valid σ) | rank (all σ) | rank (honest σ) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| v_dual_polish:dual_init_frs_polish | ok | 0.157 | 1.000 | 0.340 | 0.184 | 1.212 | 1.117 | 0.780 | +0.119 | +0.103 | +0.337 |
| v_polish:spmc_frs_polish | ok | 0.165 | 0.993 | 0.351 | 0.185 | 1.226 | 1.282 | 0.738 | +0.095 | +0.083 | +0.264 |
| v_dual:dual_init_frs | ok | 0.416 | 0.883 | 1.139 | 0.524 | 0.746 | 1.341 | 0.780 | +0.085 | +0.079 | +0.200 |
| reference:spmc_frs | ok | 0.587 | 0.821 | 1.377 | 0.636 | 0.869 | 1.677 | 0.738 | +0.000 | +0.000 | +0.000 |
| v_refine720_1440:spmc_frs_refine720_1440 | ok | 0.425 | 0.808 | 1.853 | 0.512 | 1.632 | 2.822 | 0.600 | -0.239 | -0.237 | -0.441 |
| v_refine1440:spmc_frs_refine1440 | ok | 0.420 | 0.812 | 1.687 | 0.505 | 1.646 | 2.933 | 0.586 | -0.248 | -0.244 | -0.474 |
| baselines:principal_axes | ok | 0.349 | 0.801 | 2.115 | 0.787 | 21.138 | 3.758 | 0.570 | -0.275 | -0.253 | -0.950 |
| stale_artifacts:principal_axes | ok | 0.349 | 0.801 | 2.115 | 0.787 | 21.138 | 3.758 | 0.570 | -0.275 | -0.253 | -0.950 |
| tamper_rotations:principal_axes | ok | 0.349 | 0.801 | 2.115 | 0.787 | 21.138 | 3.758 | 0.570 | -0.275 | -0.253 | -0.950 |
| reference:spmc | ok | 0.572 | 0.660 | 7.676 | 1.103 | 9.320 | 5.674 | 0.480 | -0.403 | -0.376 | -1.129 |
| reference:frs | ok | 0.837 | 0.612 | 166.022 | 0.822 | 0.976 | 3.052 | 0.584 | -1.015 | -0.939 | -1.862 |
| bruteforce:bruteforce_grid | ok | 10.071 | 0.001 | 137.241 | 10.019 | 8.803 | 9.912 | 0.122 | -1.573 | -1.428 | -5.194 |
| shortcuts:public_answer_enumeration | ok | 97.265 | 0.000 | 171.153 | 97.072 | 127.480 | 100.817 | 0.000 | -4.068 | -3.044 | -37.182 |
| baselines:identity | ok | 132.366 | 0.000 | 175.477 | 130.784 | 131.500 | 130.757 | 0.000 | -4.782 | -3.480 | -48.054 |
| shortcuts:read_hidden_seed | ok | 132.366 | 0.000 | 175.477 | 130.784 | 131.500 | 130.757 | 0.000 | -4.782 | -3.480 | -48.054 |
| stale_artifacts:identity | ok | 132.366 | 0.000 | 175.477 | 130.784 | 131.500 | 130.757 | 0.000 | -4.782 | -3.480 | -48.054 |
| tamper_rotations:identity | ok | 132.366 | 0.000 | 175.477 | 130.784 | 131.500 | 130.757 | 0.000 | -4.782 | -3.480 | -48.054 |
| budget:cpu_hog_3s | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -6.020 | -4.234 | -65.308 |
| shortcuts:skip_hard_instances | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -6.020 | -4.234 | -65.308 |
| shortcuts:empty_registry | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -6.020 | -4.234 | -65.308 |
| shortcuts:import_error | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -6.020 | -4.234 | -65.308 |
| shortcuts:nan_matrix | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -6.020 | -4.234 | -65.308 |
| shortcuts:reflection | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -6.020 | -4.234 | -65.308 |
| shortcuts:scaled_identity | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -6.020 | -4.234 | -65.308 |
| shortcuts:wrong_shape | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -6.020 | -4.234 | -65.308 |
| shortcuts:zero_matrix | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -6.020 | -4.234 | -65.308 |
| tamper_template:frs | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -6.020 | -4.234 | -65.308 |
| tamper_template:spmc | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -6.020 | -4.234 | -65.308 |
| tamper_template:spmc_frs | failed | 180.000 | 0.000 | 180.000 | 180.000 | 180.000 | 180.000 | 0.000 | -6.020 | -4.234 | -65.308 |

Reference rerun identical: True
Paired bootstrap: {
 "reference_self_rank_95pct_halfwidth": 0.04889493873995452,
 "reference_self_rank_95pct_halfwidth_honest_sigma": 0.08233812978090754,
 "baselines:identity": {
  "rank_vs_reference": -4.782108583368788,
  "paired_bootstrap_95ci": [
   -4.846447272499525,
   -4.743225514992226
  ],
  "rank_vs_reference_honest_sigma": -48.05414913201739,
  "paired_bootstrap_95ci_honest_sigma": [
   -48.62895476271066,
   -47.646948136429664
  ]
 },
 "baselines:principal_axes": {
  "rank_vs_reference": -0.2752613804362675,
  "paired_bootstrap_95ci": [
   -0.3275070388482786,
   -0.24086218403940557
  ],
  "rank_vs_reference_honest_sigma": -0.9504724468885117,
  "paired_bootstrap_95ci_honest_sigma": [
   -1.0456167308985314,
   -0.8824092989545941
  ]
 },
 "bruteforce:bruteforce_grid": {
  "rank_vs_reference": -1.5725524732264715,
  "paired_bootstrap_95ci": [
   -1.6335833357997216,
   -1.5320805461348177
  ],
  "rank_vs_reference_honest_sigma": -5.1937072643122395,
  "paired_bootstrap_95ci_honest_sigma": [
   -5.358802858063768,
   -5.053404161542174
  ]
 },
 "reference:frs": {
  "rank_vs_reference": -1.0152106779941108,
  "paired_bootstrap_95ci": [
   -1.0730144659070975,
   -0.8789878685710527
  ],
  "rank_vs_reference_honest_sigma": -1.8624274707815431,
  "paired_bootstrap_95ci_honest_sigma": [
   -1.9800913174215637,
   -1.6472308108288938
  ]
 },
 "reference:spmc": {
  "rank_vs_reference": -0.40324818357298486,
  "paired_bootstrap_95ci": [
   -0.4509040186189773,
   -0.371062655791121
  ],
  "rank_vs_reference_honest_sigma": -1.1292774856202232,
  "paired_bootstrap_95ci_honest_sigma": [
   -1.2587082540116934,
   -0.9885797338009403
  ]
 },
 "v_dual_polish:dual_init_frs_polish": {
  "rank_vs_reference": 0.11929961325399231,
  "paired_bootstrap_95ci": [
   0.10540950763160253,
   0.17906564336965056
  ],
  "rank_vs_reference_honest_sigma": 0.33710064559642333,
  "paired_bootstrap_95ci_honest_sigma": [
   0.2979347612669614,
   0.40838285319056666
  ]
 },
 "v_dual:dual_init_frs": {
  "rank_vs_reference": 0.09492175171555241,
  "paired_bootstrap_95ci": [
   0.08281277025530843,
   0.1543295126435449
  ],
  "rank_vs_reference_honest_sigma": 0.21435979924788315,
  "paired_bootstrap_95ci_honest_sigma": [
   0.17831172218729202,
   0.28985457725997943
  ]
 },
 "v_polish:spmc_frs_polish": {
  "rank_vs_reference": 0.09471784731336567,
  "paired_bootstrap_95ci": [
   0.08314138999312676,
   0.10583327169849376
  ],
  "rank_vs_reference_honest_sigma": 0.2637860677535105,
  "paired_bootstrap_95ci_honest_sigma": [
   0.23968823234444686,
   0.2834263776749593
  ]
 },
 "v_refine1440:spmc_frs_refine1440": {
  "rank_vs_reference": -0.24835048474651927,
  "paired_bootstrap_95ci": [
   -0.30199852859876886,
   -0.15758644994360607
  ],
  "rank_vs_reference_honest_sigma": -0.47352154265837143,
  "paired_bootstrap_95ci_honest_sigma": [
   -0.5653640113186541,
   -0.38242931692882665
  ]
 },
 "v_refine720_1440:spmc_frs_refine720_1440": {
  "rank_vs_reference": -0.23919017229174763,
  "paired_bootstrap_95ci": [
   -0.2926992492990917,
   -0.15508322829023224
  ],
  "rank_vs_reference_honest_sigma": -0.4412923247658544,
  "paired_bootstrap_95ci_honest_sigma": [
   -0.5354339852994624,
   -0.3481821763157715
  ]
 }
}
