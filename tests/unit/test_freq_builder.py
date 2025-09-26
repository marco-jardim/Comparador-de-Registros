from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
import pytest

import freqBuilder as fb


@pytest.mark.parametrize(
    "nome, esperado",
    [
        ("Ana Maria Souza", ("ana", ["maria"], "souza")),
        ("Ana", ("ana", [], "ana")),
        ("", ("", [], "")),
    ],
)
def test_split_nome_handles_various_inputs(nome, esperado):
    assert fb._split_nome(nome) == esperado


def test_update_counters_spread_tokens_across_sections():
    counters = defaultdict(Counter)
    fb._update_counters(counters, "Ana Maria Souza")
    assert counters["primeiro"]["ana"] == 1
    assert counters["meio"]["maria"] == 1
    assert counters["ultimo"]["souza"] == 1


def test_build_if_missing_uses_cache_when_files_exist(tmp_path: Path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    for idx, file_name in enumerate(fb._ARQS):
        data = "valor{};{}\n".format(idx, idx + 1)
        (cache_dir / file_name).write_text(data, encoding="utf-8")

    resultado = fb.build_if_missing("unused.csv", (0, 1, 2, 3, 4, 5), out_dir=str(cache_dir))

    assert len(resultado) == 6
    assert resultado[0]["valor0"] == 1
    assert resultado[-1]["valor5"] == 6


def test_build_if_missing_creates_cache_from_csv(tmp_path: Path):
    csv_path = tmp_path / "dados.csv"
    cache_dir = tmp_path / "freq"
    cache_dir.mkdir()

    df = pd.DataFrame(
        {
            "Nome1": ["Ana Maria", "José"],
            "Mae1": ["Clara", ""],
            "Nasc1": ["19900101", "19851212"],
            "Nome2": ["Ana M.", "Jose"],
            "Mae2": ["Clara", "Rosa"],
            "Nasc2": ["19900101", "19851212"],
        }
    )
    df.to_csv(csv_path, sep=";", index=False)

    freq_map_list = fb.build_if_missing(
        str(csv_path),
        (0, 1, 2, 3, 4, 5),
        out_dir=str(cache_dir),
        chunksize=1,
    )

    assert len(freq_map_list) == 6
    assert (cache_dir / fb._ARQS[0]).exists()
    primeiro_nome_map = freq_map_list[0]
    assert primeiro_nome_map["ana"] >= 1
    assert any("clara" in mapa for mapa in freq_map_list)
