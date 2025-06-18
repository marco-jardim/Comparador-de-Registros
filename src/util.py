from __future__ import annotations
import re, unicodedata
from typing import List
from unidecode import unidecode
from jellyfish import soundex as _j_soundex
from Levenshtein import distance as levenshtein


__all__ = ["padroniza", "soundex", "levenshtein", "minusculo_sem_acento"]


_STOP_WORDS = {"de", "do", "da", "dos", "das"}
_SUFIXOS = (
    " junior", " jr", " neto", " bisneto",
    " filho", " filha", " sobrinha", " sobrinho",
    " segundo", " terceiro"
)


def minusculo_sem_acento(s: str) -> str:
    s = unidecode(s.lower().strip())
    return s


def _remove_caracteres_especiais(s: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", s)


def padroniza(nome: str) -> str:
    if not nome.strip():
        return ""
    s = minusculo_sem_acento(nome)
    s = _remove_caracteres_especiais(s)
    # remove partículas
    partes = [p for p in s.split() if p not in _STOP_WORDS]
    s = " ".join(partes)
    # remove sufixos de parentesco
    for suf in _SUFIXOS:
        if s.endswith(suf):
            s = s[: -len(suf)]
            break
    return s.strip()


def soundex(palavra: str) -> str:
    """Delegamos ao jellyfish. Sempre retorna 4 caracteres."""
    if not palavra:
        return "0000"
    return _j_soundex(palavra) or "0000"
