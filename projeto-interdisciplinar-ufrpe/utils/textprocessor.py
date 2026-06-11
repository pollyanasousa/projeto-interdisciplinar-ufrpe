"""
Este arquivo contém a função textcapitalize.
"""

import string

def textcapitalize(text):
    """
    Coloca a primeira letra de cada palavra em maiúscula, exceto as preposições.
    """

    text = string.capwords(text)
    word_list = text.split()

    prepositions = ("da", "das", "de", "do", "dos", "a", "à", "ao", "ante", "após", "até", "com", "contra", "desde", "em", "entre", "para", "perante", "por", "sem", "sob", "sobre", "trás")

    for index, word in enumerate(word_list):
        if word.lower() in prepositions:
            word_list[index] = word.lower()

    return " ".join(word_list)