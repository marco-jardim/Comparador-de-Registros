# Comparador de Registros

**Comparador de Registros** é uma aplicação Python que pontua a similaridade entre registros (paciente × paciente) usando combinações de nome completo, nome da mãe e data de nascimento. A solução surgiu partir de uma base Java legada e hoje entrega:

- **Interface gráfica em Tkinter** com barra de progresso e controle do número de núcleos utilizados.
- **Comparadores especializados** (texto, datas, nomes, logradouro) com uso automático das bibliotecas mais rápidas disponíveis.
- **Pipeline de testes e build automatizado** que distribui executáveis multi-plataforma via GitHub Actions.

> 🗂️ **Estrutura do repositório (resumo)**
>
> ```text
> src/
> ├─ gui.py                  # Interface Tk
> ├─ comparaRegistros.py     # Núcleo de pontuação
> ├─ freqBuilder.py          # Construção e cache de tabelas de frequência
> ├─ util.py                 # Normalização, Soundex e distâncias
> ├─ comparators/            # Comparadores especializados
> ├─ transformabase.py       # Conversão de bases legadas
> └─ ...
> tests/
> ├─ unit/                   # Testes de unidade
> ├─ functional/             # Fluxos completos usando CSVs reais
> └─ integration/            # Testes entre módulos principais
> .github/workflows/         # Pipeline CI (testes + build + release)
> requirements.txt           # Dependências pinadas (pip freeze)
> README.md                  # Este guia
> LICENSE                    # GPL-3.0
> ```

---

## 1. Pré-requisitos

| Item    | Versão sugerida | Observação                                       |
| ------- | ---------------- | ------------------------------------------------ |
| Python  | 3.11 ou superior | CI oficial roda em 3.11; localmente testado até 3.13 |
| pip     | Última versão    | `python -m pip install --upgrade pip`            |
| Git     | Opcional         | Facilita baixar e atualizar o repositório        |

Tkinter acompanha as distribuições oficiais do Python (Windows/macOS). Em Linux Debian/Ubuntu instale com `apt install python3-tk`.

---

## 2. Instalação passo a passo (para iniciantes)

### 2.1 Clonar o projeto

```bash
git clone https://github.com/marco-jardim/Comparador-de-Registros.git
cd Comparador-de-Registros
```

> Alternativa: baixe o ZIP pelo botão **Code ▾ ➜ Download ZIP** e extraia.

### 2.2 Criar e ativar um ambiente virtual

```bash
python -m venv .venv

# Ativar (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Ativar (Linux/macOS/Git Bash)
source .venv/bin/activate
```

Finalize com `deactivate` quando quiser sair do ambiente virtual.

### 2.3 Instalar dependências

```bash
(.venv) pip install --upgrade pip
(.venv) pip install -r requirements.txt
```

> ℹ️ O arquivo `requirements.txt` é gerado via `pip freeze`, portanto inclui tanto dependências necessárias em produção (pandas, RapidFuzz, python-Levenshtein, Unidecode, Jellyfish) quanto ferramentas usadas pela suíte de testes e notebooks (pytest, ipykernel, etc.). Todas são instaladas automaticamente para reproduzir fielmente o ambiente usado na integração contínua.

Caso esteja em um ambiente com restrições e deseje o mínimo essencial, instale manualmente `pandas`, `RapidFuzz`, `python-Levenshtein`, `Unidecode` e `jellyfish`. O código faz fallback para implementações Python puras quando esses aceleradores não estiverem disponíveis, porém com processamento mais lento.

---

## 3. Testes automatizados

A suíte de testes usa **pytest** e cobre cenários de unidade, integração e fluxo completo.

```bash
(.venv) pytest                 # executa tudo
(.venv) pytest tests/unit      # apenas unitários
(.venv) pytest -k nomes        # filtra por expressão
```

Os testes são executados automaticamente no GitHub Actions antes de cada build. É altamente recomendado rodá-los localmente antes de abrir um Pull Request ou gerar executáveis.

---

## 4. Executar a aplicação (GUI)

```bash
(.venv) python src/gui.py
```

### 4.1 Uso rápido

1. **Abrir CSV** → clique em **Abrir** e selecione o arquivo de entrada.
2. **Configurar colunas** → ajuste as letras das colunas nos comboboxes se o layout não for o padrão.
3. **Comparar** → clique em **Comparar** para iniciar o processamento. A barra de progresso mostra o andamento e, ao final, `saida.csv` é criado com o mesmo separador do arquivo original.

