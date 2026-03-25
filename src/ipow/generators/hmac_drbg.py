"""Minimal HMAC_DRBG (SHA-256) implementation inspired by NIST SP 800-90A."""
from __future__ import annotations

from dataclasses import dataclass
import hmac
import hashlib


@dataclass
class HMACDRBG:
    entropy: bytes
    nonce: bytes = b""
    personalization_string: bytes = b""
    name: str = "HMAC_DRBG_SHA256"

    def __post_init__(self) -> None:
        self.K = b"\x00" * 32
        self.V = b"\x01" * 32
        seed_material = self.entropy + self.nonce + self.personalization_string
        self._update(seed_material)
        self.reseed_counter = 1

    def _hmac(self, key: bytes, data: bytes) -> bytes:
        return hmac.new(key, data, hashlib.sha256).digest()

    def _update(self, provided_data: bytes = b"") -> None:
        self.K = self._hmac(self.K, self.V + b"\x00" + provided_data)
        self.V = self._hmac(self.K, self.V)
        if provided_data:
            self.K = self._hmac(self.K, self.V + b"\x01" + provided_data)
            self.V = self._hmac(self.K, self.V)

    def reseed(self, entropy: bytes, additional_input: bytes = b"") -> None:
        self._update(entropy + additional_input)
        self.reseed_counter = 1

    def generate(self, nbytes: int, additional_input: bytes = b"") -> bytes:
        if additional_input:
            self._update(additional_input)
        out = bytearray()
        while len(out) < nbytes:
            self.V = self._hmac(self.K, self.V)
            out.extend(self.V)
        self._update(additional_input)
        self.reseed_counter += 1
        return bytes(out[:nbytes])

    def random_bytes(self, nbytes: int) -> bytes:
        return self.generate(nbytes)

    def random_uint64(self, size: int) -> list[int]:
        raw = self.generate(size * 8)
        return [int.from_bytes(raw[i:i+8], "big") for i in range(0, len(raw), 8)]

    def random_bits(self, nbits: int) -> list[int]:
        raw = self.generate((nbits + 7) // 8)
        bits: list[int] = []
        for b in raw:
            bits.extend((b >> i) & 1 for i in range(8))
        return bits[:nbits]

    def random_floats(self, size: int) -> list[float]:
        return [x / (1 << 64) for x in self.random_uint64(size)]
