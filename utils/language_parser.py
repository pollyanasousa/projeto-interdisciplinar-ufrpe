"""
RF008 - Parser de linguagem natural do agricultor.
Converte expressões coloquiais de data, peso e área para formatos padrão.
"""

import re
from datetime import datetime, timedelta


# ─── DATAS ────────────────────────────────────────────────────────────────────

DATE_PATTERNS = [
    # Já no formato dd/mm/yyyy
    (r"^(\d{2}/\d{2}/\d{4})$", lambda m: m.group(1)),

    # Hoje / agora / esse dia
    (r"\b(hoje|agora|esse dia|este dia)\b", lambda m: datetime.today().strftime("%d/%m/%Y")),

    # Ontem
    (r"\b(ontem)\b", lambda m: (datetime.today() - timedelta(days=1)).strftime("%d/%m/%Y")),

    # Anteontem / antes de ontem
    (r"\b(anteontem|antes de ontem)\b", lambda m: (datetime.today() - timedelta(days=2)).strftime("%d/%m/%Y")),

    # X dias atrás / há X dias
    (r"\b(?:h[aá]|faz)\s+(\d+)\s+dias?\b",
     lambda m: (datetime.today() - timedelta(days=int(m.group(1)))).strftime("%d/%m/%Y")),
    (r"\b(\d+)\s+dias?\s+atr[aá]s\b",
     lambda m: (datetime.today() - timedelta(days=int(m.group(1)))).strftime("%d/%m/%Y")),

    # Semana passada / semana retrasada
    (r"\b(semana\s+retrasada|semana\s+passada)\b",
     lambda m: (datetime.today() - timedelta(weeks=(2 if "retr" in m.group(1) else 1))).strftime("%d/%m/%Y")),

    # X semanas atrás / há X semanas
    (r"\b(?:h[aá]|faz)\s+(\d+)\s+semanas?\b",
     lambda m: (datetime.today() - timedelta(weeks=int(m.group(1)))).strftime("%d/%m/%Y")),
    (r"\b(\d+)\s+semanas?\s+atr[aá]s\b",
     lambda m: (datetime.today() - timedelta(weeks=int(m.group(1)))).strftime("%d/%m/%Y")),

    # Mês passado
    (r"\b(m[eê]s\s+passado)\b", lambda m: _months_ago(1)),

    # X meses atrás
    (r"\b(?:h[aá]|faz)\s+(\d+)\s+m[eê]s(?:es)?\b",
     lambda m: _months_ago(int(m.group(1)))),
    (r"\b(\d+)\s+m[eê]s(?:es)?\s+atr[aá]s\b",
     lambda m: _months_ago(int(m.group(1)))),

    # dd/mm ou dd-mm (sem ano — assume ano corrente)
    (r"^(\d{1,2})[/\-](\d{1,2})$",
     lambda m: f"{int(m.group(1)):02d}/{int(m.group(2)):02d}/{datetime.today().year}"),
]


def _months_ago(n):
    today = datetime.today()
    month = today.month - n
    year = today.year
    while month <= 0:
        month += 12
        year -= 1
    day = min(today.day, [31,28,31,30,31,30,31,31,30,31,30,31][month-1])
    return f"{day:02d}/{month:02d}/{year}"


def parse_date(text: str) -> tuple[str, bool]:
    """
    Tenta converter a expressão de data para dd/mm/yyyy.
    Retorna (data_formatada, True) em caso de sucesso ou (texto_original, False).
    """
    text = text.strip().lower()
    for pattern, handler in DATE_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            try:
                result = handler(m)
                # Valida o resultado
                datetime.strptime(result, "%d/%m/%Y")
                return result, True
            except Exception:
                continue
    return text, False


# ─── PESOS / QUANTIDADES ──────────────────────────────────────────────────────

