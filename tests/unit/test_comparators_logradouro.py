from __future__ import annotations

import pytest

from comparators.logradouro.comparador import comparar


def test_logradouro_exact_match_scores_all_components():
    resultado = comparar("Rua das Flores 123 Bloco A", "Rua das Flores 123 Bloco A")
    assert resultado.pontos[0] == "1,0"
    assert resultado.pontos[1] == "0,80"
    assert resultado.pontos[2] == "1,0"
    assert resultado.pontos[5] == "0,50"
    assert resultado.nota > 3


def test_logradouro_sem_numero_partial_score():
    resultado = comparar("Rua das Flores SN", "Rua das Flores s/n")
    assert resultado.pontos[2] == "1,0"
    assert resultado.nota > 1


def test_logradouro_resultado_formatado_adds_total():
    resultado = comparar("Rua A 10", "Rua A 10")
    formatted = resultado.formatado()
    total = f"{resultado.nota:.2f}".replace(".", ",")
    assert formatted[-1] == total
    assert len(formatted) == len(resultado.pontos) + 1
