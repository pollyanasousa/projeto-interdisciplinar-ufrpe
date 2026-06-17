"""
voice_widget.py — VA3: Botão de microfone reutilizável para telas de cadastro.

FUNÇÃO:
  Em vez de duplicar a lógica de voz em cada tela, criamos um widget
  reutilizável. Qualquer tela pode chamar make_mic_button() + attach()
  passando o QLineEdit alvo e um callback que recebe o dict do LLM.

  Isso segue o princípio DRY (Don't Repeat Yourself) — escrevemos a
  lógica UMA VEZ e reutilizamos em Telefone, Nome, CPF, Cidade.
"""

from PyQt6.QtWidgets import QPushButton, QSizePolicy
from PyQt6.QtCore import QThread, pyqtSignal, Qt

# Roda em paralelo para não travar a interface enquanto grava e chama a API.
class _VoiceThread(QThread):
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)

    def __init__(self, duration=5):
        super().__init__()
        self.duration = duration

    def run(self):
        try:
            from utils.voice_input import VoiceInput
            from utils.llm_parser import parse_fala
            vi = VoiceInput(duration=self.duration)
            text, ok = vi.listen()
            if not ok or not text:
                self.error.emit("Não ouvi nada. Tente falar mais perto do microfone.")
                return
            result = parse_fala(text)
            result["_transcricao"] = text
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(f"Erro na voz: {e}")

# BOTÃO DE MICROFONE REUTILIZÁVEL
# Cria um QPushButton estilizado com o ícone de microfone.
# Ao clicar: grava → transcreve → parseia → chama on_result(dict).
# ─────────────────────────────────────────────────────────────────────────────

MIC_STYLE = """
    QPushButton {{
        background-color: {bg};
        color: white;
        border-radius: 10px;
        font-size: 18px;
        border: none;
        padding: 4px;
        min-width: 44px;
        min-height: 44px;
        max-width: 44px;
        max-height: 44px;
    }}
    QPushButton:hover {{ background-color: #0a3020; }}
    QPushButton:disabled {{ background-color: #999; }}
"""

def make_mic_button(parent=None) -> QPushButton:
    """Cria e retorna um QPushButton com ícone de microfone no estilo AgroBook."""
    from PyQt6.QtGui import QIcon, QPixmap
    from PyQt6.QtCore import QSize
    import os
    btn = QPushButton(parent)
    btn.setText("")  # sem texto em nenhum caso
    icon_path = os.path.join("gui", "images", "microphone-icon.png")
    if os.path.exists(icon_path):
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(28, 28))
    else:
        # fallback: renderiza o emoji como imagem
        btn.setText("")
    btn.setStyleSheet(MIC_STYLE.format(bg="#124831"))
    btn.setFixedSize(44, 44)
    btn.setToolTip("Clique e fale (5 segundos)")
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn


def attach_voice_to_lineedit(mic_btn: QPushButton, lineedit, on_result, duration=5, status_label=None):
    """
    Conecta um mic_btn a um lineedit.
    Quando clicado:
      1. Grava 5s
      2. Transcreve com Whisper
      3. Parseia com LLM
      4. Chama on_result(dict) — o caller decide o que fazer com os dados
    
    on_result recebe o dict do LLMParser. Campos sempre disponíveis:
      - result["tipo"]: "nome"|"cpf"|"cidade"|"plantio"|"colheita"|"gasto"|"desconhecido"
      - result["_transcricao"]: texto bruto transcrito pelo Whisper
    """
    _threads = []  # evita garbage collection

    def on_click():
        mic_btn.setEnabled(False)
        mic_btn.setText("")
        mic_btn.setStyleSheet(MIC_STYLE.format(bg="#b03020"))
        if status_label:
            status_label.setText(f"🎙️ Gravando… fale agora ({duration} segundos)")

        thread = _VoiceThread(duration=duration)

        def done(result):
            mic_btn.setEnabled(True)
            mic_btn.setText("")
            mic_btn.setStyleSheet(MIC_STYLE.format(bg="#124831"))
            transcricao = result.get("_transcricao", "")
            if status_label:
                status_label.setText(f'✅ "{transcricao}"')
            # preenche o lineedit com o texto transcrito
            lineedit.setText(transcricao)
            # chama o callback do caller para extrair campos específicos
            on_result(result)

        def err(msg):
            mic_btn.setEnabled(True)
            mic_btn.setText("")
            mic_btn.setStyleSheet(MIC_STYLE.format(bg="#124831"))
            if status_label:
                status_label.setText(f"❌ {msg}")

        thread.finished.connect(done)
        thread.error.connect(err)
        thread.start()
        _threads.append(thread)

    mic_btn.clicked.connect(on_click)
    mic_btn._voice_threads = _threads  # mantém referência viva no botão
