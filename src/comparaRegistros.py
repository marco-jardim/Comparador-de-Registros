from __future__ import annotations
import os
import re
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, List, Any
import time

import util
import transformaBase as tf
import freqBuilder as fb     # novo

DFMT = lambda x: format(Decimal(x).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP), "f")


# Índices para saber em qual fatia da lista de frequências procurar
PACIENTE, MAE = 0, 1

_DATE_LIKE_RE = re.compile(r"^\d{8}$")

# Globals used by worker processes
_WORK_PARES: list[tuple[int, int, str, str]] = []
_WORK_FREQ_MAPS: dict[int, any] = {}


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
            p = _criterios_data(v1, v2)
        elif t == "N":
            p = _criterios_nome_generico(v1, v2, freq_map)
        elif t == "L":
            p = _criterios_localidade(v1, v2)
        else:
            p = _criterios_str(v1, v2, freq_map or {})
        pontos_linha.extend(p[:-1])
        nota_total += float(p[-1].replace(",", "."))
    pontos_linha.append(DFMT(nota_total).replace(".", ","))
    return list(row) + pontos_linha


def _criterios_nome(nome1: str, nome2: str,
                    freq_maps: List[Dict[str, int]], flag: int) -> List[str]:
    pontos: List[str] = ["0,0"] * 7
    nota = 0.0

    parts1 = nome1.split()
    parts2 = nome2.split()
    t1 = len(parts1)

    # 1 / 8 – Primeiro fragmento igual
    if parts1[0] == parts2[0]:
        nota += 1
        pontos[0] = "1,0"

    # 2 / 9 – Último fragmento igual
    if parts1[-1] == parts2[-1]:
        nota += 1
        pontos[1] = "1,0"

    # 3 / 10 – Quantidade de fragmentos iguais
    inter = sum(1 for f in parts1 if f in parts2)
    incr = inter / t1
    nota += incr
    pontos[2] = DFMT(incr).replace(".", ",")

    # Mapas de frequência (0‑2 pac, 3‑5 mãe)
    first, middle, last = (
        freq_maps[0 + 3 * flag],
        freq_maps[1 + 3 * flag],
        freq_maps[2 + 3 * flag],
    )

    # 4 / 11 – Fragmentos raros (< 5 ocorrências)
    raros = 0
    if first.get(parts1[0], 0) < 5:
        raros += 1
    for p in parts1[1:-1]:
        if middle.get(p, 0) < 5:
            raros += 1
    if last.get(parts1[-1], 0) < 5:
        raros += 1
    incr = raros / t1
    nota += incr
    pontos[3] = DFMT(incr).replace(".", ",")

    # 5 / 12 – Fragmentos comuns (> 1000)
    comuns = 0
    if first.get(parts1[0], 0) > 1000:
        comuns += 1
    for p in parts1[1:-1]:
        if middle.get(p, 0) > 1000:
            comuns += 1
    if last.get(parts1[-1], 0) > 1000:
        comuns += 1
    incr = -(comuns / t1)
    nota += incr
    pontos[4] = DFMT(incr).replace(".", ",")

    # 6 / 13 – Fragmentos muito parecidos (≥ 3 dígitos iguais no Soundex)
    parecidos = 0
    for p1 in parts1:
        s1 = util.soundex(p1)
        if any(sum(c1 == c2 for c1, c2 in zip(s1, util.soundex(p2))) >= 3 for p2 in parts2):
            parecidos += 1
    incr = (parecidos / t1) * 0.8
    nota += incr
    pontos[5] = DFMT(incr).replace(".", ",")

    # 7 / 14 – Abreviações compatíveis
    abrevs = 0
    for p1 in parts1:
        if len(p1) == 1 and any(p2.startswith(p1) for p2 in parts2):
            abrevs += 1
    for p2 in parts2:
        if len(p2) == 1 and any(p1.startswith(p2) for p1 in parts1):
            abrevs += 1
    incr = (abrevs / t1) * 0.5
    nota += incr
    pontos[6] = DFMT(incr).replace(".", ",")

    return pontos + [DFMT(nota).replace(".", ",")]


def _criterios_data(d1: str, d2: str) -> List[str]:
    pontos = ["0,0"] * 5
    nota = 0.0

    if d1 == d2:               # 15
        nota += 1
        pontos[0] = "1,0"
    dist = util.levenshtein(d1, d2)
    if dist == 1:              # 16
        nota += 1
        pontos[1] = "1,0"
    elif dist == 2:
        dia1, mes1, ano1 = d1[6:], d1[4:6], d1[:4]
        dia2, mes2, ano2 = d2[6:], d2[4:6], d2[:4]
        if dia1[::-1] == dia2:         # 17
            nota += 1
            pontos[2] = "1,0"
        elif mes1[::-1] == mes2:       # 18
            nota += 1
            pontos[3] = "1,0"
        elif (
            util.levenshtein(ano1, ano2) == 2
            and sorted(ano1) == sorted(ano2)
        ):                             # 19
            nota += 1
            pontos[4] = "1,0"

    return pontos + [DFMT(nota).replace(".", ",")]


