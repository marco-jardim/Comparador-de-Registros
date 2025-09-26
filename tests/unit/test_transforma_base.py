from __future__ import annotations

from pathlib import Path

import transformaBase as tb


def test_guarda_frequencias_reads_frequency_tables(tmp_path: Path):
    file1 = tmp_path / "freq1.csv"
    file1.write_text("Ana;2\nMaria;5\n", encoding="utf-8")
    file2 = tmp_path / "freq2.csv"
    file2.write_text("Souza; 7\n ", encoding="utf-8")

    tabelas = tb.guarda_frequencias(str(file1), str(file2))

    assert len(tabelas) == 2
    assert tabelas[0]["ana"] == 2
    assert tabelas[0]["maria"] == 5
    assert tabelas[1]["souza"] == 7
