# Comparador de Registros

**Comparador de Registros** é uma aplicação Python que pontua a similaridade entre registros (paciente × paciente) usando:

* Nome completo do paciente
* Nome da mãe
* Data de nascimento

Originalmente escrita em Java, a lógica foi portada para Python, adicionando:

* **GUI** em Tkinter com barra de progresso em tempo real
* **Gerador de amostras sintéticas** (com typos/ruído)
* Estatísticas resumidas pós‑processamento
* Geração automática (e cache) das **tabelas de frequência** para bases grandes

> 🗂 **Estrutura do repositório**
>
> ```text
> src/
> ├─ gui.py                # Interface Tk + progresso + estatísticas
> ├─ comparaRegistros.py   # Núcleo de pontuação
> ├─ util.py               # Soundex, padronização, Levenshtein…
> ├─ freqbuilder.py        # Constrói tabelas de frequência on‑the‑fly
> └─ …                     # Módulos auxiliares
> requirements.txt         # Dependências PyPI
> README.md                # Este guia
> LICENSE                  # GPL‑3.0
> ```

---

## 1. Pré‑requisitos

| Item   | Versão Sugerida | Observação                    |
| ------ | --------------- | ----------------------------- |
| Python | ≥ 3.9           | Testado em 3.9 – 3.12         |
| Git    | opcional        | Facilita clonar o repositório |

Tkinter já acompanha a distribuição oficial do Python (Windows/macOS) ou pode ser instalado via `apt install python3-tk` (Ubuntu/Debian).

---

## 2. Instalação passo a passo (para iniciantes)

### 2.1 Clonar o projeto

```bash
# ① Clonar via Git (recomendado)
$ git clone https://github.com/marco-jardim/Comparador-de-Registros.git
$ cd Comparador-de-Registros

# ou → baixar ZIP em “Code ▾” e extrair
```

### 2.2 Criar ambiente virtual

```bash
# ② Criar venv na pasta .venv
$ python -m venv .venv

# ③ Ativar o venv
#    Windows PowerShell
$ .venv\Scripts\Activate.ps1
#    Linux / macOS / Git Bash
$ source .venv/bin/activate

(.venv) $   # o prompt muda indicando que o venv está ativo
```

Para sair depois: `deactivate`.

### 2.3 Instalar dependências

```bash
(.venv) $ pip install --upgrade pip     # opcional, mas recomendado
(.venv) $ pip install -r requirements.txt
```

> **requirements.txt**
>
> ```
> pandas>=2.0
> jellyfish>=1.0       # soundex otimizado em C
> python-Levenshtein   # distância de Levenshtein rapidíssima
> unidecode            # remoção de acentos
> ```

Instalação típica leva menos de 1 minuto.

---

## 3. Executar a aplicação (GUI)

```bash
(.venv) $ python src/gui.py
```

### 3.1 Uso rápido

1. **Gerar Amostra**  → informe quantidade (ex.: `1000`)   ▶ *Gerar amostra*.
   A barra mostrará o progresso.
2. **Comparar**  → após escolher/generar o CSV, clique **Comparar**.
   Surgirá uma janela de progresso indeterminado; ao concluir, `saida.csv` (e `saida2.csv`) são criados.
3. **Ver Estatísticas**  → clique *Estatísticas* para ver média, desvio‑padrão, etc.

### 3.2 Mapeamento de colunas

*Layout padrão (amostra)*:
\| Coluna | Campo |
\| J | Nome 1 |  K | Nome Mãe 1 |  L | Nasc. 1 |
\| N | Nome 2 |  O | Nome Mãe 2 |  P | Nasc. 2 |

Se o seu CSV real divergir, basta selecionar as letras corretas nos comboboxes antes de comparar.

---

## 4. Linha de comando (opcional/avançado)

Para rodar sem GUI:

```bash
(.venv) $ python -m src.comparaRegistros path/entrada.csv saida --idx 9 10 11 13 14 15
```

*`--idx` recebe os 6 índices (0‑based) das colunas Nome1, Mãe1, Data1, Nome2, Mãe2, Data2.*

---

## 5. Cache das tabelas de frequência

Ao comparar pela primeira vez, o script cria `.freq_cache/` lendo o CSV em *chunks* (\~500 k linhas). Se sua base mudou bastante, apague a pasta e o cache será reconstruído.

```bash
$ rm -r .freq_cache
```

---

## 6. Perguntas frequentes

| Problema                           | Causa comum         | Como resolver                           |
| ---------------------------------- | ------------------- | --------------------------------------- |
| `ModuleNotFoundError: pandas`      | venv não ativado    | Execute `activate` e reinstale deps     |
| GUI congela sem barra de progresso | Rodou script errado | Use `python src/gui.py` oficial         |
| Erro de vírgula decimal            | CSV com `2,00`      | Versão atual já converte, atualize repo |
| Colunas não batem                  | Comboboxes errados  | Selecione letras corretas e recompare   |

---

## 7. Contribuindo

* **Issues**: descreva bugs ou sugira melhorias.
* **Pull Requests** são bem‑vindos – siga PEP 8 e inclua comentários.

Para grandes novas features (e.g. suporte a Parquet, CLI detalhada), abra uma issue para discutir antes.

---

## 8. Licença

Distribuído sob a **GNU General Public License v3.0**. Consulte o arquivo [`LICENSE`](LICENSE) para detalhes completos.
