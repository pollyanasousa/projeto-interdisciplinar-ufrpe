"""
RF008 - Tratamento de medidas na linguagem do agricultor.
Wrapper que expõe parse_date e normalize_amount para o restante do sistema.
"""

import json
from utils.language_parser import parse_date, normalize_amount, parse_amount_for_report, WEIGHT_CONVERSIONS, AREA_CONVERSIONS

# Unidades aceitas para os comboboxes da UI
UNIT_NAMES = sorted({label for _, _, label, _ in WEIGHT_CONVERSIONS})
AREA_UNIT_NAMES = sorted({label for _, _, label, _ in AREA_CONVERSIONS if _ is not None})


class Measures:
    def __init__(self, measuresfile):
        self.measuresfile = measuresfile
        self.history = []   # lista de dicts {input, date_result, amount_result}

    def read(self, mute=False):
        try:
            with open(self.measuresfile, "r", encoding="utf-8-sig", errors="replace") as f:
                data = json.load(f)
            self.history = data.get("history", [])
            return 0
        except Exception:
            return 1

    def save(self, mute=False):
        try:
            with open(self.measuresfile, "w", encoding="utf-8") as f:
                json.dump({"history": self.history}, f, indent=4, ensure_ascii=False)
            return 0
        except Exception:
            return 1

    def interpret(self, text: str) -> dict:
        """
        Recebe qualquer texto do agricultor e tenta extrair data e/ou quantidade.
        Retorna dict com: date, date_ok, amount_original, amount_canonical, amount_unit
        """
        date_result, date_ok = parse_date(text)
        amount_dict = parse_amount_for_report(text)

        result = {
            "input": text,
            "date": date_result,
            "date_ok": date_ok,
            "amount_original": amount_dict["original"],
            "amount_canonical": amount_dict["canonical"],
            "amount_unit": amount_dict["unit"],
        }
        self.history.append(result)
        self.save(mute=True)
        return result

    def clear_history(self):
        self.history = []
        self.save(mute=True)
