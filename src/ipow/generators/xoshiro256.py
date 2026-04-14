from __future__ import annotations

from dataclasses import dataclass


MASK64 = 0xFFFFFFFFFFFFFFFF


def _rotl(x: int, k: int) -> int:
    return ((x << k) | (x >> (64 - k))) & MASK64


def _splitmix64(seed: int) -> list[int]:
    """Generate 4 uint64 values from a single seed."""
    result = []
    x = seed & MASK64

    for _ in range(4):
        x = (x + 0x9E3779B97F4A7C15) & MASK64
        z = x
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9 & MASK64
        z = (z ^ (z >> 27)) * 0x94D049BB133111EB & MASK64
        z = z ^ (z >> 31)
        result.append(z & MASK64)

    return result


@dataclass
class Xoshiro256StarStar:
    seed: int = 42
    name: str = "Xoshiro256**"

    def __post_init__(self) -> None:
        self.state = _splitmix64(self.seed)

    # ===== core =====

    def _next_uint64(self) -> int:
        s0, s1, s2, s3 = self.state

        result = _rotl((s1 * 5) & MASK64, 7)
        result = (result * 9) & MASK64

        t = (s1 << 17) & MASK64

        s2 ^= s0
        s3 ^= s1
        s1 ^= s2
        s0 ^= s3

        s2 ^= t
        s3 = _rotl(s3, 45)

        self.state = [s0, s1, s2, s3]

        return result

    # ===== interface (like MT19937Generator) =====

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