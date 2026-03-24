"""Statistical validation tests used directly in the notebook."""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np
from scipy import stats


def monobit_test(bits: Iterable[int]) -> dict[str, float | bool]:
    bit_array = np.asarray(list(bits), dtype=int)
    n = bit_array.size
    s_obs = abs(np.sum(2 * bit_array - 1)) / math.sqrt(n)
    p_value = math.erfc(s_obs / math.sqrt(2.0))
    return {"statistic": float(s_obs), "p_value": float(p_value), "pass": bool(p_value >= 0.01)}


def runs_test(bits: Iterable[int]) -> dict[str, float | bool]:
    bit_array = np.asarray(list(bits), dtype=int)
    n = bit_array.size
    pi = bit_array.mean()
    tau = 2.0 / math.sqrt(n)
    if abs(pi - 0.5) >= tau:
        return {"statistic": float("nan"), "p_value": 0.0, "pass": False}
    runs = 1 + np.sum(bit_array[1:] != bit_array[:-1])
    numerator = abs(runs - 2 * n * pi * (1 - pi))
    denominator = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    p_value = math.erfc(numerator / denominator)
    return {"statistic": float(runs), "p_value": float(p_value), "pass": bool(p_value >= 0.01)}


def chi_square_uniform_test(values: Iterable[int], bins: int = 256) -> dict[str, float | bool]:
    arr = np.asarray(list(values), dtype=np.uint64)
    reduced = arr % bins
    observed = np.bincount(reduced, minlength=bins)
    expected = np.full(bins, arr.size / bins)
    statistic, p_value = stats.chisquare(observed, expected)
    return {"statistic": float(statistic), "p_value": float(p_value), "pass": bool(p_value >= 0.01)}


def kolmogorov_smirnov_uniform_test(values: Iterable[float]) -> dict[str, float | bool]:
    arr = np.asarray(list(values), dtype=float)
    statistic, p_value = stats.kstest(arr, "uniform", args=(0, 1))
    return {"statistic": float(statistic), "p_value": float(p_value), "pass": bool(p_value >= 0.01)}


def approximate_entropy_test(bits: Iterable[int], m: int = 2) -> dict[str, float | bool]:
    bit_array = np.asarray(list(bits), dtype=int)
    n = bit_array.size
    if n < (m + 1) * 10:
        raise ValueError("Sample too small for approximate entropy test")

    def _phi(mm: int) -> float:
        extended = np.concatenate([bit_array, bit_array[:mm - 1]])
        counts = np.zeros(2 ** mm, dtype=int)
        for i in range(n):
            block = extended[i : i + mm]
            idx = 0
            for bit in block:
                idx = (idx << 1) | int(bit)
            counts[idx] += 1
        probs = counts[counts > 0] / n
        return float(np.sum(probs * np.log(probs)))

    phi_m = _phi(m)
    phi_m1 = _phi(m + 1)
    ap_en = phi_m - phi_m1
    chi_sq = 2.0 * n * (math.log(2) - ap_en)
    p_value = stats.chi2.sf(chi_sq, 2 ** (m - 1))
    return {"statistic": float(chi_sq), "p_value": float(p_value), "pass": bool(p_value >= 0.01)}
