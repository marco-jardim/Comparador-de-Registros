"""Compila o legado intacto e compara os CSVs publicos (tolerancia 1e-9)."""
from __future__ import annotations

import argparse
import csv
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

from gerar_lote import CAMPOS, FREQUENCIAS, SEED, gerar

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TOLERANCIA = 1e-9
ROTULOS = [f"paciente_{s}" for s in ("primeiro", "ultimo", "iguais", "raros", "comuns", "soundex", "abreviacoes")]
ROTULOS += [s.replace("paciente_", "mae_") for s in ROTULOS[:7]]
ROTULOS += ["data_igual", "data_um_digito", "data_inverte_dia", "data_inverte_mes", "data_inverte_ano", "nota_final"]


def localizar_jdk() -> tuple[Path, Path] | None:
    candidatos = []
    if os.environ.get("JAVA_HOME"):
        candidatos.append(Path(os.environ["JAVA_HOME"]) / "bin" / "javac.exe")
    candidatos.append(Path.home() / "scoop/apps/temurin21-jdk/current/bin/javac.exe")
    if shutil.which("javac"):
        candidatos.append(Path(shutil.which("javac")))
    for javac in candidatos:
        java = javac.with_name("java.exe" if os.name == "nt" else "java")
        if javac.is_file() and java.is_file():
            version = subprocess.run([str(javac), "-version"], capture_output=True, text=True, check=True)
            if int((version.stdout + version.stderr).split()[1].split(".")[0]) >= 21:
                return javac, java
    return None


def executar(command: list[str], cwd: Path = ROOT) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, errors="replace", check=True)
    output = result.stdout + result.stderr
    if output:
        print(output.rstrip())
    return output.strip()


def ler_resultado(path: Path, encoding: str) -> dict[str, list[float]]:
    with path.open(encoding=encoding, newline="") as stream:
        reader = csv.reader(stream, delimiter=";")
        header = next(reader)
        assert len(header) == len(CAMPOS) + 20, (path, header)
        rows = {}
        for row in reader:
            assert len(row) == len(header), (path, row)
            pair_id = row[6]
            assert pair_id not in rows, pair_id
            rows[pair_id] = [float(v.replace(",", ".")) for v in row[-20:]]
    return rows


def medir(java, python, inputs, sublote):
    assert java.keys() == python.keys() == inputs.keys()
    assert len(java) == 250
    resultados = []
    for i, rotulo in enumerate(ROTULOS):
        diffs = {key: abs(java[key][i] - python[key][i]) for key in java}
        divergentes = [key for key, delta in diffs.items() if delta > TOLERANCIA]
        resultados.append(dict(indice=i, subescore=rotulo, sublote=sublote, n=len(java),
                               identicos=len(java) - len(divergentes),
                               concordancia=(len(java) - len(divergentes)) / len(java),
                               diferenca_maxima=max(diffs.values()),
                               exemplos=[dict(pair_id=key, entrada=inputs[key], java=java[key][i],
                                              python=python[key][i]) for key in divergentes[:5]]))
    return resultados


def rodar(destino: Path, sublotes=("ascii", "acentos"), classes: Path | None = None):
    jdk = localizar_jdk()
    if jdk is None:
        raise FileNotFoundError("JDK 21+ nao encontrado (JAVA_HOME, Scoop Temurin 21 ou PATH)")
    javac, java = jdk
    paths = gerar(destino)
    classes = classes or destino / "classes"
    classes.mkdir(parents=True, exist_ok=True)
    fontes = sorted((ROOT / "legado/src/principal").glob("*.java"))
    avisos = executar([str(javac), "-encoding", "ISO-8859-1", "-d", str(classes),
                       *map(str, fontes), str(HERE / "java/HarnessEquivalencia.java")])
    sys.path.insert(0, str(ROOT / "src"))
    from comparaRegistros import processar

    resultados = []
    for sublote in sublotes:
        output_java = destino / f"{sublote}_java"
        # inicia captura IOException. Um resultado antigo nao pode mascarar falha.
        output_java.with_suffix(".csv").unlink(missing_ok=True)
        Path(str(output_java) + "2.csv").unlink(missing_ok=True)
        executar([str(java), "-cp", str(classes), "HarnessEquivalencia",
                  str(destino / f"{sublote}_latin1.csv"), str(destino / "frequencias"),
                  str(output_java)], cwd=destino / "frequencias")
        output_python = destino / f"{sublote}_python"
        processar(str(paths[sublote]), str(output_python), (0, 1, 2, 3, 4, 5),
                  cache_dir=str(destino / "frequencias"), sort_by=None)
        with paths[sublote].open(encoding="utf-8", newline="") as stream:
            inputs = {row["pair_id"]: row for row in csv.DictReader(stream, delimiter=";")}
        jrows = ler_resultado(output_java.with_suffix(".csv"), "latin-1")
        prows = ler_resultado(output_python.with_suffix(".csv"), "utf-8")
        resultados += medir(jrows, prows, inputs, sublote)
    metadata = dict(seed=SEED, tolerancia=TOLERANCIA, data_utc=datetime.now(timezone.utc).isoformat(), python=sys.version,
                    executavel_python=sys.executable, javac=str(javac),
                    dependencias={p: version(p) for p in ("pandas", "jellyfish", "Unidecode", "pytest")},
                    versao_javac=executar([str(javac), "-version"]),
                    versao_java=executar([str(java), "-version"]), avisos_compilacao=avisos,
                    sha_fontes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in fontes},
                    sha_entradas={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(destino.glob("*_utf8.csv"))},
                    sha_frequencias={p: hashlib.sha256((destino / "frequencias" / p).read_bytes()).hexdigest() for p in FREQUENCIAS})
    (destino / "resultados.json").write_text(json.dumps(dict(metadata=metadata, resultados=resultados), ensure_ascii=False, indent=2), encoding="utf-8")
    return resultados, metadata


