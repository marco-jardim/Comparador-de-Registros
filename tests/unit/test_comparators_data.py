from __future__ import annotations

from comparators import core
from comparators.data import comparar as comparar_data


def test_comparar_data_equal_dates():
    resultado = comparar_data("20200101", "20200101")
    assert resultado.pontos == ["1,0", "0,0", "0,0", "0,0", "0,0"]
    assert resultado.nota == 1
    assert resultado.formatado()[-1] == "1,00"


def test_comparar_data_distance_one():
    resultado = comparar_data("20200101", "20200102")
    assert resultado.pontos[1] == "1,0"
    assert resultado.nota == 1


def test_comparar_data_reversed_day():
    resultado = comparar_data("20200112", "20200121")
    assert resultado.pontos[2] == "1,0"
    assert resultado.nota == 1


def test_comparar_data_reversed_month():
    resultado = comparar_data("20211201", "20212101")
    assert resultado.pontos[3] == "1,0"
    assert resultado.nota == 1


def test_comparar_data_anagrams_in_year():
    resultado = comparar_data("20200101", "20020101")
    assert resultado.pontos[4] == "1,0"
    assert resultado.nota == 1


def test_comparacao_resultado_formata_pontos():
    resultado = core.ComparacaoResultado(["0,50"], 0.5)
    assert resultado.pontos_formatados == ["0,50", "0,50"]


def test_formatar_resultado_helper():
    assert core.formatar_resultado([0.5, 1]) == ["0,50", "1,00"]
