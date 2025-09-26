from __future__ import annotations

import pytest

from comparators.texto import comparar


def test_texto_identical_tokens_with_frequency_bias():
    freq = {"ana": 4, "maria": 3}
    resultado = comparar("ana maria", "ana maria", freq)
    assert resultado.pontos[0] == "1,0"
    assert resultado.pontos[1] == "1,0"
    assert resultado.pontos[2] == "1,00"
    assert resultado.pontos[3] == "1,00"
    assert pytest.approx(float(resultado.pontos[4].replace(",", ".")), abs=1e-6) == 0.0
    assert resultado.pontos[5] == "0,80"
    assert float(resultado.pontos[6].replace(",", ".")) == 0.0
    assert pytest.approx(resultado.nota, 0.001) == 4.8


def test_texto_date_like_skips_frequency_penalties():
    resultado = comparar("20200101", "20200101", {})
    assert float(resultado.pontos[3].replace(",", ".")) == 0.0
    assert float(resultado.pontos[4].replace(",", ".")) == 0.0
    assert resultado.nota >= 3  # primeiro, último e interseção


def test_texto_handles_empty_inputs():
    resultado = comparar("", "qualquer", {})
    assert resultado.nota == 0
    assert all(p == "0,0" for p in resultado.pontos)


def test_texto_common_and_rare_tokens_balance():
    freq = {"unico": 1, "comum": 5000}
    resultado = comparar("unico comum", "comum", freq)
    raros = float(resultado.pontos[3].replace(",", "."))
    comuns = float(resultado.pontos[4].replace(",", "."))
    assert raros > 0
    assert comuns < 0
