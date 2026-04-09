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

from model.farmer import *

def main():
	# Here it starts a beautiful story...
	# First, we start with our farmer, the protagonist:
	farmer = Farmer() # [Portuguese] farmer: agricultor

	# Then, the farmer is invited to introduce himself:

	farmer.get_phone()

	print("Bem-vindo! É um prazer tê-lo conosco!")
	print("Como você se chama?")

	farmer.get_name()
	farmer.get_town()
	farmer.get_state()

	# And now his memory will be on the data/farmer.json file:
	farmer.save()

if __name__ == "__main__":
	main()

