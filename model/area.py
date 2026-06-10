import json

from utils.validators import *
from utils.textprocessor import *

class Area:
    def __init__(self, areafile):
        """
        This class represents the area. It starts with an empty list of areas and a path to a file that stores the fields corresponding to the area. Also, with the self planting, it's possible to recognize the areas used by the plantings.

        If you desire to copy the fields present on the file to the objects of this class, use self.read() method. However, if you desire to bring the current data on the objects of this class to that same file, use self.save() method.
        """

        self.areafile = areafile
        self.planting = None

        self.list_of_area = []

    def link_to_planting(self, planting):
        """
        It makes the area class, linked to a planting object, recognize the areas being used by the plantings.
        """

        self.planting = planting

    def read(self, mute=False):
        """
        It reads the area's data on the areafile, copying the data to the self variables.

        If mute is True, then the possible error messages won't appear on the screen. If False, they will appear.

        It returns 0 in case of success and 1 in case of failure.
        """

        try:
            data = ""
            with open(self.areafile, "r", encoding='utf-8') as pf:
                data = json.load(pf)

            for area in data["list_of_area"]:
                self.list_of_area.append({"name": area["name"]})

            return 0

        except Exception as e:
            if not mute:
                print("Houve uma falha ao ler o arquivo de áreas!")
                print(e)

            return 1


    def save(self, mute=False):
        """
        It saves the area's data, present on self variables, on the areafile.

        If mute is True, then the possible error messages won't appear on the screen. If False, they will appear.

        It returns 0 in case of success and 1 in case of failure.
        """

        try:
            with open(self.areafile, "w") as pf:
                json.dump({"list_of_area": self.list_of_area}, pf, indent=4, ensure_ascii=False)

            return 0

        except Exception as e:
            print("Um erro inesperado aconteceu! Não foi possível salvar os dados de área...")
            print(e)

            return 1

    def new_area(self, name):
        """
        It adds a new area. Name argument is its name.
        """

        self.list_of_area.append({"name": name})

        # And now the area's data will be on the JSON file:
        self.save()

    def update_area(self, _id, name):
        """
        It updates an existing area whose id is given as argument. Besides, through the given list_of_planting, this function returns the ids of list_of_planting that need to be updated to receive the new area modification.
        
        Argument name is the new desired name.
        """

        if _id < 0 or _id >= len(self.list_of_area):
            print("Número de identificação inválido!")
            return

        old_name = self.list_of_area[_id]["name"]

        new_name = name
        self.list_of_area[_id]["name"] = new_name

        for planting in self.planting.list_of_planting:
            if planting["area"] == old_name:
                planting["area"] = new_name

        # And now the area's data will be on the JSON file:
        self.save()

    def delete_area(self, _id):
        """
        It deletes an existing area whose id is given as argument. Besides, through the given list_of_planting, this function does not delete an area that is already being used by at least one planting.
        """

        if _id < 0 or _id >= len(self.list_of_area):
            print("Número de identificação inválido!")
            return

        elif len(self.list_of_area) == 1:
            print("Não é possível remover a área: deve haver pelo menos uma na propriedade.")
            return

        else:
            for planting in self.planting.list_of_planting:
                if planting["area"] == self.list_of_area[_id]["name"]:
                    print("Não é possível remover a área: ela já está em uso por um plantio. Edite ou remova o plantio primeiro.")
                    return

        self.list_of_area.pop(_id)

        # And now the area's data will be on the JSON file:
        if self.save() == 0:
            print("Área removida com sucesso!")