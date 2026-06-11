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

from gui import agrobook_window
from model.farmer import Farmer
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
	# Initializes the data folder and JSON files with empty structure
	os.makedirs("data", exist_ok=True)

	if not os.path.exists("data/farmer.json"):
		with open("data/farmer.json", "w", encoding="utf-8") as f:
			json.dump({}, f)

	if not os.path.exists("data/area.json"):
		with open("data/area.json", "w", encoding="utf-8") as f:
			json.dump({"list_of_area": []}, f)

	if not os.path.exists("data/planting.json"):
		with open("data/planting.json", "w", encoding="utf-8") as f:
			json.dump({"list_of_planting": []}, f)

	if not os.path.exists("data/harvest.json"):
		with open("data/harvest.json", "w", encoding="utf-8") as f:
			json.dump({"list_of_harvest": []}, f)

	if not os.path.exists("data/expense.json"):
		with open("data/expense.json", "w", encoding="utf-8") as f:
			json.dump({"list_of_expenses": []}, f)

	if not os.path.exists("data/coowners.json"):
		with open("data/coowners.json", "w", encoding="utf-8") as f:
			json.dump({"list_of_coowners": []}, f)

	if not os.path.exists("data/measures.json"):
		with open("data/measures.json", "w", encoding="utf-8") as f:
			json.dump({"history": []}, f)

	# We start with our farmer, the protagonist:
	farmer = Farmer("data/farmer.json")

	farmer_loaded = farmer.read(True)
	""" We need this True because, on the first access, it would appear on the screen a message error of failure on reading the farmer file, because the JSON file is expected (part of the logic) to be empty.
	"""

	app = QApplication(sys.argv)
	gui = agrobook_window.AgroBookWindow(farmer)

	# If the farmer is already registered (data exists and was loaded successfully),
	# skip the initial screen and go straight to the home screen.
	if farmer_loaded == 0 and farmer.phone_number:
		gui.stacked_widget.setCurrentIndex(6)

	gui.show()
	sys.exit(app.exec())
