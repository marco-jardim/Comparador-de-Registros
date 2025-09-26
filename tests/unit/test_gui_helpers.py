from __future__ import annotations

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


def test_prepare_column_maps_openreclink_infers_pairable_columns():
    columns = [
        "R_Nome,T",
        "C_Nome,T",
        "R_cod_localidade,C",
        "C_cod_localidade,C",
        "R_endereco,L",
        "C_endereco,L",
    ]
    prep = gui.prepare_column_maps(columns, True)

    assert prep.left_map["Nome"][0] == 0
    assert prep.right_map["Nome"][0] == 1
    assert prep.left_origin["Nome"] == "R"
    assert prep.right_origin["Nome"] == "C"
    assert prep.pairable == {"Nome", "cod_localidade", "endereco"}
    left_label = prep.left_labels["Nome"]
    assert left_label in prep.label_to_left
    assert prep.label_to_left[left_label] == "Nome"


def test_prepare_column_maps_falls_back_to_generic_when_missing_pairs():
    columns = ["Nome", "codigo_localidade", "logradouro"]
    prep = gui.prepare_column_maps(columns, True)

    assert prep.left_map == prep.right_map
    assert all(origin == "G" for origin in prep.left_origin.values())
    assert prep.pairable == set()
    assert gui.EMOJIS["C"] in prep.left_labels["codigo_localidade"]
    assert gui.EMOJIS["L"] in prep.left_labels["logradouro"]


def test_calc_header_criterios_handles_all_tipo_categories():
    pares = [
        (0, 1, "D", "data_nasc"),
        (1, 2, "C", "cod_localidade"),
        (2, 3, "L", "logradouro"),
        (3, 4, "T", "nome"),
    ]
    criterios = gui.calc_header_criterios(pares)

    assert "data_nasc dt iguais" in criterios
    assert "cod_localidade local prox" in criterios
    assert "logradouro texto prox" in criterios
    assert "nome qtd frag iguais" in criterios
    assert criterios[-1] == "nota final"
