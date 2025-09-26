from __future__ import annotations

import os
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, ROUND_HALF_UP
from typing import Any
import time

from comparators import (
    comparar_data,
    comparar_logradouro,
    comparar_localidade,
    comparar_nome,
    comparar_texto,
)
import freqBuilder as fb  # novo
import util

DFMT = lambda x: format(Decimal(x).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP), "f")


# Índices para saber em qual fatia da lista de frequências procurar
PACIENTE, MAE = 0, 1

# Globals used by worker processes
_WORK_PARES: list[tuple[int, int, str, str]] = []
_WORK_FREQ_MAPS: dict[int, Any] = {}


def _init_worker(pares, freq_maps):
    """Initializer for worker processes."""
    global _WORK_PARES, _WORK_FREQ_MAPS
    _WORK_PARES = pares
    _WORK_FREQ_MAPS = freq_maps


def _process_row(row: tuple) -> list:
    """Process a single CSV row (tuple of values)."""
    pontos_linha: list[str] = []
    nota_total = 0.0
    for j, (idx1, idx2, tipo, _) in enumerate(_WORK_PARES):
        v1 = util.padroniza(str(row[idx1]))
        v2 = util.padroniza(str(row[idx2]))
        t = tipo.upper()
        freq_map = _WORK_FREQ_MAPS.get(j)
        if t == "D":
            resultado = comparar_data(v1, v2)
        elif t == "N":
            resultado = comparar_nome(v1, v2, freq_map)
        elif t == "C":
            resultado = comparar_localidade(v1, v2)
        elif t == "L":
            resultado = comparar_logradouro(v1, v2)
        else:
            resultado = comparar_texto(v1, v2, freq_map or {})
        pontos_linha.extend(resultado.pontos)
        nota_total += resultado.nota
    pontos_linha.append(DFMT(nota_total).replace(".", ","))
    return list(row) + pontos_linha


def _comparar_nome_flag(
    nome1: str,
    nome2: str,
    freq_maps: list[dict[str, int]] | None,
    flag: int,
):
    if not freq_maps:
        return comparar_nome(nome1, nome2, None)

    inicio = flag * 3
    subset = freq_maps[inicio : inicio + 3]
    if len(subset) < 3:
        return comparar_nome(nome1, nome2, None)
    return comparar_nome(nome1, nome2, subset)


def processar(
    arquivo_entrada: str,
    arquivo_saida: str,
    idxs: tuple[int, int, int, int, int, int],
    cache_dir: str = ".freq_cache",
    *,
    sep: str = ";",
    sort_by: str | None = "nota final",
    ascending: bool = False,
) -> None:
    Nome1, Mae1, Nasc1, Nome2, Mae2, Nasc2 = idxs
    freq_maps = fb.build_if_missing(arquivo_entrada, idxs, out_dir=cache_dir, sep=sep)

    df = pd.read_csv(arquivo_entrada, sep=sep, dtype=str).fillna("")

    linhas_saida = []
    for _, row in df.iterrows():
        # Normalização
        n1 = util.padroniza(row.iloc[Nome1])
        m1 = util.padroniza(row.iloc[Mae1])
        d1 = str(row.iloc[Nasc1])

        n2 = util.padroniza(row.iloc[Nome2])
        m2 = util.padroniza(row.iloc[Mae2])
        d2 = str(row.iloc[Nasc2])

        pontos: list[str] = ["0,0"] * 20  # 0..18 + nota final no 19
        nota_total = 0.0

        if n1 and n2:
            resultado = _comparar_nome_flag(n1, n2, freq_maps, PACIENTE)
            pontos[0:7] = resultado.pontos
            nota_total += resultado.nota
        if m1 and m2:
            resultado = _comparar_nome_flag(m1, m2, freq_maps, MAE)
            pontos[7:14] = resultado.pontos
            nota_total += resultado.nota
        if len(d1) == 8 and len(d2) == 8:
            resultado = comparar_data(d1, d2)
            pontos[14:19] = resultado.pontos
            nota_total += resultado.nota

        pontos[19] = DFMT(nota_total).replace(".", ",")

        linhas_saida.append(list(row) + pontos)

    header_criterios = [
        "prim frag igual",
        "ult frag igual",
        "qtd frag iguais",
        "qtd frag raros",
        "qtd frag comuns",
        "qtd frag muito parec",
        "qtd frag abrev",
        "mae prim frag igual",
        "mae ult frag igual",
        "mae qtd frag iguais",
        "mae qtd frag raros",
        "mae qtd frag comuns",
        "mae qtd frag muito parec",
        "mae qtd frag abrev",
        "dt iguais",
        "dt ap 1digi",
        "dt inv dia",
        "dt inv mes",
        "dt inv ano",
        "nota final",
    ]
    header = list(df.columns) + header_criterios
    out_df = pd.DataFrame(linhas_saida, columns=header)
    if sort_by is not None:
        if sort_by not in out_df.columns:
            raise ValueError(f"Coluna '{sort_by}' não encontrada para ordenação")
        out_df.sort_values(by=sort_by, ascending=ascending, inplace=True)

    out_df.to_csv(f"{arquivo_saida}.csv", sep=sep, index=False)


