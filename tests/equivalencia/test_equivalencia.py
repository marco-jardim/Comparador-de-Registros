from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import comparar
from comparar import TOLERANCIA, fontes_legado, ler_resultado, localizar_jdk, rodar
from gerar_lote import DATAS, FREQUENCIAS, NOMES, SEED, gerar


def test_equivalencia_ascii_nao_regride(tmp_path):
    if not fontes_legado():
        pytest.skip("protótipo Java (legado/) não versionado; equivalência só reproduzível com a cópia local do autor")
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


@pytest.mark.parametrize("existe", [False, True])
def test_equivalencia_sem_fontes_locais_pula(tmp_path, monkeypatch, existe):
    diretorio = tmp_path / "legado_local"
    if existe:
        diretorio.mkdir()
    monkeypatch.setenv("CDR_LEGADO_DIR", str(diretorio))
    with pytest.raises(pytest.skip.Exception, match="protótipo Java .* não versionado"):
        test_equivalencia_ascii_nao_regride(tmp_path)


def test_fontes_legado_diretorio_configuravel(tmp_path, monkeypatch):
    fonte = tmp_path / "Prototipo.java"
    fonte.write_text("fonte local", encoding="utf-8")
    (tmp_path / "LEIAME").write_text("nao compilar", encoding="utf-8")
    monkeypatch.setenv("CDR_LEGADO_DIR", str(tmp_path))
    assert fontes_legado() == [fonte]


def test_equivalencia_sem_jdk_pula(tmp_path, monkeypatch):
    (tmp_path / "Prototipo.java").write_text("fonte local", encoding="utf-8")
    monkeypatch.setenv("CDR_LEGADO_DIR", str(tmp_path))
    monkeypatch.setattr(sys.modules[__name__], "localizar_jdk", lambda: None)
    with pytest.raises(pytest.skip.Exception, match="javac/JDK 21"):
        test_equivalencia_ascii_nao_regride(tmp_path)


def test_erro_compilacao_nao_pula_equivalencia(tmp_path, monkeypatch):
    (tmp_path / "Prototipo.java").write_text("Java invalido", encoding="utf-8")
    monkeypatch.setenv("CDR_LEGADO_DIR", str(tmp_path))
    monkeypatch.setattr(comparar, "localizar_jdk", lambda: (Path("javac"), Path("java")))

    def falhar_compilacao(command, cwd=comparar.ROOT):
        assert str(tmp_path / "Prototipo.java") in command
        raise subprocess.CalledProcessError(1, command, stderr="erro de compilacao")

    monkeypatch.setattr(comparar, "executar", falhar_compilacao)
    with pytest.raises(subprocess.CalledProcessError):
        rodar(tmp_path / "resultados", sublotes=("ascii",))


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
