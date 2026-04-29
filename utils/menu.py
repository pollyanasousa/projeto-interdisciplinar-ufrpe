"""
Este arquivo contém a função de menu.
"""

def show_menu(options):
    """
    Exibe ao usuário um menu, usando os elementos da lista options como opções, e retorna o índice da opção escolhida (0 é o ponto de partida dos retornos, embora 1 seja o ponto de partida na tela do menu).
    """

    print("")
    for index, option in enumerate(options):
        print(f"({index+1}) {option}")
    print("")

    invalid = True

    while invalid:
        option = input("> ")

        if option.isdigit(): # We need this initial "if" because the next one treats option variable as a number.
            if int(option) <= len(options) and int(option) > 0:
                return int(option) - 1 # We use option - 1 because the user sees 1, 2, 3, 4..., and the options list sees 0, 1, 2, 3...

            else:
                print("Opção inválida!")

        else:
            print("Opção inválida!")