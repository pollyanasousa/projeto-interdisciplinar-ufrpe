"""
dialog.py — Diálogos do AgroBook
RF011: todos os diálogos usam entrada por voz como método principal.
O agricultor fala, o sistema entende e preenche. Digitação é só fallback.
"""

from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QMessageBox, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QLabel, QSizePolicy, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont
import os

# ── Estilos globais ──────────────────────────────────────────────────────────
BG       = "#E9F2EA"
GREEN    = "#124831"
GREEN2   = "#1a5c3e"
BROWN    = "#7C5A3C"
RED      = "#b03020"
WHITE    = "#FFFFFF"
BORDER   = "#c8ddc9"

STYLE_DIALOG = f"QDialog {{ background-color: {BG}; font-family: 'Roboto Flex'; }}"

STYLE_TITLE = f"""
    font-family: 'Roboto Flex'; font-weight: 800;
    font-size: 20px; color: {GREEN};
"""
STYLE_SUB = f"font-size: 13px; color: {BROWN};"

STYLE_INFO_BOX = f"""
    background: #d6e8d8; border-radius: 10px;
    padding: 10px; font-size: 12px; color: {GREEN};
"""

STYLE_OPTION_BTN = f"""
    QPushButton {{
        background-color: {WHITE}; color: #1E1E1E;
        border: 1.5px solid {BORDER}; border-radius: 12px;
        font-size: 15px; padding: 12px 16px;
        text-align: left;
    }}
    QPushButton:hover {{ background-color: #d6e8d8; border-color: {GREEN}; }}
    QPushButton:checked {{
        background-color: {GREEN}; color: white;
        border-color: {GREEN};
    }}
"""

STYLE_MIC_BTN_IDLE = f"""
    QPushButton {{
        background-color: {GREEN}; color: white;
        border-radius: 28px; font-size: 22px;
        border: none; min-width: 56px; min-height: 56px;
        max-width: 56px; max-height: 56px;
    }}
    QPushButton:hover {{ background-color: {GREEN2}; }}
    QPushButton:disabled {{ background-color: #999; }}
"""
STYLE_MIC_BTN_REC = """
    QPushButton {
        background-color: #b03020; color: white;
        border-radius: 28px; font-size: 22px;
        border: none; min-width: 56px; min-height: 56px;
        max-width: 56px; max-height: 56px;
    }
"""

STYLE_CONFIRM_BTN = f"""
    QPushButton {{
        background-color: {GREEN}; color: white;
        border-radius: 12px; font-size: 16px;
        font-weight: 700; padding: 13px; border: none;
    }}
    QPushButton:hover {{ background-color: {GREEN2}; }}
    QPushButton:disabled {{ background-color: #999; }}
"""

STYLE_CANCEL_BTN = f"""
    QPushButton {{
        background-color: transparent; color: {BROWN};
        border: 1.5px solid {BORDER}; border-radius: 12px;
        font-size: 14px; padding: 10px;
    }}
    QPushButton:hover {{ background-color: #ddd; }}
"""

STYLE_INPUT = f"""
    QLineEdit {{
        border: 2px solid {BORDER}; color: #1E1E1E;
        background-color: {WHITE}; border-radius: 12px;
        font-size: 16px; padding: 10px 14px;
    }}
    QLineEdit:focus {{ border-color: {GREEN}; }}
"""

STYLE_STATUS_OK  = f"font-size: 12px; color: {GREEN}; padding: 4px;"
STYLE_STATUS_ERR = f"font-size: 12px; color: {RED}; padding: 4px;"
STYLE_STATUS_REC = f"font-size: 12px; color: {BROWN}; font-style: italic; padding: 4px;"


# ── Thread de voz ────────────────────────────────────────────────────────────

class VoiceThread(QThread):
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)

    def __init__(self, duration=6, contexto=None):
        super().__init__()
        self.duration = duration
        self.contexto = contexto  # ex: "coproprietario", "plantio", etc.

    def run(self):
        try:
            from utils.voice_input import VoiceInput
            from utils.llm_parser import parse_fala, parse_fala_contexto
            vi = VoiceInput(duration=self.duration)
            text, ok = vi.listen()
            if not ok or not text:
                self.error.emit("Não ouvi nada. Fale mais perto do microfone.")
                return
            if self.contexto:
                result = parse_fala_contexto(text, self.contexto)
            else:
                result = parse_fala(text)
            result["_transcricao"] = text
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(f"Erro: {e}")


def _mic_icon():
    """Retorna ícone do microfone ou emoji fallback."""
    path = os.path.join("gui", "images", "microphone-icon.png")
    if os.path.exists(path):
        return QIcon(path)
    return None


CANCELLED = object()


# ── Helper: botão de microfone central ───────────────────────────────────────

