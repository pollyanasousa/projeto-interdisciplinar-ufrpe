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

	farmer.read(True)
	""" We need this True because, on the first access, it would appear on the screen a message error of failure on reading the farmer file, because the JSON file is expected (part of the logic) to be empty.
	"""

	if farmer.phone_number == "": # We need to create an account
		farmer.create_account()

	print(f"Seja bem-vindo, {farmer.name}!")

	running = True
	while running:
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

if __name__ == "__main__":
	main()

