from __future__ import annotations

from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[2]


def test_configuracao_instala_modulos_e_pacotes_existentes():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    setuptools = config["tool"]["setuptools"]
    assert setuptools["package-dir"] == {"": "src"}
    assert set(setuptools["py-modules"]) == {p.stem for p in (ROOT / "src").glob("*.py")}
    assert setuptools["packages"]["find"] == {
        "where": ["src"],
        "include": ["comparators", "comparators.*"],
        "namespaces": False,
    }
    assert "scripts" not in config["project"]
    assert "gui-scripts" not in config["project"]


def test_dependencias_correspondem_ao_requirements():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    declared = config["project"]["dependencies"] + config["project"]["optional-dependencies"]["test"]
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    assert set(declared) == {line.strip() for line in requirements if line.strip()}
