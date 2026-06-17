"""
voice_input.py — VA3: Captura e transcrição de voz com Whisper (Groq).

VA3 — ENTRADA DE DADOS POR VOZ: PRIMEIRA ETAPA DO FLUXO

  Captura o áudio do microfone e transcreve para texto usando o Whisper
  da Groq. É a PRIMEIRA etapa do pipeline de voz.
"""

import os
import tempfile
import numpy as np
import sounddevice as sd
import soundfile as sf
from groq import Groq


class VoiceInput:

    def __init__(self, duration: int = 5, sample_rate: int = 16000):
        # duration: quantos segundos gravar
        # sample_rate: 16000 Hz é o padrão do Whisper — qualidade suficiente para voz
        self.duration = duration
        self.sample_rate = sample_rate
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def record(self) -> np.ndarray:
        """Grava áudio do microfone por self.duration segundos."""
        audio = sd.rec(
            int(self.duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32"
        )
        sd.wait()  # espera terminar a gravação antes de continuar
        return audio

    def transcribe(self, audio: np.ndarray) -> str:
        """
        Envia o áudio gravado para o Whisper da Groq e retorna o texto.

        O Whisper é o modelo de transcrição de voz da OpenAI, disponível
        gratuitamente na Groq. Ele entende português brasileiro, inclusive
        sotaque nordestino e vocabulário do campo.
        """
        # Cria um arquivo temporário .wav para enviar para a API
        # No Windows o arquivo precisa ser fechado antes de ser lido
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_name = tmp.name
        tmp.close()

        try:
            # Salva o áudio no arquivo temporário
            sf.write(tmp_name, audio, self.sample_rate)

            # Envia para a Groq e recebe o texto
            with open(tmp_name, "rb") as f:
                transcricao = self.client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo",
                    file=f,
                    language="pt",          # português
                    response_format="text"  # devolve texto puro, sem JSON
                )

            # Garante que o retorno é uma string
            if isinstance(transcricao, str):
                return transcricao.strip()
            elif hasattr(transcricao, "text"):
                return transcricao.text.strip()
            else:
                return str(transcricao).strip()

        except Exception as e:
            print(f"[VoiceInput] Erro na transcrição: {e}")
            return ""

        finally:
            # Apaga o arquivo temporário sempre, mesmo se der erro
            try:
                os.unlink(tmp_name)
            except Exception:
                pass

    def listen(self) -> tuple[str, bool]:
        """
        Grava e transcreve em uma só chamada.
        Retorna (texto_transcrito, True) se funcionou.
        Retorna ("", False) se deu erro.
        """
        try:
            audio = self.record()
            texto = self.transcribe(audio)
            return (texto, True) if texto else ("", False)
        except Exception as e:
            print(f"[VoiceInput] Erro: {e}")
            return "", False
