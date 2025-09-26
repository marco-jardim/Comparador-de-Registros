from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from util import soundex


@dataclass
class ResultadoNome:
    pontos: list[str]
    nota: float

    def formatado(self) -> list[str]:
        return self.pontos + [f"{self.nota:.2f}".replace(".", ",")]


def comparar(
    nome1: str,
    nome2: str,
    freq_maps: Sequence[dict[str, int]] | None,
    *,
    incluir_abreviaturas: bool = True,
) -> ResultadoNome:
    pontos = ["0,0"] * 7
    nota = 0.0

    parts1 = nome1.split()
    parts2 = nome2.split()
    if not parts1 or not parts2:
        return ResultadoNome(pontos, nota)

    t1 = len(parts1)
    if parts1[0] == parts2[0]:
        nota += 1
        pontos[0] = "1,0"
    if parts1[-1] == parts2[-1]:
        nota += 1
        pontos[1] = "1,0"

    inter = sum(1 for f in parts1 if f in parts2)
    incr = inter / t1
    nota += incr
    pontos[2] = f"{incr:.2f}".replace(".", ",")

    if freq_maps:
        first, middle, last = freq_maps
        raros = 0
        if first.get(parts1[0], 0) < 5:
            raros += 1
        for p in parts1[1:-1]:
            if middle.get(p, 0) < 5:
                raros += 1
        if last.get(parts1[-1], 0) < 5:
            raros += 1
        incr = raros / t1
        nota += incr
        pontos[3] = f"{incr:.2f}".replace(".", ",")

        comuns = 0
        if first.get(parts1[0], 0) > 1000:
            comuns += 1
        for p in parts1[1:-1]:
            if middle.get(p, 0) > 1000:
                comuns += 1
        if last.get(parts1[-1], 0) > 1000:
            comuns += 1
        incr = -(comuns / t1)
        nota += incr
        pontos[4] = f"{incr:.2f}".replace(".", ",")

    parecidos = 0
    for p1 in parts1:
        s1 = soundex(p1)
        if any(sum(c1 == c2 for c1, c2 in zip(s1, soundex(p2))) >= 3 for p2 in parts2):
            parecidos += 1
    incr = (parecidos / t1) * 0.8
    nota += incr
    pontos[5] = f"{incr:.2f}".replace(".", ",")

    if incluir_abreviaturas:
        abrevs = 0
        for p1 in parts1:
            if len(p1) == 1 and any(p2.startswith(p1) for p2 in parts2):
                abrevs += 1
        for p2 in parts2:
            if len(p2) == 1 and any(p1.startswith(p2) for p1 in parts1):
                abrevs += 1
        incr = (abrevs / t1) * 0.5
        nota += incr
        pontos[6] = f"{incr:.2f}".replace(".", ",")

    return ResultadoNome(pontos, nota)
