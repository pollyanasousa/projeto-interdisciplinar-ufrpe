"""
llm_parser.py — Interpretação da fala do agricultor via LLM.

VA3 — ENTRADA DE DADOS POR VOZ + TRATAMENTO DE MEDIDAS VIA LLM

O QUE MUDOU:
  VA2: agricultor digitava "3 sacos" → language_parser.py usava REGEX fixo.
       Só entendia padrões programados (ex: "3 sacos" = 180kg).
       "ontonte", "duas arroba e meia", "oxxi é mio" → NÃO FUNCIONAVA.

  VA3: agricultor FALA → Whisper transcreve → LLM interpreta.
       O LLM (llama-3.3-70b) entende QUALQUER variação coloquial nordestina,
       incluindo sotaque, gírias, pronúncias erradas e medidas regionais.

FLUXO COMPLETO (leia de cima para baixo):
  ┌─────────────────────────────────────────────────────────────────────┐
  │ INÍCIO: Agricultor clica no microfone                              │
  │   ↓ voice_widget.py (make_mic_button + attach_voice_to_lineedit)  │
  │   ↓ voice_input.py (VoiceInput.record + Whisper.transcribe)       │
  │   ↓                                                                │
  │ MEIO: Texto transcrito chega AQUI (llm_parser.py)                 │
  │   ↓ parse_fala() ou parse_fala_contexto()                         │
  │   ↓ LLMParser.parse() → SYSTEM_PROMPT + fala do agricultor        │
  │   ↓ LLM Groq → JSON estruturado                                   │
  │   ↓                                                                │
  │ FIM: Dados voltam para quem chamou (events.py / dialog.py)        │
  │   ↓ Preenchem campos, salvam no JSON, atualizam a tela            │
  └─────────────────────────────────────────────────────────────────────┘
  }
"""

import os
import json
from groq import Groq
from datetime import datetime, timedelta


def _today() -> str:
    """Retorna a data de hoje no formato dd/mm/yyyy."""
    return datetime.today().strftime("%d/%m/%Y")

def _yesterday() -> str:
    """Retorna a data de ontem no formato dd/mm/yyyy."""
    return (datetime.today() - timedelta(days=1)).strftime("%d/%m/%Y")



