"""ANU API-backed QRNG generator (vacuum-fluctuation source)."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import time
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass
class ANUVacuumQRNG:
    """Generator that fetches randomness from ANU QRNG JSON API."""

    name: str = "ANU Vacuum-Fluctuation QRNG (API)"
    api_url: str = "https://qrng.anu.edu.au/API/jsonI.php"
    api_key: str | None = None
    timeout_sec: float = 20.0
    max_chunk: int = 1024
    delay_between_calls_sec: float = 0.0
    record_downloads: bool = True
    _byte_buffer: bytearray = field(default_factory=bytearray, init=False, repr=False)
    _download_log: bytearray = field(default_factory=bytearray, init=False, repr=False)
    _request_count: int = field(default=0, init=False, repr=False)
    _downloaded_bytes: int = field(default=0, init=False, repr=False)

    def _request_uint8(self, length: int) -> list[int]:
        if not (1 <= length <= self.max_chunk):
            raise ValueError(f"length must be in <1, {self.max_chunk}>")

        params = urlencode({"length": length, "type": "uint8"})
        url = f"{self.api_url}?{params}"

        headers = {"User-Agent": "ipow-anu-qrng"}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        request = Request(url, headers=headers, method="GET")
        with urlopen(request, timeout=self.timeout_sec) as response:
            payload: dict[str, Any] = json.loads(response.read().decode("utf-8"))

        if payload.get("success") is not True:
            raise RuntimeError(f"ANU API returned non-success payload: {payload}")

        data = payload.get("data")
        if not isinstance(data, list) or len(data) != length:
            raise RuntimeError(f"Unexpected ANU API payload shape: {payload}")

        result = [int(x) & 0xFF for x in data]
        self._request_count += 1
        self._downloaded_bytes += len(result)
        if self.record_downloads:
            self._download_log.extend(result)
        if self.delay_between_calls_sec > 0:
            time.sleep(self.delay_between_calls_sec)
        return result

    def _ensure_bytes(self, nbytes: int) -> None:
        while len(self._byte_buffer) < nbytes:
            missing = nbytes - len(self._byte_buffer)
            chunk = min(missing, self.max_chunk)
            self._byte_buffer.extend(self._request_uint8(chunk))

    def random_bytes(self, nbytes: int) -> bytes:
        if nbytes < 0:
            raise ValueError("nbytes must be >= 0")
        self._ensure_bytes(nbytes)
        out = bytes(self._byte_buffer[:nbytes])
        del self._byte_buffer[:nbytes]
        return out

    def random_bits(self, nbits: int) -> list[int]:
        if nbits < 0:
            raise ValueError("nbits must be >= 0")

        nbytes = (nbits + 7) // 8
        raw = self.random_bytes(nbytes)

        bits: list[int] = []
        for b in raw:
            bits.extend((b >> i) & 1 for i in range(8))
        return bits[:nbits]

    def random_uint64(self, size: int) -> list[int]:
        if size < 0:
            raise ValueError("size must be >= 0")

        raw = self.random_bytes(size * 8)
        return [
            int.from_bytes(raw[i : i + 8], byteorder="little", signed=False)
            for i in range(0, len(raw), 8)
        ]

    def random_floats(self, size: int) -> list[float]:
        # 53 bits of entropy mapped to [0.0, 1.0)
        ints = self.random_uint64(size)
        return [(x >> 11) * (1.0 / (1 << 53)) for x in ints]

    def download_stats(self) -> dict[str, int]:
        return {
            "request_count": self._request_count,
            "downloaded_bytes": self._downloaded_bytes,
            "logged_bytes": len(self._download_log),
        }

    def dump_download_log(self, path: str) -> str:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(bytes(self._download_log))
        return str(target)