def _make_mic_row(duration=6):
    """
    Cria linha com [status_label  🎤].
    Retorna (hbox, mic_btn, status_label, start_fn).
    start_fn(on_done, on_error) dispara a gravação.
    """
    mic_btn = QPushButton()
    mic_btn.setFixedSize(56, 56)
    mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE)
    icon = _mic_icon()
    if icon:
        mic_btn.setIcon(icon)
        mic_btn.setIconSize(QSize(30, 30))
    else:
        mic_btn.setText("🎤")
    mic_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    mic_btn.setToolTip(f"Clique e fale ({duration} segundos)")

    status = QLabel("Clique no microfone e fale")
    status.setStyleSheet(STYLE_STATUS_REC)
    status.setWordWrap(True)
    status.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    hbox = QHBoxLayout()
    hbox.addWidget(status)
    hbox.addWidget(mic_btn)

    _threads = []

    def start(on_done, on_error):
        mic_btn.setEnabled(False)
        mic_btn.setStyleSheet(STYLE_MIC_BTN_REC)
        if icon:
            mic_btn.setIcon(icon)
            mic_btn.setIconSize(QSize(30, 30))
        else:
            mic_btn.setText("⏺")
        status.setStyleSheet(STYLE_STATUS_REC)
        status.setText(f"🎙️ Gravando… fale agora ({duration}s)")

        t = VoiceThread(duration=duration)

        def _done(r):
            mic_btn.setEnabled(True)
            mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE)
            if icon:
                mic_btn.setIcon(icon)
                mic_btn.setIconSize(QSize(30, 30))
            else:
                mic_btn.setText("🎤")
            status.setStyleSheet(STYLE_STATUS_OK)
            status.setText(f'✅ "{r.get("_transcricao","")}"')
            on_done(r)

        def _err(msg):
            mic_btn.setEnabled(True)
            mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE)
            if icon:
                mic_btn.setIcon(icon)
                mic_btn.setIconSize(QSize(30, 30))
            else:
                mic_btn.setText("🎤")
            status.setStyleSheet(STYLE_STATUS_ERR)
            status.setText(f"❌ {msg}")
            on_error(msg)

        t.finished.connect(_done)
        t.error.connect(_err)
        t.start()
        _threads.append(t)

    mic_btn.clicked.connect(lambda: start(
        mic_btn.property("_on_done") or (lambda r: None),
        mic_btn.property("_on_error") or (lambda m: None)
    ))

    return hbox, mic_btn, status, start, _threads


# ── Diálogo: área de terra ────────────────────────────────────────────────────

class AreaDialog(QDialog):
    """
    Diálogo de cadastro de área — estilo Figma.
    Mostra áreas já cadastradas como botões clicáveis.
    Campo + microfone para falar/digitar uma nova.
    """
    def __init__(self, areas_existentes: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AgroBook")
        self.setStyleSheet(STYLE_DIALOG)
        self.setFixedWidth(340)
        self.resultado = None
        self._threads = []

        vbox = QVBoxLayout(self)
        vbox.setSpacing(10)
        vbox.setContentsMargins(20, 20, 20, 20)

        # Info
        info = QLabel("ℹ️  Antes de usar o app, cadastre pelo menos uma área de terra.")
        info.setStyleSheet(STYLE_INFO_BOX)
        info.setWordWrap(True)
        vbox.addWidget(info)

        # Título
        title = QLabel("Como chama essa terra?")
        title.setStyleSheet(STYLE_TITLE)
        vbox.addWidget(title)

        sub = QLabel("Use o nome que você já usa")
        sub.setStyleSheet(STYLE_SUB)
        vbox.addWidget(sub)

        # Botões das áreas existentes
        self._selected = None
        if areas_existentes:
            for area in areas_existentes:
                btn = QPushButton(area)
                btn.setStyleSheet(STYLE_OPTION_BTN)
                btn.setCheckable(True)
                btn.clicked.connect(lambda checked, a=area, b=btn: self._select_area(a, b))
                vbox.addWidget(btn)
            self._area_btns = vbox
        else:
            self._area_btns = None

        # Separador
        sep = QLabel("🎙️  Ou escreva / fale um nome novo")
        sep.setStyleSheet(f"font-size: 12px; color: {BROWN}; margin-top: 4px;")
        vbox.addWidget(sep)

        # Campo de texto + microfone
        self.field = QLineEdit()
        self.field.setPlaceholderText("Nome da área...")
        self.field.setStyleSheet(STYLE_INPUT)
        self.field.textChanged.connect(self._on_field_changed)

        mic_btn = QPushButton()
        mic_btn.setFixedSize(44, 44)
        mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE.replace("28px","20px").replace("56px","44px"))
        icon = _mic_icon()
        if icon:
            mic_btn.setIcon(icon)
            mic_btn.setIconSize(QSize(24, 24))
        else:
            mic_btn.setText("🎤")
        mic_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.status = QLabel("")
        self.status.setStyleSheet(STYLE_STATUS_REC)
        self.status.setWordWrap(True)

        row = QHBoxLayout()
        row.addWidget(self.field)
        row.addWidget(mic_btn)
        vbox.addLayout(row)
        vbox.addWidget(self.status)

        mic_btn.clicked.connect(self._gravar)
        self._mic_btn = mic_btn
        self._icon = icon

        # Botão confirmar
        self.confirm_btn = QPushButton("→ Próximo")
        self.confirm_btn.setStyleSheet(STYLE_CONFIRM_BTN)
        self.confirm_btn.clicked.connect(self._confirmar)
        vbox.addWidget(self.confirm_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(STYLE_CANCEL_BTN)
        cancel_btn.clicked.connect(self.reject)
        vbox.addWidget(cancel_btn)

    def _select_area(self, nome, btn_clicado):
        self._selected = nome
        self.field.clear()
        # desmarca os outros visualmente
        for i in range(self._area_btns.count()):
            item = self._area_btns.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QPushButton):
                w = item.widget()
                if w != btn_clicado:
                    w.setChecked(False)
        self.status.setText(f'✅ Selecionado: "{nome}"')
        self.status.setStyleSheet(STYLE_STATUS_OK)

    def _on_field_changed(self, txt):
        if txt.strip():
            self._selected = None  # digitou, deseleciona opção

    def _gravar(self):
        self._mic_btn.setEnabled(False)
        self._mic_btn.setStyleSheet(STYLE_MIC_BTN_REC.replace("28px","20px").replace("56px","44px"))
        self.status.setText("🎙️ Gravando… fale o nome da terra (8s)")
        self.status.setStyleSheet(STYLE_STATUS_REC)

        t = VoiceThread(duration=8)

        def done(r):
            self._mic_btn.setEnabled(True)
            self._mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE.replace("28px","20px").replace("56px","44px"))
            if self._icon:
                self._mic_btn.setIcon(self._icon)
                self._mic_btn.setIconSize(QSize(24, 24))
            else:
                self._mic_btn.setText("🎤")
            nome = r.get("_transcricao", "").strip()
            self.field.setText(nome)
            self.status.setText(f'✅ Ouvi: "{nome}" — confirme ou corrija')
            self.status.setStyleSheet(STYLE_STATUS_OK)

        def err(msg):
            self._mic_btn.setEnabled(True)
            self._mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE.replace("28px","20px").replace("56px","44px"))
            if self._icon:
                self._mic_btn.setIcon(self._icon)
                self._mic_btn.setIconSize(QSize(24, 24))
            else:
                self._mic_btn.setText("🎤")
            self.status.setText(f"❌ {msg}")
            self.status.setStyleSheet(STYLE_STATUS_ERR)

        t.finished.connect(done)
        t.error.connect(err)
        t.start()
        self._threads.append(t)

    def _confirmar(self):
        from utils.validators import is_valid_name
        nome = self._selected or self.field.text().strip()
        if not nome:
            self.status.setText("❌ Fale ou escreva o nome da área primeiro")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            return
        if not is_valid_name(nome):
            self.status.setText("❌ Nome inválido. Use apenas letras e espaços.")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            return
        self.resultado = nome
        self.accept()

    def get_result(self):
        return self.resultado