def _criterios_localidade(loc1: str, loc2: str) -> List[str]:
    pontos = ["0,0"] * 4
    nota = 0.0

    if len(loc1) != 6 or len(loc2) != 6:
        return pontos + ["0,0"]

    uf1, cod1 = loc1[:2].upper(), loc1[2:].upper()
    uf2, cod2 = loc2[:2].upper(), loc2[2:].upper()

    if uf1 == uf2:
        nota += 1
        pontos[0] = "1,0"
    else:
        dist_uf = util.levenshtein(uf1, uf2)
        if dist_uf == 1:
            nota += 0.5
            pontos[1] = "0,5"
        elif util.soundex(uf1) == util.soundex(uf2):
            nota += 0.3
            pontos[1] = "0,3"

    if cod1 == cod2:
        nota += 1
        pontos[2] = "1,0"
    else:
        dist_cod = util.levenshtein(cod1, cod2)
        if dist_cod == 1:
            nota += 0.8
            pontos[3] = "0,8"
        elif dist_cod == 2:
            nota += 0.5
            pontos[3] = "0,5"
        elif not (cod1.isdigit() and cod2.isdigit()) and util.soundex(cod1) == util.soundex(cod2):
            nota += 0.4
            pontos[3] = "0,4"

    return pontos + [DFMT(nota).replace(".", ",")]


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
    freq_paths = (
        "01_Frequencia_primeiro_nome_paciente.csv",
        "02_Frequencia_nome_do_meio_paciente.csv",
        "03_Frequencia_ultimo_nome_paciente.csv",
        "04_Frequencia_primeiro_nome_mae.csv",
        "05_Frequencia_nome_do_meio_mae.csv",
        "06_Frequencia_ultimo_nome_mae.csv",
    )
    freq_maps = fb.build_if_missing(arquivo_entrada, idxs, out_dir=cache_dir, sep=sep)

    df = pd.read_csv(arquivo_entrada, sep=sep, dtype=str).fillna("")
    saida_cols: list[str] = []

    linhas_saida = []
    for _, row in df.iterrows():
        # Normalização
        n1 = util.padroniza(row.iloc[Nome1])
        m1 = util.padroniza(row.iloc[Mae1])
        d1 = str(row.iloc[Nasc1])

        n2 = util.padroniza(row.iloc[Nome2])
        m2 = util.padroniza(row.iloc[Mae2])
        d2 = str(row.iloc[Nasc2])

        pontos: List[str] = ["0,0"] * 20  # 0..18 + nota final no 19
        nota_total = 0.0

        if n1 and n2:
            p = _criterios_nome(n1, n2, freq_maps, PACIENTE)
            pontos[0:7] = p[:-1]
            nota_total += float(p[-1].replace(",", "."))
        if m1 and m2:
            p = _criterios_nome(m1, m2, freq_maps, MAE)
            pontos[7:14] = p[:-1]
            nota_total += float(p[-1].replace(",", "."))
        if len(d1) == 8 and len(d2) == 8:
            p = _criterios_data(d1, d2)
            pontos[14:19] = p[:-1]
            nota_total += float(p[-1].replace(",", "."))

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


def _criterios_nome_generico(v1: str, v2: str, freq_maps: list[dict[str, int]]) -> list[str]:
    """
    Compare two names and calculate similarity scores based on frequency maps.

    Args:
        v1 (str): The first name to compare.
        v2 (str): The second name to compare.
        freq_maps (list[dict[str, int]]): A list of frequency maps for first, middle, and last name parts.

    Returns:
        list[str]: A list of similarity scores as strings, with the final score appended at the end.
    """
    pontos: list[str] = ["0,0"] * 7
    nota = 0.0

    parts1 = v1.split()
    parts2 = v2.split()
    if not parts1 or not parts2:
        return pontos + ["0,0"]

    t1 = len(parts1)
    if parts1[0] == parts2[0]:
        nota += 1
        pontos[0] = "1,0"
    if parts1[-1] == parts2[-1]:
        nota += 1
        pontos[1] = "1,0"

    inter = sum(1 for f in parts1 if f in parts2)
    incr = inter / t1
    nota += incr
    pontos[2] = DFMT(incr).replace(".", ",")

    first, middle, last = freq_maps
    raros = 0
    if first.get(parts1[0], 0) < 5:
        raros += 1
    for p in parts1[1:-1]:
        if middle.get(p, 0) < 5:
            raros += 1
    if last.get(parts1[-1], 0) < 5:
        raros += 1
    incr = raros / t1
    nota += incr
    pontos[3] = DFMT(incr).replace(".", ",")

    comuns = 0
    if first.get(parts1[0], 0) > 1000:
        comuns += 1
    for p in parts1[1:-1]:
        if middle.get(p, 0) > 1000:
            comuns += 1
    if last.get(parts1[-1], 0) > 1000:
        comuns += 1
    incr = -(comuns / t1)
    nota += incr
    pontos[4] = DFMT(incr).replace(".", ",")

    parecidos = 0
    for p1 in parts1:
        s1 = util.soundex(p1)
        if any(sum(c1 == c2 for c1, c2 in zip(s1, util.soundex(p2))) >= 3 for p2 in parts2):
            parecidos += 1
    incr = (parecidos / t1) * 0.8
    nota += incr
    pontos[5] = DFMT(incr).replace(".", ",")

    abrevs = 0
    for p1 in parts1:
        if len(p1) == 1 and any(p2.startswith(p1) for p2 in parts2):
            abrevs += 1
    for p2 in parts2:
        if len(p2) == 1 and any(p1.startswith(p2) for p1 in parts1):
            abrevs += 1
    incr = (abrevs / t1) * 0.5
    nota += incr
    pontos[6] = DFMT(incr).replace(".", ",")

    return pontos + [DFMT(nota).replace(".", ",")]


