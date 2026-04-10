"""
This file contains validators used to guarantee the consistency of the input data on the program.
"""

import re

def is_valid_phone(phone): # [PORTUGUESE] is_valid_phone(phone): e_celular_valido(celular)
	"""
	It evaluates if the given phone is valid or not and returns True for valid and False for invalid.
	"""

	pattern1 = r"^\(\d{2}\)\s*\d{5}-?\d{4}$" # [PORTUGUESE] pattern1: padrão1
	pattern2 = r"^\d{7}-?\d{4}$" # [PORTUGUESE] pattern2: padrão2

	return re.fullmatch(pattern1, phone) or re.fullmatch(pattern2, phone)

def is_valid_name(name): # [PORTUGUESE] is_valid_name(name): e_nome_valido(nome)
	"""
	It evaluates if the given name is valid or not and returns True for valid and False for invalid.
	"""

	pattern = r"^[a-zA-Z]+$" # [PORTUGUESE] pattern: padrão

	return re.fullmatch(pattern, name)

def is_valid_town(town): # [PORTUGUESE] is_valid_town(town): e_cidade_valida(cidade)
	"""
	It evaluates if the given town is valid or not and returns True for valid and False for invalid.
	"""

	pattern = r"^[a-zA-Z]+$" # [PORTUGUESE] pattern: padrão

	return re.fullmatch(pattern, town)

def is_valid_state(state): # [PORTUGUESE] is_valid_state(state): e_estado_valido(estado)
	"""
	It evaluates if the given state is valid or not and returns True for valid and False for invalid.
	"""

	list_of_states = ["Acre",
    "Alagoas",
    "Amapá",
    "Amazonas",
    "Bahia",
    "Ceará",
    "Distrito Federal",
    "Espírito Santo",
    "Goiás",
    "Maranhão",
    "Mato Grosso",
    "Mato Grosso do Sul",
    "Minas Gerais",
    "Pará",
    "Paraíba",
    "Paraná",
    "Pernambuco",
    "Piauí",
    "Rio de Janeiro",
    "Rio Grande do Norte",
    "Rio Grande do Sul",
    "Rondônia",
    "Roraima",
    "Santa Catarina",
    "São Paulo",
    "Sergipe",
    "Tocantins"] # [PORTUGUESE] list_of_states: lista de estados

	return state in list_of_states
