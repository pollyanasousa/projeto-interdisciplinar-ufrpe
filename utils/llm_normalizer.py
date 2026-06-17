"""
llm_normalizer.py — VA3: Normalização de datas e medidas via LLM (fallback).

VA3 — TRATAMENTO DE MEDIDAS NA LINGUAGEM DO AGRICULTOR

POR QUE EXISTE:
  O llm_parser.py pega a fala completa do agricultor
  e devolve tudo estruturado (cultura, quantidade, data). MAS os models
  (model/planting.py, model/harvest.py, model/expense.py) também precisam
  converter campos individuais — por exemplo, quando o usuário edita manualmente
  um campo "data" ou "quantidade". Esse arquivo é o fallback inteligente.

"""

import os
import json
from groq import Groq
from datetime import datetime, timedelta

# CONEXÃO COM A GROQ
# Singleton: cria a conexão uma única vez e reutiliza nas chamadas seguintes,
# evitando abrir uma nova conexão HTTP a cada normalize_date() / normalize_amount().

_client_instance = None

def _get_client():
    """Retorna o cliente da Groq, criando-o apenas na primeira chamada."""
    global _client_instance
    if _client_instance is None:
        _client_instance = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client_instance


# PROMPT DE DATAS
# Instrução que mandamos pro LLM explicando o que ele deve fazer com datas.

_hoje = datetime.today().strftime("%d/%m/%Y")
_7d  = (datetime.today() - timedelta(days=7)).strftime("%d/%m/%Y")
_1d  = (datetime.today() - timedelta(days=1)).strftime("%d/%m/%Y")
_3d  = (datetime.today() - timedelta(days=3)).strftime("%d/%m/%Y")
_2d  = (datetime.today() - timedelta(days=2)).strftime("%d/%m/%Y")
_30d = (datetime.today() - timedelta(days=30)).strftime("%d/%m/%Y")

DATE_PROMPT = f"""Você é um conversor de datas coloquiais em português (inclusive variantes nordestinas) para o formato dd/mm/yyyy.

Hoje é {_hoje}. Use esta data como referência para calcular "hoje", "ontem", etc.

## Regras
- Responda APENAS com {{"data": "dd/mm/yyyy"}} — JSON puro, sem texto, sem markdown.
- Se não conseguir converter → {{"data": null}}

## Conversões
| Fala do agricultor | Cálculo |
|--------------------|---------|
| "hoje", "agora", "esse dia" | hoje |
| "ontem" | hoje - 1 dia |
| "anteontem", "ontonte", "estonteando" | hoje - 2 dias |
| "semana passada", "semana que passou" | hoje - 7 dias |
| "semana retrasada", "semana que passou retrasada" | hoje - 14 dias |
| "mês passado", "mês que passou" | hoje - 30 dias |
| "faz X dias", "há X dias", "X dias atrás" | hoje - X dias |
| "faz X semana", "há X semanas" | hoje - (X * 7) dias |
| "segunda passada", "terça passada"... | dia da semana anterior mais próximo |
| "começo do mês", "início do mês" | dia 01 do mês atual |
| "final do mês", "fim do mês passado" | último dia do mês anterior |
| dd/mm/yyyy | mantém igual |
| dd/mm (sem ano) | adiciona ano atual |

## Exemplos (hoje = {_hoje}):
"semana passada" -> {{"data": "{_7d}"}}
"ontem" -> {{"data": "{_1d}"}}
"faz três dias" -> {{"data": "{_3d}"}}
"ontonte" -> {{"data": "{_2d}"}}
"mês passado" -> {{"data": "{_30d}"}}
"não lembro" -> {{"data": null}}
"""

# PROMPT DE QUANTIDADES
# Instrução que mandamos pro LLM explicando o que ele deve fazer com medidas.

