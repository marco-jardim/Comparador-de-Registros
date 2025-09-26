from __future__ import annotations

from dataclasses import dataclass

from util import levenshtein


@dataclass
class ResultadoData:
    pontos: list[str]
    nota: float

    def formatado(self) -> list[str]:
        return self.pontos + [f"{self.nota:.2f}".replace(".", ",")]


def comparar(d1: str, d2: str) -> ResultadoData:
    pontos = ["0,0"] * 5
    nota = 0.0

    if d1 == d2:
        nota += 1
        pontos[0] = "1,0"

    dist = levenshtein(d1, d2)
    if dist == 1:
        nota += 1
        pontos[1] = "1,0"
    elif dist == 2 and len(d1) == 8 and len(d2) == 8:
        dia1, mes1, ano1 = d1[6:], d1[4:6], d1[:4]
        dia2, mes2, ano2 = d2[6:], d2[4:6], d2[:4]
        if dia1[::-1] == dia2:
            nota += 1
            pontos[2] = "1,0"
        elif mes1[::-1] == mes2:
            nota += 1
            pontos[3] = "1,0"
        elif levenshtein(ano1, ano2) == 2 and sorted(ano1) == sorted(ano2):
            nota += 1
            pontos[4] = "1,0"

    return ResultadoData(pontos, nota)
