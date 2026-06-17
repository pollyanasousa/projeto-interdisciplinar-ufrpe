import json

from model.area import *
from model.planting import *
from model.harvest import *
from model.expense import *
from model.report import *
from model.coowners import CoOwners

from utils.validators import *

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
        self.coowners = CoOwners("data/coowners.json")

    def read(self, mute=False):
        """
        It reads the farmer's data on the farmerfile, copying the data to the self variables, and commands the self planting, harvest and expenses variables to be read.

        If mute is True, then the possible error messages won't appear on the screen. If False, they will appear.

        It returns 0 in case of success and 1 in case of failure.
        """

        try:
            data = ""
            with open(self.farmerfile, "r", encoding="utf-8-sig", errors="replace") as ff:
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
            self.coowners.read(mute=True)

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
            with open(self.farmerfile, "w", encoding="utf-8") as ff:
                json.dump({"phone_number": self.phone_number, "name": self.name, "cpf": self.cpf, "town": self.town, "state": self.state}, ff, indent=4, ensure_ascii=False)

            return 0

        except Exception as e:
            if not mute:
                print("Um erro inesperado aconteceu! Não foi possível salvar os dados do agricultor...")
                print(e)

            return 1