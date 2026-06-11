"""
RF009 - Cadastro de multiproprietários e herdeiros.
"""

import json


class CoOwners:
    ROLES = ["Proprietário principal", "Coproprietário", "Herdeiro", "Meeiro", "Arrendatário"]

    def __init__(self, coownersfile):
        self.coownersfile = coownersfile
        self.list_of_coowners = []

    def read(self, mute=False):
        try:
            with open(self.coownersfile, "r", encoding="utf-8-sig", errors="replace") as f:
                data = json.load(f)
            self.list_of_coowners = data.get("list_of_coowners", [])
            return 0
        except Exception as e:
            if not mute:
                print("Falha ao ler arquivo de multiproprietários:", e)
            return 1

    def save(self, mute=False):
        try:
            with open(self.coownersfile, "w", encoding="utf-8") as f:
                json.dump({"list_of_coowners": self.list_of_coowners}, f, indent=4, ensure_ascii=False)
            return 0
        except Exception as e:
            if not mute:
                print("Falha ao salvar multiproprietários:", e)
            return 1

    def new_coowner(self, name, cpf, role, share_pct=""):
        """share_pct: percentual de participação (opcional, para relatório bancário)."""
        self.list_of_coowners.append({
            "name": name,
            "cpf": cpf,
            "role": role,
            "share_pct": share_pct,
        })
        self.save()

    def update_coowner(self, _id, name, cpf, role, share_pct=""):
        if _id < 0 or _id >= len(self.list_of_coowners):
            print("ID inválido!")
            return
        self.list_of_coowners[_id] = {"name": name, "cpf": cpf, "role": role, "share_pct": share_pct}
        self.save()

    def delete_coowner(self, _id):
        if _id < 0 or _id >= len(self.list_of_coowners):
            print("ID inválido!")
            return
        self.list_of_coowners.pop(_id)
        self.save()