AMOUNT_PROMPT = """Você é um conversor de quantidades agrícolas ditas por agricultores nordestinos para unidades padrão.

## Regras
- Responda APENAS com {"original": "...", "canonical": "..."} — JSON puro.
- "original" = o que o agricultor disse, normalizado (ex: "3 sacos" em vez de "uns três saco").
- "canonical" = convertido para kg, ha ou litro com uma casa decimal.
- Se não conseguir converter → ambos os campos com o texto original.

## Tabela de conversão
| Unidade dita | Equivalência |
|-------------|--------------|
| 1 saco / saca | 60 kg |
| 1 arroba / @ | 15 kg |
| 1 tonelada | 1000 kg |
| 1 alqueire | 2.066 ha |
| kg, litro, ha | já está na unidade correta |
| "meia" + unidade | 0.5 x unidade (ex: "meia arroba" = 7.5 kg) |
| "meio" + unidade | 0.5 x unidade |

## Números por extenso
"um/uma"=1, "dois/duas"=2, "três"=3, "quatro"=4, "cinco"=5, "seis"=6, "sete"=7, "oito"=8, "nove"=9, "dez"=10, "onze"=11, "doze"=12, "treze"=13, "quatorze/catorze"=14, "quinze"=15, "vinte"=20, "trinta"=30, "quarenta"=40, "cinquenta"=50, "cem/cento"=100, "duzentos"=200, "trezentos"=300
Prefixos aproximativos: "uns", "umas", "cerca de" → ignore (ex: "uns três" = 3)

## Expressões vagas (mantenha como está em ambos os campos):
"pouca coisa", "coisa pouca", "uns pouquinho", "um pouco", "só um tiquim", "bem pouquinho"

## Exemplos:
"uns três saco" → {{"original": "3 sacos", "canonical": "180.0 kg"}}
"duas arroba e meia" → {{"original": "2.5 arrobas", "canonical": "37.5 kg"}}
"cinco alqueire" → {{"original": "5 alqueires", "canonical": "10.3 ha"}}
"cento e cinquenta kg" → {{"original": "150 kg", "canonical": "150.0 kg"}}
"meia tonelada" → {{"original": "0.5 tonelada", "canonical": "500.0 kg"}}
"dois saco e meio" → {{"original": "2.5 sacos", "canonical": "150.0 kg"}}
"coisa pouca" → {{"original": "coisa pouca", "canonical": "coisa pouca"}}
"uma arroba" → {{"original": "1 arroba", "canonical": "15.0 kg"}}
"sete litro de veneno" → {{"original": "7 litros", "canonical": "7.0 l"}}
"""

# FUNÇÃO AUXILIAR
# Manda o texto pro LLM e devolve o resultado como dicionário Python.

def _perguntar_llm(prompt_sistema: str, texto: str) -> dict:
    """
    Envia o texto para o LLM com as instruções do prompt e retorna o JSON.
    Se der qualquer erro, retorna um dicionário vazio {}.
    """
    try:
        client = _get_client()

        resposta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user",   "content": texto}
            ],
            temperature=0,    # 0 = resposta mais consistente e previsível
            max_tokens=100,   # a resposta é curta, não precisa de mais
        )

        texto_resposta = resposta.choices[0].message.content.strip()

        # Remove blocos ```json ``` caso o modelo coloque por engano
        if texto_resposta.startswith("```"):
            texto_resposta = texto_resposta.split("```")[1]
            if texto_resposta.startswith("json"):
                texto_resposta = texto_resposta[4:]
            texto_resposta = texto_resposta.strip()

        return json.loads(texto_resposta)

    except Exception as erro:
        print(f"[LLMNormalizer] Erro ao chamar o LLM: {erro}")
        return {}

# FUNÇÃO PRINCIPAL: DATAS
def normalize_date(texto: str) -> tuple[str, bool]:
    """
    ── VA3: substitui o parse_date() do language_parser ──

    Converte uma expressão de data coloquial para dd/mm/yyyy usando o LLM.

    Exemplos:
      "ontem"          → ("14/06/2026", True)
      "semana passada" → ("08/06/2026", True)
      "ontonte"        → ("13/06/2026", True)  ← regex da VA2 não entendia isso
      "faz uns 3 dias" → ("12/06/2026", True)

    Retorna (data_convertida, True) se conseguiu.
    Retorna (texto_original, False) se não conseguiu.
    """
    import re

    # Se vier vazio, usa hoje
    if not texto or not texto.strip():
        return datetime.today().strftime("%d/%m/%Y"), True

    texto = texto.strip()

    # Se já está no formato correto, não precisa chamar o LLM
    if re.match(r"^\d{2}/\d{2}/\d{4}$", texto):
        return texto, True

    # Chama o LLM com o DATE_PROMPT (já é f-string com a data de hoje)
    resultado = _perguntar_llm(DATE_PROMPT, texto)

    # Pega o campo "data" da resposta
    data = resultado.get("data")

    if data and re.match(r"^\d{2}/\d{2}/\d{4}$", str(data)):
        return str(data), True

    # Se não converteu, devolve o texto original
    return texto, False

# FUNÇÃO PRINCIPAL: QUANTIDADES
def normalize_amount(texto: str) -> tuple[str, str]:
    """
    ── VA3: substitui o normalize_amount() do language_parser ──

    Converte uma quantidade coloquial para a unidade padrão usando o LLM.

    Exemplos:
      "uns três saco"      → ("3 sacos", "180.0 kg")
      "duas arroba"        → ("2 arrobas", "30.0 kg")
      "cinco alqueire"     → ("5 alqueires", "10.3 ha")
      "uma arroba e meia"  → ("1.5 arrobas", "22.5 kg")  ← regex não entendia

    Retorna (original, canonical).
    Se não conseguir converter, retorna (texto, texto).
    """
    if not texto or not texto.strip():
        return texto, texto

    texto = texto.strip()

    # Chama o LLM
    resultado = _perguntar_llm(AMOUNT_PROMPT, texto)

    # Pega os campos "original" e "canonical" da resposta
    original  = resultado.get("original",  texto)
    canonical = resultado.get("canonical", texto)

    return str(original), str(canonical)
