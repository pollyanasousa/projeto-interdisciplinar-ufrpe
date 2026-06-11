import json

from utils.validators import *
from utils.textprocessor import *
from utils.language_parser import parse_date, normalize_amount

class Harvest:
    def __init__(self, harvestfile):
        """
        This class represents the harvest. It starts with an empty list of harvests and a path to a file that stores the fields corresponding to the harvest.

        If you desire to copy the fields present on the file to the objects of this class, use self.read() method. However, if you desire to bring the current data on the objects of this class to that same file, use self.save() method.
        """

        self.harvestfile = harvestfile

        self.list_of_harvest = []

    def read(self, mute=False):
        """
        It reads the harvest's data on the harvestfile, copying the data to the self variables.

        If mute is True, then the possible error messages won't appear on the screen. If False, they will appear.

        It returns 0 in case of success and 1 in case of failure.
        """

        try:
            data = ""
            with open(self.harvestfile, "r", encoding="utf-8-sig", errors="replace") as pf:
                data = json.load(pf)

            for harvest in data["list_of_harvest"]:
                self.list_of_harvest.append({"culture": harvest.get("culture", ""), "amount": harvest.get("amount", ""), "amount_canonical": harvest.get("amount_canonical", harvest.get("amount", "")), "date": harvest.get("date", "")})

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
            with open(self.harvestfile, "w", encoding="utf-8") as pf:
                json.dump({"list_of_harvest": self.list_of_harvest}, pf, indent=4, ensure_ascii=False)

            return 0

        except Exception as e:
            print("Um erro inesperado aconteceu! Não foi possível salvar os dados de colheita...")
            print(e)

            return 1

    def new_harvest(self, culture, amount, date):
        """
        It adds a new harvest, and culture, amount and date are the arguments.
        Date and amount are auto-normalized from farmer natural language.
        """
        date_norm, date_ok = parse_date(date)
        if date_ok:
            date = date_norm
        original_amount, canonical_amount = normalize_amount(amount)
        # Store both so report can use canonical
        self.list_of_harvest.append({"culture": culture, "amount": original_amount, "amount_canonical": canonical_amount, "date": date})

        # And now the harvest's data will be on the JSON file:
        self.save()

    def update_harvest(self, _id, culture, amount, date):
        """
        It updates an existing harvest whose id is given as argument.
        culture, amount and date are the new data.
        """

        if _id < 0 or _id >= len(self.list_of_harvest):
            print("Número de identificação inválido!")
            return

        date_norm, date_ok = parse_date(date)
        if date_ok:
            date = date_norm
        original_amount, canonical_amount = normalize_amount(amount)
        self.list_of_harvest[_id]["culture"] = culture
        self.list_of_harvest[_id]["amount"] = original_amount
        self.list_of_harvest[_id]["amount_canonical"] = canonical_amount
        self.list_of_harvest[_id]["date"] = date

        # And now the harvest's data will be on the JSON file:
        self.save()

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