from __future__ import annotations


from decimal import Decimal

import pandas as pd
import pytest  # type: ignore

import comparaRegistros as cr


def test_build_freq_map_counts_tokens():
    df = pd.DataFrame(
        {
            "A": ["Ana Ana"],
            "B": ["Maria"],
        }
    )

    freq = cr._build_freq_map(df, 0, 1)

    assert freq["ana"] == 2
    assert freq["maria"] == 1


def test_build_name_freq_map_splits_parts():
    df = pd.DataFrame(
        {
            "Nome": ["Ana B Silva"],
            "Mae": ["Joao C Souza"],
        }
    )

    first, middle, last = cr._build_name_freq_map(df, 0, 1)
    assert first["ana"] == 1
    assert first["joao"] == 1
    assert middle["b"] == 1
    assert middle["c"] == 1
    assert last["silva"] == 1
    assert last["souza"] == 1


def test_comparar_nome_flag_uses_correct_submaps():
    freq_maps = [
        {"ana": 1},
        {"maria": 1},
        {"silva": 1},
        {"ana": 2000},
        {"maria": 2000},
        {"silva": 2000},
    ]

    resultado_paciente = cr._comparar_nome_flag("ana maria silva", "ana maria silva", freq_maps, cr.PACIENTE)
    resultado_mae = cr._comparar_nome_flag("ana maria silva", "ana maria silva", freq_maps, cr.MAE)

    raros_paciente = float(resultado_paciente.pontos[3].replace(",", "."))
    raros_mae = float(resultado_mae.pontos[3].replace(",", "."))

    assert raros_paciente > 0
    assert raros_mae == 0


def test_process_row_aggregates_scores():
    pares = [(0, 1, "T", "campo")]
    freq_maps = {0: {"ana": 1, "silva": 1}}
    cr._init_worker(pares, freq_maps)

    linha = cr._process_row(("Ana Silva", "Ana Silva"))

    assert linha[:2] == ["Ana Silva", "Ana Silva"]
    pontos = linha[2:]
    assert len(pontos) == 8  # 7 pontos do comparador + nota final
    nota_final = Decimal(pontos[-1].replace(",", "."))
    assert nota_final > 1


def test_processar_generico_with_progress_and_workers(tmp_path):
    df = pd.DataFrame(
        {
            "nome_a": ["Ana Silva", "Carlos Souza"],
            "nome_b": ["Ana Silva", "Carla Souza"],
            "data_a": ["19900101", "19850505"],
            "data_b": ["19900101", "19860505"],
        }
    )
    entrada = tmp_path / "entrada.csv"
    df.to_csv(entrada, sep="|", index=False)

    updates: list[tuple[int, str]] = []

    def progress(pct: int, msg: str, *_):
        updates.append((pct, msg))

    cr.processar_generico(
        str(entrada),
        str(tmp_path / "saida"),
        [
            (0, 1, "N", "Paciente"),
            (2, 3, "D", "Nascimento"),
        ],
        sep="|",
        progress_cb=progress,
        workers=0,
    )

    saida = tmp_path / "saida.csv"
    assert saida.exists()
    assert any(pct == 100 for pct, _ in updates)


def test_processar_generico_invalid_sort_column(tmp_path):
    df = pd.DataFrame({"nome_a": ["Ana"], "nome_b": ["Ana"]})
    entrada = tmp_path / "entrada.csv"
    df.to_csv(entrada, sep="|", index=False)

    with pytest.raises(ValueError):
        cr.processar_generico(
            str(entrada),
            str(tmp_path / "saida"),
            [(0, 1, "T", "Campo")],
            sep="|",
            sort_by="inexistente",
        )
