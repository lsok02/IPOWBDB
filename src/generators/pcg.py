"""Wrapper around NumPy PCG64 bit generator."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class PCG64Generator:
    seed: int = 42
    name: str = "PCG64"

    def __post_init__(self) -> None:
        self.rng = np.random.Generator(np.random.PCG64(self.seed))

    def random_uint64(self, size: int) -> list[int]:
        return self.rng.integers(0, 1 << 64, size=size, dtype=np.uint64).tolist()

    def random_bytes(self, nbytes: int) -> bytes:
        arr = self.rng.integers(0, 256, size=nbytes, dtype=np.uint8)
        return arr.tobytes()

    def random_bits(self, nbits: int) -> list[int]:
        arr = self.rng.integers(0, 2, size=nbits, dtype=np.uint8)
        return arr.tolist()

    def random_floats(self, size: int) -> list[float]:
        return self.rng.random(size=size).tolist()
