"""
Mark.me - Aplicação desktop para destacar termos em PDFs com cor personalizada.
Launcher: garante que o pacote mark_me seja encontrado e abre a GUI.
"""
import os
import sys

# Permite rodar "python app.py" de dentro da pasta mark_me
_here = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_here)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from mark_me.gui import MarkMeApp

if __name__ == "__main__":
    app = MarkMeApp()
    app.run()
