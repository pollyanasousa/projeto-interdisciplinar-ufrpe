from utils.validators import *

class Farmer:
    def __init__(self):
        self.phone_number = "" # [Portuguese] phone_number: numero_do_celular
        self.name = "" # [Portuguese] name: nome
        self.town = "" # [Portuguese] town: cidade
        self.state = "" # [Portuguese] state: estado

    def get_phone(self): # [Portuguese] get_phone: obter_celular
        """
        It asks the user for the farmer's cell phone. When the user prompts a valid one, this function saves the input into the self phone_number variable. However, if the prompt was not valid, the function keeps asking for the farmer's cell phone.
        """

        invalid = True # [Portuguese] invalid: inválido

        while invalid:
            phone_number = input("Informe o número de celular: ")

            invalid = not is_valid_phone(phone_number)

            if invalid:
                print("Número de celular inválido!")

            else:
                self.phone_number = phone_number

    def get_name(self): # [Portuguese] get_name: obter_nome
        """
        It asks the user for the farmer's name. When the user prompts a valid one, this function saves the input into the self name variable. However, if the prompt was not valid, the function keeps asking for the farmer's name.
        """

        invalid = True # [Portuguese] invalid: inválido

        while invalid:
            name = input("Informe seu nome: ")

            invalid = (name == "")

            if invalid:
                print("Nome inválido!")

            else:
                self.name = name

    def get_town(self): # [Portuguese] get_town: obter_cidade
        """
        It asks the user for the farmer's town. When the user prompts a valid one, this function saves the input into the self town variable. However, if the prompt was not valid, the function keeps asking for the farmer's town.
        """

        invalid = True # [Portuguese] invalid: inválido

        while invalid:
            town = input("Informe sua cidade: ")

            invalid = (town == "")

            if invalid:
                print("Cidade inválida!")

            else:
                self.town = town

    def get_state(self): # [Portuguese] get_state: obter_estado
        """
        It asks the user for the farmer's state. When the user prompts a valid one, this function saves the input into the self state variable. However, if the prompt was not valid, the function keeps asking for the farmer's state.
        """

        invalid = True # [Portuguese] invalid: inválido

        while invalid:
            state = input("Informe seu estado: ")

            invalid = (state == "")

            if invalid:
                print("Estado inválido!")

            else:
                self.state = state

    def save(self): # [Portuguese] save: salvar
        """
        It saves the farmer's data on the data/farmer.json file.
        """

        try:
            farmer_file = open("data/farmer.json", "w")

            farmer_file.write("{" + f"\"phone_number\": {self.phone_number}, \"name\": {self.name}, \"town\": {self.town}, \"state\": {self.state}" + "}")

            farmer_file.close()

        except:
            print("Um erro inesperado aconteceu! Não foi possível salvar os dados do agricultor...")