def _build_freq_map(df: pd.DataFrame, idx1: int, idx2: int) -> dict[str, int]:
    counter: dict[str, int] = {}
    for val in pd.concat([df.iloc[:, idx1], df.iloc[:, idx2]]).astype(str):
        parts = util.padroniza(val).split()
        for p in parts:
            counter[p] = counter.get(p, 0) + 1
    return counter


def _build_name_freq_map(df: pd.DataFrame, idx1: int, idx2: int) -> list[dict[str, int]]:
    """
    Build frequency maps for first, middle, and last name parts.

    This function processes two columns of a DataFrame, extracts name parts
    (first, middle, and last), and counts their occurrences across both columns.

    Parameters:
        df (pd.DataFrame): The input DataFrame containing name data.
        idx1 (int): The index of the first column to process.
        idx2 (int): The index of the second column to process.

    Returns:
        list[dict[str, int]]: A list containing three dictionaries:
            - The first dictionary maps first name parts to their frequencies.
            - The second dictionary maps middle name parts to their frequencies.
            - The third dictionary maps last name parts to their frequencies.
    """
    first: dict[str, int] = {}
    middle: dict[str, int] = {}
    last: dict[str, int] = {}
    for val in pd.concat([df.iloc[:, idx1], df.iloc[:, idx2]]).astype(str):
        parts = util.padroniza(val).split()
        if not parts:
            continue
        first_part, last_part = parts[0], parts[-1]
        first[first_part] = first.get(first_part, 0) + 1
        last[last_part] = last.get(last_part, 0) + 1
        for m in parts[1:-1]:
            middle[m] = middle.get(m, 0) + 1
    return [first, middle, last]


