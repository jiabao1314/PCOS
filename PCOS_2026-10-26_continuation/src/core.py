"""Pure calculations. Rates are per 100,000 females unless stated otherwise."""
from itertools import permutations, combinations
import numpy as np


def standardize(rates, weights):
    rates, weights = np.asarray(rates, float), np.asarray(weights, float)
    if rates.shape != weights.shape or np.any(weights <= 0) or not np.all(np.isfinite(rates)):
        raise ValueError("Invalid rates or standard weights")
    return float(np.dot(rates, weights / weights.sum()))


def pooled_rate(numbers, populations):
    numbers, populations = np.asarray(numbers, float), np.asarray(populations, float)
    if numbers.shape != populations.shape or np.any(populations <= 0):
        raise ValueError("Invalid pooled denominator")
    return float(numbers.sum() / populations.sum() * 100000)


def shapley(pop0, pop1, p0, p1):
    """Symmetric three-factor decomposition; p is a proportion, never an ASR."""
    pop0, pop1, p0, p1 = [np.asarray(x, float) for x in (pop0, pop1, p0, p1)]
    if len({x.shape for x in (pop0, pop1, p0, p1)}) != 1:
        raise ValueError("Age arrays must align")
    if np.any(pop0 <= 0) or np.any(pop1 <= 0):
        raise ValueError("Population must be positive")
    start = [pop0.sum(), pop0 / pop0.sum(), p0]
    end = [pop1.sum(), pop1 / pop1.sum(), p1]
    def burden(state):
        return state[0] * np.dot(state[1], state[2])
    values = np.zeros(3)
    for order in permutations(range(3)):
        state = start.copy()
        for i in order:
            before = burden(state)
            state[i] = end[i]
            values[i] += (burden(state) - before) / 6
    change = burden(end) - burden(start)
    if not np.isclose(values.sum(), change, atol=1e-7, rtol=1e-10):
        raise ArithmeticError("Decomposition failed additivity")
    return dict(zip(["population_size", "age_composition", "age_specific_prevalence"], values)), change


def segmented_trend(years, rates, max_knots=2, min_segment=5):
    """Continuous grid-search log-linear segments, BIC selection, point estimates.

    This is a transparent segmented regression implementation, not the NCI
    permutation-test software. BIC counts estimated knot locations as parameters.
    Conditional AR(1) sensitivity and formal intervals remain separate modules.
    """
    x, r = np.asarray(years, int), np.asarray(rates, float)
    if np.any(r <= 0) or not np.all(np.isfinite(r)) or np.any(np.diff(x) != 1):
        raise ValueError("Trend needs consecutive years and positive finite rates")
    y, t = np.log(r), x - x[0]
    best = None
    for k in range(max_knots + 1):
        for knots in combinations(x[1:-1], k):
            boundaries = [x[0], *knots, x[-1]]
            if any(b - a + 1 < min_segment for a, b in zip(boundaries[:-1], boundaries[1:])):
                continue
            X = np.column_stack([np.ones(len(x)), t, *[np.maximum(x - v, 0) for v in knots]])
            beta = np.linalg.lstsq(X, y, rcond=None)[0]
            residual = y - X @ beta
            sse = float(residual @ residual)
            # Exact or nearly exact curves must not select knots from rounding noise.
            variance_floor = (np.finfo(float).eps * max(1.0, np.max(np.abs(y))) * 100)**2
            bic = len(x) * np.log(max(sse / len(x), variance_floor)) + (2 + 2*k) * np.log(len(x))
            if best is None or bic < best["bic"]:
                slopes = np.cumsum([beta[1], *beta[2:]])
                durations = np.diff(boundaries)
                mean_slope = np.dot(slopes, durations) / (x[-1] - x[0])
                rho = float(np.corrcoef(residual[1:], residual[:-1])[0, 1]) if sse > 1e-20 else None
                best = {"knots": [int(v) for v in knots], "bic": float(bic),
                        "segments": [{"start": int(a), "end": int(b), "apc_percent": float(100*np.expm1(s))}
                                     for a,b,s in zip(boundaries[:-1], boundaries[1:], slopes)],
                        "aapc_percent": float(100*np.expm1(mean_slope)), "residual_lag1": rho,
                        "intervals": "Not estimated: point-estimate trend only"}
    if best is None:
        raise ValueError("Insufficient years for minimum segment size")
    return best