# ── Diálogo: plantio por voz ─────────────────────────────────────────────────

class PlantioDialog(QDialog):
    """
    O agricultor fala UMA frase: 'plantei três sacos de milho no roçado ontem'
    O LLM preenche tudo. Ele confirma e pronto.
    """
    def __init__(self, areas: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AgroBook")
        self.setStyleSheet(STYLE_DIALOG)
        self.setFixedWidth(340)
        self.resultado = None
        self._threads = []

        vbox = QVBoxLayout(self)
        vbox.setSpacing(10)
        vbox.setContentsMargins(20, 20, 20, 20)

        title = QLabel("O que você plantou?")
        title.setStyleSheet(STYLE_TITLE)
        vbox.addWidget(title)

        sub = QLabel('Fale tudo de uma vez. Você pode dizer:\n"plantei três sacos de milho ontem" ou só "três sacos de mio no roçado"')
        sub.setStyleSheet(STYLE_SUB)
        sub.setWordWrap(True)
        vbox.addWidget(sub)

        # Microfone central
        mic_btn = QPushButton()
        mic_btn.setFixedSize(72, 72)
        mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE.replace("28px","34px").replace("56px","72px"))
        icon = _mic_icon()
        if icon:
            mic_btn.setIcon(icon)
            mic_btn.setIconSize(QSize(36, 36))
        else:
            mic_btn.setText("🎤")
        mic_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        mic_btn.setToolTip("Clique e fale o plantio (12 segundos)")
        mic_row.addStretch()
        mic_row.addWidget(mic_btn)
        mic_row.addStretch()
        vbox.addLayout(mic_row)

        self.status = QLabel("Clique no microfone e fale")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet(STYLE_STATUS_REC)
        self.status.setWordWrap(True)
        vbox.addWidget(self.status)

        # Campos de confirmação (aparecem após gravar)
        sep = QLabel("Confirme os dados:")
        sep.setStyleSheet(f"font-size: 12px; color: {BROWN}; margin-top: 6px;")
        vbox.addWidget(sep)

        self.culture_edit = QLineEdit(); self.culture_edit.setPlaceholderText("Cultura (ex: milho)")
        self.culture_edit.setStyleSheet(STYLE_INPUT)
        self.area_combo = QComboBox()
        self.area_combo.addItems(areas)
        self.area_combo.setStyleSheet(f"border:2px solid {BORDER}; border-radius:10px; padding:8px; font-size:14px; background:{WHITE};")
        self.amount_edit = QLineEdit(); self.amount_edit.setPlaceholderText("Quantidade (ex: 3 sacos)")
        self.amount_edit.setStyleSheet(STYLE_INPUT)
        self.date_edit = QLineEdit(); self.date_edit.setPlaceholderText("Data (ex: hoje, ontem)")
        self.date_edit.setStyleSheet(STYLE_INPUT)

        for lbl, w in [("Cultura", self.culture_edit), ("Área", self.area_combo),
                        ("Quantidade", self.amount_edit), ("Data", self.date_edit)]:
            row = QHBoxLayout()
            l = QLabel(lbl); l.setStyleSheet(f"font-size:13px; color:{BROWN}; min-width:70px;")
            row.addWidget(l); row.addWidget(w)
            vbox.addLayout(row)

        # Botões
        self.confirm_btn = QPushButton("✓ Confirmar plantio")
        self.confirm_btn.setStyleSheet(STYLE_CONFIRM_BTN)
        self.confirm_btn.clicked.connect(self._confirmar)
        vbox.addWidget(self.confirm_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(STYLE_CANCEL_BTN)
        cancel_btn.clicked.connect(self.reject)
        vbox.addWidget(cancel_btn)

        # Conectar microfone
        self._mic_btn = mic_btn
        self._icon = icon
        mic_btn.clicked.connect(self._gravar)

    def _gravar(self):
        self._mic_btn.setEnabled(False)
        self._mic_btn.setStyleSheet(STYLE_MIC_BTN_REC.replace("28px","34px").replace("56px","72px"))
        self.status.setText("🎙️ Gravando… fale agora (12s)")
        self.status.setStyleSheet(STYLE_STATUS_REC)

        # ── VA3: contexto="plantio" → LLM entende sem precisar dizer "plantei"
        # O agricultor pode falar só "três sacos de milho no roçado ontem"
        t = VoiceThread(duration=12, contexto="plantio")

        def done(r):
            self._mic_btn.setEnabled(True)
            self._mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE.replace("28px","34px").replace("56px","72px"))
            if self._icon:
                self._mic_btn.setIcon(self._icon); self._mic_btn.setIconSize(QSize(36,36))
            else:
                self._mic_btn.setText("🎤")
            transcricao = r.get("_transcricao","")
            self.status.setStyleSheet(STYLE_STATUS_OK)
            self.status.setText(f'✅ Entendi: "{transcricao}"')
            if r.get("tipo") == "plantio":
                if r.get("cultura"): self.culture_edit.setText(r["cultura"])
                if r.get("quantidade_original"): self.amount_edit.setText(r["quantidade_original"])
                if r.get("data"): self.date_edit.setText(r["data"])
                if r.get("area"):
                    idx = self.area_combo.findText(r["area"], Qt.MatchFlag.MatchContains)
                    if idx >= 0: self.area_combo.setCurrentIndex(idx)
            else:
                # ── Com o contexto=plantio, o LLM já deve identificar mesmo sem "plantei"
                # Se ainda assim não identificou, tenta preencher pelo que veio
                if r.get("cultura"): self.culture_edit.setText(r["cultura"])
                if r.get("quantidade_original"): self.amount_edit.setText(r["quantidade_original"])
                if r.get("data"): self.date_edit.setText(r["data"])
                self.status.setStyleSheet(STYLE_STATUS_ERR)
                self.status.setText(f'⚠️ Corrija os campos abaixo se precisar.')

        def err(msg):
            self._mic_btn.setEnabled(True)
            self._mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE.replace("28px","34px").replace("56px","72px"))
            if self._icon:
                self._mic_btn.setIcon(self._icon); self._mic_btn.setIconSize(QSize(36,36))
            else:
                self._mic_btn.setText("🎤")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            self.status.setText(f"❌ {msg}")

        t.finished.connect(done); t.error.connect(err); t.start()
        self._threads.append(t)

    def _confirmar(self):
        culture = self.culture_edit.text().strip()
        area    = self.area_combo.currentText()
        amount  = self.amount_edit.text().strip()
        date    = self.date_edit.text().strip()

        # ── VA3: o LLM já preencheu os campos via voz.
        # Só checamos se os campos não estão vazios — sem regex de validação.
        if not culture:
            self.status.setText("❌ Fale o plantio primeiro (clique no microfone)")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            return
        if not amount:
            self.status.setText("❌ Quantidade não preenchida. Fale novamente.")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            return
        if not date:
            self.status.setText("❌ Data não preenchida. Fale novamente.")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            return
        self.resultado = {"culture": culture, "area": area, "amount": amount, "date": date}
        self.accept()

    def get_result(self): return self.resultado