def processar_generico(
    arquivo_entrada: str,
    arquivo_saida: str,
    pares: list[tuple[int, int, str, str]],
    *,
    sep: str = "|",
    progress_cb=None,
    sort_by: str | None = "nota final",
    ascending: bool = False,
    workers: int | None = None,
) -> None:
    """Processa genericamente pares de colunas.

    ``pares`` contém ``(idx1, idx2, tipo, nome)`` onde ``tipo`` é ``"T"`` para
    strings, ``"C"`` para códigos de localidade, ``"L"`` para logradouros,
    ``"N"`` para nomes ou ``"D"`` para datas. ``nome`` é um rótulo para os
    campos.
    O delimitador das colunas é definido por ``sep`` (padrão ``"|"``).

    ``progress_cb`` recebe ``(pct, msg, eta)`` para atualizar uma barra de
    progresso opcional.
    ``workers`` define o número de processos para paralelizar o cálculo
    (``None`` usa ``os.cpu_count()``).
    """
    df = pd.read_csv(arquivo_entrada, sep=sep, dtype=str).fillna("")
    total = len(df)
    if progress_cb:
        progress_cb(0, f"0/{total}")

    freq_maps: dict[int, Any] = {}
    for i, (idx1, idx2, tipo, _) in enumerate(pares):
        t = tipo.upper()
        if t == "T":
            freq_maps[i] = _build_freq_map(df, idx1, idx2)
        elif t == "N":
            freq_maps[i] = _build_name_freq_map(df, idx1, idx2)
        else:
            freq_maps[i] = None

    linhas = []
    start = time.time()
    last_pct = -1
    last_eta_line = 0
    last_eta_time = start
    last_eta = 0.0

    if workers is None:
        workers = os.cpu_count() or 1
    if workers < 1:
        workers = 1

    if workers == 1:
        row_iter = df.itertuples(index=False, name=None)
        for i, row in enumerate(row_iter):
            pontos_linha: list[str] = []
            nota_total = 0.0
            for j, (idx1, idx2, tipo, _) in enumerate(pares):
                v1 = util.padroniza(str(row[idx1]))
                v2 = util.padroniza(str(row[idx2]))
                t = tipo.upper()
                freq_map = freq_maps.get(j)
                if t == "D":
                    resultado = comparar_data(v1, v2)
                elif t == "N":
                    resultado = comparar_nome(v1, v2, freq_map)
                elif t == "C":
                    resultado = comparar_localidade(v1, v2)
                elif t == "L":
                    resultado = comparar_logradouro(v1, v2)
                else:
                    resultado = comparar_texto(v1, v2, freq_map or {})
                pontos_linha.extend(resultado.pontos)
                nota_total += resultado.nota
            pontos_linha.append(DFMT(nota_total).replace(".", ","))
            linhas.append(list(row) + pontos_linha)
            now = time.time()
            if progress_cb and (
                (i + 1) % 1000 == 0 or i + 1 == total or int((i + 1) * 100 / total) != last_pct
            ):
                pct = int((i + 1) * 100 / total)
                if (i + 1) % 1000 == 0 or i + 1 == total:
                    elapsed = now - last_eta_time
                    lines = (i + 1) - last_eta_line
                    avg = elapsed / lines if lines else 0
                    last_eta = avg * (total - (i + 1))
                    last_eta_time = now
                    last_eta_line = i + 1
                else:
                    last_eta = max(0.0, last_eta - (now - last_eta_time))
                    last_eta_time = now
                progress_cb(pct, f"{i+1}/{total}", last_eta)
                last_pct = pct
    else:
        rows = list(df.itertuples(index=False, name=None))
        with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker, initargs=(pares, freq_maps)) as ex:
            for i, linha in enumerate(ex.map(_process_row, rows, chunksize=100)):
                linhas.append(linha)
                now = time.time()
                if progress_cb and (
                    (i + 1) % 1000 == 0 or i + 1 == total or int((i + 1) * 100 / total) != last_pct
                ):
                    pct = int((i + 1) * 100 / total)
                    if (i + 1) % 1000 == 0 or i + 1 == total:
                        elapsed = now - last_eta_time
                        lines = (i + 1) - last_eta_line
                        avg = elapsed / lines if lines else 0
                        last_eta = avg * (total - (i + 1))
                        last_eta_time = now
                        last_eta_line = i + 1
                    else:
                        last_eta = max(0.0, last_eta - (now - last_eta_time))
                        last_eta_time = now
                    progress_cb(pct, f"{i+1}/{total}", last_eta)
                    last_pct = pct

    if progress_cb and last_pct < 100:
        progress_cb(100, f"{total}/{total}", 0)

    header_criterios: list[str] = []
    for _, _, tipo, nome in pares:
        t = tipo.upper()
        if t == "D":
            header_criterios += [
                f"{nome} dt iguais",
                f"{nome} dt ap 1digi",
                f"{nome} dt inv dia",
                f"{nome} dt inv mes",
                f"{nome} dt inv ano",
            ]
        elif t == "C":
            header_criterios += [
                f"{nome} uf igual",
                f"{nome} uf prox",
                f"{nome} local igual",
                f"{nome} local prox",
            ]
        elif t == "L":
            header_criterios += [
                f"{nome} via igual",
                f"{nome} via prox",
                f"{nome} numero igual",
                f"{nome} compl prox",
                f"{nome} texto prox",
                f"{nome} tokens jacc",
            ]
        else:
            header_criterios += [
                f"{nome} prim frag igual",
                f"{nome} ult frag igual",
                f"{nome} qtd frag iguais",
                f"{nome} qtd frag raros",
                f"{nome} qtd frag comuns",
                f"{nome} qtd frag muito parec",
                f"{nome} qtd frag abrev",
            ]
    header_criterios.append("nota final")

    header = list(df.columns) + header_criterios
    out_df = pd.DataFrame(linhas, columns=header)
    if sort_by is not None:
        if sort_by not in out_df.columns:
            raise ValueError(f"Coluna '{sort_by}' não encontrada para ordenação")
        out_df.sort_values(by=sort_by, ascending=ascending, inplace=True)
    out_df.to_csv(f"{arquivo_saida}.csv", sep=sep, index=False)