def _criterios_str(v1: str, v2: str, freq: dict[str, int]) -> list[str]:
    """Avalia dois textos utilizando critérios similares aos de nome."""
    pontos: list[str] = ["0,0"] * 7
    nota = 0.0

    parts1 = v1.split()
    parts2 = v2.split()
    if not parts1 or not parts2:
        return pontos + ["0,0"]

    t1 = len(parts1)

    if parts1[0] == parts2[0]:
        nota += 1
        pontos[0] = "1,0"

    if parts1[-1] == parts2[-1]:
        nota += 1
        pontos[1] = "1,0"

    inter = sum(1 for f in parts1 if f in parts2)
    incr = inter / t1
    nota += incr
    pontos[2] = DFMT(incr).replace(".", ",")

    is_date_like = (
        len(parts1) == 1
        and len(parts2) == 1
        and _DATE_LIKE_RE.fullmatch(parts1[0])
        and _DATE_LIKE_RE.fullmatch(parts2[0])
    )

    if not is_date_like:
        raros = sum(1 for p in parts1 if freq.get(p, 0) < 5)
        incr = raros / t1
        nota += incr
        pontos[3] = DFMT(incr).replace(".", ",")

        comuns = sum(1 for p in parts1 if freq.get(p, 0) > 1000)
        incr = -(comuns / t1)
        nota += incr
        pontos[4] = DFMT(incr).replace(".", ",")

    parecidos = 0
    soundex_parts2 = {p2: util.soundex(p2) for p2 in parts2}  # Precompute soundex for parts2
    for p1 in parts1:
        s1 = util.soundex(p1)
        if any(sum(c1 == c2 for c1, c2 in zip(s1, soundex_parts2[p2])) >= 3 for p2 in parts2):
            parecidos += 1
    incr = (parecidos / t1) * 0.8
    nota += incr
    pontos[5] = DFMT(incr).replace(".", ",")

    abrevs = 0
    for p1 in parts1:
        if len(p1) == 1 and any(p2.startswith(p1) for p2 in parts2):
            abrevs += 1
    for p2 in parts2:
        if len(p2) == 1 and any(p1.startswith(p2) for p1 in parts1):
            abrevs += 1
    incr = (abrevs / t1) * 0.5
    nota += incr
    pontos[6] = DFMT(incr).replace(".", ",")

    return pontos + [DFMT(nota).replace(".", ",")]


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

    ``pares`` contém ``(idx1, idx2, tipo, nome)`` onde ``tipo`` é ``"C"`` para
    strings ou ``"D"`` para datas e ``nome`` é um rótulo para os campos.
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

    freq_maps: dict[int, any] = {}
    for i, (idx1, idx2, tipo, _) in enumerate(pares):
        t = tipo.upper()
        if t == "C":
            freq_maps[i] = _build_freq_map(df, idx1, idx2)
        elif t == "N":
            freq_maps[i] = _build_name_freq_map(df, idx1, idx2)
        elif t == "L":
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
                    p = _criterios_data(v1, v2)
                elif t == "N":
                    p = _criterios_nome_generico(v1, v2, freq_map)
                elif t == "L":
                    p = _criterios_localidade(v1, v2)
                else:
                    p = _criterios_str(v1, v2, freq_map or {})
                pontos_linha.extend(p[:-1])
                nota_total += float(p[-1].replace(",", "."))
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
        elif t == "L":
            header_criterios += [
                f"{nome} uf igual",
                f"{nome} uf prox",
                f"{nome} local igual",
                f"{nome} local prox",
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
