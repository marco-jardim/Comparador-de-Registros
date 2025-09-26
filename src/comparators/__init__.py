"""Comparators package providing per-type scoring functions."""

from .core import (
    ComparacaoResultado,
    build_criterios_labels,
    comparar_data,
    comparar_logradouro,
    comparar_localidade,
    comparar_nome,
    comparar_numero,
    comparar_texto,
)

__all__ = [
    "ComparacaoResultado",
    "build_criterios_labels",
    "comparar_data",
    "comparar_logradouro",
    "comparar_localidade",
    "comparar_nome",
    "comparar_numero",
    "comparar_texto",
]
