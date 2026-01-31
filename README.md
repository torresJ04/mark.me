# Mark.me

Aplicação **desktop** e **CLI** para destacar termos em PDFs com cor personalizada. Vários termos por vez, cada um com sua cor. **4 idiomas** (inglês padrão) com seletor na interface.

## O que faz

- **GUI:** janela com seletor de PDF; **até 32 termos** em grid 4×8 com scroll; cada termo tem campo de texto + cor ao lado (clique no quadrado para escolher); botão "+ Adicionar termo" e "×" para remover; **seletor de idioma** (English, Português, Deutsch, Español); gera PDF marcado e "Salvar como".
- **CLI:** comando `mark` com múltiplos `-t` e `-c`; cada termo pode ter sua cor.

## Idiomas (i18n)

- **Inglês** (padrão), **Português (pt_BR)**, **Alemão (de)**, **Espanhol (es)**.
- Na GUI: dropdown "Language" no canto superior direito; a troca aplica na hora em toda a interface.

## GUI — Como usar

1. Na **raiz do repositório** (pasta do repo clonado), ative o venv e entre na pasta do Mark.me:

   ```bash
   source .venv/bin/activate
   cd mark_me
   ```

2. Instale dependências e rode a aplicação:

   ```bash
   pip install -r requirements.txt
   python3 app.py
   ```

   Ou, da raiz do repo, após instalar o pacote em modo editável (veja CLI abaixo):

   ```bash
   python3 -m mark_me
   ```

   Abre uma janela: escolha o PDF, adicione termos (cada um com cor ao lado), use "+ Adicionar termo" se quiser mais (máx. 32), troque o idioma no dropdown se quiser, e clique em **Gerar PDF marcado**.

## CLI — Comando `mark`

Para ter o comando `mark` disponível no terminal, instale o projeto em modo editável na **raiz do repositório**, **não** de dentro da pasta `mark_me` (o `pyproject.toml` fica na raiz):

```bash
cd /caminho/do/repo
source .venv/bin/activate
pip install -e .
```

Depois use:

```bash
mark ARQUIVO.pdf -t "termo" -pick                    # um termo, abre seletor de cor
mark ARQUIVO.pdf -t "a" -t "b" -c "#fff" -c "#f00"   # vários termos, cada um com sua cor
mark ARQUIVO.pdf -t "a" -t "b" -o saida.pdf           # vários termos, mesma cor (amarelo)
```

- **ARQUIVO** — caminho do PDF  
- **-t / --term** — termo a destacar (pode repetir: `-t "a" -t "b"`)  
- **-pick** — abre o seletor de cor (uma cor para todos os termos)  
- **-c / --color** — cor em hex por termo. Faltando usa amarelo  
- **-o / --output** — arquivo de saída. Se omitido, usa `nome_marcado.pdf` na mesma pasta  

## Requisitos

- Python 3.10+
- **Tkinter** — na maioria das instalações já vem com o Python. No macOS com Homebrew, se der `No module named '_tkinter'`, instale: `brew install python-tk@3.14` (ou a versão do seu Python).
- **PyMuPDF** — `pip install pymupdf` (ou via `pip install -e .` na raiz).

## Estrutura (arquivos relevantes para o repo)

```
mark_me/
  __init__.py
  __main__.py
  app.py          # launcher da GUI (rodar de dentro de mark_me)
  core.py         # lógica de destaque (hex → RGB, PyMuPDF)
  gui.py          # interface Tkinter (multi-termo, i18n, switcher)
  cli.py          # interface de linha de comando (mark)
  i18n.py         # internacionalização (en, pt_BR, de, es)
  locales/        # traduções JSON
    en.json
    pt_BR.json
    de.json
    es.json
  requirements.txt
  .gitignore
pyproject.toml    # na raiz: pip install -e . e comando mark
README.md         # este arquivo (página inicial do GitHub)
```

O que **não** deve ser versionado: `__pycache__/`, `*.pyc`, `.venv/`, `*.egg-info/`, `.DS_Store` (tratados pelo `.gitignore` na raiz).
