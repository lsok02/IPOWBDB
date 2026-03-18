"""System-backed cryptographic generators."""
from __future__ import annotations

from dataclasses import dataclass
import os
import secrets


@dataclass
class SystemCSPRNG:
    """System randomness via os.urandom or secrets.SystemRandom."""

    mode: str = "os.urandom"
    name: str = "SystemCSPRNG"

    def __post_init__(self) -> None:
        self._sysrand = secrets.SystemRandom()

    def random_uint64(self, size: int) -> list[int]:
        if self.mode == "secrets":
            return [self._sysrand.getrandbits(64) for _ in range(size)]
        raw = self.random_bytes(size * 8)
        return [int.from_bytes(raw[i:i+8], "little") for i in range(0, len(raw), 8)]

    def random_bytes(self, nbytes: int) -> bytes:
        return os.urandom(nbytes)

    def random_bits(self, nbits: int) -> list[int]:
        nbytes = (nbits + 7) // 8
        raw = self.random_bytes(nbytes)
        bits: list[int] = []
        for b in raw:
            bits.extend((b >> i) & 1 for i in range(8))
        return bits[:nbits]

    def random_floats(self, size: int) -> list[float]:
        return [x / (1 << 64) for x in self.random_uint64(size)]
