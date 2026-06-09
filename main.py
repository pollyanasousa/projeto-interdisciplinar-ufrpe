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

import json
import os
import sys

from PyQt6.QtWidgets import QApplication

from gui import Gui
from model.farmer import Farmer

if __name__ == "__main__":
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

	app = QApplication(sys.argv)
	gui = Gui(farmer)
	gui.show()
	sys.exit(app.exec())
