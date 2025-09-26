from __future__ import annotations

from pathlib import Path

import pandas as pd

import comparaRegistros as cr


def test_processar_creates_scored_output(tmp_path: Path):
    df = pd.DataFrame(
        {
            "Nome1": ["Ana Silva", "Carlos Souza"],
            "Mae1": ["Maria Silva", "Patricia Souza"],
            "Nasc1": ["19900101", "19850505"],
            "Nome2": ["Ana Silva", "Joao Alves"],
            "Mae2": ["Maria Silva", "Patricia Souza"],
            "Nasc2": ["19900101", "19771212"],
        }
    )
    entrada = tmp_path / "entrada.csv"
    df.to_csv(entrada, sep=";", index=False)

    saida_prefix = tmp_path / "saida"
    cache_dir = tmp_path / "cache"

    cr.processar(
        str(entrada),
        str(saida_prefix),
        (0, 1, 2, 3, 4, 5),
        cache_dir=str(cache_dir),
        sep=";",
        sort_by="nota final",
        ascending=False,
    )

    saida_path = tmp_path / "saida.csv"
    out_df = pd.read_csv(saida_path, sep=";")

    assert "nota final" in out_df.columns
    out_df["_nota"] = out_df["nota final"].str.replace(",", ".").astype(float)
    notas_por_linha = dict(zip(out_df["Nome1"], out_df["_nota"]))
    assert notas_por_linha["Ana Silva"] > notas_por_linha["Carlos Souza"]

    cache_files = list(cache_dir.iterdir())
    assert len(cache_files) == 6
    assert all(f.exists() for f in cache_files)
