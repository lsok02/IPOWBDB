from __future__ import annotations

from dataclasses import dataclass


MASK32 = 0xFFFFFFFF


def _rotl32(x: int, k: int) -> int:
    return ((x << k) | (x >> (32 - k))) & MASK32


@dataclass
class JSF32:
    seed: int = 42
    name: str = "JSF32"

    def __post_init__(self) -> None:
        # inicjalizacja stanu (4 x 32-bit)
        self.a = 0xF1EA5EED
        self.b = self.seed & MASK32
        self.c = self.seed & MASK32
        self.d = self.seed & MASK32

        # warmup
        for _ in range(20):
            self._next_uint32()

    # ===== core =====

    def _next_uint32(self) -> int:
        e = (self.a - _rotl32(self.b, 27)) & MASK32
        self.a = (self.b ^ _rotl32(self.c, 17)) & MASK32
        self.b = (self.c + self.d) & MASK32
        self.c = (self.d + e) & MASK32
        self.d = (e + self.a) & MASK32
        return self.d

    def _next_uint64(self) -> int:
        """Złożenie dwóch 32-bitów w 64-bit."""
        high = self._next_uint32()
        low = self._next_uint32()
        return ((high << 32) | low) & 0xFFFFFFFFFFFFFFFF

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