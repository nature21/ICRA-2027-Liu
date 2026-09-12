"""Analyze RAPID versus RAPID w/o SV without conflating scenes and training runs.

Run with: python analysis/table_ii/analyze.py
Requires NumPy and SciPy. No paper files are modified.
"""

import json
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.stats import binomtest, ttest_1samp, ttest_ind


HERE = Path(__file__).resolve().parent
EXPECTED_RAPID = [
    [43, 50, 47], [42, 44, 41], [33, 37, 35], [34, 40, 44],
    [39, 40, 40], [48, 47, 26], [30, 33, 30], [30, 26, 32],
]
EXPECTED_WO_SV = [
    [46, 47, 47], [35, 50, 40], [12, 17, 31], [36, 0, 30],
    [40, 17, 10], [24, 17, 44], [0, 0, 44], [21, 29, 1],
]


def binary_matrix(runs, expected):
    assert len(runs) == 3
    matrix = np.zeros((3, 50), dtype=int)
    for r, ids in enumerate(runs):
        assert len(ids) == expected[r]
        assert len(set(ids)) == len(ids)
        assert all(1 <= case <= 50 for case in ids)
        matrix[r, np.asarray(ids, dtype=int) - 1] = 1
    np.testing.assert_array_equal(matrix.sum(axis=1), expected)
    return matrix


def holm(pvalues):
    pvalues = np.asarray(pvalues)
    order = np.argsort(pvalues)
    result = np.empty(len(pvalues))
    result[order] = np.minimum(
        1, np.maximum.accumulate(pvalues[order] * np.arange(len(pvalues), 0, -1))
    )
    return result


def seed_permutation(a_counts, b_counts):
    # Integers avoid floating-point ambiguity when counting tied statistics.
    pooled = np.concatenate([a_counts, b_counts])
    observed = int(a_counts.sum() - b_counts.sum())
    differences = [
        2 * int(pooled[list(indices)].sum()) - int(pooled.sum())
        for indices in combinations(range(6), 3)
    ]
    assert len(differences) == 20
    return sum(value >= observed for value in differences) / 20


