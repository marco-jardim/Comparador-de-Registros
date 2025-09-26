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
