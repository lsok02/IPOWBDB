# random_project

Pliki do projektu o algorytmach generowania i weryfikacji danych losowych.

## Struktura

- `generators/` – implementacje i wrappery generatorów:
  - `lcg.py`
  - `mt19937.py`
  - `pcg.py`
  - `csprng.py`
  - `hmac_drbg.py`
  - `trng_mock.py`
  - `chaotic.py`
- `tests/` – walidacja i testy statystyczne:
  - `basic_stats.py`
  - `statistical.py`
  - `validation.py`
  - `external_tools.py`
- `examples/demo_validation.py` – przykładowe użycie

## Szybki start

```python
from generators import LCGGenerator, PCG64Generator
from tests import validate_generator

result = validate_generator(PCG64Generator(seed=123))
print(result["tests"])
```

## Uwagi

- `external_tools.py` zawiera adaptery do `dieharder`, NIST STS i TestU01.
- Integracje z narzędziami zewnętrznymi są opcjonalne i działają tylko wtedy, gdy te narzędzia są zainstalowane w systemie.
