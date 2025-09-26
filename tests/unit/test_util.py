from __future__ import annotations

import pytest

import util


def test_minusculo_sem_acento_removes_accents_and_lowercases():
    assert util.minusculo_sem_acento(" ÁÉÍ ÓÚ ") == "aei ou"


def test_padroniza_removes_stop_words_and_suffix():
    resultado = util.padroniza("  João da Silva Jr.  ")
    assert resultado == "joao silva"


def test_padroniza_returns_empty_for_blank_input():
    assert util.padroniza("   ") == ""


def test_soundex_returns_code_for_word():
    codigo = util.soundex("bruno")
    assert codigo == "B650"


def test_soundex_returns_zeros_for_empty():
    assert util.soundex("") == "0000"
