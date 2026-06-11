import os
from random import randint

from twilio.rest import Client


class SMSSender:
    def __init__(self):
        """
        RF010 - Envio de código por SMS para cadastro de usuário.

        Gera um código de 4 dígitos aleatórios e armazena em self.code.
        O envio é feito pelo método send(), que usa a API da Twilio.

        Credenciais necessárias (variáveis de ambiente):
            TWILIO_ACCOUNT_SID  → SID da sua conta Twilio
            TWILIO_AUTH_TOKEN   → Auth Token da sua conta Twilio
            TWILIO_PHONE_NUMBER → Número Twilio no formato +15XXXXXXXXX

        Como configurar (Windows PowerShell, válido na sessão atual):
            $env:TWILIO_ACCOUNT_SID  = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            $env:TWILIO_AUTH_TOKEN   = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            $env:TWILIO_PHONE_NUMBER = "+15054374232"

        Como configurar (Linux/macOS, válido na sessão atual):
            export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            export TWILIO_AUTH_TOKEN="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            export TWILIO_PHONE_NUMBER="+15054374232"

        Ou crie um arquivo .env na raiz do projeto e use python-dotenv
        (ver README para instruções).
        """

        self.code = []

        for i in range(4):
            self.code.append(f"{randint(1, 9)}")

        self.code = "".join(self.code)

    def send(self, phone_number):
        """
        Envia o código SMS para o número do agricultor.

        O número deve estar no formato E.164, ex: +5581999999999.
        O sistema aceita o formato (81) 99999-9999 na UI e o converte aqui.
        """

        # Normaliza o número para E.164 (exigido pela Twilio)
        normalized = self._normalize_phone(phone_number)

        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token  = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_PHONE_NUMBER", "+15054374232")

        if not account_sid or not auth_token:
            # Em modo de desenvolvimento (sem credenciais), apenas imprime o código
            print(f"[DEV] Código SMS que seria enviado para {normalized}: {self.code}")
            return

        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=f"Seu código do AgroBook: {self.code}",
            from_=from_number,
            to=normalized,
        )

        print(f"SMS enviado — SID: {message.sid}")

    def _normalize_phone(self, phone: str) -> str:
        """
        Converte formatos brasileiros para E.164.
        Ex: (81) 99999-9999 → +5581999999999
            81999999999     → +5581999999999
            +5581999999999  → +5581999999999 (já ok)
        """
        digits = "".join(filter(str.isdigit, phone))

        if phone.startswith("+"):
            return phone  # já está em E.164

        if len(digits) == 11:          # DDD + 9 dígitos
            return f"+55{digits}"
        elif len(digits) == 10:        # DDD + 8 dígitos (fixo)
            return f"+55{digits}"
        else:
            return f"+{digits}"        # fallback