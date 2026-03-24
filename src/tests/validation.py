"""High-level orchestration for generator validation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .basic_stats import summarize_numeric_sample, bit_balance, serial_pairs
from .statistical import (
    approximate_entropy_test,
    chi_square_uniform_test,
    kolmogorov_smirnov_uniform_test,
    monobit_test,
    runs_test,
)


@dataclass
class ValidationConfig:
    n_numbers: int = 10_000
    n_bits: int = 20_000
    approx_entropy_block_size: int = 2


def validate_generator(generator: Any, config: ValidationConfig | None = None) -> dict[str, Any]:
    cfg = config or ValidationConfig()
    numbers = generator.random_uint64(cfg.n_numbers)
    floats = generator.random_floats(cfg.n_numbers)
    bits = generator.random_bits(cfg.n_bits)

    return {
        "generator": getattr(generator, "name", generator.__class__.__name__),
        "summary_numbers": summarize_numeric_sample(numbers),
        "summary_floats": summarize_numeric_sample(floats),
        "bit_balance": bit_balance(bits),
        "serial_pairs": serial_pairs(bits),
        "tests": {
            "monobit": monobit_test(bits),
            "runs": runs_test(bits),
            "chi_square_uint64_mod_256": chi_square_uniform_test(numbers, bins=256),
            "ks_uniform_floats": kolmogorov_smirnov_uniform_test(floats),
            "approximate_entropy": approximate_entropy_test(bits, m=cfg.approx_entropy_block_size),
        },
    }
