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
from utils.menu import *

def login(farmer): # [PORTUGUESE] login(): login()
	"""
	It signs in the farmer, receiving, and modifying, in case of success, the farmer object. This function returns 0 in the successful case and 1 in case of failure.
	"""

	phone_number = input("Digite seu número de celular: ")

	return farmer.read(phone_number)

def create_account(farmer): # [PORTUGUESE] create_account(): criar_conta()
	"""
	It signs up the farmer, receiving the farmer object, which will be modified.
	"""

	farmer.get_phone()

	print("Bem-vindo! É um prazer tê-lo conosco!")
	print("Como você se chama?")

	farmer.get_name()
	farmer.get_town()
	farmer.get_state()

	# And now his memory will be on the data/farmer.json file:
	farmer.save()

def main():
	print("------------------------------------------------------------------")
	print("|*************************** AGROBOOK ***************************|")
	print("|                                                                |")
	print("| Organizando a produção rural para gerar dados e oportunidades. |")
	print("|                                                                |")
	print("|****************************************************************|")
	print("------------------------------------------------------------------")
	print("")

	option = show_menu(["Login", "Criar uma conta"])

	# We start with our farmer, the protagonist:
	farmer = Farmer() # [Portuguese] farmer: agricultor

	if option == 0: # Login
		if login(farmer) == 1:
			print("Usuário com número de telefone não encontrado... vamos criar uma conta!")
			create_account(farmer)

		else:
			print(f"Seja bem-vindo, {farmer.name}!")

	else: # Create an account
		create_account(farmer)

if __name__ == "__main__":
	main()

