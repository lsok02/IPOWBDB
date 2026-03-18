"""Linear Congruential Generator implementation."""
from __future__ import annotations

from dataclasses import dataclass

MASK64 = (1 << 64) - 1


@dataclass
class LCGGenerator:
    """Classic LCG.

    Parameters default to a well-known 64-bit PCG-style multiplier/increment pair,
    but without the PCG output permutation.
    """

    seed: int = 42
    a: int = 6364136223846793005
    c: int = 1442695040888963407
    m: int = 1 << 64
    name: str = "LCG"

    def __post_init__(self) -> None:
        self.state = self.seed % self.m

    def _next(self) -> int:
        self.state = (self.a * self.state + self.c) % self.m
        return self.state

    def random_uint64(self, size: int) -> list[int]:
        return [self._next() & MASK64 for _ in range(size)]

    def random_bytes(self, nbytes: int) -> bytes:
        out = bytearray()
        while len(out) < nbytes:
            out.extend(self._next().to_bytes(8, "little", signed=False))
        return bytes(out[:nbytes])

    def random_bits(self, nbits: int) -> list[int]:
        bits: list[int] = []
        while len(bits) < nbits:
            value = self._next()
            bits.extend((value >> i) & 1 for i in range(64))
        return bits[:nbits]

    def random_floats(self, size: int) -> list[float]:
        return [self._next() / self.m for _ in range(size)]
