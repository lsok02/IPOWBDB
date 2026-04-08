from __future__ import annotations

from dataclasses import dataclass


MASK32 = 0xFFFFFFFF


@dataclass
class WELL512a:
    seed: int = 42
    name: str = "WELL512a"

    def __post_init__(self) -> None:
        # Initialize 16-element state using SplitMix64-like approach (32-bit chunks)
        self.state = []
        x = self.seed & 0xFFFFFFFFFFFFFFFF

        for _ in range(16):
            x = (x + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
            z = x
            z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9 & 0xFFFFFFFFFFFFFFFF
            z = (z ^ (z >> 27)) * 0x94D049BB133111EB & 0xFFFFFFFFFFFFFFFF
            z = z ^ (z >> 31)
            self.state.append(z & MASK32)

        self.index = 0

    # ===== core =====

    def _next_uint32(self) -> int:
        state = self.state
        i = self.index

        a = state[i]
        c = state[(i + 13) & 15]
        b = a ^ c ^ ((a << 16) & MASK32) ^ ((c << 15) & MASK32)

        c = state[(i + 9) & 15]
        c ^= (c >> 11)

        a = state[i] = (b ^ c) & MASK32

        d = a ^ ((a << 5) & 0xDA442D24 & MASK32)

        self.index = (i + 15) & 15
        a = state[self.index]

        state[self.index] = (a ^ b ^ d ^ ((a << 2) & MASK32) ^ ((b << 18) & MASK32) ^ ((c << 28) & MASK32)) & MASK32

        return state[self.index]

    def _next_uint64(self) -> int:
        """Combine two 32-bit outputs into one 64-bit."""
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