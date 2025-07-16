from __future__ import annotations
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, List

import util
import transformaBase as tf
import freqBuilder as fb     # novo

DFMT = lambda x: format(Decimal(x).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP), "f")


# Índices para saber em qual fatia da lista de frequências procurar
PACIENTE, MAE = 0, 1


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
            nota += 0.8
            pontos[2] = "0,8"
        elif mes1[::-1] == mes2:       # 18
            nota += 0.8
            pontos[3] = "0,8"
        elif (
            util.levenshtein(ano1, ano2) == 2
            and sorted(ano1) == sorted(ano2)
        ):                             # 19
            nota += 0.8
            pontos[4] = "0,8"

    return pontos + [DFMT(nota).replace(".", ",")]


def processar(arquivo_entrada: str,
              arquivo_saida : str,
              idxs           : tuple[int, int, int, int, int, int],
              cache_dir      : str = ".freq_cache") -> None:
    Nome1, Mae1, Nasc1, Nome2, Mae2, Nasc2 = idxs
    freq_paths = (
        "01_Frequencia_primeiro_nome_paciente.csv",
        "02_Frequencia_nome_do_meio_paciente.csv",
        "03_Frequencia_ultimo_nome_paciente.csv",
        "04_Frequencia_primeiro_nome_mae.csv",
        "05_Frequencia_nome_do_meio_mae.csv",
        "06_Frequencia_ultimo_nome_mae.csv",
    )
    freq_maps = fb.build_if_missing(arquivo_entrada, idxs, out_dir=cache_dir)

    df = pd.read_csv(arquivo_entrada, sep=";", dtype=str).fillna("")
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

    # ;‑separated
    out_df.to_csv(f"{arquivo_saida}.csv", sep=";", index=False)
    # |‑separated
    out_df.to_csv(f"{arquivo_saida}2.csv", sep="|", index=False)


def _build_freq_map(df: pd.DataFrame, idx1: int, idx2: int) -> dict[str, int]:
    counter: dict[str, int] = {}
    for val in pd.concat([df.iloc[:, idx1], df.iloc[:, idx2]]).astype(str):
        parts = util.padroniza(val).split()
        for p in parts:
            counter[p] = counter.get(p, 0) + 1
    return counter


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
) -> None:
    """Processa genericamente pares de colunas.

    ``pares`` contém ``(idx1, idx2, tipo, nome)`` onde ``tipo`` é ``"C"`` para
    strings ou ``"D"`` para datas e ``nome`` é um rótulo para os campos.
    O delimitador das colunas é definido por ``sep`` (padrão ``"|"``).
    """
    df = pd.read_csv(arquivo_entrada, sep=sep, dtype=str).fillna("")

    freq_maps: dict[int, dict[str, int]] = {}
    for i, (idx1, idx2, tipo, _) in enumerate(pares):
        if tipo.upper() == "C":
            freq_maps[i] = _build_freq_map(df, idx1, idx2)

    linhas = []
    for _, row in df.iterrows():
        pontos_linha: list[str] = []
        nota_total = 0.0
        for i, (idx1, idx2, tipo, _) in enumerate(pares):
            v1 = util.padroniza(str(row.iloc[idx1]))
            v2 = util.padroniza(str(row.iloc[idx2]))
            if tipo.upper() == "D":
                p = _criterios_data(v1, v2)
            else:
                p = _criterios_str(v1, v2, freq_maps[i])
            pontos_linha.extend(p[:-1])
            nota_total += float(p[-1].replace(",", "."))
        pontos_linha.append(DFMT(nota_total).replace(".", ","))
        linhas.append(list(row) + pontos_linha)

    header_criterios: list[str] = []
    for _, _, tipo, nome in pares:
        if tipo.upper() == "D":
            header_criterios += [
                f"{nome} dt iguais",
                f"{nome} dt ap 1digi",
                f"{nome} dt inv dia",
                f"{nome} dt inv mes",
                f"{nome} dt inv ano",
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
    out_df.to_csv(f"{arquivo_saida}.csv", sep=";", index=False)
    out_df.to_csv(f"{arquivo_saida}2.csv", sep="|", index=False)
