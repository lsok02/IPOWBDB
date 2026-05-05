from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


UINT64_MASK = 0xFFFFFFFFFFFFFFFF


@dataclass
class MRG32k3a:
    """MRG32k3a random generator (L'Ecuyer)."""

    seed: int = 1

    name: str = "mrg32k3a"

    # states of 2 generators
    s1: List[int] = field(init=False)
    s2: List[int] = field(init=False)

    # stałe (z publikacji)
    m1: int = 4294967087
    m2: int = 4294944443

    a12: int = 1403580
    a13n: int = -810728

    a21: int = 527612
    a23n: int = -1370589

    def __post_init__(self):

        base = self.seed & UINT64_MASK

        self.s1 = [
            (base + 1) % self.m1,
            (base + 2) % self.m1,
            (base + 3) % self.m1,
        ]

        self.s2 = [
            (base + 4) % self.m2,
            (base + 5) % self.m2,
            (base + 6) % self.m2,
        ]

    def _next(self) -> int:


        # first recursion
        p1 = (self.a12 * self.s1[1] + self.a13n * self.s1[0]) % self.m1
        self.s1 = [self.s1[1], self.s1[2], p1]

        # second recursion
        p2 = (self.a21 * self.s2[2] + self.a23n * self.s2[0]) % self.m2
        self.s2 = [self.s2[1], self.s2[2], p2]

        # combination
        x = (p1 - p2) % self.m1

        return x


    def random_uint64(self, size: int) -> List[int]:
        out = []
        while len(out) < size:
            hi = self._next()
            lo = self._next()
            val = ((hi << 32) | lo) & UINT64_MASK
            out.append(val)
        return out

    def random_bytes(self, nbytes: int) -> bytes:
        result = bytearray()
        while len(result) < nbytes:
            x = self._next()
            result.extend(x.to_bytes(4, "little"))
        return bytes(result[:nbytes])

    def random_bits(self, nbits: int) -> List[int]:
        bits = []
        while len(bits) < nbits:
            x = self._next()
            for i in range(32):
                bits.append((x >> i) & 1)
                if len(bits) == nbits:
                    break
        return bits

    def random_floats(self, size: int) -> List[float]:
        floats = []
        for _ in range(size):
            x = self._next()
            floats.append(x / self.m1) 
        return floats