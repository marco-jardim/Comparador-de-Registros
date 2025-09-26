from __future__ import annotations

import pytest

from comparators.nomes import comparar


def test_nomes_with_frequency_maps_and_abbreviations():
    freq_maps = (
        {"ana": 1, "joao": 2000},  # primeiros nomes
        {"m": 2, "maria": 3},      # nomes do meio
        {"silva": 1001, "souza": 10},  # últimos nomes
    )
    resultado = comparar("ana m silva", "ana maria silva", freq_maps)
    assert resultado.pontos[0] == "1,0"
    assert resultado.pontos[1] == "1,0"
    assert resultado.pontos[2] == "0,67"
    assert resultado.pontos[3] == "0,67"
    assert resultado.pontos[4] == "-0,33"
    assert resultado.pontos[5] != "0,00"  # som similarity
    abreviacao_bonus = float(resultado.pontos[6].replace(",", "."))
    assert pytest.approx(abreviacao_bonus, 0.001) == 0.17
    assert resultado.nota > 3


def test_nomes_without_abbreviation_bonus():
    freq_maps = ({"ana": 1}, {"maria": 1}, {"silva": 1})
    resultado = comparar(
        "ana m silva",
        "ana maria silva",
        freq_maps,
        incluir_abreviaturas=False,
    )
    assert float(resultado.pontos[6].replace(",", ".")) == 0.0


def test_nomes_without_frequency_maps():
    resultado = comparar("ana", "ana", None)
    assert resultado.pontos[0] == "1,0"
    assert float(resultado.pontos[3].replace(",", ".")) == 0.0
    assert float(resultado.pontos[4].replace(",", ".")) == 0.0