# ── Diálogo: colheita por voz ─────────────────────────────────────────────────

class ColheitaDialog(QDialog):
    """
    Mostra plantios cadastrados como opções clicáveis com detalhes completos.
    O agricultor clica no que colheu e fala a quantidade e data.
    """
    def __init__(self, plantios: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AgroBook")
        self.setStyleSheet(STYLE_DIALOG)
        self.setFixedWidth(340)
        self.resultado = None
        self._threads = []

        # Normaliza: aceita lista de dicts ou lista de strings
        if plantios and isinstance(plantios[0], dict):
            self._plantios = plantios
        else:
            self._plantios = [{"culture": c, "area": "", "amount": ""} for c in plantios]

        self._selected_culture = self._plantios[0]["culture"] if self._plantios else ""
        self._selected_area    = self._plantios[0].get("area", "") if self._plantios else ""

        vbox = QVBoxLayout(self)
        vbox.setSpacing(10)
        vbox.setContentsMargins(20, 20, 20, 20)

        title = QLabel("O que você colheu?")
        title.setStyleSheet(STYLE_TITLE)
        vbox.addWidget(title)

        sub = QLabel("Toque no plantio e depois fale a quantidade e data")
        sub.setStyleSheet(STYLE_SUB)
        sub.setWordWrap(True)
        vbox.addWidget(sub)

        # Botões clicáveis com info completa do plantio
        self._cult_btns = []
        for i, p in enumerate(self._plantios):
            label = p["culture"]
            if p.get("area"):
                label += f"  •  {p['area']}"
            if p.get("amount"):
                label += f"  •  {p['amount']}"
            btn = QPushButton(label)
            btn.setStyleSheet(STYLE_OPTION_BTN)
            btn.setCheckable(True)
            if i == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, pl=p, b=btn: self._select_plantio(pl, b))
            vbox.addWidget(btn)
            self._cult_btns.append(btn)

        # Microfone
        sep = QLabel("🎙️  Fale a quantidade e a data")
        sep.setStyleSheet(f"font-size: 12px; color: {BROWN}; margin-top:6px;")
        vbox.addWidget(sep)

        mic_btn = QPushButton()
        mic_btn.setFixedSize(72, 72)
        mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE.replace("28px","34px").replace("56px","72px"))
        icon = _mic_icon()
        if icon:
            mic_btn.setIcon(icon); mic_btn.setIconSize(QSize(36,36))
        else:
            mic_btn.setText("🎤")
        mic_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        mic_btn.setToolTip('Fale: "colhi dez sacos ontem"')

        mic_row = QHBoxLayout()
        mic_row.addStretch(); mic_row.addWidget(mic_btn); mic_row.addStretch()
        vbox.addLayout(mic_row)

        self.status = QLabel('Exemplo: "colhi dez sacos ontem"')
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet(STYLE_STATUS_REC)
        self.status.setWordWrap(True)
        vbox.addWidget(self.status)

        # Campos de confirmação
        self.amount_edit = QLineEdit(); self.amount_edit.setPlaceholderText("Quantidade (ex: 10 sacos)")
        self.amount_edit.setStyleSheet(STYLE_INPUT)
        self.date_edit = QLineEdit(); self.date_edit.setPlaceholderText("Data (ex: hoje, ontem)")
        self.date_edit.setStyleSheet(STYLE_INPUT)

        for lbl, w in [("Quantidade", self.amount_edit), ("Data", self.date_edit)]:
            row = QHBoxLayout()
            l = QLabel(lbl); l.setStyleSheet(f"font-size:13px; color:{BROWN}; min-width:70px;")
            row.addWidget(l); row.addWidget(w)
            vbox.addLayout(row)

        self.confirm_btn = QPushButton("✓ Confirmar colheita")
        self.confirm_btn.setStyleSheet(STYLE_CONFIRM_BTN)
        self.confirm_btn.clicked.connect(self._confirmar)
        vbox.addWidget(self.confirm_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(STYLE_CANCEL_BTN)
        cancel_btn.clicked.connect(self.reject)
        vbox.addWidget(cancel_btn)

        self._mic_btn = mic_btn; self._icon = icon
        mic_btn.clicked.connect(self._gravar)

    def _select_plantio(self, plantio, btn_clicado):
        self._selected_culture = plantio["culture"]
        self._selected_area    = plantio.get("area", "")
        for b in self._cult_btns:
            if b != btn_clicado:
                b.setChecked(False)

    def _gravar(self):
        self._mic_btn.setEnabled(False)
        self._mic_btn.setStyleSheet(STYLE_MIC_BTN_REC.replace("28px","34px").replace("56px","72px"))
        self.status.setText("🎙️ Gravando… fale agora (12s)")
        self.status.setStyleSheet(STYLE_STATUS_REC)

        # ── VA3: contexto="colheita" → LLM entende sem precisar dizer "colhi"
        # Ex: "dez sacos de milho" → LLM já sabe que é colheita pelo contexto
        t = VoiceThread(duration=12, contexto="colheita")

        def done(r):
            self._mic_btn.setEnabled(True)
            self._mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE.replace("28px","34px").replace("56px","72px"))
            if self._icon: self._mic_btn.setIcon(self._icon); self._mic_btn.setIconSize(QSize(36,36))
            else: self._mic_btn.setText("🎤")
            transcricao = r.get("_transcricao","")
            self.status.setStyleSheet(STYLE_STATUS_OK)
            self.status.setText(f'✅ "{transcricao}"')
            if r.get("quantidade_original"): self.amount_edit.setText(r["quantidade_original"])
            if r.get("data"): self.date_edit.setText(r["data"])

        def err(msg):
            self._mic_btn.setEnabled(True)
            self._mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE.replace("28px","34px").replace("56px","72px"))
            if self._icon: self._mic_btn.setIcon(self._icon); self._mic_btn.setIconSize(QSize(36,36))
            else: self._mic_btn.setText("🎤")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            self.status.setText(f"❌ {msg}")

        t.finished.connect(done); t.error.connect(err); t.start()
        self._threads.append(t)

    def _confirmar(self):
        amount = self.amount_edit.text().strip()
        date   = self.date_edit.text().strip()

        # ── VA3: sem regex. O LLM já preencheu — só checa se não está vazio.
        if not amount:
            self.status.setText("❌ Fale a quantidade primeiro")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            return
        if not date:
            self.status.setText("❌ Data não preenchida. Fale novamente.")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            return
        self.resultado = {"culture": self._selected_culture, "area": self._selected_area, "amount": amount, "date": date}
        self.accept()

    def get_result(self): return self.resultado
