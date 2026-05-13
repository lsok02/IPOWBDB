from dataclasses import dataclass


@dataclass
class URNG:
    """Implementation of µRNG by Cezary Glowacz.

    A Non-Periodic Deterministic Random Number Generator.
    """
    name: str = "µRNG"
    seed: int = 2  # Seed s must be: s ≡ 0 (mod 2) and s ̸≡ 0 (mod 3)
    _s: int = 2
    _t: int = 1

    def __post_init__(self) -> None:
        # Walidacja ziarna zgodnie z wymogami publikacji
        if self.seed % 2 != 0:
            raise ValueError("Seed s must be: s ≡ 0 (mod 2)")
        if self.seed % 3 == 0:
            raise ValueError("Seed s must be: s ̸≡ 0 (mod 3)")

        self._s = self.seed

    def random_bits(self, nbits: int) -> list[int]:
        # Implementacja pętli z publikacji
        r: list[int] = []
        for _ in range(nbits):
            self._s = (self._s + (self._s & 1) * self._t) >> 1
            self._t += self._t << 1
            r.append(self._s & 1)
        return r

    def random_bytes(self, nbytes: int) -> bytes:
        bits = self.random_bits(nbytes * 8)
        res = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for bit in range(8):
                if bits[i + bit]:
                    byte |= (1 << bit)
            res.append(byte)
        return bytes(res)

    def random_uint64(self, size: int) -> list[int]:
        res = []
        for _ in range(size):
            bits = self.random_bits(64)
            val = 0
            for i, bit in enumerate(bits):
                if bit:
                    val |= (1 << i)
            res.append(val)
        return res

    def random_floats(self, size: int) -> list[float]:
        # Standardowe mapowanie 53-bitowe
        res = []
        for _ in range(size):
            bits = self.random_bits(53)
            val = 0
            for i, bit in enumerate(bits):
                if bit:
                    val |= (1 << i)
            res.append(val / (1 << 53))
        return res
