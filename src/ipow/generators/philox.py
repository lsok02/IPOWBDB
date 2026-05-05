from __future__ import annotations

from dataclasses import dataclass
from typing import List


UINT32_MASK = 0xFFFFFFFF
UINT64_MASK = 0xFFFFFFFFFFFFFFFF


def _mulhilo(a: int, b: int) -> tuple[int, int]:
    product = a * b
    lo = product & UINT32_MASK
    hi = (product >> 32) & UINT32_MASK
    return hi, lo


@dataclass
class Philox:
    """Philox4x32-10 random generator."""

    seed: int = 0
    name: str = "philox4x32-10"

    def __post_init__(self):
        self.counter = [0, 0, 0, 0]  # 4x32-bit
        self.key = [
            self.seed & UINT32_MASK,
            (self.seed >> 32) & UINT32_MASK,
        ]

    # core round
    @staticmethod
    def _round(c: list[int], k: list[int]) -> list[int]:
        PHILOX_M0 = 0xD2511F53
        PHILOX_M1 = 0xCD9E8D57

        hi0, lo0 = _mulhilo(PHILOX_M0, c[0])
        hi1, lo1 = _mulhilo(PHILOX_M1, c[2])

        return [
            (hi1 ^ c[1] ^ k[0]) & UINT32_MASK,
            lo1,
            (hi0 ^ c[3] ^ k[1]) & UINT32_MASK,
            lo0,
        ]

    @staticmethod
    def _bump_key(k: list[int]) -> list[int]:
        W0 = 0x9E3779B9
        W1 = 0xBB67AE85
        return [
            (k[0] + W0) & UINT32_MASK,
            (k[1] + W1) & UINT32_MASK,
        ]

    def _generate_block(self) -> list[int]:
        """Generuje 4x32-bit."""
        c = self.counter[:]
        k = self.key[:]

        for _ in range(10):
            c = self._round(c, k)
            k = self._bump_key(k)

        # inc counter
        self.counter[0] = (self.counter[0] + 1) & UINT32_MASK
        if self.counter[0] == 0:
            self.counter[1] = (self.counter[1] + 1) & UINT32_MASK
            if self.counter[1] == 0:
                self.counter[2] = (self.counter[2] + 1) & UINT32_MASK
                if self.counter[2] == 0:
                    self.counter[3] = (self.counter[3] + 1) & UINT32_MASK

        return c



    def random_uint64(self, size: int) -> List[int]:
        out = []
        while len(out) < size:
            block = self._generate_block()
            # 4x32 -> 2x64
            for i in range(0, 4, 2):
                val = ((block[i] << 32) | block[i + 1]) & UINT64_MASK
                out.append(val)
                if len(out) == size:
                    break
        return out

    def random_bytes(self, nbytes: int) -> bytes:
        result = bytearray()
        while len(result) < nbytes:
            block = self._generate_block()
            for x in block:
                result.extend(x.to_bytes(4, "little"))
                if len(result) >= nbytes:
                    break
        return bytes(result[:nbytes])

    def random_bits(self, nbits: int) -> List[int]:
        bits = []
        while len(bits) < nbits:
            block = self._generate_block()
            for x in block:
                for i in range(32):
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
            floats.append((u >> 11) * (1.0 / (1 << 53)))  # IEEE double trick
        return floats