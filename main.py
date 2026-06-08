"""
AGROBOOK
Agricultural project for the discipline "PISI1" (Projeto Interdisciplinar para Sistemas de Informação 1), at UFRPE (Universidade Federal Rural de Pernambuco)

===============
Authors:
Gabriel Soares
Pollyana Cassia
===============

=============
Professor:
Cleyton Vanut
=============

2026

"""

import sys

from PyQt6.QtWidgets import QApplication

from gui import Gui

if __name__ == "__main__":
	app = QApplication(sys.argv)
	gui = Gui()
	gui.show()
	sys.exit(app.exec())
