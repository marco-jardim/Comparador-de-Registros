from __future__ import annotations

from comparators import comparar_data, comparar_logradouro, comparar_nome, comparar_texto


def test_comparators_package_exports_delegate_to_modules():
    assert comparar_data("20200101", "20200101").nota == 1
    assert comparar_texto("a b", "a b", {"a": 1, "b": 1}).nota >= 3
    assert comparar_nome("ana", "ana", None).nota >= 2
    assert comparar_logradouro("Rua A 10", "Rua A 10").nota > 2