# ── Diálogo: gasto por voz ───────────────────────────────────────────────────

class GastoDialog(QDialog):
    """
    O agricultor fala: 'gastei duzentos reais com adubo pro milho ontem'
    O LLM extrai tipo, valor, data e cultura.
    """
    def __init__(self, cultures: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AgroBook")
        self.setStyleSheet(STYLE_DIALOG)
        self.setFixedWidth(340)
        self.resultado = None
        self._threads = []

        vbox = QVBoxLayout(self)
        vbox.setSpacing(10)
        vbox.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Qual foi o gasto?")
        title.setStyleSheet(STYLE_TITLE)
        vbox.addWidget(title)

        sub = QLabel('Fale tudo: "gastei duzentos reais com adubo pro milho ontem"')
        sub.setStyleSheet(STYLE_SUB)
        sub.setWordWrap(True)
        vbox.addWidget(sub)

        # Microfone central
        mic_btn = QPushButton()
        mic_btn.setFixedSize(72, 72)
        mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE.replace("28px","34px").replace("56px","72px"))
        icon = _mic_icon()
        if icon: mic_btn.setIcon(icon); mic_btn.setIconSize(QSize(36,36))
        else: mic_btn.setText("🎤")
        mic_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        mic_row = QHBoxLayout()
        mic_row.addStretch(); mic_row.addWidget(mic_btn); mic_row.addStretch()
        vbox.addLayout(mic_row)

        self.status = QLabel("Clique no microfone e fale")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet(STYLE_STATUS_REC)
        self.status.setWordWrap(True)
        vbox.addWidget(self.status)

        # Campos de confirmação
        self.type_edit    = QLineEdit(); self.type_edit.setPlaceholderText("Tipo (ex: adubo, transporte)")
        self.type_edit.setStyleSheet(STYLE_INPUT)
        self.value_edit   = QLineEdit(); self.value_edit.setPlaceholderText("Valor (ex: 200 reais)")
        self.value_edit.setStyleSheet(STYLE_INPUT)
        self.date_edit    = QLineEdit(); self.date_edit.setPlaceholderText("Data (ex: hoje, ontem)")
        self.date_edit.setStyleSheet(STYLE_INPUT)
        self.culture_combo = QComboBox()
        self.culture_combo.addItems(["Geral"] + cultures)
        self.culture_combo.setStyleSheet(f"border:2px solid {BORDER}; border-radius:10px; padding:8px; font-size:14px; background:{WHITE};")

        for lbl, w in [("Tipo", self.type_edit), ("Valor", self.value_edit),
                        ("Data", self.date_edit), ("Cultura", self.culture_combo)]:
            row = QHBoxLayout()
            l = QLabel(lbl); l.setStyleSheet(f"font-size:13px; color:{BROWN}; min-width:55px;")
            row.addWidget(l); row.addWidget(w)
            vbox.addLayout(row)

        self.confirm_btn = QPushButton("✓ Confirmar gasto")
        self.confirm_btn.setStyleSheet(STYLE_CONFIRM_BTN)
        self.confirm_btn.clicked.connect(self._confirmar)
        vbox.addWidget(self.confirm_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(STYLE_CANCEL_BTN)
        cancel_btn.clicked.connect(self.reject)
        vbox.addWidget(cancel_btn)

        self._mic_btn = mic_btn; self._icon = icon
        mic_btn.clicked.connect(self._gravar)

    def _gravar(self):
        self._mic_btn.setEnabled(False)
        self._mic_btn.setStyleSheet(STYLE_MIC_BTN_REC.replace("28px","34px").replace("56px","72px"))
        self.status.setText("🎙️ Gravando… fale agora (12s)")
        self.status.setStyleSheet(STYLE_STATUS_REC)

        # ── VA3: contexto="gasto" → LLM entende sem precisar dizer "gastei"
        t = VoiceThread(duration=12, contexto="gasto")

        def done(r):
            self._mic_btn.setEnabled(True)
            self._mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE.replace("28px","34px").replace("56px","72px"))
            if self._icon: self._mic_btn.setIcon(self._icon); self._mic_btn.setIconSize(QSize(36,36))
            else: self._mic_btn.setText("🎤")
            transcricao = r.get("_transcricao","")
            self.status.setStyleSheet(STYLE_STATUS_OK)
            self.status.setText(f'✅ "{transcricao}"')
            if r.get("tipo") == "gasto":
                if r.get("descricao"): self.type_edit.setText(r["descricao"])
                if r.get("valor"):     self.value_edit.setText(r["valor"])
                if r.get("data"):      self.date_edit.setText(r["data"])
                if r.get("cultura"):
                    idx = self.culture_combo.findText(r["cultura"], Qt.MatchFlag.MatchContains)
                    if idx >= 0: self.culture_combo.setCurrentIndex(idx)
            else:
                self.status.setStyleSheet(STYLE_STATUS_ERR)
                self.status.setText("⚠️ Não identifiquei gasto. Corrija os campos.")

        def err(msg):
            self._mic_btn.setEnabled(True)
            self._mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE.replace("28px","34px").replace("56px","72px"))
            if self._icon: self._mic_btn.setIcon(self._icon); self._mic_btn.setIconSize(QSize(36,36))
            else: self._mic_btn.setText("🎤")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            self.status.setText(f"❌ {msg}")

        t.finished.connect(done); t.error.connect(err); t.start()
        self._threads.append(t)

    def _confirmar(self):
        _type   = self.type_edit.text().strip()
        value   = self.value_edit.text().strip()
        date    = self.date_edit.text().strip()
        culture = self.culture_combo.currentText()

        # ── VA3: sem regex. O LLM já preencheu — só checa se não está vazio.
        if not _type:
            self.status.setText("❌ Fale o gasto primeiro")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            return
        if not value:
            self.status.setText("❌ Valor não preenchido. Fale novamente.")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            return
        if not date:
            self.status.setText("❌ Data não preenchida. Fale novamente.")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            return
        self.resultado = {"type": _type, "value": value, "date": date, "culture": culture}
        self.accept()

    def get_result(self): return self.resultado


