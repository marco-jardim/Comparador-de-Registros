from __future__ import annotations

import pytest

from comparators.logradouro.normalizacao import (
    LogradouroNormalizado,
    jaccard_ratio,
    normalizar,
    tokenize,
    token_set_ratio,
)
from comparators.utils import tokens_to_string


def test_tokenize_and_normalizar_extracts_components():
    tokens = tokenize("Rua dos Andradas, nº 123 - Bl A")
    assert tokens[:2] == ["rua", "andradas"]
    assert "123" in tokens
    assert "bloco" in tokens

    normalizado = normalizar("Rua dos Andradas, nº 123 - Bl A")
    assert isinstance(normalizado, LogradouroNormalizado)
    assert normalizado.via == "rua andradas"
    assert normalizado.numero == "123"
    assert normalizado.complemento_tokens[-1] == "a"
    assert "123" in normalizado.all_tokens


def test_similarity_helpers():
    tokens1 = ["rua", "andradas", "123"]
    tokens2 = ["rua", "andradas", "123"]
    assert token_set_ratio(tokens1, tokens2) == 1.0
    assert jaccard_ratio(tokens1, tokens2) == 1.0

    tokens3 = ["rua", "andradas"]
    assert token_set_ratio(tokens1, tokens3) < 1.0
    assert jaccard_ratio(tokens1, tokens3) < 1.0


def test_tokens_to_string_skips_empty_tokens():
    assert tokens_to_string(["rua", "", "123"]) == "rua 123"


def test_normalizar_handles_sem_numero_and_multiple_numbers():
    normalizado = normalizar("Av Brasil s/n bloco 4 apto 501")
    assert normalizado.numero == "sn"
    assert "4" in normalizado.complemento_tokens
    assert "501" in normalizado.complemento_tokens
    assert "semnumero" not in normalizado.via_tokens


def test_normalizar_allows_single_letter_after_marker():
    normalizado = normalizar("Rua Alpha bloco B casa C")
    assert "b" in normalizado.complemento_tokens
    assert "c" in normalizado.complemento_tokens


def test_tokenize_equivalents_and_stop_words():
    tokens = tokenize("Rua de Teste n 123 ap 4")
    assert "numero" in tokens
    assert "apto" in tokens
    assert "de" not in tokens
