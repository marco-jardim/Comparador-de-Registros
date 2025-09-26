from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from . import data, logradouro, localidade, nomes, texto


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
