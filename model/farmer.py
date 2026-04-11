import json

from utils.validators import *
from utils.textprocessor import *

class Farmer:
    def __init__(self):
        self.phone_number = "" # [PORTUGUESE] phone_number: numero_do_celular
        self.name = "" # [PORTUGUESE] name: nome
        self.town = "" # [PORTUGUESE] town: cidade
        self.state = "" # [PORTUGUESE] state: estado

    def get_phone(self): # [PORTUGUESE] get_phone: obter_celular
        """
        It asks the user for the farmer's cell phone. When the user prompts a valid one, this function saves the input into the self phone_number variable. However, if the prompt was not valid, the function keeps asking for the farmer's cell phone.
        """

        invalid = True # [PORTUGUESE] invalid: inválido

        while invalid:
            phone_number = input("Informe o número de celular: ")

            invalid = not is_valid_phone(phone_number)

            if invalid:
                print("Número de celular inválido!")

            else:
                self.phone_number = phone_number

    def get_name(self): # [PORTUGUESE] get_name: obter_nome
        """
        It asks the user for the farmer's name. When the user prompts a valid one, this function saves the input into the self name variable. However, if the prompt was not valid, the function keeps asking for the farmer's name.
        """

        invalid = True # [PORTUGUESE] invalid: inválido

        while invalid:
            name = input("Informe seu nome: ")

            name = textcapitalize(name)

            invalid = not is_valid_name(name)

            if invalid:
                print("Nome inválido!")

            else:
                self.name = name

    def get_town(self): # [PORTUGUESE] get_town: obter_cidade
        """
        It asks the user for the farmer's town. When the user prompts a valid one, this function saves the input into the self town variable. However, if the prompt was not valid, the function keeps asking for the farmer's town.
        """

        invalid = True # [PORTUGUESE] invalid: inválido

        while invalid:
            town = input("Informe sua cidade: ")

            town = textcapitalize(town)

            invalid = not is_valid_town(town)

            if invalid:
                print("Cidade inválida!")

            else:
                self.town = town

    def get_state(self): # [PORTUGUESE] get_state: obter_estado
        """
        It asks the user for the farmer's state. When the user prompts a valid one, this function saves the input into the self state variable. However, if the prompt was not valid, the function keeps asking for the farmer's state.
        """

        invalid = True # [PORTUGUESE] invalid: inválido

        while invalid:
            state = input("Informe seu estado: ")

            state = textcapitalize(state)

            invalid = not is_valid_state(state)

            if invalid:
                print("Estado inválido!")

            else:
                self.state = state

    def save(self): # [PORTUGUESE] save: salvar
        """
        It saves the farmer's data on the data/farmer.json file.

        It returns 0 in case of success and 1 in case of failure.
        """

        try:
            data = ""
            with open("data/farmer.json", "r") as farmer_file:
                data = json.load(farmer_file)

            data["accounts"].append({"phone_number": self.phone_number, "name": self.name, "town": self.town, "state": self.state})

            with open("data/farmer.json", "w") as farmer_file:
                json.dump(data, farmer_file, indent=4)

            return 0

        except:
            print("Um erro inesperado aconteceu! Não foi possível salvar os dados do agricultor...")

            return 1

    def read(self, phone_number): # [PORTUGUESE] read: ler
        """
        It reads the farmer's data on the data/farmer.json file, using the given phone number as login.

        It returns 0 in case of success, 1 in case of user not found and 2 in case of failure of reading.
        """

        try:
            data = ""
            with open("data/farmer.json", "r", encoding='utf-8') as farmer_file:
                data = json.load(farmer_file)

            for users in data["accounts"]:
                if users["phone_number"] == phone_number:
                    self.phone_number = users["phone_number"]
                    self.name = users["name"]
                    self.town = users["town"]
                    self.state = users["state"]

                    return 0

            return 1


        except Exception as e:
            print("Um erro inesperado aconteceu! Não foi possível ler os dados do agricultor...")

            print(repr(e))
            return 2
