"""Optional integration with external RNG validation suites.

These helpers do not require the tools to be installed. They expose a uniform API and
return a helpful error message when a tool is unavailable.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


def _write_binary_sample(sample: bytes) -> str:
    handle = tempfile.NamedTemporaryFile(delete=False, suffix=".bin")
    handle.write(sample)
    handle.flush()
    handle.close()
    return handle.name


def run_dieharder(sample: bytes) -> dict[str, str | int]:
    exe = shutil.which("dieharder")
    if exe is None:
        return {"available": False, "message": "dieharder is not installed"}
    path = _write_binary_sample(sample)
    proc = subprocess.run(
        [exe, "-a", "-g", "201", "-f", path],
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "available": True,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "sample_path": path,
    }


def run_nist_sts(sample: bytes, sts_root: str) -> dict[str, str | int | bool]:
    root = Path(sts_root)
    exe = root / "assess"
    if not exe.exists():
        return {"available": False, "message": f"NIST STS assess not found in {root}"}
    path = _write_binary_sample(sample)
    return {
        "available": True,
        "message": (
            "Binary sample created. NIST STS usually needs interactive execution; "
            f"use sample file at {path} with assess from {root}."
        ),
        "sample_path": path,
    }


def run_testu01(sample: bytes, harness_path: str | None = None) -> dict[str, str | bool]:
    if harness_path is None:
        return {
            "available": False,
            "message": "Provide a compiled TestU01 harness path to execute this integration.",
        }
    exe = Path(harness_path)
    if not exe.exists():
        return {"available": False, "message": f"Harness not found: {exe}"}
    path = _write_binary_sample(sample)
    proc = subprocess.run([str(exe), path], capture_output=True, text=True, check=False)
    return {
        "available": True,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "sample_path": path,
    }
