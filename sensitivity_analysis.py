"""
DLMAI sensitivity & validation layer — Layer 5 (framework Section 5.4).

A composite index has no ground truth to check "accuracy" against the way
a predictive model does -- the validation that's actually possible is
asking how much the RESULT depends on judgment calls that could
reasonably have gone differently. This module stress-tests the one
judgment call with the most documented uncertainty in the whole
methodology: the AHP pillar weights (built from this project's own
domain reasoning, explicitly NOT from a real expert panel -- see
ahp_pillar_weights.py and Section 5.2 of the framework doc).

Method: randomly jitter the 7 pillar weights thousands of times
(log-normal multiplicative noise, renormalized to sum to 1 each draw),
recompute composite scores under each perturbed weighting using the SAME
already-computed pillar scores (entropy weights and normalization don't
change -- only the pillar-level AHP weights are being stress-tested), and
check two things across all the draws:
  1. Spearman rank correlation between the perturbed ranking and the base
     ranking -- a low correlation means small, plausible changes to the
     weights are enough to scramble the ranking, which means the ranking
     isn't actually decisive evidence, however confident the final number
     looks.
  2. Per-district rank volatility (mean/std/min/max rank across all
     draws) -- this identifies WHICH specific districts have a fragile
     rank (usually ones clustered tightly with a neighbor) versus which
     ones are robust leaders or laggards regardless of how the weights
     are argued.

No scipy dependency -- Spearman correlation (with proper tie handling) is
implemented directly, consistent with the rest of this project's approach
of using plain Python rather than pulling in a statistics library for one
formula.
"""

import math
import random


def rankdata(values: list) -> list:
    """
    Ascending ranks (1 = smallest value), ties given the AVERAGE of their
    tied positions -- mirrors the standard 'average' tie-breaking method
    used by Spearman correlation, without depending on scipy.
    """
    n = len(values)
    order = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg_rank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    return ranks


def spearman_correlation(scores_a: dict, scores_b: dict, codes: list) -> float:
    """scores_a, scores_b: {lgd_code: score}. Returns Spearman's rho over `codes`."""
    a = [scores_a[c] for c in codes]
    b = [scores_b[c] for c in codes]
    rank_a, rank_b = rankdata(a), rankdata(b)
    n = len(codes)
    mean_a, mean_b = sum(rank_a) / n, sum(rank_b) / n
    cov = sum((rank_a[i] - mean_a) * (rank_b[i] - mean_b) for i in range(n))
    std_a = math.sqrt(sum((x - mean_a) ** 2 for x in rank_a))
    std_b = math.sqrt(sum((x - mean_b) ** 2 for x in rank_b))
    if std_a == 0 or std_b == 0:
        return 1.0   # no variance in one of the rankings -- degenerate, treat as perfectly correlated
    return cov / (std_a * std_b)


def perturb_weights(base_weights: dict, sigma: float, rng: random.Random) -> dict:
    """
    Log-normal multiplicative jitter on each pillar weight, renormalized
    to sum to 1. sigma is the log-space standard deviation -- sigma=0.15
    means a typical draw is roughly +/-15% relative to the base weight,
    with occasional larger swings, and weights can never go negative
    (unlike additive Gaussian noise, which would need clamping).
    """
    jittered = {p: w * math.exp(rng.gauss(0, sigma)) for p, w in base_weights.items()}
    total = sum(jittered.values())
    return {p: w / total for p, w in jittered.items()}


