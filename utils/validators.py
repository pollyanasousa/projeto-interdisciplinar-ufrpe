"""
This file contains validators used to guarantee the consistency of the input data on the program.
"""

import re

def is_valid_phone(phone): # [PORTUGUESE] is_valid_phone(phone): e_celular_valido(celular)
	pattern1 = r"^\(\d{2}\)\s*\d{5}-?\d{4}$" # [PORTUGUESE] pattern1: padrão1
	pattern2 = r"^\d{7}-?\d{4}$" # [PORTUGUESE] pattern2: padrão2

	return re.fullmatch(pattern1, phone) or re.fullmatch(pattern2, phone)