# PROMPT DO SISTEMA (VA3)"manual de instruções" que enviamos para o LLM (llama-3.3-70b) antes de cada pergunta. 
SYSTEM_PROMPT = f"""Você é um EXTRATOR DE DADOS. Sua ÚNICA função é converter fala em JSON. NUNCA responda com texto solto, NUNCA faça perguntas, NUNCA adicione explicações.

Data de hoje: {_today()}.

# 1. IDENTIFICAÇÃO DO TIPO DE FALA

Classifique a fala em UM dos tipos abaixo. Use o contexto [Contexto: ...] quando presente para desambiguar.

| Tipo | Indicadores | Contexto obrigatório |
|------|-------------|---------------------|
| **plantio** | semear, plantar, colocar/ botar na terra, semente; ou cultura+quantidade sem verbo de colheita | [Contexto: plantio] |
| **colheita** | colher, tirar/apanhar da terra, "colhei", "coiei", "cuiei" | [Contexto: colheita] |
| **gasto** | dinheiro, reais, custo, pagar/ paguei, comprar/ comprei, gastar/ gastei, "gastemo" | [Contexto: gasto] |
| **nome** | "meu nome é", "chamo", ou nome próprio isolado | — |
| **cpf** | "CPF", "meu CPF", ou sequência de 11 dígitos/ números | — |
| **telefone** | "telefone", "celular", "whats", ou número com DDD | — |
| **cidade** | "moro em", "sou de", "cidade de", ou nome de município | — |
| **coproprietario** | nome + CPF + vínculo + percentual | [Contexto: coproprietario] |
| **desconhecido** | não se encaixa em nenhum acima | — |

Regra de ouro: na dúvida entre plantio e colheita, se houver contexto use-o; senão, se falar de "plantar"/"semear" → plantio, se falar de "colher"/"apanhar" → colheita. Se realmente não der para identificar, use "desconhecido".

Regra para coproprietario: quando o contexto for [Contexto: coproprietario], SEMPRE use tipo "coproprietario" e extraia os campos nome, cpf, vinculo e percentual. Se algum campo não for mencionado, preencha com null. NUNCA classifique como "nome", "cpf" ou "desconhecido" quando o contexto for coproprietario.

# 2. LINGUAGEM DO AGRICULTOR NORDESTINO

## 2.1 Culturas — normalize para o nome canônico (minúsculas):
| Variações | Canônico |
|-----------|----------|
| milho, mio, mío, mii, "oxxi é mio", mío véio, milho verde | milho |
| feijão, fejão, feijão preto/ carioca/ fradinho/ de corda/ caupi | feijão |
| mandioca, macaxeira, aipim, manioc, macaxera | mandioca |
| tomate, tomatinho, tomatão | tomate |
| arroz | arroz |
| cana, cana-de-açúcar, cana doce | cana |
| batata, batatinha, batata-doce | batata |
| fava, favinha | fava |
| gergelim, gerjerim | gergelim |
| sorgo | sorgo |
| Outras culturas: mantenha o nome como o agricultor falou, em minúsculas.

## 2.2 Quantidades agrícolas — NÃO converta para kg (deixe em "sacos"/"arrobas"/etc no original). Preencha "quantidade_canonical" em kg usando:
- 1 saco/saca = 60 kg
- 1 arroba/@ = 15 kg
- 1 tonelada = 1000 kg
- 1 alqueire = 2.066 ha
- "meia" em quantidade agrícola = 0.5 (ex: "meia saca" = 30 kg)
- Números por extenso: "três" = 3, "uns cinco" = 5, "dez" = 10, "doze" = 12, "vinte" = 20
- Expressões vagas: "pouca coisa", "coisa pouca", "uns pouquinho" → mantenha como está

## 2.3 Datas coloquiais — converta para dd/mm/yyyy:
"hoje", "agora" → {_today()}
"ontem" → {_yesterday()}
"anteontem", "ontonte", "estonteando" → {(datetime.today() - timedelta(days=2)).strftime('%d/%m/%Y')}
"semana passada" → {(datetime.today() - timedelta(days=7)).strftime('%d/%m/%Y')}
"semana retrasada" → {(datetime.today() - timedelta(days=14)).strftime('%d/%m/%Y')}
"mês passado" → {(datetime.today() - timedelta(days=30)).strftime('%d/%m/%Y')}
"faz X dias" / "há X dias" → X dias atrás
"segunda/terça/... passada" → dia da semana anterior
Sem menção de data → {_today()}

## 2.4 Regra crítica: "meia" tem DOIS significados
- **Em CPF/telefone**: "meia" = 6 (sempre). Ex: "meia quatro" = 64, "zero meia" = 06.
- **Em quantidades agrícolas**: "meia" = 0.5. Ex: "meia saca" = 0.5 saca, "meia arroba" = 0.5 arroba.
- Se houver ambiguidade, use o contexto para decidir.

## 2.5 Pronúncia nordestina — sempre corrija para o termo normalizado:
"pantei"/"prantei" → plantio
"coiei"/"coihi"/"cuiei" → colheita
"gastei"/"gastemo" → gasto
"mio"/"mió" → milho
"fejão" → feijão
"macaxera"/"macaxeira" → mandioca
"batata doce" → batata-doce

# 3. FORMATO DE SAÍDA — REGRAS ABSOLUTAS (NÃO VIOLAR)

1. Responda APENAS com UM ÚNICO objeto JSON. NADA de Markdown, texto explicativo, múltiplos JSONs ou caracteres antes/depois.
2. NUNCA inclua pontos finais (.), interrogações (?) ou exclamações (!) nos valores das strings.
3. NUNCA faça perguntas. NUNCA responda com "Onde?", "Como?", "Quando?" ou similar.
4. Campos não mencionados pelo agricultor → null
5. Nomes de cultura sempre em minúsculas
6. "meia" = 6 em CPF/telefone; "meia" = 0.5 em quantidades agrícolas
7. Extraia apenas o que foi dito — não invente informações

## Schemas por tipo:

**plantio**: {{"tipo":"plantio","cultura": "string|null","quantidade_original": "string|null","quantidade_canonical": "string|null","data": "dd/mm/yyyy|null","area": "string|null"}}
**colheita**: {{"tipo":"colheita","cultura": "string|null","quantidade_original": "string|null","quantidade_canonical": "string|null","data": "dd/mm/yyyy|null"}}
**gasto**: {{"tipo":"gasto","descricao": "string|null","valor": "string|null","data": "dd/mm/yyyy|null","cultura": "string|null"}}
**nome**: {{"tipo":"nome","valor": "string"}}
**cpf**: {{"tipo":"cpf","valor": "string"}} (APENAS 11 dígitos)
**telefone**: {{"tipo":"telefone","valor": "string"}} (APENAS dígitos)
**cidade**: {{"tipo":"cidade","valor": "string"}}
**coproprietario**: {{"tipo":"coproprietario","nome": "string|null","cpf": "string|null","vinculo": "string|null","percentual": "string|null"}} (vínculos: Proprietário principal, Coproprietário, Herdeiro, Meeiro, Arrendatário)
**desconhecido**: {{"tipo":"desconhecido","texto_original": "string"}}

# 4. EXEMPLOS
# Cobrem: sotaque nordestino, datas relativas, medidas fracionadas, contexto de tela,
# "meia"=0.5 em agricola vs "meia"=6 em CPF, coproprietário com e sem campos completos.

"prantei uns dois saco de mio semana retrasada no sítio"
→ {{"tipo":"plantio","cultura":"milho","quantidade_original":"2 sacos","quantidade_canonical":"120.0 kg","data":"{(datetime.today() - timedelta(days=14)).strftime('%d/%m/%Y')}","area":"sítio"}}

"plantei três sacos de milho no roçado de fundo semana passada"
→ {{"tipo":"plantio","cultura":"milho","quantidade_original":"3 sacos","quantidade_canonical":"180.0 kg","data":"{(datetime.today() - timedelta(days=7)).strftime('%d/%m/%Y')}","area":"roçado de fundo"}}

"[Contexto: plantio] duas arroba e meia de feijão ontem"
→ {{"tipo":"plantio","cultura":"feijão","quantidade_original":"2.5 arrobas","quantidade_canonical":"37.5 kg","data":"{_yesterday()}","area":null}}

"[Contexto: plantio] uns cinco saco de fejão"
→ {{"tipo":"plantio","cultura":"feijão","quantidade_original":"5 sacos","quantidade_canonical":"300.0 kg","data":"{_today()}","area":null}}

"coiei uns cinco saco de mio ontonte"
→ {{"tipo":"colheita","cultura":"milho","quantidade_original":"5 sacos","quantidade_canonical":"300.0 kg","data":"{(datetime.today() - timedelta(days=2)).strftime('%d/%m/%Y')}"}}

"[Contexto: colheita] dez saco de milho"
→ {{"tipo":"colheita","cultura":"milho","quantidade_original":"10 sacos","quantidade_canonical":"600.0 kg","data":"{_today()}"}}

"gastei duzentos reais com adubo pro milho ontem"
→ {{"tipo":"gasto","descricao":"adubo","valor":"200 reais","data":"{_yesterday()}","cultura":"milho"}}

"paguei trezentos no veneno do tomate semana passada"
→ {{"tipo":"gasto","descricao":"veneno","valor":"300 reais","data":"{(datetime.today() - timedelta(days=7)).strftime('%d/%m/%Y')}","cultura":"tomate"}}

"meu nome é João da Silva"
→ {{"tipo":"nome","valor":"João da Silva"}}

"meu CPF é um dois três quatro cinco seis sete oito nove um zero"
→ {{"tipo":"cpf","valor":"12345678910"}}

"moro em Caruaru"
→ {{"tipo":"cidade","valor":"Caruaru"}}

"Ana Lima, CPF um dois três quatro cinco meia sete oito nove um zero, coproprietária, vinte e cinco por cento"
→ {{"tipo":"coproprietario","nome":"Ana Lima","cpf":"12345678910","vinculo":"Coproprietário","percentual":"25"}}

"[Contexto: coproprietario] Pedro Alves, CPF nove oito sete meia cinco quatro três dois um zero zero, arrendatário, dez por cento"
→ {{"tipo":"coproprietario","nome":"Pedro Alves","cpf":"98765432100","vinculo":"Arrendatário","percentual":"10"}}

"[Contexto: coproprietario] Maria Souza, CPF zero um dois três quatro cinco meia sete oito nove zero, herdeira, cinquenta por cento"
→ {{"tipo":"coproprietario","nome":"Maria Souza","cpf":"01234567890","vinculo":"Herdeiro","percentual":"50"}}

"[Contexto: coproprietario] João Pereira"
→ {{"tipo":"coproprietario","nome":"João Pereira","cpf":null,"vinculo":null,"percentual":null}}
"""

