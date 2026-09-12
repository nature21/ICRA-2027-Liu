# RAPID versus RAPID w/o SV: exploratory analysis

All 48 supplied runs were checked against their success counts. Each run contains 50 completed tests. Task numbers below use the current order (original 1,2,3,4,5,8,6,7). Replicate IDs are preserved; the user corrected old Task 7 experiment 003 to replicate 3. Its identical outcomes to replicate 1 are retained. The user instructs treating the supplied runs as independent, with omitted replicate numbers used for debugging.

## What the tests answer

- **Training-run Welch test:** compares mean performance over independent training runs on the fixed 50-scene benchmark. Each group has n=3. Sample SD is computed directly from raw run scores with ddof=1; reported table SD uses ddof=0. The t approximation is difficult to justify with three runs and strongly uneven scores. These p-values are exploratory and conditional on this benchmark.
- **Training-run exact permutation sensitivity check:** permutes six whole training runs between two groups of three (20 allocations), using the mean difference. Exactness requires exchangeability under the same-distribution null. This is stronger than merely equal means with different variances. Individual scene observations are never permuted as if they were independent training runs.
- **Conditional paired-scene t test:** fixes the three observed programs per method, averages their binary outcomes within each scene, and compares the 50 paired scene scores. It concerns mean scene performance for these fixed programs, assumes independent representative scenes and a suitable approximation for the mean difference, and does not include uncertainty from retraining.
- **Conditional exact scene sign test:** compares the two methods' success counts (0 to 3) within each scene. Ties are excluded. Under equal probabilities of a scene win and loss, wins follow Binomial(wins + losses, 0.5). This tests a scene-win probability for the fixed supplied programs, not equality of population mean success rates over new training runs. It requires independent representative scenes. A fixed, curated benchmark by itself does not guarantee this sampling assumption.

All tests are one-sided in the direction RAPID > w/o SV. Holm corrections are applied separately to each test's family of eight tasks. They do not account for choosing among tests, directions or thresholds after seeing results. These analyses were discussed after viewing the data and should be described as exploratory.

## Results

| Task | Original task | Gain (pp) | Scene wins/ties/losses | Seed Welch p | Seed permutation p | Conditional scene paired-t p | Conditional scene sign p | Conditional scene sign Holm p |
|---|---|---:|---|---:|---:|---:|---:|---:|
| 1 | 1 | 0.00 | 8/33/9 | 0.5 | 0.65 | 0.5 | 0.685471 | 0.711071 |
| 2 | 2 | 1.33 | 16/21/13 | 0.447422 | 0.45 | 0.397918 | 0.355536 | 0.711071 |
| 3 | 3 | 30.00 | 31/17/2 | 0.0566659 | 0.05 | 6.0116e-09 | 6.54254e-08 | 3.92552e-07 |
| 4 | 4 | 34.67 | 38/8/4 | 0.12825 | 0.10 | 3.97339e-10 | 2.82657e-08 | 1.9786e-07 |
| 5 | 5 | 34.67 | 37/10/3 | 0.0978734 | 0.20 | 3.97339e-10 | 9.7325e-09 | 7.786e-08 |
| 6 | 8 | 24.67 | 30/14/6 | 0.1373 | 0.10 | 3.84045e-06 | 3.48008e-05 | 0.000104403 |
| 7 | 6 | 24.00 | 30/17/3 | 0.165043 | 0.10 | 4.33639e-07 | 7.00587e-07 | 3.50294e-06 |
| 8 | 7 | 32.67 | 30/15/5 | 0.190654 | 0.20 | 5.51451e-08 | 1.11808e-05 | 4.4723e-05 |

At the conventional 0.05 threshold, conditional scene analyses identify Tasks 3-8 even after their eight-task Holm corrections. This supports a conditional scene-level advantage for the supplied programs, subject to the scene sampling assumptions. It does not establish a significant training-algorithm advantage over new seeds. The seed-level Welch tests all have unadjusted p > 0.05. Neither seed-level method has any task with Holm-adjusted p <= 0.05.

Paper data and bold formatting were not changed by this analysis.

## Method references

- [Welch test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html)
- [Exact permutation assumptions](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html)
- [Paired t test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html)
- [Exact binomial test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html)
