from __future__ import annotations

from dataclasses import dataclass
from typing import List


UINT64_MASK = 0xFFFFFFFFFFFFFFFF


def _rotl(x: int, k: int) -> int:
    return ((x << k) & UINT64_MASK) | (x >> (64 - k))


@dataclass
class Threefry:
    """Threefry2x64-20 random generator."""

    seed: int = 0

    name: str = "threefry2x64-20"

    def __post_init__(self):
        self.counter = [0, 0]  # 2x64-bit
        self.key = [
            self.seed & UINT64_MASK,
            (self.seed >> 64) & UINT64_MASK,
        ]

        self.ks = [
            self.key[0],
            self.key[1],
            (self.key[0] ^ self.key[1] ^ 0x1BD11BDAA9FC1A22) & UINT64_MASK,
        ]


    def _generate_block(self) -> list[int]:
        x0, x1 = self.counter
        ks = self.ks


        ROT = [16, 42, 12, 31, 16, 32, 24, 21]

        # initial key injection
        x0 = (x0 + ks[0]) & UINT64_MASK
        x1 = (x1 + ks[1]) & UINT64_MASK

        for r in range(20):
            # mix
            x0 = (x0 + x1) & UINT64_MASK
            x1 = _rotl(x1, ROT[r % 8])
            x1 ^= x0


            if (r + 1) % 4 == 0:
                s = (r + 1) // 4
                x0 = (x0 + ks[s % 3]) & UINT64_MASK
                x1 = (x1 + ks[(s + 1) % 3] + s) & UINT64_MASK


        self.counter[0] = (self.counter[0] + 1) & UINT64_MASK
        if self.counter[0] == 0:
            self.counter[1] = (self.counter[1] + 1) & UINT64_MASK

        return [x0, x1]



    def random_uint64(self, size: int) -> List[int]:
        out = []
        while len(out) < size:
            block = self._generate_block()
            for x in block:
                out.append(x)
                if len(out) == size:
                    break
        return out

    def random_bytes(self, nbytes: int) -> bytes:
        result = bytearray()
        while len(result) < nbytes:
            block = self._generate_block()
            for x in block:
                result.extend(x.to_bytes(8, "little"))
                if len(result) >= nbytes:
                    break
        return bytes(result[:nbytes])

    def random_bits(self, nbits: int) -> List[int]:
        bits = []
        while len(bits) < nbits:
            block = self._generate_block()
            for x in block:
                for i in range(64):
                    bits.append((x >> i) & 1)
                    if len(bits) == nbits:
                        break
                if len(bits) == nbits:
                    break
        return bits

    def random_floats(self, size: int) -> List[float]:
        floats = []
        uints = self.random_uint64(size)
        for u in uints:
            floats.append((u >> 11) * (1.0 / (1 << 53)))
        return floats