def causa(indice: int) -> str:
    deslocamento = ("Estado/posicao: Java ComparaRegistros.java:94,110-117,164-166 usa contador sequencial; "
                    "Python comparaRegistros.py:114-125 fixa os indices, mesmo com paciente ausente. ")
    if indice < 14:
        local = indice % 7
        extra = {
            0: "Primeiro fragmento: Java ComparaRegistros.java:161-166; Python comparators/nomes.py:34-36.",
            1: "Ultimo fragmento: Java ComparaRegistros.java:168-173; Python comparators/nomes.py:37-39.",
            2: "Precisao de saida: Java ComparaRegistros.java:21,185-186 usa 2 a 4 casas; Python comparators/nomes.py:41-44 fixa 2.",
            3: "Frequencias: Java TransformaBase.java:38-46 descarta a primeira linha e insere cada mapa na posicao 0 (ordem invertida), consumidos em ComparaRegistros.java:190-223; Python transformaBase.py:12-21 preserva todas as linhas e a ordem. Nome de um fragmento: Java ComparaRegistros.java:208-221 nao conta ultimo; Python comparators/nomes.py:49-58 conta primeiro e ultimo. Precisao: Java :21,223 versus Python :58.",
            4: "Mesma inversao/descarte dos mapas: Java TransformaBase.java:38-46 e ComparaRegistros.java:226-248; Python transformaBase.py:12-21 e comparators/nomes.py:60-70. Nome unico e precisao diferem como nos raros. Ambos usam estritamente >1000, nao >=1000.",
            5: "Soundex adaptado (minusculas, regras H/Y/W/K/C/G, supressao de codigos repetidos): Java Utilidade.java:158-236 e ComparaRegistros.java:278-291; Python util.py:67-71 delega ao jellyfish e comparators/nomes.py:72-79 compara codigos. As letras iniciais diferem de caixa entre implementacoes, mas a comparacao ocorre dentro de cada implementacao; nao se comparam codigos Java contra codigos Python. Precisao 4 versus 2 casas tambem interfere.",
            6: "Abreviacoes bidirecionais e denominador do primeiro nome nos dois lados: Java ComparaRegistros.java:294-320; Python comparators/nomes.py:81-91. Precisao de saida Java :21 versus Python :91.",
        }[local]
        return deslocamento + extra + " Normalizacao numerica: Java Utilidade.java:60-104 remove digitos; Python util.py:47-55 preserva digitos."
    if indice in (14, 15):
        return "Sem divergencia observada: Java ComparaRegistros.java:119-122,328-338; Python comparaRegistros.py:122-125 e comparators/data.py:21-28."
    if indice in (16, 17, 18):
        return ("Inversoes valem 0,8 no Java ComparaRegistros.java:347-369 e 1,0 no Python comparators/data.py:32-40. "
                "Python :32,35 aceita dia/mes palindromo inalterado sem exigir distancia 2 local, desviando inversoes do ano para dia/mes; Java :348,353 exige distancia local 2. "
                "Ano: Java :358-369 exige troca de duas posicoes; Python :38 aceita anagrama com distancia 2.")
    return ("Soma dos comportamentos acima: Java ComparaRegistros.java:91-127,222-248,290-320,347-369 acumula sequencialmente e formata com 2 a 4 casas (:21); "
            "Python comparaRegistros.py:111-127 soma notas dos comparadores e formata com 2 casas; nomes.py:49-91 e data.py:32-40 alteram componentes.")


