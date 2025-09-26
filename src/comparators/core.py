from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from . import data, logradouro, localidade, nomes, numeros, texto


@dataclass
class ComparacaoResultado:
    """Container que armazena os pontos parciais e a nota final."""

    pontos: list[str]
    nota: float

    @property
    def pontos_formatados(self) -> list[str]:
        return self.pontos + [f"{self.nota:.2f}".replace(".", ",")]


def comparar_data(v1: str, v2: str) -> ComparacaoResultado:
    return data.comparar(v1, v2)


def comparar_nome(
    v1: str,
    v2: str,
    freq_maps: Sequence[dict[str, int]] | None = None,
    *,
    incluir_abreviaturas: bool = True,
) -> ComparacaoResultado:
    return nomes.comparar(v1, v2, freq_maps, incluir_abreviaturas=incluir_abreviaturas)


def comparar_texto(v1: str, v2: str, freq: dict[str, int] | None = None) -> ComparacaoResultado:
    return texto.comparar(v1, v2, freq or {})


def comparar_localidade(v1: str, v2: str) -> ComparacaoResultado:
    return localidade.comparar(v1, v2)


def comparar_logradouro(v1: str, v2: str) -> ComparacaoResultado:
    return logradouro.comparar(v1, v2)


def formatar_resultado(pontos: Iterable[float]) -> list[str]:
    return [f"{p:.2f}".replace(".", ",") for p in pontos]


def comparar_numero(v1: str, v2: str) -> ComparacaoResultado:
    return numeros.comparar(v1, v2)


def build_criterios_labels(pares: Sequence[tuple[int, int, str, str]]) -> list[str]:
    header_criterios: list[str] = []
    for _, _, tipo, nome in pares:
        t = (tipo or "").upper()
        if t == "D":
            header_criterios += [
                f"{nome} dt iguais",
                f"{nome} dt ap 1digi",
                f"{nome} dt inv dia",
                f"{nome} dt inv mes",
                f"{nome} dt inv ano",
            ]
        elif t == "C":
            header_criterios += [
                f"{nome} uf igual",
                f"{nome} uf prox",
                f"{nome} local igual",
                f"{nome} local prox",
            ]
        elif t == "L":
            header_criterios += [
                f"{nome} via igual",
                f"{nome} via prox",
                f"{nome} numero igual",
                f"{nome} compl prox",
                f"{nome} texto prox",
                f"{nome} tokens jacc",
            ]
        elif t == "M":
            header_criterios += [
                f"{nome} num igual",
                f"{nome} num prox abs",
                f"{nome} num prox rel",
                f"{nome} num prox arred",
            ]
        else:
            header_criterios += [
                f"{nome} prim frag igual",
                f"{nome} ult frag igual",
                f"{nome} qtd frag iguais",
                f"{nome} qtd frag raros",
                f"{nome} qtd frag comuns",
                f"{nome} qtd frag muito parec",
                f"{nome} qtd frag abrev",
            ]
    header_criterios.append("nota final")
    return header_criterios
