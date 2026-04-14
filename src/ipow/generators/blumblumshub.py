from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass
class BlumBlumShub:
    seed: int = 42
    name: str = "BlumBlumShub"

    # przykładowe liczby pierwsze (Blum primes: p % 4 == 3)
    p: int = 1000003
    q: int = 1000039

    def __post_init__(self) -> None:
        if self.p % 4 != 3 or self.q % 4 != 3:
            raise ValueError("p and q must be congruent to 3 mod 4")

        self.n = self.p * self.q

        # seed musi być względnie pierwszy z n
        x = self.seed % self.n
        if math.gcd(x, self.n) != 1:
            x += 1

        self.state = (x * x) % self.n  # x0 = seed^2 mod n

    # ===== core =====

    def _next_bit(self) -> int:
        self.state = pow(self.state, 2, self.n)
        return self.state & 1

    def _next_uint64(self) -> int:
        value = 0
        for i in range(64):
            value |= (self._next_bit() << i)
        return value

    # ===== interface =====

    def random_uint64(self, size: int) -> list[int]:
        return [self._next_uint64() for _ in range(size)]

    def random_bytes(self, nbytes: int) -> bytes:
        return bytes(self._next_uint64() & 0xFF for _ in range(nbytes))

    def random_bits(self, nbits: int) -> list[int]:
        return [self._next_bit() for _ in range(nbits)]

    def random_floats(self, size: int) -> list[float]:
        return [
            (self._next_uint64() >> 11) * (1.0 / (1 << 53))
            for _ in range(size)
        ]