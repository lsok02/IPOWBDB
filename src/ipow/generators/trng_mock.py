"""TRNG-inspired generator using a simulated noisy entropy source."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import time

import numpy as np


@dataclass
class MockTRNG:
    seed: int = 42
    bias: float = 0.52
    correlation: float = 0.10
    block_size: int = 64
    name: str = "MockTRNG"

    def __post_init__(self) -> None:
        self.rng = np.random.default_rng(self.seed)
        self._last = int(self.rng.random() < self.bias)

    def _raw_bit(self) -> int:
        if self.rng.random() < self.correlation:
            return self._last
        bit = int(self.rng.random() < self.bias)
        self._last = bit
        return bit

    def raw_bits(self, nbits: int) -> list[int]:
        return [self._raw_bit() for _ in range(nbits)]

    def _condition(self, bits: list[int]) -> bytes:
        payload = bytes(bits)
        now = time.time_ns().to_bytes(8, "little", signed=False)
        return hashlib.sha256(payload + now).digest()

    def random_bytes(self, nbytes: int) -> bytes:
        out = bytearray()
        while len(out) < nbytes:
            bits = self.raw_bits(self.block_size)
            out.extend(self._condition(bits))
        return bytes(out[:nbytes])

    def random_uint64(self, size: int) -> list[int]:
        raw = self.random_bytes(size * 8)
        return [int.from_bytes(raw[i:i+8], "little") for i in range(0, len(raw), 8)]

    def random_bits(self, nbits: int) -> list[int]:
        raw = self.random_bytes((nbits + 7) // 8)
        bits: list[int] = []
        for b in raw:
            bits.extend((b >> i) & 1 for i in range(8))
        return bits[:nbits]

    def random_floats(self, size: int) -> list[float]:
        return [x / (1 << 64) for x in self.random_uint64(size)]
