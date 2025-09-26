from __future__ import annotations

from dataclasses import dataclass

from .normalizacao import jaccard_ratio, normalizar, token_set_ratio


@dataclass
class ResultadoLogradouro:
    pontos: list[str]
    nota: float

    def formatado(self) -> list[str]:
        return self.pontos + [f"{self.nota:.2f}".replace(".", ",")]


def comparar(v1: str, v2: str) -> ResultadoLogradouro:
    dados1 = normalizar(v1)
    dados2 = normalizar(v2)

    pontos = ["0,0"] * 6
    nota = 0.0

    if dados1.via and dados1.via == dados2.via:
        nota += 1
        pontos[0] = "1,0"

    via_ratio = token_set_ratio(dados1.via_tokens, dados2.via_tokens)
    via_score = via_ratio * 0.8
    nota += via_score
    pontos[1] = f"{via_score:.2f}".replace(".", ",")

    if dados1.numero and dados2.numero and dados1.numero == dados2.numero:
        nota += 1
        pontos[2] = "1,0"
    elif dados1.numero == "sn" and dados2.numero == "sn":
        nota += 0.5
        pontos[2] = "0,5"

    compl_ratio = token_set_ratio(dados1.complemento_tokens, dados2.complemento_tokens)
    compl_score = compl_ratio * 0.5
    nota += compl_score
    pontos[3] = f"{compl_score:.2f}".replace(".", ",")

    full_ratio = token_set_ratio(dados1.all_tokens, dados2.all_tokens)
    full_score = full_ratio * 0.8
    nota += full_score
    pontos[4] = f"{full_score:.2f}".replace(".", ",")

    jacc = jaccard_ratio(dados1.all_tokens, dados2.all_tokens)
    jacc_score = jacc * 0.5
    nota += jacc_score
    pontos[5] = f"{jacc_score:.2f}".replace(".", ",")

    return ResultadoLogradouro(pontos, nota)
