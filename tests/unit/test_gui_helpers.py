from __future__ import annotations

import os
from pathlib import Path

import gui


def test_guess_tipo_from_name_handles_patterns():
    assert gui.guess_tipo_from_name("logradouro_cliente") == "L"
    assert gui.guess_tipo_from_name("codigo_localidade") == "C"
    assert gui.guess_tipo_from_name("data_nascimento") == "D"
    assert gui.guess_tipo_from_name("descricao") == "T"


def test_normalize_tipo_code_resolves_conflicts():
    assert gui.normalize_tipo_code("L", "codigo_localidade") == "C"
    assert gui.normalize_tipo_code("C", "logradouro_cliente") == "L"
    assert gui.normalize_tipo_code("T", "descricao") == "T"
    assert gui.normalize_tipo_code("", "nome") == ""


def test_openreclink_helpers_extract_base_names():
    assert gui._split_openreclink_column("R_Nome") == ("R", "Nome")
    assert gui._base_without_prefix("R_Codigo") == "Codigo"
    assert gui._base_without_prefix("Nome") == "Nome"


def test_format_column_label_includes_emoji():
    label = gui._format_column_label("Nome", "R", "T", "1")
    assert label.startswith(gui.EMOJIS["T"])  # emoji prefix
    assert "1·" in label


def test_parse_env_file_and_format_version_date(tmp_path: Path, monkeypatch):
    env_path = tmp_path / "version.env"
    env_path.write_text("APP_VERSION=1.2.3\nAPP_VERSION_DATE=2024-11-30\n", encoding="utf-8")

    parsed = gui._parse_env_file(env_path)
    assert parsed["APP_VERSION"] == "1.2.3"
    assert gui._format_version_date(parsed["APP_VERSION_DATE"]) == "30/11/2024"

    monkeypatch.setenv("APP_VERSION", "")
    monkeypatch.setenv("APP_VERSION_DATE", "")
    monkeypatch.setattr(gui, "_find_version_file", lambda: env_path)

    version, date = gui._load_version_info()
    assert version == "1.2.3"
    assert date == "2024-11-30"
