import json

from model.planting import *

from utils.validators import *
from utils.textprocessor import *

class Farmer:
    def __init__(self, farmerfile):
        """

        """

        self.farmerfile = farmerfile

        self.phone_number = ""
        self.name = ""
        self.town = ""
        self.state = ""

        self.planting = Planting(".../data/planting.json")

        # Reading the farmer's data on farmerfile:

        try:
            data = ""
            with open(farmerfile, "r", encoding='utf-8') as ff:
                data = json.load(ff)

            self.phone_number = data["phone_number"]
            self.name = data["name"]
            self.town = data["town"]
            self.state = data["state"]

        except Exception as e:
            self.create_account()


    def capture_phone(self):
        """
        It asks the user for the farmer's cell phone. When the user prompts a valid one, this function saves the input into the self phone_number variable. However, if the prompt was not valid, the function keeps asking for the farmer's cell phone.
        """

        invalid = True

        while invalid:
            phone_number = input("Informe o seu número de celular: ")

            invalid = not is_valid_phone(phone_number)

            if invalid:
                print("Número de celular inválido!")

            else:
                self.phone_number = phone_number

    def capture_name(self):
        """
        It asks the user for the farmer's name. When the user prompts a valid one, this function saves the input into the self name variable. However, if the prompt was not valid, the function keeps asking for the farmer's name.
        """

        invalid = True

        while invalid:
            name = input("Informe seu nome: ")

            name = textcapitalize(name)

            invalid = not is_valid_name(name)

            if invalid:
                print("Nome inválido!")

            else:
                self.name = name

    def capture_town(self):
        """
        It asks the user for the farmer's town. When the user prompts a valid one, this function saves the input into the self town variable. However, if the prompt was not valid, the function keeps asking for the farmer's town.
        """

        invalid = True

        while invalid:
            town = input("Informe sua cidade: ")

            town = textcapitalize(town)

            invalid = not is_valid_town(town)

            if invalid:
                print("Cidade inválida!")

            else:
                self.town = town

    def capture_state(self):
        """
        It asks the user for the farmer's state. When the user prompts a valid one, this function saves the input into the self state variable. However, if the prompt was not valid, the function keeps asking for the farmer's state.
        """

        invalid = True

        while invalid:
            state = input("Informe seu estado: ")

            state = textcapitalize(state)

            invalid = not is_valid_state(state)

            if invalid:
                print("Estado inválido!")

            else:
                self.state = state

    def save(self):
        """
        It saves the farmer's data on the farmerfile.

        It returns 0 in case of success and 1 in case of failure.
        """

        try:
            with open(self.farmerfile, "w") as ff:
                json.dump({"phone_number": self.phone_number, "name": self.name, "town": self.town, "state": self.state}, ff, indent=4)

            return 0

        except:
            print("Um erro inesperado aconteceu! Não foi possível salvar os dados do agricultor...")

            return 1

    def create_account(self):
        """
        It signs up the farmer.
        """

        print("Bem-vindo! É um prazer tê-lo conosco!")

        self.capture_phone()

        print("Como você se chama?")
        self.capture_name()

        self.capture_town()
        self.capture_state()

        self.planting.new_planting()

        # And now the farmer's data will be on the JSON file:
        if self.save() == 0:
            print("Conta criada com sucesso!")
