"""Comparators package providing per-type scoring functions."""

from .core import (
    ComparacaoResultado,
    comparar_data,
    comparar_logradouro,
    comparar_localidade,
    comparar_nome,
    comparar_texto,
)

__all__ = [
    "ComparacaoResultado",
    "comparar_data",
    "comparar_logradouro",
    "comparar_localidade",
    "comparar_nome",
    "comparar_texto",
]
