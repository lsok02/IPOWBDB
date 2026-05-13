
from dataclasses import dataclass, field
from hashlib import sha256
from secrets import randbits
from typing import Final


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _is_probable_prime(n: int, rounds: int = 16) -> bool:
    """Miller-Rabin primality test."""
    if n < 2:
        return False

    small_primes = (
        2,
        3,
        5,
        7,
        11,
        13,
        17,
        19,
        23,
        29,
        31,
        37,
    )

    for p in small_primes:
        if n % p == 0:
            return n == p

    d = n - 1
    s = 0

    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(rounds):
        a = randbits(n.bit_length() - 1) % (n - 3) + 2
        x = pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        for _ in range(s - 1):
            x = pow(x, 2, n)

            if x == n - 1:
                break
        else:
            return False

    return True


def _generate_safe_prime(bits: int) -> int:
    """Generate a safe prime p = 2q + 1."""
    while True:
        q = randbits(bits - 1)
        q |= 1
        q |= (1 << (bits - 2))

        if not _is_probable_prime(q):
            continue

        p = 2 * q + 1

        if _is_probable_prime(p):
            return p


def _find_generator(p: int) -> int:
    """Find generator for Z*_p."""
    q = (p - 1) // 2

    for g in range(2, p - 1):
        if pow(g, 2, p) != 1 and pow(g, q, p) != 1:
            return g

    raise RuntimeError("generator not found")


def _split_u64(x: int) -> tuple[int, int]:
    """Split uint64 into two uint32 halves."""
    left = (x >> 32) & 0xFFFFFFFF
    right = x & 0xFFFFFFFF
    return left, right


def _join_u64(left: int, right: int) -> int:
    """Join two uint32 halves into uint64."""
    return ((left & 0xFFFFFFFF) << 32) | (right & 0xFFFFFFFF)



@dataclass
class ModExpFeistelRNG:
    """Feistel + modular exponentiation based CSPRNG."""

    seed: int

    name: str = "mod_exp_feistel_rng"

    rounds: int = 6
    small_prime_bits: int = 32
    large_prime_bits: int = 256


    # exponents from paper
    E1: Final[int] = 17
    E2: Final[int] = 9

    def __post_init__(self) -> None:
        # Large safe prime q
        self.q = _generate_safe_prime(self.large_prime_bits)
        self.g = _find_generator(self.q)

        # Small safe primes pool
        self.primes = [
            _generate_safe_prime(self.small_prime_bits)
            for _ in range(8)
        ]

        # internal state
        seed_bytes = sha256(str(self.seed).encode()).digest()
        self.state = int.from_bytes(seed_bytes, "big")

        self.counter = 1

    # ------------------------------------------------------------------ #
    # Core nonlinear function (Algorithm 2 inspired)
    # ------------------------------------------------------------------ #

    def _feistel_box(self, x: int, modulus: int) -> int:
        left, right = _split_u64(x)

        for _ in range(self.rounds):
            w = pow(self.counter + 3, 3, modulus)

            mixed = (
                pow(w + (right ^ left), self.E2, modulus)
            ) & 0xFFFFFFFF

            new_right = left ^ mixed
            left, right = right, new_right

            self.counter += 1

        return _join_u64(left, right)

    # ------------------------------------------------------------------ #
    # Single 64-bit output
    # ------------------------------------------------------------------ #

    def _next_u64(self) -> int:
        p0 = self.primes[self.counter % len(self.primes)]
        p1 = self.primes[(self.counter + 1) % len(self.primes)]

        # modular exponentiation chain
        x1 = pow(self.state + self.counter, self.E1, p0)
        x2 = pow(x1, self.E1, p1)

        # Blum-Micali style transform
        gx = pow(self.g, x2, self.q)

        # use lower 64 bits
        z = gx & 0xFFFFFFFFFFFFFFFF

        # Feistel nonlinear mixing
        output = self._feistel_box(z, p1)

        # update internal state
        self.state = gx ^ output ^ self.counter
        self.counter += 1

        return output & 0xFFFFFFFFFFFFFFFF
    

    def random_uint64(self, size: int) -> list[int]:
        """Return ``size`` unsigned 64-bit integers."""
        return [self._next_u64() for _ in range(size)]

    def random_bytes(self, nbytes: int) -> bytes:
        """Return ``nbytes`` random bytes."""
        out = bytearray()

        while len(out) < nbytes:
            value = self._next_u64()
            out.extend(value.to_bytes(8, "big"))

        return bytes(out[:nbytes])

    def random_bits(self, nbits: int) -> list[int]:
        """Return list of random bits."""
        result: list[int] = []

        while len(result) < nbits:
            value = self._next_u64()

            for i in range(64):
                result.append((value >> i) & 1)

                if len(result) >= nbits:
                    break

        return result

    def random_floats(self, size: int) -> list[float]:
        """Return floats in [0, 1)."""
        scale = 1.0 / (1 << 64)

        return [
            self._next_u64() * scale
            for _ in range(size)
        ]

