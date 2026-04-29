import json

from model.area import *
from model.planting import *
from model.harvest import *
from model.expense import *
from model.report import *

from utils.validators import *
from utils.textprocessor import *
from utils.menu import *

class Farmer:
    def __init__(self, farmerfile):
        """
        This class represents the farmer. It starts with empty fields and a path to a file that stores the fields corresponding to the farmer.

        If you desire to copy the fields present on the file to the objects of this class, use self.read() method. However, if you desire to bring the current data on the objects of this class to that same file, use self.save() method.
        """

        self.farmerfile = farmerfile

        self.phone_number = ""
        self.name = ""
        self.cpf = ""
        self.town = ""
        self.state = ""

        self.area = Area("data/area.json")
        self.planting = Planting("data/planting.json", self.area)
        self.area.link_to_planting(self.planting)
        self.harvest = Harvest("data/harvest.json")
        self.expense = Expense("data/expense.json")
        self.report = Report(self, self.area, self.planting, self.harvest, self.expense)


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

    def capture_cpf(self):
        """
        It asks the user for the farmer's CPF. When the user prompts a valid one, this function saves the input into the self cpf variable. However, if the prompt was not valid, the function keeps asking for the farmer's CPF.
        """

        invalid = True

        while invalid:
            cpf = input("Informe seu CPF: ")

            invalid = not is_valid_cpf(cpf)

            if invalid:
                print("CPF inválido!")

            else:
                self.cpf = cpf

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

            if len(state) == 2: # Perhaps user gave us the acronym of the state (example: PE)
                state = state.upper()
            else: # Perhaps the full name of the state (example: Pernambuco)
                state = textcapitalize(state)

            invalid = not is_valid_state(state)

            if invalid:
                print("Estado inválido!")

            else:
                self.state = state

    def who_am_i(self):
        """
        This function shows the farmer's data and asks if the user wants to change one of them.
        """

        print(f"Nome: {self.name}")
        print(f"CPF: {self.cpf}")
        print(f"Telefone: {self.phone_number}")
        print(f"Cidade: {self.town}")
        print(f"Estado: {self.state}")

        print("")
        print("Deseja alterar algum dado?")
        option = show_menu(["Sim", "Não"])

        if option == 0:
            print("Qual dado deseja alterar?")
            option = show_menu(["Nome", "Telefone", "Cidade", "Estado", "Cancelar"])

            if option == 0:
                self.capture_name()
            elif option == 1:
                self.capture_phone()
            elif option == 2:
                self.capture_town()
            elif option == 3:
                self.capture_state()
            else:
                return

            self.save()

    def read(self, mute=False):
        """
        It reads the farmer's data on the farmerfile, copying the data to the self variables, and commands the self planting, harvest and expenses variables to be read.

        If mute is True, then the possible error messages won't appear on the screen. If False, they will appear.

        It returns 0 in case of success and 1 in case of failure.
        """

        try:
            data = ""
            with open(self.farmerfile, "r", encoding='utf-8') as ff:
                data = json.load(ff)

            self.phone_number = data["phone_number"]
            self.name = data["name"]
            self.cpf = data["cpf"]
            self.town = data["town"]
            self.state = data["state"]

            self.area.read()
            self.planting.read()
            self.harvest.read()
            self.expense.read()

            return 0

        except Exception as e:
            if not mute:
                print("Houve uma falha ao ler o arquivo do agricultor!")
                print(e)

            return 1

    def save(self, mute=False):
        """
        It saves the farmer's data, present on self variables, on the farmerfile.

        If mute is True, then the possible error messages won't appear on the screen. If False, they will appear.

        It returns 0 in case of success and 1 in case of failure.
        """

        try:
            with open(self.farmerfile, "w") as ff:
                json.dump({"phone_number": self.phone_number, "name": self.name, "cpf": self.cpf, "town": self.town, "state": self.state}, ff, indent=4, ensure_ascii=False)

            return 0

        except Exception as e:
            if not mute:
                print("Um erro inesperado aconteceu! Não foi possível salvar os dados do agricultor...")
                print(e)

            return 1

    def create_account(self):
        """
        It signs up the farmer.
        """

        print("Bem-vindo! É um prazer tê-lo conosco!")
        print("")

        self.capture_phone()
        print("")

        print("Como você se chama?")
        self.capture_name()
        print("")

        self.capture_cpf()
        print("")

        self.capture_town()
        print("")

        self.capture_state()
        print("")

        print("Excelente! Agora, precisamos criar uma área, é nela onde são feitos os plantios.")
        print("")

        self.area.new_area()
        print("")

        # And now the farmer's data will be on the JSON file:
        if self.save() == 0:
            print("Conta criada com sucesso!")