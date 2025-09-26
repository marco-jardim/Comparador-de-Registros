from __future__ import annotations
import re, unicodedata
from typing import List
from unidecode import unidecode
from jellyfish import soundex as _j_soundex

try:
    from Levenshtein import distance as levenshtein
except ImportError:  # pragma: no cover - fallback para ambientes sem extensão nativa

    def levenshtein(a: str, b: str) -> int:
        if a == b:
            return 0
        if not a:
            return len(b)
        if not b:
            return len(a)

        prev_row = list(range(len(b) + 1))
        for i, ca in enumerate(a, start=1):
            cur_row = [i]
            for j, cb in enumerate(b, start=1):
                insert_cost = cur_row[j - 1] + 1
                delete_cost = prev_row[j] + 1
                replace_cost = prev_row[j - 1] + (ca != cb)
                cur_row.append(min(insert_cost, delete_cost, replace_cost))
            prev_row = cur_row
        return prev_row[-1]


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