# CLASSE PRINCIPAL
class LLMParser:

    def __init__(self):
        # Conecta com a Groq usando a chave do arquivo .env
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def parse(self, fala: str) -> dict:
        """
        Recebe o texto transcrito pelo Whisper e devolve um dicionário
        com os dados estruturados extraídos pelo LLM.

        temperature=0 garante respostas mais consistentes e previsíveis.
        """
        if not fala or not fala.strip():
            return {"tipo": "desconhecido", "texto_original": ""}

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": fala}
                ],
                temperature=0,
                max_tokens=500,
            )

            raw = response.choices[0].message.content.strip()

            # Remove blocos ```json ``` caso o modelo inclua por engano
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            # Tenta converter o texto para dicionário Python
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                # Se o LLM devolveu múltiplos JSONs, mescla todos num só
                decoder = json.JSONDecoder()
                merged = {}
                idx = 0
                while idx < len(raw):
                    try:
                        obj, end = decoder.raw_decode(raw, idx)
                        if isinstance(obj, dict):
                            merged.update(obj)
                        idx = end
                        while idx < len(raw) and raw[idx] in " \n\r\t":
                            idx += 1
                    except json.JSONDecodeError:
                        break
                if merged:
                    return merged
                return {"tipo": "desconhecido", "texto_original": fala}

        except json.JSONDecodeError as e:
            print(f"[LLMParser] JSON inválido: {e}")
            return {"tipo": "desconhecido", "texto_original": fala}
        except Exception as e:
            print(f"[LLMParser] Erro API: {e}")
            return {"tipo": "desconhecido", "texto_original": fala}


# FUNÇÕES DE ATALHO
# Usadas pelos outros arquivos para não precisar criar o LLMParser manualmente.
# O _parser_instance evita criar uma nova conexão toda vez (singleton).

_parser_instance = None

def parse_fala(fala: str) -> dict:
    """Interpreta a fala do agricultor e retorna os dados estruturados."""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = LLMParser()
    return _parser_instance.parse(fala)


def parse_fala_contexto(fala: str, contexto: str) -> dict:
    """
    Igual a parse_fala mas avisa o LLM qual é o contexto da fala.
    Ex: contexto="plantio" → LLM sabe que qualquer menção de cultura e
    quantidade é um plantio, mesmo sem o verbo "plantei".
    Ex: contexto="colheita" → mesmo que o agricultor fale só "dez sacos de milho",
    o LLM entende que é uma colheita.
    """
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = LLMParser()
    fala_com_contexto = f"[Contexto: {contexto}] {fala}"
    return _parser_instance.parse(fala_com_contexto)