"""
This file contains the menu function.
"""

def show_menu(options): # [PORTUGUESE] show_menu(options): mostrar_menu(opcoes)
    """
    It shows the user a menu, using the options list elements as options, and returns the index of the chosen option (0 is the start point of the returns, although 1 is the start point of the menu screen).
    """

    for index, option in enumerate(options):
        print(f"({index+1}) {option}")

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
