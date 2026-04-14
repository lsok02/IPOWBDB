from __future__ import annotations

from dataclasses import dataclass


MASK64 = 0xFFFFFFFFFFFFFFFF


@dataclass
class SplitMix64:
    seed: int = 42
    name: str = "SplitMix64"

    def __post_init__(self) -> None:
        self.state = self.seed & MASK64

    # ===== core =====

    def _next_uint64(self) -> int:
        self.state = (self.state + 0x9E3779B97F4A7C15) & MASK64
        z = self.state

        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9 & MASK64
        z = (z ^ (z >> 27)) * 0x94D049BB133111EB & MASK64
        z = z ^ (z >> 31)

        return z & MASK64

    # ===== interface =====

    def random_uint64(self, size: int) -> list[int]:
        return [self._next_uint64() for _ in range(size)]

    def random_bytes(self, nbytes: int) -> bytes:
        out = bytearray()
        while len(out) < nbytes:
            out.extend(self._next_uint64().to_bytes(8, "little"))
        return bytes(out[:nbytes])

    def random_bits(self, nbits: int) -> list[int]:
        bits: list[int] = []
        while len(bits) < nbits:
            value = self._next_uint64()
            for i in range(64):
                bits.append((value >> i) & 1)
                if len(bits) >= nbits:
                    break
        return bits

    def random_floats(self, size: int) -> list[float]:
        return [
            (self._next_uint64() >> 11) * (1.0 / (1 << 53))
            for _ in range(size)
        ]