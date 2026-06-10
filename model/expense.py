import json

from utils.validators import *
from utils.textprocessor import *

class Expense:
    def __init__(self, expensefile):
        """
        This class represents the expenses. It starts with an empty list of expenses and a path to a file that stores the fields corresponding to the expenses.

        If you desire to copy the fields present on the file to the objects of this class, use self.read() method. However, if you desire to bring the current data on the objects of this class to that same file, use self.save() method.
        """

        self.expensefile = expensefile

        self.list_of_expenses = []

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
                json.dump({"list_of_expenses": self.list_of_expenses}, pf, indent=4, ensure_ascii=False)

            return 0

        except Exception as e:
            print("Um erro inesperado aconteceu! Não foi possível salvar os dados de gastos...")
            print(e)

            return 1

    def new_expense(self, _type, value, date):
        """
        It adds a new expense, receiving _type, value and date arguments.
        """

        self.list_of_expenses.append({"type": _type, "value": value, "date": date})

        self.save()

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