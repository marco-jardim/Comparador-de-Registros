from __future__ import annotations

from pathlib import Path

import pandas as pd

import comparaRegistros as cr


def test_processar_generico_scores_records(tmp_path: Path):
    df = pd.DataFrame(
        {
            "NomeA": ["Ana Maria Silva"],
            "NomeB": ["Ana Maria Silva"],
            "LocalA": ["SP1234"],
            "LocalB": ["SP1234"],
            "LogA": ["Rua das Flores 123"],
            "LogB": ["Rua das Flores 123"],
            "DataA": ["19900101"],
            "DataB": ["19900101"],
        }
    )
    entrada = tmp_path / "entrada.csv"
    df.to_csv(entrada, sep="|", index=False)

    saida_prefix = tmp_path / "resultado"

    updates: list[tuple[int, str]] = []

    def progresso(pct: int, msg: str, eta: float | None = None):
        updates.append((pct, msg))

    pares = [
        (0, 1, "N", "paciente"),
        (2, 3, "C", "local"),
        (4, 5, "L", "endereco"),
        (6, 7, "D", "nascimento"),
    ]

    cr.processar_generico(
        str(entrada),
        str(saida_prefix),
        pares,
        sep="|",
        progress_cb=progresso,
        workers=1,
    )

    saida_path = tmp_path / "resultado.csv"
    out_df = pd.read_csv(saida_path, sep="|")

    assert "paciente prim frag igual" in out_df.columns
    assert out_df.shape[0] == 1
    nota_final = float(out_df.loc[0, "nota final"].replace(",", "."))
    assert nota_final > 3
    assert updates and updates[-1][0] == 100
