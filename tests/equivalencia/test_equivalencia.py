from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from comparar import TOLERANCIA, ler_resultado, localizar_jdk, rodar
from gerar_lote import DATAS, FREQUENCIAS, NOMES, SEED, gerar


def test_equivalencia_ascii_nao_regride(tmp_path):
    if localizar_jdk() is None:
        pytest.skip("javac/JDK 21+ nao encontrado")
    baseline = json.loads((HERE / "baseline_ascii.json").read_text(encoding="utf-8"))
    assert baseline["seed"] == SEED
    assert baseline["tolerancia"] == TOLERANCIA == 1e-9
    resultados, _ = rodar(tmp_path, sublotes=("ascii",))
    assert {r["subescore"] for r in resultados} == set(baseline["identicos"])
    for r in resultados:
        assert r["n"] == baseline["n"] == 250
        assert r["identicos"] >= baseline["identicos"][r["subescore"]], r
    java = ler_resultado(tmp_path / "ascii_java.csv", "latin-1")
    python = ler_resultado(tmp_path / "ascii_python.csv", "utf-8")
    # Caso dedicado de fronteira: exatamente 1000 nao e comum em nenhum lado.
    assert java["ascii_0002"][4] == python["ascii_0002"][4] == 0.0


def test_gerador_reprodutivel_e_cobertura(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    gerar(a)
    gerar(b)
    for sublote in ("ascii", "acentos"):
        utf8 = a / f"{sublote}_utf8.csv"
        latin1 = a / f"{sublote}_latin1.csv"
        assert utf8.read_bytes() == (b / utf8.name).read_bytes()
        assert utf8.read_text(encoding="utf-8") == latin1.read_text(encoding="latin-1")
        with utf8.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream, delimiter=";"))
        assert len(rows) == len({r["pair_id"] for r in rows}) == 250
        assert {r["caso_nome"] for r in rows} == {c[0] for c in NOMES}
        assert {r["caso_data"] for r in rows} == {c[0] for c in DATAS}
        assert any(not r["mae1"] or not r["mae2"] for r in rows)
        if sublote == "ascii":
            assert utf8.read_text(encoding="utf-8").isascii()
        else:
            assert "Ç" in utf8.read_text(encoding="utf-8")
    for filename in FREQUENCIAS:
        content = (a / "frequencias" / filename).read_bytes()
        assert content == (b / "frequencias" / filename).read_bytes()
        frequencies = [int(row[1]) for row in csv.reader(content.decode("ascii").splitlines(), delimiter=";")]
        assert any(n < 5 for n in frequencies)
        assert 5 in frequencies and 1000 in frequencies
        assert any(n > 1000 for n in frequencies)
