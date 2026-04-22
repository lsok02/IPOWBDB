import math
import random
from dataclasses import dataclass
from typing import final

# Tu zakładasz, że w pliku są już zaimportowane/zdefiniowane: 
# RandomGenerator, GeneratorMetadata

@dataclass
@final
class HCCSRNG:
    """Generator Pseudolosowy oparty na Konserwatywnym Układzie Chaotycznym (HCCS).

    Implementuje przyspieszoną ekstrakcję 8-strefową (3 bity na krok równania).
    """
    seed: int = 42
    name: str = "HCCSRNG"

    def __post_init__(self) -> None:
        # K to krytyczny parametr chaosu z publikacji (powoduje ergodyczność układu)
        self.K = 259.14
        self.TWO_PI = 2 * math.pi
        
        # Inicjalizacja warunków początkowych dla 2 niezależnych układów.
        seeder = random.Random(self.seed)
        self.x1 = seeder.uniform(0, self.TWO_PI)
        self.y1 = seeder.uniform(0, self.TWO_PI)
        self.x2 = seeder.uniform(0, self.TWO_PI)
        self.y2 = seeder.uniform(0, self.TWO_PI)

        self.bit_buffer_str = ""

    def _ensure_bits(self, required: int) -> None:
        """Główny silnik chaosu.

        Pętla działa, dopóki bufor nie napełni się wymaganą liczbą bitów. Każdy obieg
        równań daje dokładnie 3 bity.
        """
        while len(self.bit_buffer_str) < required:
            # Równania układu chaotycznego (Mapa Standardowa)
            self.x1 = (self.x1 + self.K * math.sin(self.y1)) % self.TWO_PI
            self.y1 = (self.x1 + self.y1) % self.TWO_PI
            
            self.x2 = (self.x2 + self.K * math.sin(self.y2)) % self.TWO_PI
            self.y2 = (self.x2 + self.y2) % self.TWO_PI
            
            # Przesunięcie współrzędnych układu z zakresu [0, 2pi] do[-pi, pi]
            a = self.x1 - math.pi
            b = self.x2 - math.pi
            
            # Decydujemy, w którą z 8 części wpadł układ i przydzielamy kod (3 bity):
            if a < 0.0:
                if b < 0.0:
                    new_bits = "000" if a > b else "001"
                else:
                    new_bits = "010" if -a > b else "011"
            else:
                if b >= 0.0:
                    new_bits = "100" if a < b else "101"
                else:
                    new_bits = "110" if a > -b else "111"
                    
            # Doklejamy wygenerowany fragment jako tekst
            self.bit_buffer_str += new_bits

    def _extract_bits_as_string(self, n: int) -> str:
        """
        Wydobywa `n` pierwszych bitów jako tekst i usuwa je z bufora.
        """
        self._ensure_bits(n)
        extracted = self.bit_buffer_str[:n]
        self.bit_buffer_str = self.bit_buffer_str[n:]

        return extracted

    def random_uint64(self, size: int) -> list[int]:
        result =[]
        for _ in range(size):
            # Prosimy o 64 znaki zer i jedynek
            bit_string = self._extract_bits_as_string(64)
            # Konwersja binarnego zapisu tekstowego ("1010...") na liczbę całkowitą (base 2)
            number = int(bit_string, 2)
            result.append(number)
        return result

    def random_bytes(self, nbytes: int) -> bytes:
        bit_string = self._extract_bits_as_string(nbytes * 8)
        out = bytearray()
        
        # Idziemy co 8 znaków i każdy 8-znakowy ciąg zmieniamy w 1 bajt
        for i in range(0, len(bit_string), 8):
            byte_chunk_str = bit_string[i : i+8]
            out.append(int(byte_chunk_str, 2))

        return bytes(out)

    def random_bits(self, nbits: int) -> list[int]:
        bit_string = self._extract_bits_as_string(nbits)
        # Zamieniamy każdy pojedynczy znak tekstu np. "1" z powrotem na liczbę 1 w liście
        return[int(char) for char in bit_string]

    def random_floats(self, size: int) -> list[float]:
        result =[]
        # Precyzja zmiennoprzecinkowa (float) w Pythonie opiera się na 53 bitach ułamka
        for _ in range(size):
            bit_string = self._extract_bits_as_string(53)
            # Zamieniamy 53-znakowy ciąg na inta i dzielimy przez 2^53, żeby otrzymać[0.0, 1.0)
            float_val = int(bit_string, 2) / (2**53)
            result.append(float_val)
        return result
