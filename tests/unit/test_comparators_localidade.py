from __future__ import annotations

import pytest

from comparators.localidade import comparar


def test_localidade_equal_codes():
    resultado = comparar("SP1234", "SP1234")
    assert resultado.pontos == ["1,0", "0,0", "1,0", "0,0"]
    assert resultado.nota == 2


def test_localidade_similar_uf_and_code():
    resultado = comparar("SP1234", "SQ1235")
    # SP vs SQ -> distância 1 (0,5) e 1234 vs 1235 -> distância 1 (0,8)
    assert resultado.pontos[1] == "0,5"
    assert resultado.pontos[3] == "0,8"
    assert pytest.approx(resultado.nota, 0.001) == 1.3


def test_localidade_invalid_length_returns_zero():
    resultado = comparar("SP123", "SP1234")
    assert resultado.nota == 0
    assert all(ponto == "0,0" for ponto in resultado.pontos)
