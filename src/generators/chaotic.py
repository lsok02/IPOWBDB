"""Chaotic-map-based generators."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LogisticMapGenerator:
    x0: float = 0.123456789
    r: float = 3.99
    discard: int = 100
    name: str = "LogisticMap"

    def __post_init__(self) -> None:
        if not (0.0 < self.x0 < 1.0):
            raise ValueError("x0 must be in (0, 1)")
        if not (0.0 < self.r <= 4.0):
            raise ValueError("r must be in (0, 4]")
        self.x = self.x0
        for _ in range(self.discard):
            self._step()

    def _step(self) -> float:
        self.x = self.r * self.x * (1.0 - self.x)
        return self.x

    def random_bits(self, nbits: int) -> list[int]:
        return [1 if self._step() >= 0.5 else 0 for _ in range(nbits)]

    def random_bytes(self, nbytes: int) -> bytes:
        bits = self.random_bits(nbytes * 8)
        out = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j, bit in enumerate(bits[i:i+8]):
                byte |= (bit & 1) << j
            out.append(byte)
        return bytes(out)

    def random_uint64(self, size: int) -> list[int]:
        raw = self.random_bytes(size * 8)
        return [int.from_bytes(raw[i:i+8], "little") for i in range(0, len(raw), 8)]

    def random_floats(self, size: int) -> list[float]:
        return [self._step() for _ in range(size)]
