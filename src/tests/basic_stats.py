"""Basic descriptive statistics for generator output."""
from __future__ import annotations

from collections import Counter
from typing import Iterable, Any

import numpy as np


def summarize_numeric_sample(values: Iterable[float | int]) -> dict[str, float]:
    arr = np.asarray(list(values), dtype=float)
    return {
        "count": float(arr.size),
        "mean": float(arr.mean()),
        "variance": float(arr.var(ddof=1)) if arr.size > 1 else 0.0,
        "std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def byte_frequencies(data: bytes) -> dict[int, int]:
    return dict(Counter(data))


def bit_balance(bits: Iterable[int]) -> dict[str, float]:
    bit_list = list(bits)
    ones = sum(bit_list)
    zeros = len(bit_list) - ones
    return {
        "count": len(bit_list),
        "zeros": zeros,
        "ones": ones,
        "p_zero": zeros / len(bit_list) if bit_list else 0.0,
        "p_one": ones / len(bit_list) if bit_list else 0.0,
    }


def serial_pairs(bits: Iterable[int]) -> dict[str, int]:
    bit_list = list(bits)
    counts = {"00": 0, "01": 0, "10": 0, "11": 0}
    for a, b in zip(bit_list[:-1], bit_list[1:]):
        counts[f"{a}{b}"] += 1
    return counts
