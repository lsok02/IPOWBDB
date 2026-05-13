"""ANU API-backed QRNG generator (vacuum-fluctuation source)."""
from __future__ import annotations
import base64
import math
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar
from urllib.request import Request, urlopen


@dataclass
class ANUVacuumQRNG:
    """Generator that fetches randomness from ANU QRNG."""

    _TEST_ENDPOINT_URL: ClassVar[str] = "https://qrng.anu.edu.au/wp-content/plugins/colours-plugin/get_block_alpha.php"

    name: str = "ANU Vacuum-Fluctuation QRNG (API)"
    api_url: str = "https://api.quantumnumbers.anu.edu.au"
    api_key: str | None = None
    max_workers: int = 5
    use_test_endpoint: bool = False  # Flag to switch to the .php string endpoint
    timeout_sec: float = 20.0
    max_chunk: int = 1024
    record_downloads: bool = True
    cache_path: Path | str = Path(__file__).parent / "quantum_cache.bin"

    _byte_buffer: bytearray = field(default_factory=bytearray, init=False, repr=False)
    _download_log: bytearray = field(default_factory=bytearray, init=False, repr=False)
    _request_count: int = field(default=0, init=False, repr=False)
    _downloaded_bytes: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        # Przy starcie zawsze wczytujemy WSZYSTKO co mamy na dysku do RAMu
        self.cache_path = Path(self.cache_path).resolve()
        self._load_full_cache()

    def _load_full_cache(self) -> None:
        p = Path(self.cache_path)
        if p.exists():
            data = p.read_bytes()
            self._byte_buffer = bytearray(data)
            print(f"Loaded {len(self._byte_buffer)} bytes from cache at {p.resolve().as_posix()}")

    def _append_to_disk(self, chunk: bytes) -> None:
        with open(self.cache_path, "ab") as f:
            f.write(chunk)

    def _decode_base64_url(self, data: str) -> bytes:
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        return base64.urlsafe_b64decode(data)

    def _fetch_single_chunk_from_test_endpoint(self) -> bytes:
        try:
            req = Request(self._TEST_ENDPOINT_URL)
            with urlopen(req, timeout=self.timeout_sec) as response:
                raw_text = response.read().decode("utf-8").strip()
                return self._decode_base64_url(raw_text)
        except Exception as e:
            print(f"Download error: {e}")
            return b""

    def _request_from_test_endpoint(self, nbytes: int) -> None:
        while len(self._byte_buffer) < nbytes:
            needed = nbytes - len(self._byte_buffer)
            # Jeden chunk to ok. 768 bajtów. Obliczamy ile requestów wysłać.
            reqs_to_fire = min(self.max_workers, math.ceil(needed / 768))

            print(f"Downloading {reqs_to_fire} chunks in parallel to fill {needed} bytes...")

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [
                    executor.submit(self._fetch_single_chunk_from_test_endpoint)
                    for _ in range(reqs_to_fire)
                ]

                for future in futures:
                    chunk = future.result()
                    if chunk:
                        self._byte_buffer.extend(chunk)
                        self._download_log.extend(chunk)
                        self._request_count += 1
                        self._downloaded_bytes += len(chunk)
                        self._append_to_disk(chunk)

            # Pozwólmy serwerowi odpocząć
            time.sleep(0.5)

    def random_bytes(self, nbytes: int) -> bytes:
        if nbytes <= 0:
            return b""

        self._ensure_bytes(nbytes)
        # Wycinamy bity tylko z RAMu na potrzeby obecnego testu
        out = bytes(self._byte_buffer[:nbytes])
        del self._byte_buffer[:nbytes]
        return out

    def _ensure_bytes(self, nbytes: int) -> None:
        while len(self._byte_buffer) < nbytes:
            if self.use_test_endpoint:
                self._request_from_test_endpoint(nbytes)
            else:
                raise NotImplementedError
                # missing = nbytes - len(self._byte_buffer)
                # elements = min(math.ceil(missing / 2), self.max_chunk)
                # self._request_uint16(elements)

    def random_bits(self, nbits: int) -> list[int]:
        if nbits < 0:
            raise ValueError("nbits must be >= 0")

        raw = self.random_bytes((nbits + 7) // 8)
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
        """53 bits of entropy uniformly mapped to [0.0, 1.0)."""
        return [(x >> 11) * (1.0 / (1 << 53)) for x in self.random_uint64(size)]

    def download_stats(self) -> dict[str, Any]:
        return {
            "session_requests": self._request_count,
            "session_downloaded": self._downloaded_bytes,
            "current_ram_buffer": len(self._byte_buffer),
            "total_disk_cache_size": Path(self.cache_path).stat().st_size if Path(self.cache_path).exists() else 0
        }

    def dump_download_log(self, path: str) -> str:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(bytes(self._download_log))
        return str(target)

    # def _request_uint16_from_api(self, length: int) -> None:
    #     """Fetch `length` uint16 values and append them as raw bytes to the buffer.

    #     Each uint16 element yields 2 bytes (little-endian), so one call with
    #     length=1024 delivers 2048 bytes — double what uint8 would give.
    #     """
    #     if not (1 <= length <= self.max_chunk):
    #         raise ValueError(f"length must be in [1, {self.max_chunk}]")

    #     params = urlencode({"length": length, "type": "uint16"})
    #     url = f"{self.api_url}?{params}"
    #     headers = {"User-Agent": "ipow-anu-qrng"}
    #     if self.api_key:
    #         headers["x-api-key"] = self.api_key

    #     request = Request(url, headers=headers)
    #     with urlopen(request, timeout=self.timeout_sec) as response:
    #         payload = json.loads(response.read().decode("utf-8"))

    #     if payload.get("success") is not True:
    #         raise RuntimeError(f"ANU API Error: {payload}")

    #     data = payload.get("data")
    #     raw = bytearray(len(data) * 2)
    #     for i, x in enumerate(data):
    #         v = int(x) & 0xFFFF
    #         raw[i*2] = v & 0xFF
    #         raw[i*2+1] = v >> 8
            
    #     self._request_count += 1
    #     self._downloaded_bytes += len(raw)
    #     if self.record_downloads:
    #         self._download_log.extend(raw)
    #     self._byte_buffer.extend(raw)
        
    #     if self._cache_file:
    #         self._cache_file.parent.mkdir(parents=True, exist_ok=True)
    #         with self._cache_file.open("ab") as f:
    #             f.write(raw)

    # def _requests_needed(self, nbytes: int) -> int:
    #     """How many API calls are required to fill `nbytes` from an empty buffer."""
    #     bytes_per_call = self.max_chunk * 2  # uint16 → 2 bytes each
    #     return math.ceil(nbytes / bytes_per_call)
