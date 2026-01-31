"""
Permite rodar: python -m mark_me (GUI) ou python -m mark_me mark file -term x -pick (CLI).
"""
import sys
import os

# Garante que o pacote mark_me seja encontrado ao rodar de qualquer diretório
_here = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_here)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

if len(sys.argv) >= 2 and sys.argv[1].lower() == "mark":
    # CLI: python -m mark_me mark file.pdf -term x -pick
    sys.argv.pop(1)
    from mark_me.cli import main
    sys.exit(main())
else:
    # GUI
    from mark_me.gui import MarkMeApp
    app = MarkMeApp()
    app.run()