def composite_from_weights(pillar_scores_by_district: dict, weights: dict, codes: list) -> dict:
    """
    pillar_scores_by_district: {lgd_code: {pillar_id: score}} -- NOTE: a
        district with a per-district total data desert in one pillar
        (scoring_engine.py's score_districts()) simply omits that pillar's
        KEY from its dict entirely, it does not include it with a None
        value. This function has to handle that, not assume every
        district has every key in `weights`.
    weights: {pillar_id: weight}, assumed to sum to ~1 over the FULL
        pillar set -- which may be more pillars than a specific district
        actually has.
    Returns {lgd_code: composite_score} via the same geometric-mean
    aggregation scoring_engine.py uses for the base case, with the same
    coverage-aware renormalization: a district missing one pillar has its
    weights renormalized among whichever pillars it actually has, rather
    than crashing on a missing key or silently treating the missing
    pillar as a zero.

    Caught by external code review: the previous version assumed every
    district in pillar_scores_by_district had every key present in
    weights, and raised a bare KeyError otherwise -- which would have
    crashed an entire Monte Carlo run (thousands of iterations) over a
    single district's single missing pillar.
    """
    # Import here to avoid circular dependency at module level
    from scoring_engine import VALUE_DRIVER_PILLARS, VALUE_DAMPENER_PILLAR, W5_DAMPENER, AHP_PILLAR_WEIGHTS
    out = {}
    for code in codes:
        available = pillar_scores_by_district[code]
        usable_drivers = [p for p in VALUE_DRIVER_PILLARS if p in available]
        has_dampener = VALUE_DAMPENER_PILLAR in available

        if not usable_drivers:
            out[code] = None
            continue

        # Apply the same image formula as score_districts():
        # renormalized arithmetic sum of driver pillars, minus dampener penalty
        driver_w_sum = sum(weights.get(p, AHP_PILLAR_WEIGHTS.get(p, 0)) for p in usable_drivers)
        if driver_w_sum == 0:
            out[code] = None
            continue
        driver_score = sum(
            (weights.get(p, AHP_PILLAR_WEIGHTS.get(p, 0)) / driver_w_sum) * available[p]
            for p in usable_drivers
        )
        dampener_score = W5_DAMPENER * available[VALUE_DAMPENER_PILLAR] if has_dampener else 0.0
        out[code] = max(0.0, min(100.0, driver_score - dampener_score))
    return out


def run_monte_carlo(pillar_scores_by_district: dict, base_weights: dict, codes: list,
                     n_iterations: int = 3000, sigma: float = 0.15, seed: int = 42) -> dict:
    rng = random.Random(seed)
    base_composite = composite_from_weights(pillar_scores_by_district, base_weights, codes)

    # A district with a total data desert (zero usable pillars at all --
    # see composite_from_weights) gets None here. There's no score to
    # rank, so it's excluded from the sensitivity analysis entirely
    # rather than crashing the whole run -- tracked explicitly so this
    # exclusion is visible, not a silent drop.
    excluded_no_data = [c for c in codes if base_composite[c] is None]
    scoreable_codes = [c for c in codes if base_composite[c] is not None]

    base_ranking = sorted(scoreable_codes, key=lambda c: -base_composite[c])
    base_rank_of = {code: i + 1 for i, code in enumerate(base_ranking)}
    base_top1 = base_ranking[0] if base_ranking else None

    correlations = []
    rank_samples = {code: [] for code in scoreable_codes}
    top1_matches = 0

    for _ in range(n_iterations):
        w = perturb_weights(base_weights, sigma, rng)
        composite = composite_from_weights(pillar_scores_by_district, w, scoreable_codes)
        correlations.append(spearman_correlation(base_composite, composite, scoreable_codes))

        # rank 1 = highest score: rank ascending order of NEGATIVE score
        neg_scores = [-composite[c] for c in scoreable_codes]
        ranks = rankdata(neg_scores)
        for i, code in enumerate(scoreable_codes):
            rank_samples[code].append(ranks[i])

        if base_top1 is not None and max(scoreable_codes, key=lambda c: composite[c]) == base_top1:
            top1_matches += 1

    correlations.sort()
    n = len(correlations)
    rank_stats = {}
    for code in scoreable_codes:
        samples = rank_samples[code]
        m = len(samples)
        mean_r = sum(samples) / m
        var = sum((x - mean_r) ** 2 for x in samples) / m
        rank_stats[code] = {
            "base_rank": base_rank_of[code],
            "mean_rank": round(mean_r, 2),
            "std_rank": round(math.sqrt(var), 2),
            "min_rank": min(samples),
            "max_rank": max(samples),
        }

    return {
        "n_iterations": n_iterations, "sigma": sigma,
        "excluded_no_data": excluded_no_data,
        "mean_correlation": sum(correlations) / n,
        "p5_correlation": correlations[int(0.05 * n)],     # 5th percentile -- "worst case" robustness
        "min_correlation": correlations[0],
        "top1_stability_pct": round(100 * top1_matches / n_iterations, 1),
        "rank_stats": rank_stats,
        "base_composite": base_composite,
        "base_ranking": base_ranking,
    }
