"""Gerador de amostras sintéticas.

Este módulo centraliza a criação de dados aleatórios utilizados
pelos testes e pela GUI.
"""

from __future__ import annotations

import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

import pandas as pd

__all__ = ["random_name", "random_date", "maybe_typo", "generate_sample"]

random.seed(42)

MALE_FIRST: List[str] = [
    "João", "Pedro", "Lucas", "Gabriel", "Marcos", "Felipe", "Rafael",
    "Carlos", "Bruno", "Ricardo",
]
FEMALE_FIRST: List[str] = [
    "Maria", "Ana", "Beatriz", "Larissa", "Juliana", "Camila", "Patrícia",
    "Aline", "Fernanda", "Vanessa",
]
LAST_NAMES: List[str] = [
    "Silva", "Souza", "Oliveira", "Santos", "Pereira", "Lima", "Costa",
    "Gomes", "Ribeiro", "Almeida", "Nunes", "Carvalho", "Araujo",
    "Rodrigues", "Barbosa",
]

TYPO_FUNCS = [
    lambda s: s[:-1] if len(s) > 3 else s,
    lambda s: s + s[-1] if len(s) > 3 else s,
    lambda s: s.replace("a", "á", 1) if "a" in s else s,
    lambda s: s.replace("e", "3", 1) if "e" in s else s,
    lambda s: s[1:] + s[0] if len(s) > 3 else s,
]


def random_name(gender: str = "any") -> str:
    pool = FEMALE_FIRST + MALE_FIRST if gender == "any" else (
        FEMALE_FIRST if gender == "female" else MALE_FIRST
    )
    return f"{random.choice(pool)} {random.choice(LAST_NAMES)}"


def random_date(start_year: int = 1980, end_year: int = 2010) -> str:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return (
        start + timedelta(days=random.randint(0, (end - start).days))
    ).strftime("%Y%m%d")


def maybe_typo(name: str, prob: float = 0.15) -> str:
    if random.random() < prob:
        func = random.choice(TYPO_FUNCS)
        return " ".join(
            func(p) if random.random() < 0.5 else p for p in name.split()
        )
    return name


def _unique_var(base: str, used: set[str]) -> str:
    suffix = ""
    while base + suffix in used:
        suffix += random.choice(string.ascii_uppercase)
    used.add(base + suffix)
    return base + suffix


def _generate_headers(n_cols: int) -> list[str]:
    base_names = [
        "NOME",
        "DATANASC",
        "ENDERECO",
        "CPF",
        "RG",
        "CIDADE",
        "ESTADO",
        "PAIS",
        "TELEFONE",
        "EMAIL",
        "PROFISSAO",
        "EMPRESA",
        "SALARIO",
        "CEP",
        "RUA",
        "BAIRRO",
        "NUM",
        "OBS",
        "INFO",
        "CODIGO",
    ]
    used: set[str] = set()
    headers: list[str] = []
    for _ in range(n_cols):
        prefix = random.choice("CR")
        base = random.choice(base_names)
        var = _unique_var(base, used)
        cd = random.choice("CD")
        n1 = random.randint(1, 99)
        n2 = random.randint(0, 9)
        headers.append(f"{prefix}_{var},{cd},{n1},{n2}")
    return headers


def _random_cell() -> str:
    if random.random() < 0.5:
        return maybe_typo(random_name())
    return random_date()


def generate_sample(
    n: int,
    out_path: Path,
    *,
    sep: str = "|",
    progress_cb=None,
) -> None:
    """Gera ``n`` linhas de dados sintéticos em ``out_path``.

    O número de colunas é aleatório (30‑100) e os nomes seguem o formato
    ``[C|R]_VAR,C|D,numero,outro``. O separador padrão é ``|``,
    mas pode ser alterado pelo parâmetro ``sep``.
    """

    n_cols = random.randint(30, 100)
    cols = _generate_headers(n_cols)
    rows: List[dict[str, str]] = []
    for i in range(n):
        row = {c: _random_cell() for c in cols}
        rows.append(row)
        if progress_cb and (i + 1) % max(1, n // 100) == 0:
            progress_cb(int((i + 1) / n * 100))
    pd.DataFrame(rows, columns=cols).to_csv(out_path, sep=sep, index=False)


