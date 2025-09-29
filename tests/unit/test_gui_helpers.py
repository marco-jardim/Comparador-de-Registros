from __future__ import annotations

from pathlib import Path

import gui


def test_guess_tipo_from_name_handles_patterns():
    assert gui.guess_tipo_from_name("logradouro_cliente") == "L"
    assert gui.guess_tipo_from_name("codigo_localidade") == "C"
    assert gui.guess_tipo_from_name("data_nascimento") == "D"
    assert gui.guess_tipo_from_name("ano") == "M"
    assert gui.guess_tipo_from_name("descricao") == "T"


def test_normalize_tipo_code_resolves_conflicts():
    assert gui.normalize_tipo_code("L", "codigo_localidade") == "C"
    assert gui.normalize_tipo_code("C", "logradouro_cliente") == "L"
    assert gui.normalize_tipo_code("T", "descricao") == "T"
    assert gui.normalize_tipo_code("T", "ano_referencia") == "M"
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
    columns = ["Nome", "codigo_localidade", "logradouro", "ano"]
    prep = gui.prepare_column_maps(columns, True)

    assert prep.left_map == prep.right_map
    assert all(origin == "G" for origin in prep.left_origin.values())
    assert prep.pairable == set()
    assert gui.EMOJIS["C"] in prep.left_labels["codigo_localidade"]
    assert gui.EMOJIS["L"] in prep.left_labels["logradouro"]
    assert gui.EMOJIS["M"] in prep.left_labels["ano"]


def test_calc_header_criterios_handles_all_tipo_categories():
    pares = [
        (0, 1, "D", "data_nasc"),
        (1, 2, "C", "cod_localidade"),
        (2, 3, "L", "logradouro"),
        (3, 4, "T", "nome"),
        (4, 5, "M", "ano_base"),
    ]
    criterios = gui.calc_header_criterios(pares)

    assert "data_nasc dt iguais" in criterios
    assert "cod_localidade local prox" in criterios
    assert "logradouro texto prox" in criterios
    assert "nome qtd frag iguais" in criterios
    assert "ano_base num prox rel" in criterios
    assert criterios[-1] == "nota final"


class DummyCombo:
    def __init__(self, value: str = "") -> None:
        self._value = value

    def get(self) -> str:
        return self._value

    def set(self, value: str) -> None:
        self._value = value


class PairHarness:
    def __init__(self) -> None:
        self.label_to_left = {"R Nome": "Nome"}
        self.label_to_right = {"C Nome": "Nome", "C Outro": "Outro"}
        self.left_labels = {"Nome": "R Nome"}
        self.right_labels = {"Nome": "C Nome", "Outro": "C Outro"}
        self.left_map = {"Nome": (0, "T"), "Outro": (1, "T")}
        self.right_map = {"Nome": (0, "T"), "Outro": (1, "T")}
        self.pairable = {"Nome"}
        self._update_calls = 0

    def _update_sort_options(self) -> None:  # pragma: no cover - simple counter
        self._update_calls += 1

    def _find_pair_key(self, nome: str, target_map: dict[str, tuple[int, str]]) -> str | None:
        return gui.App._find_pair_key(self, nome, target_map)


def test_sync_pair_keeps_correlated_selection_when_manual_reverse():
    harness = PairHarness()
    cb_left = DummyCombo("R Nome")
    cb_right = DummyCombo("C Nome")

    gui.App._sync_pair_reverse(harness, cb_left, cb_right)

    assert cb_left.get() == "R Nome"
    assert cb_right.get() == "C Nome"


def test_sync_pair_autofills_cod_local_labels():
    harness = PairHarness()
    harness.label_to_left = {"📍 R·cod_localidade": "cod_localidade"}
    harness.label_to_right = {"📍 C·cod_localidade": "cod_localidade"}
    harness.left_labels = {"cod_localidade": "📍 R·cod_localidade"}
    harness.right_labels = {"cod_localidade": "📍 C·cod_localidade"}
    harness.left_map = {"cod_localidade": (0, "C")}
    harness.right_map = {"cod_localidade": (1, "C")}
    harness.pairable = {"cod_localidade"}

    cb_left = DummyCombo("📍 R·cod_localidade")
    cb_right = DummyCombo("")

    gui.App._sync_pair(harness, cb_left, cb_right)

    assert cb_right.get() == "📍 C·cod_localidade"


def test_prepare_column_maps_normalizes_pairable_for_prefixed_columns():
    columns = ["R_CODMUNRES", "C_CODMUNRES"]
    prep = gui.prepare_column_maps(columns, False)

    assert prep.pairable == {"CODMUNRES"}


def test_sync_pair_respects_generic_labels_without_prefix():
    harness = PairHarness()
    harness.label_to_left = {"Nome": "Nome"}
    harness.label_to_right = {"Nome": "Nome"}
    harness.left_labels = {"Nome": "Nome"}
    harness.right_labels = {"Nome": "Nome"}
    harness.left_map = {"Nome": (0, "T")}
    harness.right_map = {"Nome": (0, "T")}
    harness.pairable = {"Nome"}

    cb_left = DummyCombo("Nome")
    cb_right = DummyCombo("Nome")

    gui.App._sync_pair(harness, cb_left, cb_right)
    gui.App._sync_pair_reverse(harness, cb_left, cb_right)

    assert cb_left.get() == "Nome"
    assert cb_right.get() == "Nome"


def test_sync_pair_leaves_unmatched_selection_untouched():
    harness = PairHarness()
    harness.label_to_right = {"C Outro": "Outro"}
    harness.right_labels = {"Outro": "C Outro"}
    harness.right_map = {"Outro": (0, "T")}
    harness.pairable = set()

    cb_left = DummyCombo("R Nome")
    cb_right = DummyCombo("C Outro")

    gui.App._sync_pair(harness, cb_left, cb_right)

    assert cb_right.get() == "C Outro"
