"""
Mark.me - Interface de linha de comando.

Uso:
  mark <arquivo.pdf> -t "termo1" -t "termo2" [-c "#hex1" -c "#hex2"] [-o saida.pdf]
  Vários -t e -c: primeiro -t com primeiro -c, etc. Cores faltando usam amarelo.
  -pick abre o seletor de cor (um único) para todos os termos; use -c para cores por termo.
"""
import argparse
import os
import sys

try:
    from mark_me.core import contar_ocorrencias_multi, destacar_pdf_multi
except ImportError:
    from core import contar_ocorrencias_multi, destacar_pdf_multi


def _pick_color() -> str:
    """Abre o seletor de cor do sistema e retorna hex."""
    import tkinter as tk
    from tkinter import colorchooser
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    rgb, hex_str = colorchooser.askcolor(title="Cor do marca-texto", initialcolor="#ffff00")
    root.destroy()
    return (hex_str or "#ffff00").strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="mark",
        description="Mark.me — destaque termos em PDF com cor personalizada.",
    )
    parser.add_argument(
        "pdf",
        metavar="ARQUIVO",
        help="Caminho do arquivo PDF",
    )
    parser.add_argument(
        "-t", "--term",
        action="append",
        metavar="TERMO",
        default=None,
        help="Termo a destacar (pode repetir: -t 'a' -t 'b')",
    )
    parser.add_argument(
        "-pick",
        action="store_true",
        help="Abrir seletor de cor (uma cor para todos os termos)",
    )
    parser.add_argument(
        "-c", "--color",
        action="append",
        metavar="HEX",
        default=None,
        help="Cor em hex por termo (ex: -t 'a' -t 'b' -c '#fff' -c '#f00')",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="ARQUIVO",
        help="Arquivo de saída. Se omitido, usa <nome>_marcado.pdf na mesma pasta.",
    )
    args = parser.parse_args()

    termos_raw = args.term or []
    termos = [t.strip() for t in termos_raw if t and t.strip()]
    if not termos:
        print("Erro: informe ao menos um termo (-t 'termo').", file=sys.stderr)
        return 1

    pdf_path = os.path.abspath(args.pdf)
    if not os.path.isfile(pdf_path):
        print(f"Erro: arquivo não encontrado: {pdf_path}", file=sys.stderr)
        return 1

    try:
        n = contar_ocorrencias_multi(pdf_path, termos)
    except Exception as e:
        print(f"Erro ao ler o PDF: {e}", file=sys.stderr)
        return 1
    if n == 0:
        print("Nenhuma ocorrência dos termos no PDF. Nada a processar.", file=sys.stderr)
        return 1

    cores_raw = (args.color or [])
    cores = []
    for c in cores_raw:
        cx = (c or "#ffff00").strip()
        if not cx.startswith("#"):
            cx = "#" + cx
        cores.append(cx)
    if args.pick:
        cor_unica = _pick_color()
        pares = [(t, cor_unica) for t in termos]
    else:
        pares = []
        for i, t in enumerate(termos):
            pares.append((t, cores[i] if i < len(cores) else "#ffff00"))

    if args.output:
        out_path = os.path.abspath(args.output)
    else:
        nome_base = os.path.splitext(os.path.basename(pdf_path))[0]
        dir_base = os.path.dirname(pdf_path)
        out_path = os.path.join(dir_base, f"{nome_base}_marcado.pdf")

    try:
        destacar_pdf_multi(pdf_path, out_path, pares)
        print(f"Pronto: {out_path}")
        return 0
    except Exception as e:
        print(f"Erro ao processar o PDF: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
