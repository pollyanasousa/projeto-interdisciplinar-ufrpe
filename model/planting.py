import json

from utils.validators import *
from utils.textprocessor import *

class Planting:
    def __init__(self, plantingfile):
        """

        """

        self.plantingfile = plantingfile

        self.list_of_planting = []

        # Reading the planting data on plantingfile:

        try:
            data = ""
            with open(plantingfile, "r", encoding='utf-8') as pf:
                data = json.load(pf)

            for planting in data["list_of_planting"]:
                self.list_of_planting.append({"culture": planting["culture"], "area": planting["area"], "amount": planting["amount"], "date": planting["date"]})

        except Exception as e:
            print("Houve uma falha ao ler o arquivo de plantios!")


    def capture_culture(self):
        """
        It asks the user for the planting's culture. When the user prompts a valid one, this function returns the input. However, if the prompt was not valid, the function keeps asking for the planting's culture.
        """

        invalid = True

        while invalid:
            culture = input("Informe o nome da cultura: ")

            invalid = not is_valid_name(culture)

            if invalid:
                print("Nome de cultura inválido!")

            else:
                return culture

    def capture_area(self):
        """
        It asks the user for the planting's area. When the user prompts a valid one, this function returns the input. However, if the prompt was not valid, the function keeps asking for the planting's area.
        """

        invalid = True

        while invalid:
            area = input("Informe a área da cultura: ")

            area = textcapitalize(area)

            invalid = not is_valid_name(area)

            if invalid:
                print("Área inválida!")

            else:
                return area

    def capture_amount(self):
        """
        It asks the user for the planting's amount. When the user prompts a valid one, this function returns the input. However, if the prompt was not valid, the function keeps asking for the planting's amount.
        """

        invalid = True

        while invalid:
            amount = input("Informe a quantidade da cultura: ")

            amount = textcapitalize(amount)

            invalid = not is_valid_name(amount)

            if invalid:
                print("Quantidade inválida!")

            else:
                return amount

    def capture_date(self):
        """
        It asks the user for the planting's date. When the user prompts a valid one, this function returns the input. However, if the prompt was not valid, the function keeps asking for the planting's date.
        """

        invalid = True

        while invalid:
            date = input("Informe a data do plantio: ")

            invalid = not is_valid_date(date)

            if invalid:
                print("Data inválida!")

            else:
                return date

    def save(self):
        """
        It saves the planting's data on the plantingfile.

        It returns 0 in case of success and 1 in case of failure.
        """

        try:
            with open(self.plantingfile, "w") as pf:
                json.dump({"list_of_planting": list_of_planting}, pf, indent=4)

            return 0

        except:
            print("Um erro inesperado aconteceu! Não foi possível salvar os dados de plantio...")

            return 1

    def new_planting(self):
        """
        It adds a new planting.
        """

        print("Adicionando área de plantio...")

        culture = self.capture_culture()
        area = self.capture_area()
        amount = self.capture_amount()
        date = self.capture_date()

        self.list_of_planting.append({"culture": culture, "area": area, "amount": amount, "date": date})

        # And now the planting's data will be on the JSON file:
        if self.save() == 0:
            print("Área de plantio criada com sucesso!")
