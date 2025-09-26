from __future__ import annotations

from comparators import comparar_numero


def test_comparar_numero_exact_match_awards_full_points():
    resultado = comparar_numero("2020", "2020")

    assert resultado.pontos[0] == "1,0"
    assert resultado.nota >= 3.5


def test_comparar_numero_handles_integer_proximity():
    resultado = comparar_numero("2020", "2021")

    abs_score = float(resultado.pontos[1].replace(",", "."))
    arred_score = float(resultado.pontos[3].replace(",", "."))

    assert abs_score > 0
    assert arred_score == 1.0
    assert resultado.nota > 1.0


def test_comparar_numero_parses_floats_with_commas():
    resultado = comparar_numero("10,50", "10.5")

    assert resultado.pontos[0] == "1,0"
    assert float(resultado.pontos[2].replace(",", ".")) == 1.0
    assert resultado.nota >= 3.5
