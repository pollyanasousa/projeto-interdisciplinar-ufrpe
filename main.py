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

from model.farmer import *
from utils.menu import *

def main():
	print("------------------------------------------------------------------")
	print("|*************************** AGROBOOK ***************************|")
	print("|                                                                |")
	print("| Organizando a produção rural para gerar dados e oportunidades. |")
	print("|                                                                |")
	print("|****************************************************************|")
	print("------------------------------------------------------------------")
	print("")

	# We start with our farmer, the protagonist:
	farmer = Farmer("data/farmer.json")

	print(f"Seja bem-vindo, {farmer.name}!")
	option = show_menu(["Consultar plantio", "Consultar colheita", "Consultar despesas", "Gerar relatório de safra", "Sair"])

	if option == 0:
		pass
	elif option == 1:
		pass
	elif option == 2:
		pass
	elif option == 3:
		pass
	elif option == 4:
		sys.exit(0)

	main()

if __name__ == "__main__":
	main()

