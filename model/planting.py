import json

from utils.validators import *
from utils.textprocessor import *
from utils.menu import *
from utils.io import *

class Planting:
    def __init__(self, plantingfile, area):
        """
        This class represents the planting. It starts with empty fields and a path to a file that stores the fields corresponding to the planting, besides an object of area.

        If you desire to copy the fields present on the file to the objects of this class, use self.read() method. However, if you desire to bring the current data on the objects of this class to that same file, use self.save() method.
        """

        self.plantingfile = plantingfile
        self.area = area

        self.list_of_planting = []


    def capture_culture(self, write_new=False):
        """
        It asks the user for the planting's culture. When the user prompts a valid one, this function returns the input. However, if the prompt was not valid, the function keeps asking for the planting's culture. The argument write_new makes the input message display it is a new culture when True.
        """

        invalid = True

        while invalid:
            culture = ""

            if write_new:
                culture = input("Informe o novo nome da cultura (exemplo: milho, feijão, mandioca): ")
            else:
                culture = input("Informe o nome da cultura (exemplo: milho, feijão, mandioca): ")

            culture = culture.capitalize()

            invalid = not is_valid_name(culture)

            if invalid:
                print("Nome de cultura inválido!")

            else:
                return culture

    def capture_area(self, write_new=False):
        """
        It asks the user for the planting's area. When the user prompts a valid one, this function returns the input. However, if the prompt was not valid, the function keeps asking for the planting's area. The argument write_new makes the input message display it is a new area when True.
        """

        print("Áreas disponíveis para o plantio:")

        for area in self.area.list_of_area:
            print(f"| {area['name']} |", end=" ")
        print("")

        invalid = True

        while invalid:
            area = ""

            if write_new:
                area = input("Informe a nova área da cultura: ")
            else:
                area = input("Informe a área da cultura: ")

            invalid = not is_valid_name(area, True)

            if invalid:
                print("Área inválida!")

            elif not area in [i["name"] for i in self.area.list_of_area]:
                print("Área não existente! Por gentileza, informe uma das áreas disponíveis para plantio.")
                invalid = True

            else:
                return area

    def capture_amount(self, write_new=False):
        """
        It asks the user for the planting's amount. When the user prompts a valid one, this function returns the input. However, if the prompt was not valid, the function keeps asking for the planting's amount. The argument write_new makes the input message display it is a new amount when True.
        """

        invalid = True

        while invalid:
            amount = ""

            if write_new:
                amount = input("Informe a nova quantidade da cultura (exemplo: 3 sacos, 2 caixas): ")
            else:
                amount = input("Informe a quantidade da cultura (exemplo: 3 sacos, 2 caixas): ")

            amount = amount.capitalize()

            invalid = not is_valid_name(amount, True)

            if invalid:
                print("Quantidade inválida!")

            else:
                return amount

    def capture_date(self, write_new=False):
        """
        It asks the user for the planting's date. When the user prompts a valid one, this function returns the input. However, if the prompt was not valid, the function keeps asking for the planting's date. The argument write_new makes the input message display it is a new date when True.
        """

        invalid = True

        while invalid:
            date = ""

            if write_new:
                date = input("Informe a nova data do plantio: ")
            else:
                date = input("Informe a data do plantio: ")

            invalid = not is_valid_date(date)

            if invalid:
                print("Data inválida!")

            else:
                return date

    def show_planting(self):
        if len(self.list_of_planting) == 0:
            print("Não há plantios cadastrados.")

            print("Deseja realizar o cadastro de um plantio?")
            option = show_menu(["Sim", "Não"])

            if option == 0:
                self.new_planting()

        else:
            print("Lista de plantio:\n")

            for _id, planting in enumerate(self.list_of_planting):
                print("Número de identificação:", _id+1)
                print("Cultura:", planting["culture"])
                print("Área:", planting["area"])
                print("Quantidade:", planting["amount"])
                print("Data do plantio:", planting["date"])

                print("")

            print("Deseja realizar alguma alteração na lista de plantio?")
            option = show_menu(["Sim", "Não"])

            if option == 0:
                print("Qual alteração desejada?")
                option = show_menu(["Adicionar novo plantio", "Alterar plantio existente", "Remover plantio existente", "Cancelar"])

                if option == 0:
                    self.new_planting()
                elif option == 1:
                    _id = inputint("Digite o número de identificação do plantio: ")
                    self.update_planting(_id-1) # The internal counting starts from id 0
                elif option == 2:
                    _id = inputint("Digite o número de identificação do plantio: ")
                    self.delete_planting(_id-1) # The internal counting starts from 0
                else:
                    pass

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
                json.dump({"list_of_planting": self.list_of_planting}, pf, indent=4)

            return 0

        except Exception as e:
            print("Um erro inesperado aconteceu! Não foi possível salvar os dados de plantio...")
            print(e)

            return 1

    def new_planting(self):
        """
        It adds a new planting.
        """

        print("Adicionando plantio...")

        culture = self.capture_culture()
        area = self.capture_area()
        amount = self.capture_amount()
        date = self.capture_date()

        self.list_of_planting.append({"culture": culture, "area": area, "amount": amount, "date": date})

        # And now the planting's data will be on the JSON file:
        if self.save() == 0:
            print("Plantio registrado com sucesso!")

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