def main():
    raw = json.loads((HERE / 'raw_success_cases.json').read_text())
    results = []
    for current, original in enumerate(raw['current_task_order'], start=1):
        i = original - 1
        a = binary_matrix(raw['rapid_success_ids'][i], EXPECTED_RAPID[i])
        b = binary_matrix(raw['wo_sv_success_ids'][i], EXPECTED_WO_SV[i])
        a_rates, b_rates = a.mean(axis=1), b.mean(axis=1)
        # A scene is counted once after averaging the three fixed programs.
        scene_count_difference = a.sum(axis=0) - b.sum(axis=0)
        d = scene_count_difference / 3
        wins = int(np.sum(scene_count_difference > 0))
        ties = int(np.sum(scene_count_difference == 0))
        losses = int(np.sum(scene_count_difference < 0))
        assert wins + ties + losses == 50
        np.testing.assert_allclose(d.mean(), a_rates.mean() - b_rates.mean(), atol=1e-14)
        results.append({
            'current_task': current,
            'original_task': original,
            'rapid_replicate_ids': raw['replicates_rapid'][i],
            'wo_sv_replicate_ids': raw['replicates_wo_sv'],
            'rapid_success_counts': a.sum(axis=1).tolist(),
            'wo_sv_success_counts': b.sum(axis=1).tolist(),
            'rapid_mean': float(a_rates.mean()),
            'wo_sv_mean': float(b_rates.mean()),
            'rapid_std_ddof0': float(a_rates.std(ddof=0)),
            'wo_sv_std_ddof0': float(b_rates.std(ddof=0)),
            'difference_percentage_points': float(100 * d.mean()),
            'scene_wins_ties_losses': [wins, ties, losses],
            'seed_welch_one_sided_p': float(ttest_ind(
                a_rates, b_rates, equal_var=False, alternative='greater'
            ).pvalue),
            'seed_permutation_one_sided_p': seed_permutation(a.sum(axis=1), b.sum(axis=1)),
            'conditional_scene_paired_t_one_sided_p': float(ttest_1samp(
                d, 0, alternative='greater'
            ).pvalue),
            'conditional_scene_sign_one_sided_p': float(binomtest(
                wins, wins + losses, 0.5, alternative='greater'
            ).pvalue) if wins + losses else 1.0,
        })
    pkeys = [key for key in results[0] if key.endswith('_p')]
    for key in pkeys:
        adjusted = holm([row[key] for row in results])
        for row, value in zip(results, adjusted):
            row[key + '_holm'] = float(value)
    (HERE / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    report = [
        '# RAPID versus RAPID w/o SV: exploratory analysis',
        '',
        'All 48 supplied runs were checked against their success counts. Each run contains '
        '50 completed tests. Task numbers below use the current order (original 1,2,3,4,5,8,6,7). '
        'Replicate IDs are preserved; the user corrected old Task 7 experiment 003 to replicate 3. '
        'Its identical outcomes to replicate 1 are retained. The user instructs treating the supplied '
        'runs as independent, with omitted replicate numbers used for debugging.',
        '',
        '## What the tests answer',
        '',
        '- **Training-run Welch test:** compares mean performance over independent training runs '
        'on the fixed 50-scene benchmark. Each group has n=3. Sample SD is computed directly '
        'from raw run scores with ddof=1; reported table SD uses ddof=0. The t approximation '
        'is difficult to justify with three runs and strongly uneven scores. These p-values '
        'are exploratory and conditional on this benchmark.',
        '- **Training-run exact permutation sensitivity check:** permutes six whole training '
        'runs between two groups of three (20 allocations), using the mean difference. Exactness '
        'requires exchangeability under the same-distribution null. This is stronger than merely '
        'equal means with different variances. Individual scene observations are never permuted '
        'as if they were independent training runs.',
        '- **Conditional paired-scene t test:** fixes the three observed programs per method, '
        'averages their binary outcomes within each scene, and compares the 50 paired scene '
        'scores. It concerns mean scene performance for these fixed programs, assumes independent '
        'representative scenes and a suitable approximation for the mean difference, and does '
        'not include uncertainty from retraining.',
        '- **Conditional exact scene sign test:** compares the two methods\' success counts '
        '(0 to 3) within each scene. Ties are excluded. Under equal probabilities of a scene win '
        'and loss, wins follow Binomial(wins + losses, 0.5). This tests a scene-win probability '
        'for the fixed supplied programs, not equality of population mean success rates over '
        'new training runs. It requires independent representative scenes. A fixed, curated '
        'benchmark by itself does not guarantee this sampling assumption.',
        '',
        'All tests are one-sided in the direction RAPID > w/o SV. Holm corrections are applied '
        'separately to each test\'s family of eight tasks. They do not account for choosing among '
        'tests, directions or thresholds after seeing results. These analyses were discussed '
        'after viewing the data and should be described as exploratory.',
        '',
        '## Results',
        '',
        '| Task | Original task | Gain (pp) | Scene wins/ties/losses | Seed Welch p | Seed permutation p | Conditional scene paired-t p | Conditional scene sign p | Conditional scene sign Holm p |',
        '|---|---|---:|---|---:|---:|---:|---:|---:|',
    ]
    for r in results:
        wtl = '/'.join(map(str, r['scene_wins_ties_losses']))
        report.append(
            f"| {r['current_task']} | {r['original_task']} | {r['difference_percentage_points']:.2f} | {wtl} "
            f"| {r['seed_welch_one_sided_p']:.6g} | {r['seed_permutation_one_sided_p']:.2f} "
            f"| {r['conditional_scene_paired_t_one_sided_p']:.6g} "
            f"| {r['conditional_scene_sign_one_sided_p']:.6g} "
            f"| {r['conditional_scene_sign_one_sided_p_holm']:.6g} |"
        )
    report += [
        '',
        'At the conventional 0.05 threshold, conditional scene analyses identify Tasks 3-8 '
        'even after their eight-task Holm corrections. This supports a conditional scene-level '
        'advantage for the supplied programs, subject to the scene sampling assumptions. '
        'It does not establish a significant training-algorithm advantage over new seeds. '
        'The seed-level Welch tests all have unadjusted p > 0.05. Neither seed-level method '
        'has any task with Holm-adjusted p <= 0.05.',
        '',
        'Paper data and bold formatting were not changed by this analysis.',
        '',
        '## Method references',
        '',
        '- [Welch test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html)',
        '- [Exact permutation assumptions](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html)',
        '- [Paired t test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html)',
        '- [Exact binomial test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html)',
    ]
    (HERE / 'results.md').write_text('\n'.join(report) + '\n')
    print('\n'.join(report[report.index('## Results'):]))


if __name__ == '__main__':
    main()