def relatar(resultados, metadata, destino: Path, artefatos: Path):
    destino.mkdir(parents=True, exist_ok=True)
    tabela = ["| Indice | Subescore | ASCII identicos/250 (%) | Max ASCII | Acentos identicos/250 (%) | Max acentos |",
              "|---|---|---:|---:|---:|---:|"]
    rows = []
    for i, rotulo in enumerate(ROTULOS):
        a, b = [next(r for r in resultados if r["indice"] == i and r["sublote"] == s) for s in ("ascii", "acentos")]
        tabela.append(f"| {i} | {rotulo} | {a['identicos']} ({a['concordancia']:.1%}) | {a['diferenca_maxima']:.9g} | {b['identicos']} ({b['concordancia']:.1%}) | {b['diferenca_maxima']:.9g} |")
        rows.append(dict(indice=i, subescore=rotulo, n=500,
                         concordancia=(a["identicos"] + b["identicos"]) / 500,
                         diferenca_maxima=max(a["diferenca_maxima"], b["diferenca_maxima"]),
                         concordancia_ascii=a["concordancia"], diferenca_maxima_ascii=a["diferenca_maxima"],
                         concordancia_acentos=b["concordancia"], diferenca_maxima_acentos=b["diferenca_maxima"], causa=causa(i)))
    with (destino / "resultado_agregado.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    texto = ["# Equivalencia parcial Java x Python: nome e data", "",
             "## Escopo e reproducao", "",
             "Prototipo de Daniele B. Pecanha, IESC/UFRJ, 01/09/2015 (legado/src/principal/LEIAME:1-2). "
             "Sem alteracoes em legado/ ou src/. Nao e validacao clinica nem prova de equivalencia para entradas arbitrarias.", "",
             f"Seed {SEED}; 500 pares exclusivamente ficticios, 250 ASCII e 250 com acentos/cedilha. Tolerancia absoluta {TOLERANCIA:g}. "
             "Comparamos os subescores serializados nos CSVs e a nota final serializada, nao valores internos arredondados artificialmente. "
             "Cada linha e conferida por pair_id; cardinalidade e conjunto de identificadores devem coincidir.", "",
             "Reproduzir na raiz: `python tests/equivalencia/comparar.py`. "
             "O padrao usa `%TEMP%/cdr_java`, compila todas as fontes legado/src/principal/*.java com JDK 21 e "
             "`-encoding ISO-8859-1 -d .../classes`, depois compila junto o harness. "
             "Executa uma JVM nova por sublote, com cwd na pasta das seis tabelas, evitando interferencia de estado estatico "
             "(ComparaRegistros.java:16-18). O harness recebe entrada, pasta das frequencias e prefixo de saida. "
             "O Python usa processar, o caminho fixo de seis colunas, sem ordenar; nao usa processar_generico.", "",
             "### Frequencias, codificacao e alinhamento", "",
             "As seis tabelas sinteticas usam os nomes e o formato sem cabecalho do legado/.freq_cache/: duas colunas nome;frequencia. "
             "Os arquivos reais nao sao carregados, nem mesmo para compor o lote. As tabelas reais de meio estao vazias; as sinteticas nao, "
             "para exercitar as seis posicoes. Todas incluem valores <5, =5, =1000 e >1000; diferem por posicao para revelar inversao de mapas. "
             "Os mesmos arquivos (bytes ASCII, hashes no JSON) sao usados pelos dois programas, via "
             "Java TransformaBase.java:21-46 e Python freqBuilder.py:61-64 / transformaBase.py:7-21. "
             "Java readHeaders descarta a primeira linha valida, e add(0, mapa) inverte as seis tabelas; nao corrigimos nenhum dos dois efeitos.", "",
             "Mapeamento confirmado nos corpos: Java criterios 0..6 para paciente e 7..13 para mae "
             "(ComparaRegistros.java:49-63,152-322), Python nomes.py pontos[0..6], chamado com mapas [0:3] ou [3:6] "
             "(comparaRegistros.py:69-82,114-121). Java 14..18 (ComparaRegistros.java:65-69,325-375) corresponde "
             "a data.py pontos[0..4] (comparaRegistros.py:122-125). O contador Java pode deslocar a mae para 0..6 se paciente ausente; "
             "a comparacao mantem as colunas publicadas, sem realinhamento corretivo. Mae ausente deixa 7..13 zerados.", "",
             "As proporcoes dos nomes usam o numero de fragmentos do PRIMEIRO registro nos dois lados "
             "(Java ComparaRegistros.java:158,185,222,247,290,319; Python nomes.py:33,42,56,68,77,89). "
             "O limiar comum e >1000 nos dois lados (Java :230,237,243; Python nomes.py:61,64,66): exatamente 1000 nao e comum, "
             "diferentemente da expressao 'a partir de 1.000' atribuida a Lucena no enunciado (a dissertacao nao foi reconsultada nesta verificacao). Nenhum limiar foi modificado.", "",
             "Separador de entrada e saida principal: ; (Java ComparaRegistros.java:42,79 e Python processar sep padrao). "
             "CsvReader.java:149-151 e CsvWriter.java:95-101 usam ISO-8859-1; Python pandas usa UTF-8. "
             "O gerador grava as mesmas strings Unicode em Latin-1 para Java e UTF-8 para Python, com tabelas ASCII compartilhadas. "
             "Os sublotes usam as mesmas combinacoes e variantes acentuadas que normalizam para as mesmas letras (Celia / Çélia, por exemplo). "
             "Portanto acentos aqui testam normalizacao com decodificacao correta, nao mojibake causado por entregar UTF-8 ao leitor Latin-1. "
             "Este segundo cenario nao foi medido. Normalizacao Java NFD (:47-49 de Utilidade.java) versus Python unidecode (util.py:42-44); "
             "os nomes incluem digitos para explicitar outra diferenca (Java remove, Python preserva).", "",
             "Datas incluem iguais, um digito, inversoes de dia/mes/ano, troca dia-mes, palindromos, invalidas e vazias. "
             "Nenhuma implementacao valida calendario: comprimento 8 habilita comparacao, inclusive texto e datas impossiveis. "
             "O lote cobre nomes iguais, trocados, abreviaturas, frequencias fronteiricas, Soundex adaptado, nomes unicos, "
             "comprimentos assimetricos, repeticoes, particulas e ausencias.", "",
             "## Resultados por subescore", "", *tabela, "", "## Causas e exemplos", "",
             "Caminhos Java abaixo sao relativos a legado/src/principal/; caminhos Python sao relativos a src/. "
             "Cada causa lista os mecanismos relevantes ao criterio, nao atribui todas as divergencias a um unico mecanismo. "
             "Exemplos preservam entradas sinteticas para inspecao; ate cinco por subescore e sublote.", ""]
    for i, rotulo in enumerate(ROTULOS):
        texto += [f"### {i}: {rotulo}", "", causa(i), ""]
        for r in [r for r in resultados if r["indice"] == i]:
            for ex in r["exemplos"]:
                texto.append(f"* `{ex['pair_id']}`: Java={ex['java']:.9g}; Python={ex['python']:.9g}; entrada ficticia: `{json.dumps(ex['entrada'], ensure_ascii=False)}`")
        texto.append("")
    texto += ["## Ambiente e avisos", "", f"Artefatos brutos locais: `{artefatos}` (nao versionados).", "",
              "```json", json.dumps(metadata, ensure_ascii=False, indent=2), "```", "",
              "## Regressao e limites", "",
              "baseline_ascii.json congela as contagens iniciais, sem recalculo automatico nos testes. "
              "O teste exige no minimo essa concordancia por subescore, inclusive nota final, com tolerancia 1e-9. "
              "Skip somente se JDK 21+ nao for encontrado. Aumentar a concordancia e permitido; reduzi-la exige investigacao. "
              "Os resultados sao condicionados ao lote e as tabelas sinteticas, nao a distribuicao de nomes de uma populacao. "
              "Nenhuma correcao ou refatoracao dos comparadores foi feita; causas individuais nao foram isoladas por ablation.", ""]
    (destino / "relatorio_equivalencia.md").write_text("\n".join(texto), encoding="utf-8")
    print("\n".join(tabela))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trabalho", type=Path, default=Path(tempfile.gettempdir()) / "cdr_java")
    parser.add_argument("--relatorio", type=Path, default=HERE)
    parser.add_argument("--registrar-baseline", action="store_true", help="Somente na medicao inicial; recusa sobrescrever")
    args = parser.parse_args()
    resultados, metadata = rodar(args.trabalho.resolve())
    relatar(resultados, metadata, args.relatorio, args.trabalho.resolve())
    if args.registrar_baseline:
        baseline = dict(seed=SEED, n=250, tolerancia=TOLERANCIA,
                        identicos={r["subescore"]: r["identicos"] for r in resultados if r["sublote"] == "ascii"})
        with (HERE / "baseline_ascii.json").open("x", encoding="utf-8") as stream:
            json.dump(baseline, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
