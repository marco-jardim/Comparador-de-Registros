# transformabase.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, List            # para compat. Py < 3.9
import pandas as pd

def _le_tabela(p: Path) -> dict[str, int]:        # ou Dict[str, int] em <3.9
    """
    Lê a tabela de duas colunas (nome;frequência) e devolve
    um dicionário {nome_minusculo: frequência}.
    """
    df = (
        pd.read_csv(p, sep=";", header=None, names=["nome", "freq"], dtype=str)
          .fillna("")              # garante string vazia, nunca NaN
    )
    return {str(row.nome).lower(): int(str(row.freq).strip())  # ← CAST explícito com tratamento seguro
            for row in df.itertuples(index=False)}

def guarda_frequencias(*paths: str) -> List[Dict[str, int]]:
    """Lê as seis tabelas de frequência externas usadas pelo algoritmo."""
    return [_le_tabela(Path(p)) for p in paths]
