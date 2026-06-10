import json

from utils.validators import *
from utils.textprocessor import *

class Planting:
    def __init__(self, plantingfile, area):
        """
        This class represents the planting. It starts with empty fields and a path to a file that stores the fields corresponding to the planting, besides an object of area.

        If you desire to copy the fields present on the file to the objects of this class, use self.read() method. However, if you desire to bring the current data on the objects of this class to that same file, use self.save() method.
        """

        self.plantingfile = plantingfile
        self.area = area

        self.list_of_planting = []

    def read(self, mute=False):
        """
        It reads the planting's data on the plantingfile, copying the data to the self variables.

        If mute is True, then the possible error messages won't appear on the screen. If False, they will appear.

        It returns 0 in case of success and 1 in case of failure.
        """

        try:
            data = ""
            with open(self.plantingfile, "r", encoding='utf-8') as pf:
                data = json.load(pf)

            for planting in data["list_of_planting"]:
                self.list_of_planting.append({"culture": planting["culture"], "area": planting["area"], "amount": planting["amount"], "date": planting["date"]})

            return 0

        except Exception as e:
            if not mute:
                print("Houve uma falha ao ler o arquivo de plantios!")
                print(e)

            return 1


    def save(self, mute=False):
        """
        It saves the planting's data, present on self variables, on the plantingfile.

        If mute is True, then the possible error messages won't appear on the screen. If False, they will appear.

        It returns 0 in case of success and 1 in case of failure.
        """

        try:
            with open(self.plantingfile, "w") as pf:
                json.dump({"list_of_planting": self.list_of_planting}, pf, indent=4, ensure_ascii=False)

            return 0

        except Exception as e:
            print("Um erro inesperado aconteceu! Não foi possível salvar os dados de plantio...")
            print(e)

            return 1

    def new_planting(self, culture, area, amount, date):
        """
        It adds a new planting.
        """

        self.list_of_planting.append({"culture": culture, "area": area, "amount": amount, "date": date})

        # And now the planting's data will be on the JSON file:
        self.save()

    def update_planting(self, _id):
        """
        It updates an existing planting whose id is given as argument.
        """

        if _id < 0 or _id >= len(self.list_of_planting):
            print("Número de identificação inválido!")
            return

        print("Qual atributo você deseja alterar?")
        option = show_menu(["Cultura", "Área", "Quantidade", "Data do plantio"])

        if option == 0:
            culture = self.capture_culture(True)
            self.list_of_planting[_id]["culture"] = culture
        elif option == 1:
            area = self.capture_area(True)
            self.list_of_planting[_id]["area"] = area
        elif option == 2:
            amount = self.capture_amount(True)
            self.list_of_planting[_id]["amount"] = amount
        elif option == 3:
            date = self.capture_date(True)
            self.list_of_planting[_id]["date"] = date

        # And now the planting's data will be on the JSON file:
        if self.save() == 0:
            print("Plantio editado com sucesso!")

    def delete_planting(self, _id):
        """
        It deletes an existing planting whose id is given as argument.
        """

        if _id < 0 or _id >= len(self.list_of_planting):
            print("Número de identificação inválido!")
            return

        self.list_of_planting.pop(_id)

        # And now the planting's data will be on the JSON file:
        if self.save() == 0:
            print("Plantio removido com sucesso!")