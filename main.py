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
import os
import json

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

	# Initializes the data folder and JSON files with empty structure
	os.makedirs("data", exist_ok=True)

	if not os.path.exists("data/farmer.json"):
		with open("data/farmer.json", "w") as f:
			json.dump({}, f)

	if not os.path.exists("data/area.json"):
		with open("data/area.json", "w") as f:
			json.dump({"list_of_area": []}, f)

	if not os.path.exists("data/planting.json"):
		with open("data/planting.json", "w") as f:
			json.dump({"list_of_planting": []}, f)

	if not os.path.exists("data/harvest.json"):
		with open("data/harvest.json", "w") as f:
			json.dump({"list_of_harvest": []}, f)

	if not os.path.exists("data/expense.json"):
		with open("data/expense.json", "w") as f:
			json.dump({"list_of_expenses": []}, f)

	# We start with our farmer, the protagonist:
	farmer = Farmer("data/farmer.json")

	farmer.read(True)
	""" We need this True because, on the first access, it would appear on the screen a message error of failure on reading the farmer file, because the JSON file is expected (part of the logic) to be empty.
	"""

	if farmer.phone_number == "": # If there is no phone, it's a signal we need to create an account
		farmer.create_account()

	print(f"Seja bem-vindo, {farmer.name}!")

	running = True
	while running:
		print("")
		print("------------------------------------------------------------------")
		print("|" + "  Escolha uma opção  ".center(64, "*") + "|")
		print("------------------------------------------------------------------")
		print("")
		option = show_menu(["Meus dados pessoais", "Consultar áreas", "Consultar plantio", "Colheita e gastos", "Gerar relatório de safra", "Sair"])

		if option == 0:
			farmer.who_am_i()
		elif option == 1:
			farmer.area.show_area()
		elif option == 2:
			farmer.planting.show_planting()
		elif option == 3:
			option = show_menu(["Gerenciar colheita", "Gerenciar gastos", "Ver histórico"])

			if option == 0:
				farmer.harvest.manage_harvest()
			elif option == 1:
				farmer.expense.manage_expenses()
			elif option == 2:
				farmer.harvest.show_harvest()
				farmer.expense.show_expenses()

		elif option == 4:
			farmer.report.gen_report()
		elif option == 5:
			print("Até a próxima!")
			sys.exit(0)

if __name__ == "__main__":
	main()