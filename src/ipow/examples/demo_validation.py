"""Example script showing how to validate selected generators."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from generators import (
    HMACDRBG,
    LCGGenerator,
    LogisticMapGenerator,
    MT19937Generator,
    MockTRNG,
    PCG64Generator,
    SystemCSPRNG,
)
from tests import ValidationConfig, validate_generator, run_visual_tests


def main() -> None:
    generators = [
        LCGGenerator(seed=12345),
        MT19937Generator(seed=12345),
        PCG64Generator(seed=12345),
        SystemCSPRNG(),
        HMACDRBG(entropy=b"example-entropy-seed-32-bytes!!!!", nonce=b"demo"),
        MockTRNG(seed=12345),
        LogisticMapGenerator(x0=0.314159265, r=3.99),
    ]
    cfg = ValidationConfig(n_numbers=5000, n_bits=10000)
    results = [validate_generator(gen, cfg) for gen in generators]
    print(json.dumps(results, indent=2))

    # for gen in generators:
    #     run_visual_tests(gen)


if __name__ == "__main__":
    main()
