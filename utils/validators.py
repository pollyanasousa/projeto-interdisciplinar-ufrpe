"""
validators.py — Validadores de dados do AgroBook.

O QUE MUDOU NA VA3:
Na VA2, esse arquivo tinha uma função is_valid_date() que usava regex
para validar expressões de data como "ontem" ou "semana passada".

Na VA3, essa função foi REMOVIDA porque o LLM (llm_normalizer.py) já
converte qualquer expressão coloquial para o formato dd/mm/yyyy antes
de salvar. Não faz sentido validar o que o próprio LLM já garantiu.

O que ficou são só as validações que o LLM não faz:
- CPF: precisa do algoritmo matemático da Receita Federal
- Telefone: precisa de formato técnico específico
- Nome e cidade: garante que não veio vazio
"""

import re
from utils.states import list_of_states


def is_valid_phone(phone):
    """
    Verifica se o número de telefone está em um formato válido.
    Aceita: (81) 99999-9999 ou 81999999999
    """
    pattern1 = r"^\(\d{2}\)\s*\d{5}-?\d{4}$"
    pattern2 = r"^\d{7}-?\d{4}$"
    return re.fullmatch(pattern1, phone) or re.fullmatch(pattern2, phone)


def is_valid_name(name, allow_numbers=False):
    """
    Verifica se o nome não está vazio e tem só letras e espaços.

    allow_numbers=True é usado para campos de quantidade como '3 sacos'
    ou '180.0 kg', que o LLM pode entregar com números e ponto.
    """
    if not name or not name.strip():
        return False
    if allow_numbers:
        pattern = r"^[0-9a-zA-ZÁ-ÿ .,@]+$"
    else:
        pattern = r"^[a-zA-ZÁ-ÿ ]+$"
    return bool(re.fullmatch(pattern, name.strip()))


def is_valid_cpf(cpf):
    """
    Valida o CPF usando o algoritmo real da Receita Federal.

    Mantido na VA3 mesmo com entrada por voz, porque o CPF precisa ser
    matematicamente correto — não basta o LLM transcrever os números.
    O agricultor pode falar um dígito errado sem perceber.
    """
    cpf = re.sub(r"\D", "", cpf)  # remove pontos e traços se tiver
    if len(cpf) != 11:
        return False

    # Calcula o primeiro dígito verificador
    soma = 0
    for i, peso in enumerate(range(10, 1, -1)):
        soma += int(cpf[i]) * peso
    resto = (soma * 10) % 11
    primeiro_digito = resto if resto < 10 else 0

    # Calcula o segundo dígito verificador
    soma = 0
    for i, peso in enumerate(range(11, 1, -1)):
        soma += int(cpf[i]) * peso
    resto = (soma * 10) % 11
    segundo_digito = resto if resto < 10 else 0

    return primeiro_digito == int(cpf[-2]) and segundo_digito == int(cpf[-1])


def is_valid_town(town):
    """Verifica se a cidade não está vazia e tem só letras e espaços."""
    if not town or not town.strip():
        return False
    return bool(re.fullmatch(r"^[a-zA-ZÁ-ÿ ]+$", town.strip()))


def is_valid_state(state):
    """Verifica se o estado está na lista oficial de estados brasileiros."""
    return state in list_of_states