# (padrão_regex, fator_para_kg, unidade_canônica)
WEIGHT_CONVERSIONS = [
    (r"(\d+(?:[.,]\d+)?)\s*sacos?\b",        60.0,    "saco(s)",   "kg"),
    (r"(\d+(?:[.,]\d+)?)\s*sacas?\b",        60.0,    "saca(s)",   "kg"),
    (r"(\d+(?:[.,]\d+)?)\s*arrobas?\b",      15.0,    "arroba(s)", "kg"),
    (r"(\d+(?:[.,]\d+)?)\s*@\b",             15.0,    "@",         "kg"),
    (r"(\d+(?:[.,]\d+)?)\s*toneladas?\b",  1000.0,    "t",         "kg"),
    (r"(\d+(?:[.,]\d+)?)\s*kg\b",             1.0,    "kg",        "kg"),
    (r"(\d+(?:[.,]\d+)?)\s*quilos?\b",        1.0,    "kg",        "kg"),
    (r"(\d+(?:[.,]\d+)?)\s*gramas?\b",      0.001,    "g",         "kg"),
    (r"(\d+(?:[.,]\d+)?)\s*g\b",            0.001,    "g",         "kg"),
    (r"(\d+(?:[.,]\d+)?)\s*litros?\b",        1.0,    "L",         "L"),   # volume
    (r"(\d+(?:[.,]\d+)?)\s*l\b",             1.0,    "L",         "L"),
    (r"(\d+(?:[.,]\d+)?)\s*ml\b",          0.001,    "mL",        "L"),
]

# (padrão_regex, fator_para_hectare, unidade_canônica)
AREA_CONVERSIONS = [
    (r"(\d+(?:[.,]\d+)?)\s*alqueires?\b",    2.066,   "alqueire(s)", "ha"),
    (r"(\d+(?:[.,]\d+)?)\s*alq\.?\b",        2.066,   "alq.",        "ha"),
    (r"(\d+(?:[.,]\d+)?)\s*acres?\b",        0.4047,  "acre(s)",     "ha"),
    (r"(\d+(?:[.,]\d+)?)\s*hectares?\b",     1.0,     "ha",          "ha"),
    (r"(\d+(?:[.,]\d+)?)\s*ha\b",            1.0,     "ha",          "ha"),
    (r"(\d+(?:[.,]\d+)?)\s*m[²2]\b",     0.0001,     "m²",          "ha"),
    # Expressões coloquiais de tamanho de área
    (r"\b(ro[çc]ado)\b",                     None,    "roçado",      None),
    (r"\b(s[íi]tio)\b",                      None,    "sítio",       None),
    (r"\b(fazenda)\b",                        None,    "fazenda",     None),
    (r"\b(chácara)\b",                        None,    "chácara",     None),
]


def _to_float(s: str) -> float:
    return float(s.replace(",", "."))


def normalize_amount(text: str) -> tuple[str, str]:
    """
    Recebe a descrição de quantidade (ex: '3 sacos', '2 arrobas', '150 kg').
    Retorna (valor_original_formatado, valor_em_kg_ou_L_formatado).
    Se não reconhecer, retorna (texto, texto).
    """
    text = text.strip()
    for pattern, factor, label, unit in WEIGHT_CONVERSIONS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            qty = _to_float(m.group(1))
            canonical = round(qty * factor, 4)
            original_label = f"{qty} {label}"
            canonical_label = f"{canonical} {unit}"
            if original_label == canonical_label:
                return original_label, canonical_label
            return original_label, canonical_label
    return text, text


def normalize_area_name(text: str) -> str:
    """
    Normaliza nomes de área coloquiais, retornando o nome como capitalizado.
    Não converte — só padroniza graficamente.
    """
    return text.strip().title()


def parse_amount_for_report(text: str) -> dict:
    """
    Retorna dict com campos prontos para o relatório bancário:
      original  → como o agricultor digitou
      canonical → em unidade padrão (kg, L, ha)
      unit      → unidade canônica
    """
    text = text.strip()
    for pattern, factor, label, unit in WEIGHT_CONVERSIONS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            qty = _to_float(m.group(1))
            canonical = round(qty * factor, 4)
            return {"original": text, "canonical": f"{canonical} {unit}", "unit": unit}
    return {"original": text, "canonical": text, "unit": ""}
