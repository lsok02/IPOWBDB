"""Wrapper around Python/NumPy Mersenne Twister implementations."""
from __future__ import annotations

from dataclasses import dataclass
import random

import numpy as np


@dataclass
class MT19937Generator:
    seed: int = 42
    use_numpy: bool = True
    name: str = "MT19937"

    def __post_init__(self) -> None:
        if self.use_numpy:
            bitgen = np.random.MT19937(self.seed)
            self.rng = np.random.Generator(bitgen)
        else:
            self.rng = random.Random(self.seed)

    def random_uint64(self, size: int) -> list[int]:
        if self.use_numpy:
            return self.rng.integers(0, 1 << 64, size=size, dtype=np.uint64).tolist()
        return [self.rng.getrandbits(64) for _ in range(size)]

    def random_bytes(self, nbytes: int) -> bytes:
        if self.use_numpy:
            arr = self.rng.integers(0, 256, size=nbytes, dtype=np.uint8)
            return arr.tobytes()
        return bytes(self.rng.getrandbits(8) for _ in range(nbytes))

    def random_bits(self, nbits: int) -> list[int]:
        if self.use_numpy:
            arr = self.rng.integers(0, 2, size=nbits, dtype=np.uint8)
            return arr.tolist()
        return [self.rng.getrandbits(1) for _ in range(nbits)]

    def random_floats(self, size: int) -> list[float]:
        if self.use_numpy:
            return self.rng.random(size=size).tolist()
        return [self.rng.random() for _ in range(size)]
