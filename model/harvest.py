import json

from utils.validators import *
from utils.textprocessor import *
from utils.menu import *
from utils.io import *

class Harvest:
    def __init__(self, harvestfile):
        """
        This class represents the harvest. It starts with an empty list of harvests and a path to a file that stores the fields corresponding to the harvest.

        If you desire to copy the fields present on the file to the objects of this class, use self.read() method. However, if you desire to bring the current data on the objects of this class to that same file, use self.save() method.
        """

        self.harvestfile = harvestfile

        self.list_of_harvest = []


    def capture_culture(self, write_new=False):
        """
        It asks the user for the harvest's culture. When the user prompts a valid one, this function returns the input. However, if the prompt was not valid, the function keeps asking for the harvest's culture. The argument write_new makes the input message display it is a new culture when True.
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

    def capture_amount(self, write_new=False):
        """
        It asks the user for the harvest's amount. When the user prompts a valid one, this function returns the input. However, if the prompt was not valid, the function keeps asking for the harvest's amount. The argument write_new makes the input message display it is a new amount when True.
        """

        invalid = True

        while invalid:
            amount = ""

            if write_new:
                amount = input("Informe a nova quantidade da colheita (exemplo: 10 sacos, 5 caixas): ")
            else:
                amount = input("Informe a quantidade da colheita (exemplo: 10 sacos, 5 caixas): ")

            amount = amount.capitalize()

            invalid = not is_valid_name(amount, True)

            if invalid:
                print("Quantidade inválida!")

            else:
                return amount

    def capture_date(self, write_new=False):
        """
        It asks the user for the harvest's date. When the user prompts a valid one, this function returns the input. However, if the prompt was not valid, the function keeps asking for the harvest's date. The argument write_new makes the input message display it is a new date when True.
        """

        invalid = True

        while invalid:
            date = ""

            if write_new:
                date = input("Informe a nova data da colheita: ")
            else:
                date = input("Informe a data da colheita: ")

            invalid = not is_valid_date(date)

            if invalid:
                print("Data inválida!")

            else:
                return date

    def show_harvest(self):
        if len(self.list_of_harvest) == 0:
            print("Não há colheitas cadastradas.")

        else:
            print("Lista de colheita:\n")

            for _id, harvest in enumerate(self.list_of_harvest):
                print("Número de identificação:", _id+1)
                print("Cultura:", harvest["culture"])
                print("Quantidade:", harvest["amount"])
                print("Data da colheita:", harvest["date"])

                print("")

    def manage_harvest(self):
        """
        It manages the harvest.
        """

        self.show_harvest()

        if len(self.list_of_harvest) == 0:
            print("Deseja realizar o cadastro de uma colheita?")
            option = show_menu(["Sim", "Não"])

            if option == 0:
                self.new_harvest()
        else:
            print("Deseja realizar alguma alteração na lista de colheita?")
            option = show_menu(["Sim", "Não"])

            if option == 0:
                print("Qual alteração desejada?")
                option = show_menu(["Adicionar nova colheita", "Alterar colheita existente", "Remover colheita existente", "Cancelar"])

                if option == 0:
                    self.new_harvest()
                elif option == 1:
                    _id = inputint("Digite o número de identificação da colheita: ")
                    self.update_harvest(_id-1) # The internal counting starts from id 0
                elif option == 2:
                    _id = inputint("Digite o número de identificação da colheita: ")
                    self.delete_harvest(_id-1) # The internal counting starts from 0
                else:
                    pass

    def read(self, mute=False):
        """
        It reads the harvest's data on the harvestfile, copying the data to the self variables.

        If mute is True, then the possible error messages won't appear on the screen. If False, they will appear.

        It returns 0 in case of success and 1 in case of failure.
        """

        try:
            data = ""
            with open(self.harvestfile, "r", encoding='utf-8') as pf:
                data = json.load(pf)

            for harvest in data["list_of_harvest"]:
                self.list_of_harvest.append({"culture": harvest["culture"], "amount": harvest["amount"], "date": harvest["date"]})

            return 0

        except Exception as e:
            if not mute:
                print("Houve uma falha ao ler o arquivo de colheita!")
                print(e)

            return 1


    def save(self, mute=False):
        """
        It saves the harvest's data, present on self variables, on the harvestfile.

        If mute is True, then the possible error messages won't appear on the screen. If False, they will appear.

        It returns 0 in case of success and 1 in case of failure.
        """

        try:
            with open(self.harvestfile, "w") as pf:
                json.dump({"list_of_harvest": self.list_of_harvest}, pf, indent=4)

            return 0

        except Exception as e:
            print("Um erro inesperado aconteceu! Não foi possível salvar os dados de colheita...")
            print(e)

            return 1

    def new_harvest(self):
        """
        It adds a new harvest.
        """

        print("Adicionando colheita...")

        culture = self.capture_culture()
        amount = self.capture_amount()
        date = self.capture_date()

        self.list_of_harvest.append({"culture": culture, "amount": amount, "date": date})

        # And now the harvest's data will be on the JSON file:
        if self.save() == 0:
            print("Colheita registrada com sucesso!")

    def update_harvest(self, _id):
        """
        It updates an existing harvest whose id is given as argument.
        """

        if _id < 0 or _id >= len(self.list_of_harvest):
            print("Número de identificação inválido!")
            return

        print("Qual atributo você deseja alterar?")
        option = show_menu(["Cultura", "Quantidade", "Data da colheita"])

        if option == 0:
            culture = self.capture_culture(True)
            self.list_of_harvest[_id]["culture"] = culture
        elif option == 1:
            amount = self.capture_amount(True)
            self.list_of_harvest[_id]["amount"] = amount
        elif option == 2:
            date = self.capture_date(True)
            self.list_of_harvest[_id]["date"] = date

        # And now the harvest's data will be on the JSON file:
        if self.save() == 0:
            print("Colheita editada com sucesso!")

    def delete_harvest(self, _id):
        """
        It deletes an existing harvest whose id is given as argument.
        """

        if _id < 0 or _id >= len(self.list_of_harvest):
            print("Número de identificação inválido!")
            return

        self.list_of_harvest.pop(_id)

        # And now the harvest's data will be on the JSON file:
        if self.save() == 0:
            print("Colheita removida com sucesso!")