O resultado é ordenado pela nota final (decrescente). Alterar o critério de ordenação antes de iniciar reflete imediatamente no arquivo gerado.

### 4.2 Mapeamento de colunas padrão

| Coluna | Campo             |
| ------ | ----------------- |
| J      | Nome 1            |
| K      | Nome da mãe 1     |
| L      | Data de nascimento 1 |
| N      | Nome 2            |
| O      | Nome da mãe 2     |
| P      | Data de nascimento 2 |

Se os nomes das colunas forem simples (sem prefixos do OpenRecLink), desmarque **Formato OpenRecLink** antes de abrir o arquivo. O separador padrão é vírgula (`,`); no modo OpenRecLink é pipe (`|`). Ambos podem ser alterados no campo **Separador**.

### 4.3 Uso de múltiplos núcleos

A caixa **Núcleos** define quantos processadores serão utilizados para paralelizar a comparação. O valor inicial corresponde a 75 % dos núcleos disponíveis, mas você pode aumentar ou reduzir conforme o hardware.

---

## 5. Linha de comando (CLI)

Para executar sem interface gráfica:

```bash
(.venv) python -m src.comparaRegistros path/entrada.csv saida --idx 9 10 11 13 14 15
```

O parâmetro `--idx` recebe os seis índices (0-based) referentes aos campos Nome1, Mãe1, Data1, Nome2, Mãe2, Data2. Consulte `python -m src.comparaRegistros --help` para ver todas as opções disponíveis.

---

## 6. Cache das tabelas de frequência

Na primeira execução, o sistema cria a pasta `.freq_cache/` processando o CSV em blocos de aproximadamente 500 mil linhas. Se a base for atualizada ou o cache ficar obsoleto, basta removê-lo:

```bash
rm -r .freq_cache
```

O diretório será reconstruído automaticamente em uma nova execução.

---

## 7. Perguntas frequentes

| Problema / Mensagem                                      | Causa provável                         | Como resolver                                                        |
| -------------------------------------------------------- | -------------------------------------- | -------------------------------------------------------------------- |
| `ModuleNotFoundError: pandas`                            | Ambiente virtual não ativado           | Rode o comando de ativação do venv e reinstale as dependências       |
| GUI abre mas congela sem barra de progresso              | Script incorreto foi executado         | Utilize `python src/gui.py` em vez de chamar módulos internos        |
| Notas muito diferentes das versões antigas               | Tabelas de frequência desatualizadas   | Exclua `.freq_cache/` para reconstruir com a base atual              |
| RapidFuzz/python-Levenshtein não instala (ambiente ARM)  | Sem wheels pré-compiladas              | A aplicação funciona com fallback Python puro, porém mais lento      |
| Erros com vírgula decimal (`ValueError: could not parse`) | Dados com `2,00` ou similar            | Versões atuais normalizam automaticamente; garanta estar na branch main |

---

## 8. Pipeline e build de executáveis

- O workflow `build-release.yml` roda em todo push para `main` e quando PRs são mesclados.
- As etapas seguem a ordem **prepare-version ➜ tests ➜ build ➜ release**: o build só começa se toda a suíte `pytest` passar.
- Executáveis são empacotados com **PyInstaller** para Windows, macOS e Linux e publicados como artefatos.

Para gerar manualmente um executável local (exemplo em Windows, com venv ativo):

```bash
(.venv) pyinstaller --noconfirm --onefile --add-data "version.env;." src/gui.py
```

Em sistemas Unix-like substitua `;` por `:` dentro do argumento `--add-data`. O arquivo `version.env` é criado automaticamente no pipeline; para gerar manualmente em desenvolvimento, crie o arquivo com o conteúdo:

```text
APP_VERSION=0.0-dev
APP_VERSION_DATE=2025-09-26
```

Substitua pelos valores desejados (por exemplo, usando a data atual). Executar o workflow no GitHub também produz o `version.env` correto como parte dos artefatos.

---

## 9. Contribuindo

1. Abra uma issue para discutir mudanças maiores (ex.: novos formatos de entrada, integrações externas).
2. Crie um branch dedicado.
3. Rode `pytest` antes do commit final para garantir que a suíte continue verde.
4. Abra o Pull Request seguindo o estilo PEP 8 e descrevendo o impacto da alteração.

Contribuições pequenas (refactors, documentação, traduções) também são muito bem-vindas.

---

## 10. Licença

Distribuído sob a **GNU General Public License v3.0**. Consulte o arquivo [`LICENSE`](LICENSE) para detalhes completos.
