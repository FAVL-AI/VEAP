"""X1 statistics (pre-registration v3): scenario-clustered bootstrap (M1) and descriptive Wilson CIs."""
from __future__ import annotations
import math
import random
from typing import Callable, Sequence


def clustered_bootstrap(clusters: dict[str, Sequence[float]], stat: Callable[[list[float]], float] | None = None,
                        resamples: int = 10_000, seed: int = 0, alpha: float = 0.05) -> dict:
    """Resample scenarios with replacement, then seeds within each resampled scenario with replacement.

    ``clusters`` maps scenario id -> per-seed values. Returns the point estimate on the pooled data and
    the percentile (1-alpha) CI. Default statistic is the pooled mean.
    """
    stat = stat or (lambda v: sum(v) / len(v))
    keys = sorted(clusters)
    if not keys or any(len(clusters[k]) == 0 for k in keys):
        raise ValueError("every cluster needs at least one value")
    rng = random.Random(seed)
    pooled = [v for k in keys for v in clusters[k]]
    draws = []
    for _ in range(resamples):
        sample: list[float] = []
        for _ in keys:
            vals = clusters[keys[rng.randrange(len(keys))]]
            sample.extend(vals[rng.randrange(len(vals))] for _ in vals)
        draws.append(stat(sample))
    draws.sort()
    lo = draws[int(math.floor((alpha / 2) * resamples))]
    hi = draws[min(resamples - 1, int(math.ceil((1 - alpha / 2) * resamples)) - 1)]
    return {"estimate": stat(pooled), "ci_low": lo, "ci_high": hi, "resamples": resamples, "seed": seed,
            "n_clusters": len(keys), "n_units": len(pooled), "method": "scenario-clustered percentile bootstrap"}


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Descriptive only (per-scenario), per v3 step 4."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))
