# freqbuilder.py
from __future__ import annotations
import pandas as pd
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Tuple, List
import util


_PARTE = ("primeiro", "meio", "ultimo")
_ARQS = (
    "01_Frequencia_primeiro_nome_paciente.csv",
    "02_Frequencia_nome_do_meio_paciente.csv",
    "03_Frequencia_ultimo_nome_paciente.csv",
    "04_Frequencia_primeiro_nome_mae.csv",
    "05_Frequencia_nome_do_meio_mae.csv",
    "06_Frequencia_ultimo_nome_mae.csv",
)


def _split_nome(nome: str) -> Tuple[str, List[str], str]:
    """Devolve (primeiro, [meios], ultimo) já padronizados."""
    partes = util.padroniza(nome).split()
    if not partes:
        return "", [], ""
    if len(partes) == 1:
        return partes[0], [], partes[0]
    return partes[0], partes[1:-1], partes[-1]


def _update_counters(counter_map, nome):
    p, meios, u = _split_nome(nome)
    if p:
        counter_map["primeiro"][p] += 1
    if meios:
        for m in meios:
            counter_map["meio"][m] += 1
    if u:
        counter_map["ultimo"][u] += 1


def build_if_missing(
    csv_path: str,
    idxs: Tuple[int, int, int, int, int, int],
    out_dir: str = ".freq_cache",
    chunksize: int = 500_000,
    *,
    sep: str = ";",
) -> List[Dict[str, int]]:
    """
    Gera (ou carrega) as 6 tabelas de frequência.
    • csv_path  — base completa separada por ``sep``
    • idxs      — (Nome1, Mae1, Nasc1, Nome2, Mae2, Nasc2)-colunas
    • out_dir   — onde gravar/ler os arquivos de frequência
    • chunksize — linhas a carregar por vez (RAM ~300 MiB/1 M linhas)
    """
    out = Path(out_dir)
    out.mkdir(exist_ok=True)
    freq_files = [out / f for f in _ARQS]

    # Se TODOS já existem, apenas leia-os
    if all(f.exists() for f in freq_files):
        import transformaBase as tf
        return tf.guarda_frequencias(*map(str, freq_files))

    # ---------- construir em streaming ----------
    Nome1, Mae1, _, Nome2, Mae2, _ = idxs
    counters = [defaultdict(Counter) for _ in range(2)]  # 0=pac,1=mãe

    col_keep = [Nome1, Mae1, Nome2, Mae2]  # reduz memória

    for chunk in pd.read_csv(csv_path, sep=sep, dtype=str, chunksize=chunksize,
                             usecols=col_keep):
        chunk = chunk.fillna("")
        for nome in chunk.iloc[:, 0].values:  # Nome1
            _update_counters(counters[0], nome)
        for mae in chunk.iloc[:, 1].values:   # Mae1
            _update_counters(counters[1], mae)
        for nome in chunk.iloc[:, 2].values:  # Nome2
            _update_counters(counters[0], nome)
        for mae in chunk.iloc[:, 3].values:   # Mae2
            _update_counters(counters[1], mae)

    # Grava cada conjunto
    for flag, pessoa in enumerate(("paciente", "mae")):
        for i, parte in enumerate(_PARTE):
            idx = flag * 3 + i
            file_path = freq_files[idx]
            # grava ordenado por freq decrescente
            pd.Series(counters[flag][parte]).sort_values(ascending=False).to_csv(
                file_path,
                sep=sep,
                header=False,
            )

    import transformaBase as tf
    return tf.guarda_frequencias(*map(str, freq_files))
