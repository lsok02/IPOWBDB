from __future__ import annotations

from dataclasses import dataclass
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.backends import default_backend


@dataclass
class ChaCha20RNG:
    seed: int = 42
    name: str = "ChaCha20RNG"

    def __post_init__(self) -> None:
        # 32-byte key + 16-byte nonce
        self.key = self.seed.to_bytes(32, "little", signed=False)
        self.nonce = b"\x00" * 16

        self._reset_cipher()
        self.buffer = b""
        self.buffer_pos = 0

    def _reset_cipher(self) -> None:
        algorithm = algorithms.ChaCha20(self.key, self.nonce)
        cipher = Cipher(algorithm, mode=None, backend=default_backend())
        self.encryptor = cipher.encryptor()

    def _refill(self) -> None:
        self.buffer = self.encryptor.update(b"\x00" * 64)
        self.buffer_pos = 0

    def _get_bytes(self, n: int) -> bytes:
        out = bytearray()

        while len(out) < n:
            if self.buffer_pos >= len(self.buffer):
                self._refill()

            remaining = len(self.buffer) - self.buffer_pos
            take = min(n - len(out), remaining)

            out.extend(self.buffer[self.buffer_pos:self.buffer_pos + take])
            self.buffer_pos += take

        return bytes(out)

    def _next_uint64(self) -> int:
        return int.from_bytes(self._get_bytes(8), "little")

    # ===== interface =====

    def random_uint64(self, size: int) -> list[int]:
        return [self._next_uint64() for _ in range(size)]

    def random_bytes(self, nbytes: int) -> bytes:
        return self._get_bytes(nbytes)

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