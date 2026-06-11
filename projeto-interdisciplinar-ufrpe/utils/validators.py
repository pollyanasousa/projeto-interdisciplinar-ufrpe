"""
This file contains validators used to guarantee the consistency of the input data on the program.
"""

from datetime import datetime

import re

from utils.textprocessor import *
from utils.states import list_of_states
from utils.language_parser import parse_date

def is_valid_phone(phone):
	"""
	It evaluates if the given phone is valid or not and returns True for valid and False for invalid.
	"""

	pattern1 = r"^\(\d{2}\)\s*\d{5}-?\d{4}$"
	pattern2 = r"^\d{7}-?\d{4}$"

	return re.fullmatch(pattern1, phone) or re.fullmatch(pattern2, phone)

def is_valid_name(name, allow_numbers=False):
	"""
	It evaluates if the given name is valid or not and returns True for valid and False for invalid.

    The allow_numbers, if True, considers numbers as valid letters, and the opposite if False.
	"""

	pattern = r"^[a-zA-ZÁ-ÿ ]+$" if allow_numbers == False else r"^[0-9a-zA-ZÁ-ÿ ]+$"

	return re.fullmatch(pattern, name)

def is_valid_cpf(cpf):
	"""
	It evaluates if the given CPF is valid or not and returns True for valid and False for invalid.
	"""

	pattern = r"^(\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})$"

	if re.fullmatch(pattern, cpf):
		# Testing the so called "dígitos verificadores":
		cpf = re.sub(r'\D', '', cpf)

		_sum = 0
		for i, weight in enumerate(range(10, 1, -1)):
			_sum += int(cpf[i]) * weight

		remainder = (_sum * 10) % 11
		first_digit = remainder if remainder < 10 else 0

		_sum = 0
		for i, weight in enumerate(range(11, 1, -1)):
			_sum += int(cpf[i]) * weight

		remainder = (_sum * 10) % 11
		second_digit = remainder if remainder < 10 else 0

		return first_digit == int(cpf[-2]) and second_digit == int(cpf[-1])

	else:
		return False

def is_valid_town(town):
	"""
	It evaluates if the given town is valid or not and returns True for valid and False for invalid.
	"""

	pattern = r"^[a-zA-ZÁ-ÿ ]+$"

	return re.fullmatch(pattern, town)

def is_valid_state(state):
	"""
	It evaluates if the given state is valid or not and returns True for valid and False for invalid.
	"""

	return state in list_of_states

def is_valid_date(date):
	"""
	Aceita datas em formato dd/mm/yyyy OU em linguagem natural do agricultor
	(ex: hoje, ontem, semana passada, ha 3 dias, etc).
	Retorna True se válido, False caso contrário.
	"""
	# Tenta formato padrão
	pattern = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$"
	if re.fullmatch(pattern, date.strip()):
		try:
			datetime.strptime(date.strip(), "%d/%m/%Y")
			return True
		except ValueError:
			return False
	# Tenta linguagem natural
	_, ok = parse_date(date)
	return ok

