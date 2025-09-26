from __future__ import annotations

from dataclasses import dataclass

from util import levenshtein, soundex


@dataclass
class ResultadoLocalidade:
    pontos: list[str]
    nota: float

    def formatado(self) -> list[str]:
        return self.pontos + [f"{self.nota:.2f}".replace(".", ",")]


def comparar(loc1: str, loc2: str) -> ResultadoLocalidade:
    pontos = ["0,0"] * 4
    nota = 0.0

    if len(loc1) != 6 or len(loc2) != 6:
        return ResultadoLocalidade(pontos, nota)

    uf1, cod1 = loc1[:2].upper(), loc1[2:].upper()
    uf2, cod2 = loc2[:2].upper(), loc2[2:].upper()

    if uf1 == uf2:
        nota += 1
        pontos[0] = "1,0"
    else:
        dist_uf = levenshtein(uf1, uf2)
        if dist_uf == 1:
            nota += 0.5
            pontos[1] = "0,5"
        elif soundex(uf1) == soundex(uf2):
            nota += 0.3
            pontos[1] = "0,3"

    if cod1 == cod2:
        nota += 1
        pontos[2] = "1,0"
    else:
        dist_cod = levenshtein(cod1, cod2)
        if dist_cod == 1:
            nota += 0.8
            pontos[3] = "0,8"
        elif dist_cod == 2:
            nota += 0.5
            pontos[3] = "0,5"
        elif not (cod1.isdigit() and cod2.isdigit()) and soundex(cod1) == soundex(cod2):
            nota += 0.4
            pontos[3] = "0,4"

    return ResultadoLocalidade(pontos, nota)
