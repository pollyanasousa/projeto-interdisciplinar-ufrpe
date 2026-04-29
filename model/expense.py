import json

from utils.validators import *
from utils.textprocessor import *
from utils.menu import *
from utils.io import *

class Expense:
    def __init__(self, expensefile):
        """
        This class represents the expenses. It starts with an empty list of expenses and a path to a file that stores the fields corresponding to the expenses.

        If you desire to copy the fields present on the file to the objects of this class, use self.read() method. However, if you desire to bring the current data on the objects of this class to that same file, use self.save() method.
        """

        self.expensefile = expensefile

        self.list_of_expenses = []


    def capture_type(self, write_new=False):
        """
        It asks the user for the expenses's type. When the user prompts a valid one, this function returns the input. However, if the prompt was not valid, the function keeps asking for the expenses's type. The argument write_new makes the input message display it is a new type when True.
        """

        invalid = True

        while invalid:
            _type = ""

            if write_new:
                _type = input("Informe o novo tipo de gasto (exemplo: adubo, transporte, mão de obra): ")
            else:
                _type = input("Informe o tipo de gasto (exemplo: adubo, transporte, mão de obra): ")

            _type = _type.capitalize()

            invalid = not is_valid_name(_type)

            if invalid:
                print("Tipo de gasto inválido!")

            else:
                return _type

    def capture_value(self, write_new=False):
        """
        It asks the user for the expenses's value. When the user prompts a valid one, this function returns the input. However, if the prompt was not valid, the function keeps asking for the expenses's value. The argument write_new makes the input message display it is a new value when True.
        """

        invalid = True

        while invalid:
            value = ""

            if write_new:
                value = input("Informe o novo valor do gasto (exemplo: 100 reais): ")
            else:
                value = input("Informe o valor do gasto (exemplo: 100 reais): ")

            value = value.capitalize()

            invalid = not is_valid_name(value, True)

            if invalid:
                print("Valor inválido!")

            else:
                return value

    def capture_date(self, write_new=False):
        """
        It asks the user for the expenses's date. When the user prompts a valid one, this function returns the input. However, if the prompt was not valid, the function keeps asking for the expenses's date. The argument write_new makes the input message display it is a new area when True.
        """

        invalid = True

        while invalid:
            date = ""

            if write_new:
                date = input("Informe a nova data do gasto: ")
            else:
                date = input("Informe a data do gasto: ")

            invalid = not is_valid_date(date)

            if invalid:
                print("Data inválida!")

            else:
                return date

    def show_expenses(self):
        if len(self.list_of_expenses) == 0:
            print("Não há gastos cadastrados.")

        else:
            print("Lista de gastos:\n")

            for _id, expense in enumerate(self.list_of_expenses):
                print("Número de identificação:", _id+1)
                print("Tipo de gasto:", expense["type"])
                print("Valor:", expense["value"])
                print("Data:", expense["date"])

                print("")

    def manage_expenses(self):
        """
        It manages the expenses.
        """

        self.show_expenses()

        if len(self.list_of_expenses) == 0:
            print("Deseja realizar o cadastro de um gasto?")
            option = show_menu(["Sim", "Não"])

            if option == 0:
                self.new_expense()

        else:
            print("Deseja realizar alguma alteração na lista de gastos?")
            option = show_menu(["Sim", "Não"])

            if option == 0:
                print("Qual alteração desejada?")
                option = show_menu(["Adicionar novo gasto", "Alterar gasto existente", "Remover gasto existente", "Cancelar"])

                if option == 0:
                    self.new_expenses()
                elif option == 1:
                    _id = inputint("Digite o número de identificação do gasto: ")
                    self.update_expenses(_id-1) # The internal counting starts from id 0
                elif option == 2:
                    _id = inputint("Digite o número de identificação do gasto: ")
                    self.delete_expenses(_id-1) # The internal counting starts from 0
                else:
                    pass

    def read(self, mute=False):
        """
        It reads the expenses's data on the expensefile, copying the data to the self variables.

        If mute is True, then the possible error messages won't appear on the screen. If False, they will appear.

        It returns 0 in case of success and 1 in case of failure.
        """

        try:
            data = ""
            with open(self.expensefile, "r", encoding='utf-8') as pf:
                data = json.load(pf)

            for expenses in data["list_of_expenses"]:
                self.list_of_expenses.append({"type": expenses["type"], "value": expenses["value"], "date": expenses["date"]})

            return 0

        except Exception as e:
            if not mute:
                print("Houve uma falha ao ler o arquivo de gastos!")
                print(e)

            return 1


    def save(self, mute=False):
        """
        It saves the expenses's data, present on self variables, on the expensefile.

        If mute is True, then the possible error messages won't appear on the screen. If False, they will appear.

        It returns 0 in case of success and 1 in case of failure.
        """

        try:
            with open(self.expensefile, "w") as pf:
                json.dump({"list_of_expenses": self.list_of_expenses}, pf, indent=4)

            return 0

        except Exception as e:
            print("Um erro inesperado aconteceu! Não foi possível salvar os dados de gastos...")
            print(e)

            return 1

    def new_expense(self):
        """
        It adds a new expense.
        """

        print("Adicionando gasto...")

        _type = self.capture_type()
        value = self.capture_value()
        date = self.capture_date()

        self.list_of_expenses.append({"type": _type, "value": value, "date": date})

        # And now the expenses's data will be on the JSON file:
        if self.save() == 0:
            print("Gasto registrado com sucesso!")

    def update_expense(self, _id):
        """
        It updates an existing expense whose id is given as argument.
        """

        if _id < 0 or _id >= len(self.list_of_expenses):
            print("Número de identificação inválido!")
            return

        print("Qual atributo você deseja alterar?")
        option = show_menu(["Tipo de gasto", "Valor", "Data"])

        if option == 0:
            _type = self.capture_type(True)
            self.list_of_expenses[_id]["type"] = _type
        elif option == 1:
            value = self.capture_value(True)
            self.list_of_expenses[_id]["value"] = value
        elif option == 2:
            amount = self.capture_amount(True)
            self.list_of_expenses[_id]["amount"] = amount
        elif option == 3:
            date = self.capture_date(True)
            self.list_of_expenses[_id]["date"] = date

        # And now the expenses's data will be on the JSON file:
        if self.save() == 0:
            print("Gasto editado com sucesso!")

    def delete_expense(self, _id):
        """
        It deletes an existing expense whose id is given as argument.
        """

        if _id < 0 or _id >= len(self.list_of_expenses):
            print("Número de identificação inválido!")
            return

        self.list_of_expenses.pop(_id)

        # And now the expenses's data will be on the JSON file:
        if self.save() == 0:
            print("Gasto removido com sucesso!")