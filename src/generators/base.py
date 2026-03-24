"""Common interfaces for random number generators used in the project."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class RandomGenerator(Protocol):
    """Protocol implemented by all generators in the package."""

    name: str

    def random_uint64(self, size: int) -> list[int]:
        """Return ``size`` unsigned 64-bit integers."""

    def random_bytes(self, nbytes: int) -> bytes:
        """Return ``nbytes`` random bytes."""

    def random_bits(self, nbits: int) -> list[int]:
        """Return a list of 0/1 bits."""

    def random_floats(self, size: int) -> list[float]:
        """Return ``size`` floats in the interval [0, 1)."""


@dataclass(slots=True)
class GeneratorMetadata:
    name: str
    category: str
    is_cryptographic: bool = False
    notes: str = ""
