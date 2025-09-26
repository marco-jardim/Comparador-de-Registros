from __future__ import annotations

from comparators import (
    build_criterios_labels,
    comparar_data,
    comparar_logradouro,
    comparar_nome,
    comparar_numero,
    comparar_texto,
)


def test_comparators_package_exports_delegate_to_modules():
    assert comparar_data("20200101", "20200101").nota == 1
    assert comparar_texto("a b", "a b", {"a": 1, "b": 1}).nota >= 3
    assert comparar_nome("ana", "ana", None).nota >= 2
    assert comparar_logradouro("Rua A 10", "Rua A 10").nota > 2
    assert comparar_numero("10", "10").nota >= 3


def test_build_criterios_labels_includes_numeric_entries():
    pares = [
        (0, 1, "M", "ano"),
        (1, 2, "D", "data"),
    ]
    criterios = build_criterios_labels(pares)

    assert "ano num prox arred" in criterios
    assert criterios[-1] == "nota final"
