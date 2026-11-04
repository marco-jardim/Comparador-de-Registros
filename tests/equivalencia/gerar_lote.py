"""Lote exclusivamente ficticio, sem leitura de bases ou caches reais."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import random

SEED = 20150901
FREQUENCIAS = (
    "01_Frequencia_primeiro_nome_paciente.csv",
    "02_Frequencia_nome_do_meio_paciente.csv",
    "03_Frequencia_ultimo_nome_paciente.csv",
    "04_Frequencia_primeiro_nome_mae.csv",
    "05_Frequencia_nome_do_meio_mae.csv",
    "06_Frequencia_ultimo_nome_mae.csv",
)
CAMPOS = ("nome1", "mae1", "data1", "nome2", "mae2", "data2",
          "pair_id", "sublote", "caso_nome", "caso_data")
NOMES = (
    ("iguais_raros", "Alva Zuno", "Alva Zuno"),
    ("iguais_comuns", "Breno Vale", "Breno Vale"),
    ("limiar_1000", "Limiar Limiar", "Limiar Limiar"),
    ("frequencia_5", "Medio Medio", "Medio Medio"),
    ("cabecalho_descartado", "Cabecalho Cabecalho", "Cabecalho Cabecalho"),
    ("trocados", "Alva Zuno", "Zuno Alva"),
    ("abreviatura_1", "A Zuno", "Alva Zuno"),
    ("abreviatura_2", "Alva Zuno", "A Zuno"),
    ("soundex_h", "Heraldo Vale", "Eraldo Vale"),
    ("soundex_k", "Karla Zuno", "Carla Zuno"),
    ("soundex_c", "Celia Vale", "Selia Vale"),
    ("soundex_y", "Yara Vale", "Iara Vale"),
    ("soundex_w", "Walter Zuno", "Valter Zuno"),
    ("tres_fragmentos", "Alva Breno Zuno", "Alva Zuno"),
    ("assimetria_volta", "Alva Zuno", "Alva Breno Zuno"),
    ("unico_raro", "Alva", "Alva"),
    ("unico_comum", "Breno", "Breno"),
    ("particulas", "Alva de Zuno Junior", "Alva Zuno"),
    ("duplicados", "Alva Alva Zuno", "Alva Zuno"),
    ("quatro_fragmentos", "Alva Breno Medio Vale", "Alva Vale"),
    ("diferentes", "Alva Zuno", "Breno Vale"),
    ("numeros", "Alva2 Zuno", "Alva Zuno"),
    ("paciente_ausente", "", "Alva Zuno"),
    ("ambos_ausentes", "", ""),
)
DATAS = (
    ("igual", "19801221", "19801221"),
    ("um_digito", "19801221", "19801222"),
    ("inverte_dia", "19801221", "19801212"),
    ("inverte_mes", "19801221", "19802121"),
    ("inverte_ano", "19801221", "18901221"),
    ("troca_dia_mes", "19801221", "19802112"),
    ("invalida_igual", "99999999", "99999999"),
    ("invalida_texto", "abcdefgh", "abcdfegh"),
    ("vazias", "", ""),
    ("uma_vazia", "19801221", ""),
    ("curta", "1980", "1981"),
    ("dia_palindromo_ano", "19801211", "18901211"),
    ("mes_palindromo_ano", "19801121", "18901121"),
    ("ano_permutado", "19801221", "91801221"),
)


def gravar_csv(path: Path, rows, encoding: str, header=None) -> None:
    with path.open("w", encoding=encoding, newline="") as stream:
        writer = csv.writer(stream, delimiter=";")
        if header:
            writer.writerow(header)
        writer.writerows(rows)


def gerar(destino: Path) -> dict[str, Path]:
    destino.mkdir(parents=True, exist_ok=True)
    freq = destino / "frequencias"
    freq.mkdir(exist_ok=True)
    # Mesmo formato do cache legado: sem cabecalho, nome;frequencia.
    # Chaves ASCII permitem que os dois leitores usem os MESMOS bytes.
    for i, filename in enumerate(FREQUENCIAS):
        rows = [("cabecalho", 1001), ("alva", 1 + i % 4),
                ("breno", 1001 + i), ("limiar", 1000), ("medio", 5),
                ("zuno", (2, 1002, 5, 1003, 3, 1000)[i]),
                ("vale", (1002, 3, 1000, 2, 1004, 5)[i])]
        gravar_csv(freq / filename, rows, "ascii")

    paths = {}
    for sublote in ("ascii", "acentos"):
        rng = random.Random(SEED)
        rows = []
        for i in range(250):
            caso, n1, n2 = NOMES[i % len(NOMES)]
            # Datas independentes dos nomes, com cobertura garantida inicial.
            cd, d1, d2 = DATAS[i if i < len(DATAS) else rng.randrange(len(DATAS))]
            _, m1, m2 = NOMES[(i * 7 + 3) % (len(NOMES) - 2)]
            if i % 9 == 0:
                m1 = ""
            if i % 13 == 0:
                m2 = ""
            if sublote == "acentos":
                def acentuar(value: str) -> str:
                    return value.replace("Alva", "Álva").replace("Zuno", "Zunó").replace("Breno", "Brêno").replace("Vale", "Vále").replace("Celia", "Çélia")
                n1, n2, m1, m2 = map(acentuar, (n1, n2, m1, m2))
            rows.append((n1, m1, d1, n2, m2, d2, f"{sublote}_{i:04d}", sublote, caso, cd))
        python_path = destino / f"{sublote}_utf8.csv"
        java_path = destino / f"{sublote}_latin1.csv"
        gravar_csv(python_path, rows, "utf-8", CAMPOS)
        gravar_csv(java_path, rows, "latin-1", CAMPOS)
        paths[sublote] = python_path
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destino", type=Path)
    args = parser.parse_args()
    gerar(args.destino)
    print(f"500 pares ficticios, seed {SEED}, em {args.destino.resolve()}")
