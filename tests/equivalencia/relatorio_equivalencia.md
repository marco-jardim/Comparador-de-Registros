# Equivalencia parcial Java x Python: nome e data

## Escopo e reproducao

Prototipo de Daniele B. Pecanha, IESC/UFRJ, 01/09/2015 (legado/src/principal/LEIAME:1-2). Sem alteracoes em legado/ ou src/. Nao e validacao clinica nem prova de equivalencia para entradas arbitrarias.

Seed 20150901; 500 pares exclusivamente ficticios, 250 ASCII e 250 com acentos/cedilha. Tolerancia absoluta 1e-09. Comparamos os subescores serializados nos CSVs e a nota final serializada, nao valores internos arredondados artificialmente. Cada linha e conferida por pair_id; cardinalidade e conjunto de identificadores devem coincidir.

Reproduzir na raiz: `python tests/equivalencia/comparar.py`. O padrao usa `%TEMP%/cdr_java`, compila todas as fontes legado/src/principal/*.java com JDK 21 e `-encoding ISO-8859-1 -d .../classes`, depois compila junto o harness. Executa uma JVM nova por sublote, com cwd na pasta das seis tabelas, evitando interferencia de estado estatico (ComparaRegistros.java:16-18). O harness recebe entrada, pasta das frequencias e prefixo de saida. O Python usa processar, o caminho fixo de seis colunas, sem ordenar; nao usa processar_generico.

### Frequencias, codificacao e alinhamento

As seis tabelas sinteticas usam os nomes e o formato sem cabecalho do legado/.freq_cache/: duas colunas nome;frequencia. Os arquivos reais nao sao carregados, nem mesmo para compor o lote. As tabelas reais de meio estao vazias; as sinteticas nao, para exercitar as seis posicoes. Todas incluem valores <5, =5, =1000 e >1000; diferem por posicao para revelar inversao de mapas. Os mesmos arquivos (bytes ASCII, hashes no JSON) sao usados pelos dois programas, via Java TransformaBase.java:21-46 e Python freqBuilder.py:61-64 / transformaBase.py:7-21. Java readHeaders descarta a primeira linha valida, e add(0, mapa) inverte as seis tabelas; nao corrigimos nenhum dos dois efeitos.

Mapeamento confirmado nos corpos: Java criterios 0..6 para paciente e 7..13 para mae (ComparaRegistros.java:49-63,152-322), Python nomes.py pontos[0..6], chamado com mapas [0:3] ou [3:6] (comparaRegistros.py:69-82,114-121). Java 14..18 (ComparaRegistros.java:65-69,325-375) corresponde a data.py pontos[0..4] (comparaRegistros.py:122-125). O contador Java pode deslocar a mae para 0..6 se paciente ausente; a comparacao mantem as colunas publicadas, sem realinhamento corretivo. Mae ausente deixa 7..13 zerados.

As proporcoes dos nomes usam o numero de fragmentos do PRIMEIRO registro nos dois lados (Java ComparaRegistros.java:158,185,222,247,290,319; Python nomes.py:33,42,56,68,77,89). O limiar comum e >1000 nos dois lados (Java :230,237,243; Python nomes.py:61,64,66): exatamente 1000 nao e comum, diferentemente da expressao 'a partir de 1.000' atribuida a Lucena no enunciado (a dissertacao nao foi reconsultada nesta verificacao). Nenhum limiar foi modificado.

Separador de entrada e saida principal: ; (Java ComparaRegistros.java:42,79 e Python processar sep padrao). CsvReader.java:149-151 e CsvWriter.java:95-101 usam ISO-8859-1; Python pandas usa UTF-8. O gerador grava as mesmas strings Unicode em Latin-1 para Java e UTF-8 para Python, com tabelas ASCII compartilhadas. Os sublotes usam as mesmas combinacoes e variantes acentuadas que normalizam para as mesmas letras (Celia / Çélia, por exemplo). Portanto acentos aqui testam normalizacao com decodificacao correta, nao mojibake causado por entregar UTF-8 ao leitor Latin-1. Este segundo cenario nao foi medido. Normalizacao Java NFD (:47-49 de Utilidade.java) versus Python unidecode (util.py:42-44); os nomes incluem digitos para explicitar outra diferenca (Java remove, Python preserva).

Datas incluem iguais, um digito, inversoes de dia/mes/ano, troca dia-mes, palindromos, invalidas e vazias. Nenhuma implementacao valida calendario: comprimento 8 habilita comparacao, inclusive texto e datas impossiveis. O lote cobre nomes iguais, trocados, abreviaturas, frequencias fronteiricas, Soundex adaptado, nomes unicos, comprimentos assimetricos, repeticoes, particulas e ausencias.

## Resultados por subescore

| Indice | Subescore | ASCII identicos/250 (%) | Max ASCII | Acentos identicos/250 (%) | Max acentos |
|---|---|---:|---:|---:|---:|
| 0 | paciente_primeiro | 229 (91.6%) | 1 | 229 (91.6%) | 1 |
| 1 | paciente_ultimo | 233 (93.2%) | 1 | 233 (93.2%) | 1 |
| 2 | paciente_iguais | 212 (84.8%) | 1 | 212 (84.8%) | 1 |
| 3 | paciente_raros | 142 (56.8%) | 1 | 142 (56.8%) | 1 |
| 4 | paciente_comuns | 98 (39.2%) | 1 | 98 (39.2%) | 1 |
| 5 | paciente_soundex | 222 (88.8%) | 0.8 | 222 (88.8%) | 0.8 |
| 6 | paciente_abreviacoes | 248 (99.2%) | 0.25 | 248 (99.2%) | 0.25 |
| 7 | mae_primeiro | 232 (92.8%) | 1 | 232 (92.8%) | 1 |
| 8 | mae_ultimo | 233 (93.2%) | 1 | 233 (93.2%) | 1 |
| 9 | mae_iguais | 216 (86.4%) | 1 | 216 (86.4%) | 1 |
| 10 | mae_raros | 120 (48.0%) | 2 | 120 (48.0%) | 2 |
| 11 | mae_comuns | 177 (70.8%) | 2 | 177 (70.8%) | 2 |
| 12 | mae_soundex | 224 (89.6%) | 0.8 | 224 (89.6%) | 0.8 |
| 13 | mae_abreviacoes | 248 (99.2%) | 0.25 | 248 (99.2%) | 0.25 |
| 14 | data_igual | 250 (100.0%) | 0 | 250 (100.0%) | 0 |
| 15 | data_um_digito | 250 (100.0%) | 0 | 250 (100.0%) | 0 |
| 16 | data_inverte_dia | 206 (82.4%) | 1 | 206 (82.4%) | 1 |
| 17 | data_inverte_mes | 192 (76.8%) | 1 | 192 (76.8%) | 1 |
| 18 | data_inverte_ano | 189 (75.6%) | 0.8 | 189 (75.6%) | 0.8 |
| 19 | nota_final | 28 (11.2%) | 4 | 28 (11.2%) | 4 |

## Causas e exemplos

Caminhos Java abaixo sao relativos a legado/src/principal/; caminhos Python sao relativos a src/. Cada causa lista os mecanismos relevantes ao criterio, nao atribui todas as divergencias a um unico mecanismo. Exemplos preservam entradas sinteticas para inspecao; ate cinco por subescore e sublote.

### 0: paciente_primeiro

Estado/posicao: Java ComparaRegistros.java:94,110-117,164-166 usa contador sequencial; Python comparaRegistros.py:114-125 fixa os indices, mesmo com paciente ausente. Primeiro fragmento: Java ComparaRegistros.java:161-166; Python comparators/nomes.py:34-36. Normalizacao numerica: Java Utilidade.java:60-104 remove digitos; Python util.py:47-55 preserva digitos.

* `ascii_0021`: Java=1; Python=0; entrada ficticia: `{"nome1": "Alva2 Zuno", "mae1": "Alva Alva Zuno", "data1": "19801211", "nome2": "Alva Zuno", "mae2": "Alva Zuno", "data2": "18901211", "pair_id": "ascii_0021", "sublote": "ascii", "caso_nome": "numeros", "caso_data": "dia_palindromo_ano"}`
* `ascii_0022`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Alva Zuno", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "ascii_0022", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `ascii_0045`: Java=1; Python=0; entrada ficticia: `{"nome1": "Alva2 Zuno", "mae1": "", "data1": "19801221", "nome2": "Alva Zuno", "mae2": "Selia Vale", "data2": "91801221", "pair_id": "ascii_0045", "sublote": "ascii", "caso_nome": "numeros", "caso_data": "ano_permutado"}`
* `ascii_0046`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Alva de Zuno Junior", "data1": "19801121", "nome2": "Alva Zuno", "mae2": "Alva Zuno", "data2": "18901121", "pair_id": "ascii_0046", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `ascii_0047`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Limiar Limiar", "data1": "19801211", "nome2": "", "mae2": "Limiar Limiar", "data2": "18901211", "pair_id": "ascii_0047", "sublote": "ascii", "caso_nome": "ambos_ausentes", "caso_data": "dia_palindromo_ano"}`
* `acentos_0021`: Java=1; Python=0; entrada ficticia: `{"nome1": "Álva2 Zunó", "mae1": "Álva Álva Zunó", "data1": "19801211", "nome2": "Álva Zunó", "mae2": "Álva Zunó", "data2": "18901211", "pair_id": "acentos_0021", "sublote": "acentos", "caso_nome": "numeros", "caso_data": "dia_palindromo_ano"}`
* `acentos_0022`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Álva Zunó", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "acentos_0022", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `acentos_0045`: Java=1; Python=0; entrada ficticia: `{"nome1": "Álva2 Zunó", "mae1": "", "data1": "19801221", "nome2": "Álva Zunó", "mae2": "Selia Vále", "data2": "91801221", "pair_id": "acentos_0045", "sublote": "acentos", "caso_nome": "numeros", "caso_data": "ano_permutado"}`
* `acentos_0046`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Álva de Zunó Junior", "data1": "19801121", "nome2": "Álva Zunó", "mae2": "Álva Zunó", "data2": "18901121", "pair_id": "acentos_0046", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `acentos_0047`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Limiar Limiar", "data1": "19801211", "nome2": "", "mae2": "Limiar Limiar", "data2": "18901211", "pair_id": "acentos_0047", "sublote": "acentos", "caso_nome": "ambos_ausentes", "caso_data": "dia_palindromo_ano"}`

### 1: paciente_ultimo

Estado/posicao: Java ComparaRegistros.java:94,110-117,164-166 usa contador sequencial; Python comparaRegistros.py:114-125 fixa os indices, mesmo com paciente ausente. Ultimo fragmento: Java ComparaRegistros.java:168-173; Python comparators/nomes.py:37-39. Normalizacao numerica: Java Utilidade.java:60-104 remove digitos; Python util.py:47-55 preserva digitos.

* `ascii_0022`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Alva Zuno", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "ascii_0022", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `ascii_0023`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Celia Vale", "data1": "19801121", "nome2": "", "mae2": "Selia Vale", "data2": "18901121", "pair_id": "ascii_0023", "sublote": "ascii", "caso_nome": "ambos_ausentes", "caso_data": "mes_palindromo_ano"}`
* `ascii_0046`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Alva de Zuno Junior", "data1": "19801121", "nome2": "Alva Zuno", "mae2": "Alva Zuno", "data2": "18901121", "pair_id": "ascii_0046", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `ascii_0047`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Limiar Limiar", "data1": "19801211", "nome2": "", "mae2": "Limiar Limiar", "data2": "18901211", "pair_id": "ascii_0047", "sublote": "ascii", "caso_nome": "ambos_ausentes", "caso_data": "dia_palindromo_ano"}`
* `ascii_0070`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Karla Zuno", "data1": "99999999", "nome2": "Alva Zuno", "mae2": "Carla Zuno", "data2": "99999999", "pair_id": "ascii_0070", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "invalida_igual"}`
* `acentos_0022`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Álva Zunó", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "acentos_0022", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `acentos_0023`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Çélia Vále", "data1": "19801121", "nome2": "", "mae2": "Selia Vále", "data2": "18901121", "pair_id": "acentos_0023", "sublote": "acentos", "caso_nome": "ambos_ausentes", "caso_data": "mes_palindromo_ano"}`
* `acentos_0046`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Álva de Zunó Junior", "data1": "19801121", "nome2": "Álva Zunó", "mae2": "Álva Zunó", "data2": "18901121", "pair_id": "acentos_0046", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `acentos_0047`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Limiar Limiar", "data1": "19801211", "nome2": "", "mae2": "Limiar Limiar", "data2": "18901211", "pair_id": "acentos_0047", "sublote": "acentos", "caso_nome": "ambos_ausentes", "caso_data": "dia_palindromo_ano"}`
* `acentos_0070`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Karla Zunó", "data1": "99999999", "nome2": "Álva Zunó", "mae2": "Carla Zunó", "data2": "99999999", "pair_id": "acentos_0070", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "invalida_igual"}`

### 2: paciente_iguais

Estado/posicao: Java ComparaRegistros.java:94,110-117,164-166 usa contador sequencial; Python comparaRegistros.py:114-125 fixa os indices, mesmo com paciente ausente. Precisao de saida: Java ComparaRegistros.java:21,185-186 usa 2 a 4 casas; Python comparators/nomes.py:41-44 fixa 2. Normalizacao numerica: Java Utilidade.java:60-104 remove digitos; Python util.py:47-55 preserva digitos.

* `ascii_0013`: Java=0.6667; Python=0.67; entrada ficticia: `{"nome1": "Alva Breno Zuno", "mae1": "A Zuno", "data1": "19801221", "nome2": "Alva Zuno", "mae2": "", "data2": "91801221", "pair_id": "ascii_0013", "sublote": "ascii", "caso_nome": "tres_fragmentos", "caso_data": "ano_permutado"}`
* `ascii_0021`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Alva2 Zuno", "mae1": "Alva Alva Zuno", "data1": "19801211", "nome2": "Alva Zuno", "mae2": "Alva Zuno", "data2": "18901211", "pair_id": "ascii_0021", "sublote": "ascii", "caso_nome": "numeros", "caso_data": "dia_palindromo_ano"}`
* `ascii_0022`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Alva Zuno", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "ascii_0022", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `ascii_0023`: Java=0.5; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Celia Vale", "data1": "19801121", "nome2": "", "mae2": "Selia Vale", "data2": "18901121", "pair_id": "ascii_0023", "sublote": "ascii", "caso_nome": "ambos_ausentes", "caso_data": "mes_palindromo_ano"}`
* `ascii_0037`: Java=0.6667; Python=0.67; entrada ficticia: `{"nome1": "Alva Breno Zuno", "mae1": "Alva Zuno", "data1": "19801221", "nome2": "Alva Zuno", "mae2": "Breno Vale", "data2": "19802112", "pair_id": "ascii_0037", "sublote": "ascii", "caso_nome": "tres_fragmentos", "caso_data": "troca_dia_mes"}`
* `acentos_0013`: Java=0.6667; Python=0.67; entrada ficticia: `{"nome1": "Álva Brêno Zunó", "mae1": "A Zunó", "data1": "19801221", "nome2": "Álva Zunó", "mae2": "", "data2": "91801221", "pair_id": "acentos_0013", "sublote": "acentos", "caso_nome": "tres_fragmentos", "caso_data": "ano_permutado"}`
* `acentos_0021`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Álva2 Zunó", "mae1": "Álva Álva Zunó", "data1": "19801211", "nome2": "Álva Zunó", "mae2": "Álva Zunó", "data2": "18901211", "pair_id": "acentos_0021", "sublote": "acentos", "caso_nome": "numeros", "caso_data": "dia_palindromo_ano"}`
* `acentos_0022`: Java=1; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Álva Zunó", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "acentos_0022", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `acentos_0023`: Java=0.5; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Çélia Vále", "data1": "19801121", "nome2": "", "mae2": "Selia Vále", "data2": "18901121", "pair_id": "acentos_0023", "sublote": "acentos", "caso_nome": "ambos_ausentes", "caso_data": "mes_palindromo_ano"}`
* `acentos_0037`: Java=0.6667; Python=0.67; entrada ficticia: `{"nome1": "Álva Brêno Zunó", "mae1": "Álva Zunó", "data1": "19801221", "nome2": "Álva Zunó", "mae2": "Brêno Vále", "data2": "19802112", "pair_id": "acentos_0037", "sublote": "acentos", "caso_nome": "tres_fragmentos", "caso_data": "troca_dia_mes"}`

### 3: paciente_raros

Estado/posicao: Java ComparaRegistros.java:94,110-117,164-166 usa contador sequencial; Python comparaRegistros.py:114-125 fixa os indices, mesmo com paciente ausente. Frequencias: Java TransformaBase.java:38-46 descarta a primeira linha e insere cada mapa na posicao 0 (ordem invertida), consumidos em ComparaRegistros.java:190-223; Python transformaBase.py:12-21 preserva todas as linhas e a ordem. Nome de um fragmento: Java ComparaRegistros.java:208-221 nao conta ultimo; Python comparators/nomes.py:49-58 conta primeiro e ultimo. Precisao: Java :21,223 versus Python :58. Normalizacao numerica: Java Utilidade.java:60-104 remove digitos; Python util.py:47-55 preserva digitos.

* `ascii_0001`: Java=0.5; Python=0; entrada ficticia: `{"nome1": "Breno Vale", "mae1": "Celia Vale", "data1": "19801221", "nome2": "Breno Vale", "mae2": "Selia Vale", "data2": "19801222", "pair_id": "ascii_0001", "sublote": "ascii", "caso_nome": "iguais_comuns", "caso_data": "um_digito"}`
* `ascii_0004`: Java=1; Python=0; entrada ficticia: `{"nome1": "Cabecalho Cabecalho", "mae1": "Karla Zuno", "data1": "19801221", "nome2": "Cabecalho Cabecalho", "mae2": "Carla Zuno", "data2": "18901221", "pair_id": "ascii_0004", "sublote": "ascii", "caso_nome": "cabecalho_descartado", "caso_data": "inverte_ano"}`
* `ascii_0008`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Heraldo Vale", "mae1": "Alva", "data1": "", "nome2": "Eraldo Vale", "mae2": "Alva", "data2": "", "pair_id": "ascii_0008", "sublote": "ascii", "caso_nome": "soundex_h", "caso_data": "vazias"}`
* `ascii_0010`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Celia Vale", "mae1": "Alva Zuno", "data1": "1980", "nome2": "Selia Vale", "mae2": "A Zuno", "data2": "1981", "pair_id": "ascii_0010", "sublote": "ascii", "caso_nome": "soundex_c", "caso_data": "curta"}`
* `ascii_0011`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Yara Vale", "mae1": "Alva Zuno", "data1": "19801211", "nome2": "Iara Vale", "mae2": "Alva Breno Zuno", "data2": "18901211", "pair_id": "ascii_0011", "sublote": "ascii", "caso_nome": "soundex_y", "caso_data": "dia_palindromo_ano"}`
* `acentos_0001`: Java=0.5; Python=0; entrada ficticia: `{"nome1": "Brêno Vále", "mae1": "Çélia Vále", "data1": "19801221", "nome2": "Brêno Vále", "mae2": "Selia Vále", "data2": "19801222", "pair_id": "acentos_0001", "sublote": "acentos", "caso_nome": "iguais_comuns", "caso_data": "um_digito"}`
* `acentos_0004`: Java=1; Python=0; entrada ficticia: `{"nome1": "Cabecalho Cabecalho", "mae1": "Karla Zunó", "data1": "19801221", "nome2": "Cabecalho Cabecalho", "mae2": "Carla Zunó", "data2": "18901221", "pair_id": "acentos_0004", "sublote": "acentos", "caso_nome": "cabecalho_descartado", "caso_data": "inverte_ano"}`
* `acentos_0008`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Heraldo Vále", "mae1": "Álva", "data1": "", "nome2": "Eraldo Vále", "mae2": "Álva", "data2": "", "pair_id": "acentos_0008", "sublote": "acentos", "caso_nome": "soundex_h", "caso_data": "vazias"}`
* `acentos_0010`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Çélia Vále", "mae1": "Álva Zunó", "data1": "1980", "nome2": "Selia Vále", "mae2": "A Zunó", "data2": "1981", "pair_id": "acentos_0010", "sublote": "acentos", "caso_nome": "soundex_c", "caso_data": "curta"}`
* `acentos_0011`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Yara Vále", "mae1": "Álva Zunó", "data1": "19801211", "nome2": "Iara Vále", "mae2": "Álva Brêno Zunó", "data2": "18901211", "pair_id": "acentos_0011", "sublote": "acentos", "caso_nome": "soundex_y", "caso_data": "dia_palindromo_ano"}`

### 4: paciente_comuns

Estado/posicao: Java ComparaRegistros.java:94,110-117,164-166 usa contador sequencial; Python comparaRegistros.py:114-125 fixa os indices, mesmo com paciente ausente. Mesma inversao/descarte dos mapas: Java TransformaBase.java:38-46 e ComparaRegistros.java:226-248; Python transformaBase.py:12-21 e comparators/nomes.py:60-70. Nome unico e precisao diferem como nos raros. Ambos usam estritamente >1000, nao >=1000. Normalizacao numerica: Java Utilidade.java:60-104 remove digitos; Python util.py:47-55 preserva digitos.

* `ascii_0000`: Java=-0.5; Python=-0; entrada ficticia: `{"nome1": "Alva Zuno", "mae1": "", "data1": "19801221", "nome2": "Alva Zuno", "mae2": "", "data2": "19801221", "pair_id": "ascii_0000", "sublote": "ascii", "caso_nome": "iguais_raros", "caso_data": "igual"}`
* `ascii_0004`: Java=-0; Python=-1; entrada ficticia: `{"nome1": "Cabecalho Cabecalho", "mae1": "Karla Zuno", "data1": "19801221", "nome2": "Cabecalho Cabecalho", "mae2": "Carla Zuno", "data2": "18901221", "pair_id": "ascii_0004", "sublote": "ascii", "caso_nome": "cabecalho_descartado", "caso_data": "inverte_ano"}`
* `ascii_0005`: Java=-0.5; Python=-0; entrada ficticia: `{"nome1": "Alva Zuno", "mae1": "Breno", "data1": "19801221", "nome2": "Zuno Alva", "mae2": "Breno", "data2": "19802112", "pair_id": "ascii_0005", "sublote": "ascii", "caso_nome": "trocados", "caso_data": "troca_dia_mes"}`
* `ascii_0006`: Java=-0.5; Python=-0; entrada ficticia: `{"nome1": "A Zuno", "mae1": "Breno Vale", "data1": "99999999", "nome2": "Alva Zuno", "mae2": "Breno Vale", "data2": "99999999", "pair_id": "ascii_0006", "sublote": "ascii", "caso_nome": "abreviatura_1", "caso_data": "invalida_igual"}`
* `ascii_0007`: Java=-0.5; Python=-0; entrada ficticia: `{"nome1": "Alva Zuno", "mae1": "Heraldo Vale", "data1": "abcdefgh", "nome2": "A Zuno", "mae2": "Eraldo Vale", "data2": "abcdfegh", "pair_id": "ascii_0007", "sublote": "ascii", "caso_nome": "abreviatura_2", "caso_data": "invalida_texto"}`
* `acentos_0000`: Java=-0.5; Python=-0; entrada ficticia: `{"nome1": "Álva Zunó", "mae1": "", "data1": "19801221", "nome2": "Álva Zunó", "mae2": "", "data2": "19801221", "pair_id": "acentos_0000", "sublote": "acentos", "caso_nome": "iguais_raros", "caso_data": "igual"}`
* `acentos_0004`: Java=-0; Python=-1; entrada ficticia: `{"nome1": "Cabecalho Cabecalho", "mae1": "Karla Zunó", "data1": "19801221", "nome2": "Cabecalho Cabecalho", "mae2": "Carla Zunó", "data2": "18901221", "pair_id": "acentos_0004", "sublote": "acentos", "caso_nome": "cabecalho_descartado", "caso_data": "inverte_ano"}`
* `acentos_0005`: Java=-0.5; Python=-0; entrada ficticia: `{"nome1": "Álva Zunó", "mae1": "Brêno", "data1": "19801221", "nome2": "Zunó Álva", "mae2": "Brêno", "data2": "19802112", "pair_id": "acentos_0005", "sublote": "acentos", "caso_nome": "trocados", "caso_data": "troca_dia_mes"}`
* `acentos_0006`: Java=-0.5; Python=-0; entrada ficticia: `{"nome1": "A Zunó", "mae1": "Brêno Vále", "data1": "99999999", "nome2": "Álva Zunó", "mae2": "Brêno Vále", "data2": "99999999", "pair_id": "acentos_0006", "sublote": "acentos", "caso_nome": "abreviatura_1", "caso_data": "invalida_igual"}`
* `acentos_0007`: Java=-0.5; Python=-0; entrada ficticia: `{"nome1": "Álva Zunó", "mae1": "Heraldo Vále", "data1": "abcdefgh", "nome2": "A Zunó", "mae2": "Eraldo Vále", "data2": "abcdfegh", "pair_id": "acentos_0007", "sublote": "acentos", "caso_nome": "abreviatura_2", "caso_data": "invalida_texto"}`

### 5: paciente_soundex

Estado/posicao: Java ComparaRegistros.java:94,110-117,164-166 usa contador sequencial; Python comparaRegistros.py:114-125 fixa os indices, mesmo com paciente ausente. Soundex adaptado (minusculas, regras H/Y/W/K/C/G, supressao de codigos repetidos): Java Utilidade.java:158-236 e ComparaRegistros.java:278-291; Python util.py:67-71 delega ao jellyfish e comparators/nomes.py:72-79 compara codigos. As letras iniciais diferem de caixa entre implementacoes, mas a comparacao ocorre dentro de cada implementacao; nao se comparam codigos Java contra codigos Python. Precisao 4 versus 2 casas tambem interfere. Normalizacao numerica: Java Utilidade.java:60-104 remove digitos; Python util.py:47-55 preserva digitos.

* `ascii_0013`: Java=0.5333; Python=0.53; entrada ficticia: `{"nome1": "Alva Breno Zuno", "mae1": "A Zuno", "data1": "19801221", "nome2": "Alva Zuno", "mae2": "", "data2": "91801221", "pair_id": "ascii_0013", "sublote": "ascii", "caso_nome": "tres_fragmentos", "caso_data": "ano_permutado"}`
* `ascii_0022`: Java=0.8; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Alva Zuno", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "ascii_0022", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `ascii_0023`: Java=0.8; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Celia Vale", "data1": "19801121", "nome2": "", "mae2": "Selia Vale", "data2": "18901121", "pair_id": "ascii_0023", "sublote": "ascii", "caso_nome": "ambos_ausentes", "caso_data": "mes_palindromo_ano"}`
* `ascii_0037`: Java=0.5333; Python=0.53; entrada ficticia: `{"nome1": "Alva Breno Zuno", "mae1": "Alva Zuno", "data1": "19801221", "nome2": "Alva Zuno", "mae2": "Breno Vale", "data2": "19802112", "pair_id": "ascii_0037", "sublote": "ascii", "caso_nome": "tres_fragmentos", "caso_data": "troca_dia_mes"}`
* `ascii_0046`: Java=0.8; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Alva de Zuno Junior", "data1": "19801121", "nome2": "Alva Zuno", "mae2": "Alva Zuno", "data2": "18901121", "pair_id": "ascii_0046", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `acentos_0013`: Java=0.5333; Python=0.53; entrada ficticia: `{"nome1": "Álva Brêno Zunó", "mae1": "A Zunó", "data1": "19801221", "nome2": "Álva Zunó", "mae2": "", "data2": "91801221", "pair_id": "acentos_0013", "sublote": "acentos", "caso_nome": "tres_fragmentos", "caso_data": "ano_permutado"}`
* `acentos_0022`: Java=0.8; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Álva Zunó", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "acentos_0022", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `acentos_0023`: Java=0.8; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Çélia Vále", "data1": "19801121", "nome2": "", "mae2": "Selia Vále", "data2": "18901121", "pair_id": "acentos_0023", "sublote": "acentos", "caso_nome": "ambos_ausentes", "caso_data": "mes_palindromo_ano"}`
* `acentos_0037`: Java=0.5333; Python=0.53; entrada ficticia: `{"nome1": "Álva Brêno Zunó", "mae1": "Álva Zunó", "data1": "19801221", "nome2": "Álva Zunó", "mae2": "Brêno Vále", "data2": "19802112", "pair_id": "acentos_0037", "sublote": "acentos", "caso_nome": "tres_fragmentos", "caso_data": "troca_dia_mes"}`
* `acentos_0046`: Java=0.8; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Álva de Zunó Junior", "data1": "19801121", "nome2": "Álva Zunó", "mae2": "Álva Zunó", "data2": "18901121", "pair_id": "acentos_0046", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`

### 6: paciente_abreviacoes

Estado/posicao: Java ComparaRegistros.java:94,110-117,164-166 usa contador sequencial; Python comparaRegistros.py:114-125 fixa os indices, mesmo com paciente ausente. Abreviacoes bidirecionais e denominador do primeiro nome nos dois lados: Java ComparaRegistros.java:294-320; Python comparators/nomes.py:81-91. Precisao de saida Java :21 versus Python :91. Normalizacao numerica: Java Utilidade.java:60-104 remove digitos; Python util.py:47-55 preserva digitos.

* `ascii_0142`: Java=0.25; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Alva Zuno", "data1": "19801211", "nome2": "Alva Zuno", "mae2": "A Zuno", "data2": "18901211", "pair_id": "ascii_0142", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "dia_palindromo_ano"}`
* `ascii_0167`: Java=0.25; Python=0; entrada ficticia: `{"nome1": "", "mae1": "A Zuno", "data1": "19801221", "nome2": "", "mae2": "Alva Zuno", "data2": "91801221", "pair_id": "ascii_0167", "sublote": "ascii", "caso_nome": "ambos_ausentes", "caso_data": "ano_permutado"}`
* `acentos_0142`: Java=0.25; Python=0; entrada ficticia: `{"nome1": "", "mae1": "Álva Zunó", "data1": "19801211", "nome2": "Álva Zunó", "mae2": "A Zunó", "data2": "18901211", "pair_id": "acentos_0142", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "dia_palindromo_ano"}`
* `acentos_0167`: Java=0.25; Python=0; entrada ficticia: `{"nome1": "", "mae1": "A Zunó", "data1": "19801221", "nome2": "", "mae2": "Álva Zunó", "data2": "91801221", "pair_id": "acentos_0167", "sublote": "acentos", "caso_nome": "ambos_ausentes", "caso_data": "ano_permutado"}`

### 7: mae_primeiro

Estado/posicao: Java ComparaRegistros.java:94,110-117,164-166 usa contador sequencial; Python comparaRegistros.py:114-125 fixa os indices, mesmo com paciente ausente. Primeiro fragmento: Java ComparaRegistros.java:161-166; Python comparators/nomes.py:34-36. Normalizacao numerica: Java Utilidade.java:60-104 remove digitos; Python util.py:47-55 preserva digitos.

* `ascii_0012`: Java=1; Python=0; entrada ficticia: `{"nome1": "Walter Zuno", "mae1": "Alva2 Zuno", "data1": "19801121", "nome2": "Valter Zuno", "mae2": "Alva Zuno", "data2": "18901121", "pair_id": "ascii_0012", "sublote": "ascii", "caso_nome": "soundex_w", "caso_data": "mes_palindromo_ano"}`
* `ascii_0022`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Alva Zuno", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "ascii_0022", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `ascii_0034`: Java=1; Python=0; entrada ficticia: `{"nome1": "Celia Vale", "mae1": "Alva2 Zuno", "data1": "19801221", "nome2": "Selia Vale", "mae2": "Alva Zuno", "data2": "", "pair_id": "ascii_0034", "sublote": "ascii", "caso_nome": "soundex_c", "caso_data": "uma_vazia"}`
* `ascii_0046`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Alva de Zuno Junior", "data1": "19801121", "nome2": "Alva Zuno", "mae2": "Alva Zuno", "data2": "18901121", "pair_id": "ascii_0046", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `ascii_0047`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Limiar Limiar", "data1": "19801211", "nome2": "", "mae2": "Limiar Limiar", "data2": "18901211", "pair_id": "ascii_0047", "sublote": "ascii", "caso_nome": "ambos_ausentes", "caso_data": "dia_palindromo_ano"}`
* `acentos_0012`: Java=1; Python=0; entrada ficticia: `{"nome1": "Walter Zunó", "mae1": "Álva2 Zunó", "data1": "19801121", "nome2": "Valter Zunó", "mae2": "Álva Zunó", "data2": "18901121", "pair_id": "acentos_0012", "sublote": "acentos", "caso_nome": "soundex_w", "caso_data": "mes_palindromo_ano"}`
* `acentos_0022`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Álva Zunó", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "acentos_0022", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `acentos_0034`: Java=1; Python=0; entrada ficticia: `{"nome1": "Çélia Vále", "mae1": "Álva2 Zunó", "data1": "19801221", "nome2": "Selia Vále", "mae2": "Álva Zunó", "data2": "", "pair_id": "acentos_0034", "sublote": "acentos", "caso_nome": "soundex_c", "caso_data": "uma_vazia"}`
* `acentos_0046`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Álva de Zunó Junior", "data1": "19801121", "nome2": "Álva Zunó", "mae2": "Álva Zunó", "data2": "18901121", "pair_id": "acentos_0046", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `acentos_0047`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Limiar Limiar", "data1": "19801211", "nome2": "", "mae2": "Limiar Limiar", "data2": "18901211", "pair_id": "acentos_0047", "sublote": "acentos", "caso_nome": "ambos_ausentes", "caso_data": "dia_palindromo_ano"}`

### 8: mae_ultimo

Estado/posicao: Java ComparaRegistros.java:94,110-117,164-166 usa contador sequencial; Python comparaRegistros.py:114-125 fixa os indices, mesmo com paciente ausente. Ultimo fragmento: Java ComparaRegistros.java:168-173; Python comparators/nomes.py:37-39. Normalizacao numerica: Java Utilidade.java:60-104 remove digitos; Python util.py:47-55 preserva digitos.

* `ascii_0022`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Alva Zuno", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "ascii_0022", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `ascii_0023`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Celia Vale", "data1": "19801121", "nome2": "", "mae2": "Selia Vale", "data2": "18901121", "pair_id": "ascii_0023", "sublote": "ascii", "caso_nome": "ambos_ausentes", "caso_data": "mes_palindromo_ano"}`
* `ascii_0046`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Alva de Zuno Junior", "data1": "19801121", "nome2": "Alva Zuno", "mae2": "Alva Zuno", "data2": "18901121", "pair_id": "ascii_0046", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `ascii_0047`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Limiar Limiar", "data1": "19801211", "nome2": "", "mae2": "Limiar Limiar", "data2": "18901211", "pair_id": "ascii_0047", "sublote": "ascii", "caso_nome": "ambos_ausentes", "caso_data": "dia_palindromo_ano"}`
* `ascii_0070`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Karla Zuno", "data1": "99999999", "nome2": "Alva Zuno", "mae2": "Carla Zuno", "data2": "99999999", "pair_id": "ascii_0070", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "invalida_igual"}`
* `acentos_0022`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Álva Zunó", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "acentos_0022", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `acentos_0023`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Çélia Vále", "data1": "19801121", "nome2": "", "mae2": "Selia Vále", "data2": "18901121", "pair_id": "acentos_0023", "sublote": "acentos", "caso_nome": "ambos_ausentes", "caso_data": "mes_palindromo_ano"}`
* `acentos_0046`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Álva de Zunó Junior", "data1": "19801121", "nome2": "Álva Zunó", "mae2": "Álva Zunó", "data2": "18901121", "pair_id": "acentos_0046", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `acentos_0047`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Limiar Limiar", "data1": "19801211", "nome2": "", "mae2": "Limiar Limiar", "data2": "18901211", "pair_id": "acentos_0047", "sublote": "acentos", "caso_nome": "ambos_ausentes", "caso_data": "dia_palindromo_ano"}`
* `acentos_0070`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Karla Zunó", "data1": "99999999", "nome2": "Álva Zunó", "mae2": "Carla Zunó", "data2": "99999999", "pair_id": "acentos_0070", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "invalida_igual"}`

### 9: mae_iguais

Estado/posicao: Java ComparaRegistros.java:94,110-117,164-166 usa contador sequencial; Python comparaRegistros.py:114-125 fixa os indices, mesmo com paciente ausente. Precisao de saida: Java ComparaRegistros.java:21,185-186 usa 2 a 4 casas; Python comparators/nomes.py:41-44 fixa 2. Normalizacao numerica: Java Utilidade.java:60-104 remove digitos; Python util.py:47-55 preserva digitos.

* `ascii_0012`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Walter Zuno", "mae1": "Alva2 Zuno", "data1": "19801121", "nome2": "Valter Zuno", "mae2": "Alva Zuno", "data2": "18901121", "pair_id": "ascii_0012", "sublote": "ascii", "caso_nome": "soundex_w", "caso_data": "mes_palindromo_ano"}`
* `ascii_0014`: Java=0.6667; Python=0.67; entrada ficticia: `{"nome1": "Alva Zuno", "mae1": "Alva Breno Zuno", "data1": "1980", "nome2": "Alva Breno Zuno", "mae2": "Alva Zuno", "data2": "1981", "pair_id": "ascii_0014", "sublote": "ascii", "caso_nome": "assimetria_volta", "caso_data": "curta"}`
* `ascii_0022`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Alva Zuno", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "ascii_0022", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `ascii_0023`: Java=0; Python=0.5; entrada ficticia: `{"nome1": "", "mae1": "Celia Vale", "data1": "19801121", "nome2": "", "mae2": "Selia Vale", "data2": "18901121", "pair_id": "ascii_0023", "sublote": "ascii", "caso_nome": "ambos_ausentes", "caso_data": "mes_palindromo_ano"}`
* `ascii_0034`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Celia Vale", "mae1": "Alva2 Zuno", "data1": "19801221", "nome2": "Selia Vale", "mae2": "Alva Zuno", "data2": "", "pair_id": "ascii_0034", "sublote": "ascii", "caso_nome": "soundex_c", "caso_data": "uma_vazia"}`
* `acentos_0012`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Walter Zunó", "mae1": "Álva2 Zunó", "data1": "19801121", "nome2": "Valter Zunó", "mae2": "Álva Zunó", "data2": "18901121", "pair_id": "acentos_0012", "sublote": "acentos", "caso_nome": "soundex_w", "caso_data": "mes_palindromo_ano"}`
* `acentos_0014`: Java=0.6667; Python=0.67; entrada ficticia: `{"nome1": "Álva Zunó", "mae1": "Álva Brêno Zunó", "data1": "1980", "nome2": "Álva Brêno Zunó", "mae2": "Álva Zunó", "data2": "1981", "pair_id": "acentos_0014", "sublote": "acentos", "caso_nome": "assimetria_volta", "caso_data": "curta"}`
* `acentos_0022`: Java=0; Python=1; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Álva Zunó", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "acentos_0022", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `acentos_0023`: Java=0; Python=0.5; entrada ficticia: `{"nome1": "", "mae1": "Çélia Vále", "data1": "19801121", "nome2": "", "mae2": "Selia Vále", "data2": "18901121", "pair_id": "acentos_0023", "sublote": "acentos", "caso_nome": "ambos_ausentes", "caso_data": "mes_palindromo_ano"}`
* `acentos_0034`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Çélia Vále", "mae1": "Álva2 Zunó", "data1": "19801221", "nome2": "Selia Vále", "mae2": "Álva Zunó", "data2": "", "pair_id": "acentos_0034", "sublote": "acentos", "caso_nome": "soundex_c", "caso_data": "uma_vazia"}`

### 10: mae_raros

Estado/posicao: Java ComparaRegistros.java:94,110-117,164-166 usa contador sequencial; Python comparaRegistros.py:114-125 fixa os indices, mesmo com paciente ausente. Frequencias: Java TransformaBase.java:38-46 descarta a primeira linha e insere cada mapa na posicao 0 (ordem invertida), consumidos em ComparaRegistros.java:190-223; Python transformaBase.py:12-21 preserva todas as linhas e a ordem. Nome de um fragmento: Java ComparaRegistros.java:208-221 nao conta ultimo; Python comparators/nomes.py:49-58 conta primeiro e ultimo. Precisao: Java :21,223 versus Python :58. Normalizacao numerica: Java Utilidade.java:60-104 remove digitos; Python util.py:47-55 preserva digitos.

* `ascii_0002`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Limiar Limiar", "mae1": "Alva de Zuno Junior", "data1": "19801221", "nome2": "Limiar Limiar", "mae2": "Alva Zuno", "data2": "19801212", "pair_id": "ascii_0002", "sublote": "ascii", "caso_nome": "limiar_1000", "caso_data": "inverte_dia"}`
* `ascii_0004`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Cabecalho Cabecalho", "mae1": "Karla Zuno", "data1": "19801221", "nome2": "Cabecalho Cabecalho", "mae2": "Carla Zuno", "data2": "18901221", "pair_id": "ascii_0004", "sublote": "ascii", "caso_nome": "cabecalho_descartado", "caso_data": "inverte_ano"}`
* `ascii_0008`: Java=1; Python=2; entrada ficticia: `{"nome1": "Heraldo Vale", "mae1": "Alva", "data1": "", "nome2": "Eraldo Vale", "mae2": "Alva", "data2": "", "pair_id": "ascii_0008", "sublote": "ascii", "caso_nome": "soundex_h", "caso_data": "vazias"}`
* `ascii_0010`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Celia Vale", "mae1": "Alva Zuno", "data1": "1980", "nome2": "Selia Vale", "mae2": "A Zuno", "data2": "1981", "pair_id": "ascii_0010", "sublote": "ascii", "caso_nome": "soundex_c", "caso_data": "curta"}`
* `ascii_0011`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Yara Vale", "mae1": "Alva Zuno", "data1": "19801211", "nome2": "Iara Vale", "mae2": "Alva Breno Zuno", "data2": "18901211", "pair_id": "ascii_0011", "sublote": "ascii", "caso_nome": "soundex_y", "caso_data": "dia_palindromo_ano"}`
* `acentos_0002`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Limiar Limiar", "mae1": "Álva de Zunó Junior", "data1": "19801221", "nome2": "Limiar Limiar", "mae2": "Álva Zunó", "data2": "19801212", "pair_id": "acentos_0002", "sublote": "acentos", "caso_nome": "limiar_1000", "caso_data": "inverte_dia"}`
* `acentos_0004`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Cabecalho Cabecalho", "mae1": "Karla Zunó", "data1": "19801221", "nome2": "Cabecalho Cabecalho", "mae2": "Carla Zunó", "data2": "18901221", "pair_id": "acentos_0004", "sublote": "acentos", "caso_nome": "cabecalho_descartado", "caso_data": "inverte_ano"}`
* `acentos_0008`: Java=1; Python=2; entrada ficticia: `{"nome1": "Heraldo Vále", "mae1": "Álva", "data1": "", "nome2": "Eraldo Vále", "mae2": "Álva", "data2": "", "pair_id": "acentos_0008", "sublote": "acentos", "caso_nome": "soundex_h", "caso_data": "vazias"}`
* `acentos_0010`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Çélia Vále", "mae1": "Álva Zunó", "data1": "1980", "nome2": "Selia Vále", "mae2": "A Zunó", "data2": "1981", "pair_id": "acentos_0010", "sublote": "acentos", "caso_nome": "soundex_c", "caso_data": "curta"}`
* `acentos_0011`: Java=1; Python=0.5; entrada ficticia: `{"nome1": "Yara Vále", "mae1": "Álva Zunó", "data1": "19801211", "nome2": "Iara Vále", "mae2": "Álva Brêno Zunó", "data2": "18901211", "pair_id": "acentos_0011", "sublote": "acentos", "caso_nome": "soundex_y", "caso_data": "dia_palindromo_ano"}`

### 11: mae_comuns

Estado/posicao: Java ComparaRegistros.java:94,110-117,164-166 usa contador sequencial; Python comparaRegistros.py:114-125 fixa os indices, mesmo com paciente ausente. Mesma inversao/descarte dos mapas: Java TransformaBase.java:38-46 e ComparaRegistros.java:226-248; Python transformaBase.py:12-21 e comparators/nomes.py:60-70. Nome unico e precisao diferem como nos raros. Ambos usam estritamente >1000, nao >=1000. Normalizacao numerica: Java Utilidade.java:60-104 remove digitos; Python util.py:47-55 preserva digitos.

* `ascii_0001`: Java=-0.5; Python=-0; entrada ficticia: `{"nome1": "Breno Vale", "mae1": "Celia Vale", "data1": "19801221", "nome2": "Breno Vale", "mae2": "Selia Vale", "data2": "19801222", "pair_id": "ascii_0001", "sublote": "ascii", "caso_nome": "iguais_comuns", "caso_data": "um_digito"}`
* `ascii_0005`: Java=-1; Python=-2; entrada ficticia: `{"nome1": "Alva Zuno", "mae1": "Breno", "data1": "19801221", "nome2": "Zuno Alva", "mae2": "Breno", "data2": "19802112", "pair_id": "ascii_0005", "sublote": "ascii", "caso_nome": "trocados", "caso_data": "troca_dia_mes"}`
* `ascii_0006`: Java=-1; Python=-0.5; entrada ficticia: `{"nome1": "A Zuno", "mae1": "Breno Vale", "data1": "99999999", "nome2": "Alva Zuno", "mae2": "Breno Vale", "data2": "99999999", "pair_id": "ascii_0006", "sublote": "ascii", "caso_nome": "abreviatura_1", "caso_data": "invalida_igual"}`
* `ascii_0007`: Java=-0.5; Python=-0; entrada ficticia: `{"nome1": "Alva Zuno", "mae1": "Heraldo Vale", "data1": "abcdefgh", "nome2": "A Zuno", "mae2": "Eraldo Vale", "data2": "abcdfegh", "pair_id": "ascii_0007", "sublote": "ascii", "caso_nome": "abreviatura_2", "caso_data": "invalida_texto"}`
* `ascii_0014`: Java=-0.3333; Python=-0.33; entrada ficticia: `{"nome1": "Alva Zuno", "mae1": "Alva Breno Zuno", "data1": "1980", "nome2": "Alva Breno Zuno", "mae2": "Alva Zuno", "data2": "1981", "pair_id": "ascii_0014", "sublote": "ascii", "caso_nome": "assimetria_volta", "caso_data": "curta"}`
* `acentos_0001`: Java=-0.5; Python=-0; entrada ficticia: `{"nome1": "Brêno Vále", "mae1": "Çélia Vále", "data1": "19801221", "nome2": "Brêno Vále", "mae2": "Selia Vále", "data2": "19801222", "pair_id": "acentos_0001", "sublote": "acentos", "caso_nome": "iguais_comuns", "caso_data": "um_digito"}`
* `acentos_0005`: Java=-1; Python=-2; entrada ficticia: `{"nome1": "Álva Zunó", "mae1": "Brêno", "data1": "19801221", "nome2": "Zunó Álva", "mae2": "Brêno", "data2": "19802112", "pair_id": "acentos_0005", "sublote": "acentos", "caso_nome": "trocados", "caso_data": "troca_dia_mes"}`
* `acentos_0006`: Java=-1; Python=-0.5; entrada ficticia: `{"nome1": "A Zunó", "mae1": "Brêno Vále", "data1": "99999999", "nome2": "Álva Zunó", "mae2": "Brêno Vále", "data2": "99999999", "pair_id": "acentos_0006", "sublote": "acentos", "caso_nome": "abreviatura_1", "caso_data": "invalida_igual"}`
* `acentos_0007`: Java=-0.5; Python=-0; entrada ficticia: `{"nome1": "Álva Zunó", "mae1": "Heraldo Vále", "data1": "abcdefgh", "nome2": "A Zunó", "mae2": "Eraldo Vále", "data2": "abcdfegh", "pair_id": "acentos_0007", "sublote": "acentos", "caso_nome": "abreviatura_2", "caso_data": "invalida_texto"}`
* `acentos_0014`: Java=-0.3333; Python=-0.33; entrada ficticia: `{"nome1": "Álva Zunó", "mae1": "Álva Brêno Zunó", "data1": "1980", "nome2": "Álva Brêno Zunó", "mae2": "Álva Zunó", "data2": "1981", "pair_id": "acentos_0014", "sublote": "acentos", "caso_nome": "assimetria_volta", "caso_data": "curta"}`

### 12: mae_soundex

Estado/posicao: Java ComparaRegistros.java:94,110-117,164-166 usa contador sequencial; Python comparaRegistros.py:114-125 fixa os indices, mesmo com paciente ausente. Soundex adaptado (minusculas, regras H/Y/W/K/C/G, supressao de codigos repetidos): Java Utilidade.java:158-236 e ComparaRegistros.java:278-291; Python util.py:67-71 delega ao jellyfish e comparators/nomes.py:72-79 compara codigos. As letras iniciais diferem de caixa entre implementacoes, mas a comparacao ocorre dentro de cada implementacao; nao se comparam codigos Java contra codigos Python. Precisao 4 versus 2 casas tambem interfere. Normalizacao numerica: Java Utilidade.java:60-104 remove digitos; Python util.py:47-55 preserva digitos.

* `ascii_0014`: Java=0.5333; Python=0.53; entrada ficticia: `{"nome1": "Alva Zuno", "mae1": "Alva Breno Zuno", "data1": "1980", "nome2": "Alva Breno Zuno", "mae2": "Alva Zuno", "data2": "1981", "pair_id": "ascii_0014", "sublote": "ascii", "caso_nome": "assimetria_volta", "caso_data": "curta"}`
* `ascii_0022`: Java=0; Python=0.8; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Alva Zuno", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "ascii_0022", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `ascii_0023`: Java=0; Python=0.8; entrada ficticia: `{"nome1": "", "mae1": "Celia Vale", "data1": "19801121", "nome2": "", "mae2": "Selia Vale", "data2": "18901121", "pair_id": "ascii_0023", "sublote": "ascii", "caso_nome": "ambos_ausentes", "caso_data": "mes_palindromo_ano"}`
* `ascii_0046`: Java=0; Python=0.8; entrada ficticia: `{"nome1": "", "mae1": "Alva de Zuno Junior", "data1": "19801121", "nome2": "Alva Zuno", "mae2": "Alva Zuno", "data2": "18901121", "pair_id": "ascii_0046", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `ascii_0047`: Java=0; Python=0.8; entrada ficticia: `{"nome1": "", "mae1": "Limiar Limiar", "data1": "19801211", "nome2": "", "mae2": "Limiar Limiar", "data2": "18901211", "pair_id": "ascii_0047", "sublote": "ascii", "caso_nome": "ambos_ausentes", "caso_data": "dia_palindromo_ano"}`
* `acentos_0014`: Java=0.5333; Python=0.53; entrada ficticia: `{"nome1": "Álva Zunó", "mae1": "Álva Brêno Zunó", "data1": "1980", "nome2": "Álva Brêno Zunó", "mae2": "Álva Zunó", "data2": "1981", "pair_id": "acentos_0014", "sublote": "acentos", "caso_nome": "assimetria_volta", "caso_data": "curta"}`
* `acentos_0022`: Java=0; Python=0.8; entrada ficticia: `{"nome1": "", "mae1": "Medio Medio", "data1": "19801121", "nome2": "Álva Zunó", "mae2": "Medio Medio", "data2": "18901121", "pair_id": "acentos_0022", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `acentos_0023`: Java=0; Python=0.8; entrada ficticia: `{"nome1": "", "mae1": "Çélia Vále", "data1": "19801121", "nome2": "", "mae2": "Selia Vále", "data2": "18901121", "pair_id": "acentos_0023", "sublote": "acentos", "caso_nome": "ambos_ausentes", "caso_data": "mes_palindromo_ano"}`
* `acentos_0046`: Java=0; Python=0.8; entrada ficticia: `{"nome1": "", "mae1": "Álva de Zunó Junior", "data1": "19801121", "nome2": "Álva Zunó", "mae2": "Álva Zunó", "data2": "18901121", "pair_id": "acentos_0046", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "mes_palindromo_ano"}`
* `acentos_0047`: Java=0; Python=0.8; entrada ficticia: `{"nome1": "", "mae1": "Limiar Limiar", "data1": "19801211", "nome2": "", "mae2": "Limiar Limiar", "data2": "18901211", "pair_id": "acentos_0047", "sublote": "acentos", "caso_nome": "ambos_ausentes", "caso_data": "dia_palindromo_ano"}`

### 13: mae_abreviacoes

Estado/posicao: Java ComparaRegistros.java:94,110-117,164-166 usa contador sequencial; Python comparaRegistros.py:114-125 fixa os indices, mesmo com paciente ausente. Abreviacoes bidirecionais e denominador do primeiro nome nos dois lados: Java ComparaRegistros.java:294-320; Python comparators/nomes.py:81-91. Precisao de saida Java :21 versus Python :91. Normalizacao numerica: Java Utilidade.java:60-104 remove digitos; Python util.py:47-55 preserva digitos.

* `ascii_0142`: Java=0; Python=0.25; entrada ficticia: `{"nome1": "", "mae1": "Alva Zuno", "data1": "19801211", "nome2": "Alva Zuno", "mae2": "A Zuno", "data2": "18901211", "pair_id": "ascii_0142", "sublote": "ascii", "caso_nome": "paciente_ausente", "caso_data": "dia_palindromo_ano"}`
* `ascii_0167`: Java=0; Python=0.25; entrada ficticia: `{"nome1": "", "mae1": "A Zuno", "data1": "19801221", "nome2": "", "mae2": "Alva Zuno", "data2": "91801221", "pair_id": "ascii_0167", "sublote": "ascii", "caso_nome": "ambos_ausentes", "caso_data": "ano_permutado"}`
* `acentos_0142`: Java=0; Python=0.25; entrada ficticia: `{"nome1": "", "mae1": "Álva Zunó", "data1": "19801211", "nome2": "Álva Zunó", "mae2": "A Zunó", "data2": "18901211", "pair_id": "acentos_0142", "sublote": "acentos", "caso_nome": "paciente_ausente", "caso_data": "dia_palindromo_ano"}`
* `acentos_0167`: Java=0; Python=0.25; entrada ficticia: `{"nome1": "", "mae1": "A Zunó", "data1": "19801221", "nome2": "", "mae2": "Álva Zunó", "data2": "91801221", "pair_id": "acentos_0167", "sublote": "acentos", "caso_nome": "ambos_ausentes", "caso_data": "ano_permutado"}`

### 14: data_igual

Sem divergencia observada: Java ComparaRegistros.java:119-122,328-338; Python comparaRegistros.py:122-125 e comparators/data.py:21-28.


### 15: data_um_digito

Sem divergencia observada: Java ComparaRegistros.java:119-122,328-338; Python comparaRegistros.py:122-125 e comparators/data.py:21-28.


### 16: data_inverte_dia

Inversoes valem 0,8 no Java ComparaRegistros.java:347-369 e 1,0 no Python comparators/data.py:32-40. Python :32,35 aceita dia/mes palindromo inalterado sem exigir distancia 2 local, desviando inversoes do ano para dia/mes; Java :348,353 exige distancia local 2. Ano: Java :358-369 exige troca de duas posicoes; Python :38 aceita anagrama com distancia 2.

* `ascii_0002`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Limiar Limiar", "mae1": "Alva de Zuno Junior", "data1": "19801221", "nome2": "Limiar Limiar", "mae2": "Alva Zuno", "data2": "19801212", "pair_id": "ascii_0002", "sublote": "ascii", "caso_nome": "limiar_1000", "caso_data": "inverte_dia"}`
* `ascii_0011`: Java=0; Python=1; entrada ficticia: `{"nome1": "Yara Vale", "mae1": "Alva Zuno", "data1": "19801211", "nome2": "Iara Vale", "mae2": "Alva Breno Zuno", "data2": "18901211", "pair_id": "ascii_0011", "sublote": "ascii", "caso_nome": "soundex_y", "caso_data": "dia_palindromo_ano"}`
* `ascii_0018`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Alva Alva Zuno", "mae1": "", "data1": "19801221", "nome2": "Alva Zuno", "mae2": "Alva Vale", "data2": "19801212", "pair_id": "ascii_0018", "sublote": "ascii", "caso_nome": "duplicados", "caso_data": "inverte_dia"}`
* `ascii_0020`: Java=0; Python=1; entrada ficticia: `{"nome1": "Alva Zuno", "mae1": "Yara Vale", "data1": "19801211", "nome2": "Breno Vale", "mae2": "Iara Vale", "data2": "18901211", "pair_id": "ascii_0020", "sublote": "ascii", "caso_nome": "diferentes", "caso_data": "dia_palindromo_ano"}`
* `ascii_0021`: Java=0; Python=1; entrada ficticia: `{"nome1": "Alva2 Zuno", "mae1": "Alva Alva Zuno", "data1": "19801211", "nome2": "Alva Zuno", "mae2": "Alva Zuno", "data2": "18901211", "pair_id": "ascii_0021", "sublote": "ascii", "caso_nome": "numeros", "caso_data": "dia_palindromo_ano"}`
* `acentos_0002`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Limiar Limiar", "mae1": "Álva de Zunó Junior", "data1": "19801221", "nome2": "Limiar Limiar", "mae2": "Álva Zunó", "data2": "19801212", "pair_id": "acentos_0002", "sublote": "acentos", "caso_nome": "limiar_1000", "caso_data": "inverte_dia"}`
* `acentos_0011`: Java=0; Python=1; entrada ficticia: `{"nome1": "Yara Vále", "mae1": "Álva Zunó", "data1": "19801211", "nome2": "Iara Vále", "mae2": "Álva Brêno Zunó", "data2": "18901211", "pair_id": "acentos_0011", "sublote": "acentos", "caso_nome": "soundex_y", "caso_data": "dia_palindromo_ano"}`
* `acentos_0018`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Álva Álva Zunó", "mae1": "", "data1": "19801221", "nome2": "Álva Zunó", "mae2": "Álva Vále", "data2": "19801212", "pair_id": "acentos_0018", "sublote": "acentos", "caso_nome": "duplicados", "caso_data": "inverte_dia"}`
* `acentos_0020`: Java=0; Python=1; entrada ficticia: `{"nome1": "Álva Zunó", "mae1": "Yara Vále", "data1": "19801211", "nome2": "Brêno Vále", "mae2": "Iara Vále", "data2": "18901211", "pair_id": "acentos_0020", "sublote": "acentos", "caso_nome": "diferentes", "caso_data": "dia_palindromo_ano"}`
* `acentos_0021`: Java=0; Python=1; entrada ficticia: `{"nome1": "Álva2 Zunó", "mae1": "Álva Álva Zunó", "data1": "19801211", "nome2": "Álva Zunó", "mae2": "Álva Zunó", "data2": "18901211", "pair_id": "acentos_0021", "sublote": "acentos", "caso_nome": "numeros", "caso_data": "dia_palindromo_ano"}`

### 17: data_inverte_mes

Inversoes valem 0,8 no Java ComparaRegistros.java:347-369 e 1,0 no Python comparators/data.py:32-40. Python :32,35 aceita dia/mes palindromo inalterado sem exigir distancia 2 local, desviando inversoes do ano para dia/mes; Java :348,353 exige distancia local 2. Ano: Java :358-369 exige troca de duas posicoes; Python :38 aceita anagrama com distancia 2.

* `ascii_0003`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Medio Medio", "mae1": "Limiar Limiar", "data1": "19801221", "nome2": "Medio Medio", "mae2": "Limiar Limiar", "data2": "19802121", "pair_id": "ascii_0003", "sublote": "ascii", "caso_nome": "frequencia_5", "caso_data": "inverte_mes"}`
* `ascii_0007`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Alva Zuno", "mae1": "Heraldo Vale", "data1": "abcdefgh", "nome2": "A Zuno", "mae2": "Eraldo Vale", "data2": "abcdfegh", "pair_id": "ascii_0007", "sublote": "ascii", "caso_nome": "abreviatura_2", "caso_data": "invalida_texto"}`
* `ascii_0012`: Java=0; Python=1; entrada ficticia: `{"nome1": "Walter Zuno", "mae1": "Alva2 Zuno", "data1": "19801121", "nome2": "Valter Zuno", "mae2": "Alva Zuno", "data2": "18901121", "pair_id": "ascii_0012", "sublote": "ascii", "caso_nome": "soundex_w", "caso_data": "mes_palindromo_ano"}`
* `ascii_0016`: Java=0; Python=1; entrada ficticia: `{"nome1": "Breno", "mae1": "Alva Zuno", "data1": "19801121", "nome2": "Breno", "mae2": "Zuno Alva", "data2": "18901121", "pair_id": "ascii_0016", "sublote": "ascii", "caso_nome": "unico_comum", "caso_data": "mes_palindromo_ano"}`
* `ascii_0017`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Alva de Zuno Junior", "mae1": "Walter Zuno", "data1": "19801221", "nome2": "Alva Zuno", "mae2": "Valter Zuno", "data2": "19802121", "pair_id": "ascii_0017", "sublote": "ascii", "caso_nome": "particulas", "caso_data": "inverte_mes"}`
* `acentos_0003`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Medio Medio", "mae1": "Limiar Limiar", "data1": "19801221", "nome2": "Medio Medio", "mae2": "Limiar Limiar", "data2": "19802121", "pair_id": "acentos_0003", "sublote": "acentos", "caso_nome": "frequencia_5", "caso_data": "inverte_mes"}`
* `acentos_0007`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Álva Zunó", "mae1": "Heraldo Vále", "data1": "abcdefgh", "nome2": "A Zunó", "mae2": "Eraldo Vále", "data2": "abcdfegh", "pair_id": "acentos_0007", "sublote": "acentos", "caso_nome": "abreviatura_2", "caso_data": "invalida_texto"}`
* `acentos_0012`: Java=0; Python=1; entrada ficticia: `{"nome1": "Walter Zunó", "mae1": "Álva2 Zunó", "data1": "19801121", "nome2": "Valter Zunó", "mae2": "Álva Zunó", "data2": "18901121", "pair_id": "acentos_0012", "sublote": "acentos", "caso_nome": "soundex_w", "caso_data": "mes_palindromo_ano"}`
* `acentos_0016`: Java=0; Python=1; entrada ficticia: `{"nome1": "Brêno", "mae1": "Álva Zunó", "data1": "19801121", "nome2": "Brêno", "mae2": "Zunó Álva", "data2": "18901121", "pair_id": "acentos_0016", "sublote": "acentos", "caso_nome": "unico_comum", "caso_data": "mes_palindromo_ano"}`
* `acentos_0017`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Álva de Zunó Junior", "mae1": "Walter Zunó", "data1": "19801221", "nome2": "Álva Zunó", "mae2": "Valter Zunó", "data2": "19802121", "pair_id": "acentos_0017", "sublote": "acentos", "caso_nome": "particulas", "caso_data": "inverte_mes"}`

### 18: data_inverte_ano

Inversoes valem 0,8 no Java ComparaRegistros.java:347-369 e 1,0 no Python comparators/data.py:32-40. Python :32,35 aceita dia/mes palindromo inalterado sem exigir distancia 2 local, desviando inversoes do ano para dia/mes; Java :348,353 exige distancia local 2. Ano: Java :358-369 exige troca de duas posicoes; Python :38 aceita anagrama com distancia 2.

* `ascii_0004`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Cabecalho Cabecalho", "mae1": "Karla Zuno", "data1": "19801221", "nome2": "Cabecalho Cabecalho", "mae2": "Carla Zuno", "data2": "18901221", "pair_id": "ascii_0004", "sublote": "ascii", "caso_nome": "cabecalho_descartado", "caso_data": "inverte_ano"}`
* `ascii_0011`: Java=0.8; Python=0; entrada ficticia: `{"nome1": "Yara Vale", "mae1": "Alva Zuno", "data1": "19801211", "nome2": "Iara Vale", "mae2": "Alva Breno Zuno", "data2": "18901211", "pair_id": "ascii_0011", "sublote": "ascii", "caso_nome": "soundex_y", "caso_data": "dia_palindromo_ano"}`
* `ascii_0012`: Java=0.8; Python=0; entrada ficticia: `{"nome1": "Walter Zuno", "mae1": "Alva2 Zuno", "data1": "19801121", "nome2": "Valter Zuno", "mae2": "Alva Zuno", "data2": "18901121", "pair_id": "ascii_0012", "sublote": "ascii", "caso_nome": "soundex_w", "caso_data": "mes_palindromo_ano"}`
* `ascii_0013`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Alva Breno Zuno", "mae1": "A Zuno", "data1": "19801221", "nome2": "Alva Zuno", "mae2": "", "data2": "91801221", "pair_id": "ascii_0013", "sublote": "ascii", "caso_nome": "tres_fragmentos", "caso_data": "ano_permutado"}`
* `ascii_0015`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Alva", "mae1": "Alva Zuno", "data1": "19801221", "nome2": "Alva", "mae2": "Breno Vale", "data2": "91801221", "pair_id": "ascii_0015", "sublote": "ascii", "caso_nome": "unico_raro", "caso_data": "ano_permutado"}`
* `acentos_0004`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Cabecalho Cabecalho", "mae1": "Karla Zunó", "data1": "19801221", "nome2": "Cabecalho Cabecalho", "mae2": "Carla Zunó", "data2": "18901221", "pair_id": "acentos_0004", "sublote": "acentos", "caso_nome": "cabecalho_descartado", "caso_data": "inverte_ano"}`
* `acentos_0011`: Java=0.8; Python=0; entrada ficticia: `{"nome1": "Yara Vále", "mae1": "Álva Zunó", "data1": "19801211", "nome2": "Iara Vále", "mae2": "Álva Brêno Zunó", "data2": "18901211", "pair_id": "acentos_0011", "sublote": "acentos", "caso_nome": "soundex_y", "caso_data": "dia_palindromo_ano"}`
* `acentos_0012`: Java=0.8; Python=0; entrada ficticia: `{"nome1": "Walter Zunó", "mae1": "Álva2 Zunó", "data1": "19801121", "nome2": "Valter Zunó", "mae2": "Álva Zunó", "data2": "18901121", "pair_id": "acentos_0012", "sublote": "acentos", "caso_nome": "soundex_w", "caso_data": "mes_palindromo_ano"}`
* `acentos_0013`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Álva Brêno Zunó", "mae1": "A Zunó", "data1": "19801221", "nome2": "Álva Zunó", "mae2": "", "data2": "91801221", "pair_id": "acentos_0013", "sublote": "acentos", "caso_nome": "tres_fragmentos", "caso_data": "ano_permutado"}`
* `acentos_0015`: Java=0.8; Python=1; entrada ficticia: `{"nome1": "Álva", "mae1": "Álva Zunó", "data1": "19801221", "nome2": "Álva", "mae2": "Brêno Vále", "data2": "91801221", "pair_id": "acentos_0015", "sublote": "acentos", "caso_nome": "unico_raro", "caso_data": "ano_permutado"}`

### 19: nota_final

Soma dos comportamentos acima: Java ComparaRegistros.java:91-127,222-248,290-320,347-369 acumula sequencialmente e formata com 2 a 4 casas (:21); Python comparaRegistros.py:111-127 soma notas dos comparadores e formata com 2 casas; nomes.py:49-91 e data.py:32-40 alteram componentes.

* `ascii_0000`: Java=4.8; Python=5.3; entrada ficticia: `{"nome1": "Alva Zuno", "mae1": "", "data1": "19801221", "nome2": "Alva Zuno", "mae2": "", "data2": "19801221", "pair_id": "ascii_0000", "sublote": "ascii", "caso_nome": "iguais_raros", "caso_data": "igual"}`
* `ascii_0002`: Java=9.4; Python=9.1; entrada ficticia: `{"nome1": "Limiar Limiar", "mae1": "Alva de Zuno Junior", "data1": "19801221", "nome2": "Limiar Limiar", "mae2": "Alva Zuno", "data2": "19801212", "pair_id": "ascii_0002", "sublote": "ascii", "caso_nome": "limiar_1000", "caso_data": "inverte_dia"}`
* `ascii_0003`: Java=8.4; Python=8.6; entrada ficticia: `{"nome1": "Medio Medio", "mae1": "Limiar Limiar", "data1": "19801221", "nome2": "Medio Medio", "mae2": "Limiar Limiar", "data2": "19802121", "pair_id": "ascii_0003", "sublote": "ascii", "caso_nome": "frequencia_5", "caso_data": "inverte_mes"}`
* `ascii_0004`: Java=8.9; Python=6.6; entrada ficticia: `{"nome1": "Cabecalho Cabecalho", "mae1": "Karla Zuno", "data1": "19801221", "nome2": "Cabecalho Cabecalho", "mae2": "Carla Zuno", "data2": "18901221", "pair_id": "ascii_0004", "sublote": "ascii", "caso_nome": "cabecalho_descartado", "caso_data": "inverte_ano"}`
* `ascii_0005`: Java=4.6; Python=4.1; entrada ficticia: `{"nome1": "Alva Zuno", "mae1": "Breno", "data1": "19801221", "nome2": "Zuno Alva", "mae2": "Breno", "data2": "19802112", "pair_id": "ascii_0005", "sublote": "ascii", "caso_nome": "trocados", "caso_data": "troca_dia_mes"}`
* `acentos_0000`: Java=4.8; Python=5.3; entrada ficticia: `{"nome1": "Álva Zunó", "mae1": "", "data1": "19801221", "nome2": "Álva Zunó", "mae2": "", "data2": "19801221", "pair_id": "acentos_0000", "sublote": "acentos", "caso_nome": "iguais_raros", "caso_data": "igual"}`
* `acentos_0002`: Java=9.4; Python=9.1; entrada ficticia: `{"nome1": "Limiar Limiar", "mae1": "Álva de Zunó Junior", "data1": "19801221", "nome2": "Limiar Limiar", "mae2": "Álva Zunó", "data2": "19801212", "pair_id": "acentos_0002", "sublote": "acentos", "caso_nome": "limiar_1000", "caso_data": "inverte_dia"}`
* `acentos_0003`: Java=8.4; Python=8.6; entrada ficticia: `{"nome1": "Medio Medio", "mae1": "Limiar Limiar", "data1": "19801221", "nome2": "Medio Medio", "mae2": "Limiar Limiar", "data2": "19802121", "pair_id": "acentos_0003", "sublote": "acentos", "caso_nome": "frequencia_5", "caso_data": "inverte_mes"}`
* `acentos_0004`: Java=8.9; Python=6.6; entrada ficticia: `{"nome1": "Cabecalho Cabecalho", "mae1": "Karla Zunó", "data1": "19801221", "nome2": "Cabecalho Cabecalho", "mae2": "Carla Zunó", "data2": "18901221", "pair_id": "acentos_0004", "sublote": "acentos", "caso_nome": "cabecalho_descartado", "caso_data": "inverte_ano"}`
* `acentos_0005`: Java=4.6; Python=4.1; entrada ficticia: `{"nome1": "Álva Zunó", "mae1": "Brêno", "data1": "19801221", "nome2": "Zunó Álva", "mae2": "Brêno", "data2": "19802112", "pair_id": "acentos_0005", "sublote": "acentos", "caso_nome": "trocados", "caso_data": "troca_dia_mes"}`

## Ambiente e avisos

Artefatos brutos locais: `C:\Users\Marquinho\AppData\Local\Temp\cdr_java` (nao versionados).

```json
{
  "seed": 20150901,
  "tolerancia": 1e-09,
  "data_utc": "2026-11-04T20:23:05.528652+00:00",
  "python": "3.13.11 | packaged by Anaconda, Inc. | (main, Dec 10 2025, 21:21:58) [MSC v.1929 64 bit (AMD64)]",
  "executavel_python": "C:\\Users\\Marquinho\\miniconda3\\python.exe",
  "javac": "C:\\Users\\Marquinho\\scoop\\apps\\temurin21-jdk\\current\\bin\\javac.exe",
  "dependencias": {
    "pandas": "3.0.1",
    "jellyfish": "1.3.0",
    "Unidecode": "1.4.0",
    "pytest": "9.0.2"
  },
  "versao_javac": "javac 21.0.13",
  "versao_java": "openjdk version \"21.0.13\" 2026-10-20 LTS\nOpenJDK Runtime Environment Temurin-21.0.13+9 (build 21.0.13+9-LTS)\nOpenJDK 64-Bit Server VM Temurin-21.0.13+9 (build 21.0.13+9-LTS, mixed mode, sharing)",
  "avisos_compilacao": "D:\\git\\Comparador-de-Registros\\legado\\src\\principal\\CsvReader.java:511: warning: [removal] Integer(int) in Integer has been deprecated and marked for removal\n\t\t\theadersHolder.IndexByName.put(headers[i], new Integer(i));\n\t\t\t                                          ^\nD:\\git\\Comparador-de-Registros\\legado\\src\\principal\\CsvReader.java:1242: warning: [removal] Integer(int) in Integer has been deprecated and marked for removal\n\t\t\theadersHolder.IndexByName.put(columnValue, new Integer(i));\n\t\t\t                                           ^\nD:\\git\\Comparador-de-Registros\\legado\\src\\principal\\CsvReader.java:1596: warning: [removal] finalize() in Object has been deprecated and marked for removal\n\tprotected void finalize() {\n\t               ^\nD:\\git\\Comparador-de-Registros\\legado\\src\\principal\\CsvWriter.java:530: warning: [removal] finalize() in Object has been deprecated and marked for removal\n\tprotected void finalize() {\n\t               ^\nNote: Some input files use unchecked or unsafe operations.\nNote: Recompile with -Xlint:unchecked for details.\n4 warnings",
  "sha_fontes": {
    "legado\\src\\principal\\ComparaRegistros.java": "23aa035421dfb3485a06e0e97449031e43b0b5ca5699ba5b1f5781a862165d5c",
    "legado\\src\\principal\\CsvReader.java": "093885825f74a4a80228ec37fc9740976a1cc9eccf29140c8b914641281accf4",
    "legado\\src\\principal\\CsvWriter.java": "e8fab8ad2f847821c1398677bead279dfc251538f16c282862506e828f2f8e87",
    "legado\\src\\principal\\TelaGUI.java": "15d5635e4be4f8a992760256baeec5fed638ccaab63096a7cc9b3c88f13c8554",
    "legado\\src\\principal\\Testa.java": "7a24506564cd9ec029cbf6bf6cd2a00ff9752eedc05eba6d07d4a3d7b039691c",
    "legado\\src\\principal\\TransformaBase.java": "1c6eb980bc2f413bff4175fd1bd1b3500035a579d6065337700d3c8aee982607",
    "legado\\src\\principal\\Utilidade.java": "120fc45a4524d3313e79a3c8feb2b2548a5b5a71c428350ae9bf2dbe26e2eb0f"
  },
  "sha_entradas": {
    "acentos_utf8.csv": "ce80f026fa82887dc67b5797424eec33317194691d4093e80121c6b468ace417",
    "ascii_utf8.csv": "9b973f8539352eb7ec855c974c6ed25c5af4d0c2c4340fce6b54e60cbae92228"
  },
  "sha_frequencias": {
    "01_Frequencia_primeiro_nome_paciente.csv": "e7c98756ee857868a76fed81469698d9629fa7dcb65eaaa6920c49a3be553b22",
    "02_Frequencia_nome_do_meio_paciente.csv": "da5ac9a5d99e091e5a6401d262f4bb23c2404e96123fe84881ab0cee378c5724",
    "03_Frequencia_ultimo_nome_paciente.csv": "23ffcb9cf5cdfa4ddceee43bced81ba89214692514f92cf07f42fdb34b9aeb00",
    "04_Frequencia_primeiro_nome_mae.csv": "ccac7d3130c15a0ec1409c6df90401e3c3de1d9dd090a9ac4abec8964bb8ee4f",
    "05_Frequencia_nome_do_meio_mae.csv": "3165ab1814e4cb65e5a49dac3d9da2a6d5f1dd71ace632f0073851ca16cd40c5",
    "06_Frequencia_ultimo_nome_mae.csv": "a80cda5a0dda3de8271359da0a75318991973624c3cfd19a31a19104e0e04a03"
  }
}
```

## Regressao e limites

baseline_ascii.json congela as contagens iniciais, sem recalculo automatico nos testes. O teste exige no minimo essa concordancia por subescore, inclusive nota final, com tolerancia 1e-9. Skip somente se JDK 21+ nao for encontrado. Aumentar a concordancia e permitido; reduzi-la exige investigacao. Os resultados sao condicionados ao lote e as tabelas sinteticas, nao a distribuicao de nomes de uma populacao. Nenhuma correcao ou refatoracao dos comparadores foi feita; causas individuais nao foram isoladas por ablation.

## Verificacao desta entrega (04/11/2026)

* `python tests/equivalencia/comparar.py`: concluido com os 500 pares, tabela acima e quatro avisos de compilacao registrados em `avisos_compilacao`.
* `python -m pytest tests -q`: `70 passed in 3.87s`, incluindo os dois testes novos. Nenhum skip nesta execucao.
* Ambiente: Python do miniconda (`C:\Users\Marquinho\miniconda3\python.exe`), nao o `venv/` do repositorio; Temurin 21.0.13 para compilacao e execucao, nao Java 1.8 do PATH.
* Os avisos sao dois usos de `Integer(int)` (CsvReader.java:511,1242) e dois de `finalize()` (CsvReader.java:1596 e CsvWriter.java:530), alem da nota sobre operacoes unchecked/unsafe. O legado foi preservado.
* A secao de verificacao registra a execucao desta entrega; ao regenerar o relatorio, os testes precisam ser executados e registrados novamente.
