"""
Este arquivo contém as funções para lidar com E/S (entrada/saída).
"""

import re

def inputint(msg):
    """
    Solicita um número inteiro e retorna o valor digitado pelo usuário. A variável msg é a mensagem exibida na tela. Enquanto o usuário não digitar um inteiro válido, a função continua pedindo.
    """

    ret = ""
    while not bool(re.match(r"^[-+]?\d+$", ret)):
        ret = input(msg)

    return int(ret)