# ── Diálogo: coproprietário por voz ──────────────────────────────────────────

class CoOwnerDialog(QDialog):
    """
    Cadastro de coproprietário por voz — fala tudo de uma vez.
    Ex: "Maria Silva, CPF zero cinco zero sete dois dois zero sete quatro noventa e oito, herdeira, vinte e cinco por cento"
    """
    ROLES = ["Proprietário principal", "Coproprietário", "Herdeiro", "Meeiro", "Arrendatário"]

    def __init__(self, prefill=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AgroBook")
        self.setStyleSheet(STYLE_DIALOG)
        self.setFixedWidth(340)
        self.resultado = None
        self._threads = []
        self._selected_role = None
        self._icon = _mic_icon()

        vbox = QVBoxLayout(self)
        vbox.setSpacing(10)
        vbox.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Coproprietários e Herdeiros")
        title.setStyleSheet(STYLE_TITLE)
        title.setWordWrap(True)
        vbox.addWidget(title)

        sub = QLabel('Fale tudo de uma vez:\n"Maria Silva, CPF zero cinco zero... herdeira, vinte e cinco por cento"')
        sub.setStyleSheet(STYLE_SUB)
        sub.setWordWrap(True)
        vbox.addWidget(sub)

        # Microfone central
        mic_btn = QPushButton()
        mic_btn.setFixedSize(72, 72)
        mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE.replace("28px","34px").replace("56px","72px"))
        if self._icon:
            mic_btn.setIcon(self._icon)
            mic_btn.setIconSize(QSize(36, 36))
        mic_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        mic_btn.setToolTip("Clique e fale (12 segundos)")

        mic_row = QHBoxLayout()
        mic_row.addStretch(); mic_row.addWidget(mic_btn); mic_row.addStretch()
        vbox.addLayout(mic_row)

        self.status = QLabel("Clique no microfone e fale")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet(STYLE_STATUS_REC)
        self.status.setWordWrap(True)
        vbox.addWidget(self.status)

        sep = QLabel("Confirme os dados:")
        sep.setStyleSheet(f"font-size: 12px; color: {BROWN}; margin-top:4px;")
        vbox.addWidget(sep)

        # Campos de confirmação
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nome completo")
        self.name_edit.setStyleSheet(STYLE_INPUT)

        self.cpf_edit = QLineEdit()
        self.cpf_edit.setPlaceholderText("CPF (só números)")
        self.cpf_edit.setStyleSheet(STYLE_INPUT)

        for lbl, w in [("Nome", self.name_edit), ("CPF", self.cpf_edit)]:
            row = QHBoxLayout()
            l = QLabel(lbl); l.setStyleSheet(f"font-size:13px; color:{BROWN}; min-width:40px;")
            row.addWidget(l); row.addWidget(w)
            vbox.addLayout(row)

        # Vínculo — botões compactos em grid 2x3
        role_lbl = QLabel("Vínculo")
        role_lbl.setStyleSheet(f"font-size:13px; color:{BROWN}; font-weight:600;")
        vbox.addWidget(role_lbl)

        self._role_btns = []
        grid1 = QHBoxLayout()
        grid2 = QHBoxLayout()
        for i, role in enumerate(self.ROLES):
            btn = QPushButton(role)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFFFFF; color: #1E1E1E;
                    border: 1.5px solid {BORDER}; border-radius: 10px;
                    font-size: 12px; padding: 8px 4px;
                }}
                QPushButton:hover {{ background-color: #d6e8d8; border-color: {GREEN}; }}
                QPushButton:checked {{ background-color: {GREEN}; color: white; border-color: {GREEN}; }}
            """)
            btn.clicked.connect(lambda checked, r=role, b=btn: self._select_role(r, b))
            if i < 3:
                grid1.addWidget(btn)
            else:
                grid2.addWidget(btn)
            self._role_btns.append(btn)
        vbox.addLayout(grid1)
        vbox.addLayout(grid2)

        # % de participação opcional
        pct_lbl = QLabel("% participação (opcional)")
        pct_lbl.setStyleSheet(f"font-size:12px; color:{BROWN};")
        vbox.addWidget(pct_lbl)
        self.pct_edit = QLineEdit()
        self.pct_edit.setPlaceholderText("Ex: 25")
        self.pct_edit.setStyleSheet(STYLE_INPUT)
        vbox.addWidget(self.pct_edit)

        # Botões
        self.confirm_btn = QPushButton("→ Adicionar")
        self.confirm_btn.setStyleSheet(STYLE_CONFIRM_BTN)
        self.confirm_btn.clicked.connect(self._confirmar)
        vbox.addWidget(self.confirm_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(STYLE_CANCEL_BTN)
        cancel_btn.clicked.connect(self.reject)
        vbox.addWidget(cancel_btn)

        self._mic_btn = mic_btn
        mic_btn.clicked.connect(self._gravar)

        # Prefill se for edição
        if prefill:
            self.name_edit.setText(prefill[0] if len(prefill) > 0 else "")
            self.cpf_edit.setText(prefill[1] if len(prefill) > 1 else "")
            if len(prefill) > 2:
                for btn in self._role_btns:
                    if btn.text() == prefill[2]:
                        btn.setChecked(True)
                        self._selected_role = prefill[2]
            if len(prefill) > 3:
                self.pct_edit.setText(prefill[3] or "")

    def _select_role(self, role, btn_clicado):
        self._selected_role = role
        for b in self._role_btns:
            if b != btn_clicado:
                b.setChecked(False)

    def _gravar(self):
        self._mic_btn.setEnabled(False)
        self._mic_btn.setStyleSheet(STYLE_MIC_BTN_REC.replace("28px","34px").replace("56px","72px"))
        self.status.setText("🎙️ Gravando… fale agora (12s)")
        self.status.setStyleSheet(STYLE_STATUS_REC)

        t = VoiceThread(duration=12, contexto="coproprietario")

        def done(r):
            import re as _re
            self._mic_btn.setEnabled(True)
            self._mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE.replace("28px","34px").replace("56px","72px"))
            if self._icon:
                self._mic_btn.setIcon(self._icon)
                self._mic_btn.setIconSize(QSize(36, 36))
            transcricao = r.get("_transcricao", "")
            self.status.setStyleSheet(STYLE_STATUS_OK)
            self.status.setText(f'✅ "{transcricao}"')

            # Preenche nome — limpa pontuação do Whisper
            if r.get("nome"):
                nome = _re.sub(r"[^a-zA-ZÁ-ÿ ]", "", r["nome"]).strip()
                self.name_edit.setText(nome)
            # Preenche CPF — só dígitos
            if r.get("cpf") or r.get("valor"):
                cpf_raw = r.get("cpf") or r.get("valor") or ""
                self.cpf_edit.setText(_re.sub(r"\D", "", str(cpf_raw)))
            # Seleciona vínculo
            if r.get("vinculo"):
                vinculo = r["vinculo"].lower()
                for btn in self._role_btns:
                    if vinculo in btn.text().lower():
                        btn.setChecked(True)
                        self._selected_role = btn.text()
                    else:
                        btn.setChecked(False)
            # % participação
            if r.get("percentual") or r.get("pct"):
                self.pct_edit.setText(str(r.get("percentual") or r.get("pct") or ""))

        def err(msg):
            self._mic_btn.setEnabled(True)
            self._mic_btn.setStyleSheet(STYLE_MIC_BTN_IDLE.replace("28px","34px").replace("56px","72px"))
            if self._icon:
                self._mic_btn.setIcon(self._icon)
                self._mic_btn.setIconSize(QSize(36, 36))
            self.status.setText(f"❌ {msg}")
            self.status.setStyleSheet(STYLE_STATUS_ERR)

        t.finished.connect(done)
        t.error.connect(err)
        t.start()
        self._threads.append(t)

    def _confirmar(self):
        import re as _re
        from utils.validators import is_valid_cpf
        # Pega o texto do campo sem re.sub agressivo — o campo já foi limpo ao preencher
        nome_raw = self.name_edit.text()
        # Limpeza mínima: só remove caracteres que definitivamente não são letra
        nome = _re.sub(r"[^a-zA-ZÁ-ÿàáâãäåèéêëìíîïòóôõöùúûüýÿÀÁÂÃÄÅÈÉÊËÌÍÎÏÒÓÔÕÖÙÚÛÜÝ ]", "", nome_raw).strip()
        cpf  = _re.sub(r"\D", "", self.cpf_edit.text().strip())
        role = self._selected_role
        pct  = self.pct_edit.text().strip()

        if not nome or len(nome) < 2:
            self.status.setText("❌ Digite ou fale o nome primeiro")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            return
        if not cpf or not is_valid_cpf(cpf):
            self.status.setText("❌ CPF inválido. Verifique os 11 dígitos.")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            return
        if not role:
            self.status.setText("❌ Selecione o vínculo acima")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            return
        if pct and not (pct.replace(".","").replace(",","").isdigit()):
            self.status.setText("❌ % inválido")
            self.status.setStyleSheet(STYLE_STATUS_ERR)
            return

        self.resultado = [nome, cpf, role, pct]
        self.accept()

    def get_result(self):
        return self.resultado

# ── Classe Dialog (mantém compatibilidade com events.py) ─────────────────────

class Dialog:
    def __init__(self, parent=None):
        pass

    def error_dialog(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Erro")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def yes_or_no_dialog(self, message):
        r = QMessageBox.question(None, "Pergunta", message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes)
        return r == QMessageBox.StandardButton.Yes

    def coowner_dialog(self, prefill=None):
        """Diálogo de coproprietário com voz."""
        d = CoOwnerDialog(prefill=prefill)
        if not d.exec():
            return CANCELLED
        return d.get_result()

    def area_dialog(self, areas_existentes: list):
        """Diálogo de área com estilo Figma + microfone."""
        d = AreaDialog(areas_existentes)
        if not d.exec():
            return CANCELLED
        return d.get_result()

    def form_dialog(self, entries, validations, prefill=None):
        """Mantido para compatibilidade com outros usos no events.py."""
        dialog = QDialog()
        dialog.setWindowTitle("AgroBook")
        dialog.setStyleSheet(STYLE_DIALOG)
        form_layout = QFormLayout()
        lineedits = [QLineEdit() for _ in range(len(entries))]
        if prefill:
            for i, val in enumerate(prefill):
                if i < len(lineedits) and val:
                    lineedits[i].setText(str(val))
        for i, entry in enumerate(entries):
            lineedits[i].setStyleSheet(STYLE_INPUT)
            form_layout.addRow(entry, lineedits[i])
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        vbox = QVBoxLayout()
        vbox.addLayout(form_layout)
        vbox.addWidget(buttons)
        dialog.setLayout(vbox)
        if not dialog.exec():
            return CANCELLED
        result = []
        for i in range(len(entries)):
            if validations[i](lineedits[i].text()):
                result.append(lineedits[i].text())
            else:
                return None
        return result

    def planting_dialog(self, areas, prefill=None):
        """Plantio com voz."""
        d = PlantioDialog(areas)
        if prefill:
            d.culture_edit.setText(prefill.get("culture",""))
            d.amount_edit.setText(prefill.get("amount",""))
            d.date_edit.setText(prefill.get("date",""))
            idx = d.area_combo.findText(prefill.get("area",""))
            if idx >= 0: d.area_combo.setCurrentIndex(idx)
        if not d.exec():
            return CANCELLED
        return d.get_result()

    def harvest_dialog(self, cultures, prefill=None):
        """Colheita com voz."""
        d = ColheitaDialog(cultures)
        if prefill:
            d.amount_edit.setText(prefill.get("amount",""))
            d.date_edit.setText(prefill.get("date",""))
        if not d.exec():
            return CANCELLED
        return d.get_result()

    def expense_dialog(self, cultures, prefill=None):
        """Gasto com voz."""
        d = GastoDialog(cultures)
        if prefill:
            d.type_edit.setText(prefill.get("type",""))
            d.value_edit.setText(prefill.get("value",""))
            d.date_edit.setText(prefill.get("date",""))
            idx = d.culture_combo.findText(prefill.get("culture","Geral"))
            if idx >= 0: d.culture_combo.setCurrentIndex(idx)
        if not d.exec():
            return CANCELLED
        return d.get_result()

    # Mantidos para compatibilidade
    def voice_planting_dialog(self, areas): return self.planting_dialog(areas)
    def voice_harvest_dialog(self, cultures): return self.harvest_dialog(cultures)
    def voice_expense_dialog(self, cultures): return self.expense_dialog(cultures)