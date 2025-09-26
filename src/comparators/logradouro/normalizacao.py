from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable

try:
    from rapidfuzz import fuzz
except ImportError:  # pragma: no cover - fallback quando rapidfuzz não estiver disponível
    import difflib

    class _Fuzz:
        @staticmethod
        def token_set_ratio(str1: str, str2: str) -> float:
            tokens1 = " ".join(sorted(str1.split()))
            tokens2 = " ".join(sorted(str2.split()))
            if not tokens1 or not tokens2:
                return 0.0
            return difflib.SequenceMatcher(None, tokens1, tokens2).ratio() * 100.0

    fuzz = _Fuzz()

from unidecode import unidecode

from comparators.utils import tokens_to_string

_ADDRESS_STOP_WORDS = {"de", "da", "do", "das", "dos", "e"}
_LOGRADOURO_EQUIV = {
    "av": "avenida",
    "avd": "avenida",
    "aven": "avenida",
    "avenida": "avenida",
    "ave": "avenida",
    "al": "alameda",
    "alm": "alameda",
    "alameda": "alameda",
    "r": "rua",
    "rua": "rua",
    "rod": "rodovia",
    "rodovia": "rodovia",
    "estr": "estrada",
    "est": "estrada",
    "estrada": "estrada",
    "tv": "travessa",
    "trav": "travessa",
    "travessa": "travessa",
    "pc": "praca",
    "prac": "praca",
    "praca": "praca",
    "lgo": "largo",
    "largo": "largo",
    "vl": "vila",
    "vila": "vila",
    "jd": "jardim",
    "jardim": "jardim",
    "pq": "parque",
    "pqe": "parque",
    "parque": "parque",
}
_COMPLEMENT_EQUIV = {
    "ap": "apto",
    "apt": "apto",
    "apto": "apto",
    "apartamento": "apto",
    "apart": "apto",
    "bl": "bloco",
    "blc": "bloco",
    "bloco": "bloco",
    "cj": "conjunto",
    "cjto": "conjunto",
    "conj": "conjunto",
    "conjunto": "conjunto",
    "sala": "sala",
    "sl": "sala",
    "casa": "casa",
    "cs": "casa",
    "andar": "andar",
    "qd": "quadra",
    "quadra": "quadra",
    "lt": "lote",
    "lote": "lote",
    "fundos": "fundos",
    "frente": "frente",
    "galpao": "galpao",
    "blocos": "bloco",
    "box": "box",
}
_NUM_TOKEN_MAP = {
    "n": "numero",
    "no": "numero",
    "num": "numero",
    "numero": "numero",
    "nro": "numero",
    "nr": "numero",
    "nro.": "numero",
}
_SEM_NUM_TOKENS = {"sn", "s", "semnumero", "sem_numero", "semn"}
_COMPLEMENT_MARKERS = set(_COMPLEMENT_EQUIV.values()) | {
    "bloco",
    "apto",
    "casa",
    "conjunto",
    "quadra",
    "lote",
    "sala",
    "andar",
    "fundos",
    "frente",
    "box",
    "galpao",
}
_ALLOW_SINGLE_AFTER = {"bloco", "casa", "apto", "quadra", "lote", "andar", "box"}
_RE_DIGIT_LETTER = re.compile(r"(\d+)([a-z])")
_RE_LETTER_DIGIT = re.compile(r"([a-z])(\d+)")


def tokenize(valor: str) -> list[str]:
    if not valor:
        return []
    txt = unidecode(valor.lower())
    txt = txt.replace("º", " ").replace("°", " ").replace("ª", " ")
    txt = re.sub(r"[#'\"()\[\]{}]", " ", txt)
    txt = txt.replace("-", " ").replace("/", " ").replace("\\", " ")
    txt = re.sub(r"[.,;:]", " ", txt)
    txt = _RE_DIGIT_LETTER.sub(r"\1 \2", txt)
    txt = _RE_LETTER_DIGIT.sub(r"\1 \2", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    if not txt:
        return []

    tokens: list[str] = []
    for raw in txt.split():
        tok = raw.strip()
        if not tok:
            continue
        tok = _NUM_TOKEN_MAP.get(tok, tok)
        tok = _LOGRADOURO_EQUIV.get(tok, tok)
        tok = _COMPLEMENT_EQUIV.get(tok, tok)
        if tok in _SEM_NUM_TOKENS:
            tok = "semnumero"
        if tok in _ADDRESS_STOP_WORDS:
            continue
        tokens.append(tok)
    return tokens


@dataclass
class LogradouroNormalizado:
    via: str
    via_tokens: list[str]
    numero: str
    complemento: str
    complemento_tokens: list[str]
    all_tokens: list[str]


def normalizar(valor: str) -> LogradouroNormalizado:
    tokens = tokenize(valor)
    if not tokens:
        return LogradouroNormalizado("", [], "", "", [], [])

    via_tokens: list[str] = []
    complemento_tokens: list[str] = []
    numero = ""
    complement_mode = False
    last_marker: str | None = None

    for tok in tokens:
        if tok == "numero":
            complement_mode = True
            last_marker = None
            continue
        if tok == "semnumero":
            numero = "sn"
            complement_mode = True
            last_marker = None
            continue
        if tok.isdigit():
            val = tok.lstrip("0") or "0"
            if not numero:
                numero = val
            else:
                complemento_tokens.append(val)
            complement_mode = True
            last_marker = None
            continue
        if tok in _COMPLEMENT_MARKERS:
            complemento_tokens.append(tok)
            complement_mode = True
            last_marker = tok
            continue
        if len(tok) == 1 and (last_marker in _ALLOW_SINGLE_AFTER or complement_mode):
            complemento_tokens.append(tok)
            continue
        if complement_mode:
            complemento_tokens.append(tok)
        else:
            via_tokens.append(tok)
        last_marker = None

    all_tokens: list[str] = []
    all_tokens.extend(via_tokens)
    if numero:
        all_tokens.append(numero)
    all_tokens.extend(complemento_tokens)

    return LogradouroNormalizado(
        via=tokens_to_string(via_tokens),
        via_tokens=via_tokens,
        numero=numero,
        complemento=tokens_to_string(complemento_tokens),
        complemento_tokens=complemento_tokens,
        all_tokens=all_tokens,
    )


def token_set_ratio(tokens1: Iterable[str], tokens2: Iterable[str]) -> float:
    list1, list2 = list(tokens1), list(tokens2)
    if not list1 or not list2:
        return 0.0

    base_score = fuzz.token_set_ratio(" ".join(list1), " ".join(list2)) / 100.0

    counter1 = Counter(list1)
    counter2 = Counter(list2)
    intersection = sum((counter1 & counter2).values())
    max_len = max(len(list1), len(list2))
    if max_len == 0:
        return 0.0

    coverage = intersection / max_len
    return base_score * coverage


def jaccard_ratio(tokens1: Iterable[str], tokens2: Iterable[str]) -> float:
    set1, set2 = set(tokens1), set(tokens2)
    if not set1 or not set2:
        return 0.0
    inter = len(set1 & set2)
    union = len(set1 | set2)
    if union == 0:
        return 0.0
    return inter / union
