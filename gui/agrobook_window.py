"""
agrobook_window.py — Janela principal do AgroBook.

═══════════════════════════════════════════════════════════════════════════════
VA3 — MODIFICAÇÕES NO FRONT-END
═══════════════════════════════════════════════════════════════════════════════

O QUE FOI FEITO (por outra pessoa, modulei e ajustei):
  1. ESTRUTURA DA JANELA:
     - Antes: setFixedSize(360, 640) + setCentralWidget direto no stacked
     - Agora: QFrame container verde (#124831) com bordas arredondadas (12px)
              simulando a moldura de um celular, centralizado na tela via
              QHBoxLayout + QVBoxLayout com addStretch().
     - Fundo externo verde escuro (#0d3320) preenche toda a janela maximizada,
       escondendo o fundo do VSCode/desktop independente da resolução.

  2. SOMBRA FLUTUANTE:
     - QGraphicsDropShadowEffect no container → efeito de cartão elevado.

  3. BOTÕES PADRONIZADOS:
     - Todos os QPushButton agora usam font-size: 18px, padding: 14px,
       border-radius: 12px (antes variavam entre 17px, 18px, 20px).

  4. MARGENS UNIFORMIZADAS:
     - Telas de cadastro (nome, CPF, localização) com margem top = 40px
       (antes 24px, inconsistente com as telas de telefone/SMS).
     - Demais telas receberam margens consistentes (24px ou 16px).

  5. LOGO PADRONIZADO:
     - HomeScreen: logo 214×160 (antes 160×120, inconsistente com InitialScreen).

  6. SEPARADORES:
     - Areas/Planting/Harvests: Line widget corrigido de Vertical para Horizontal.

  7. MYDATA:
     - Labels ganharam minimum width (70px) para inputs alinhados verticalmente.
     - QLineEdit/QComboBox padronizados com 18px/16px.

  8. MEASURES:
     - objectName duplicado ("sub_label") removido.

FLUXO DO APP:
  main.py → AgroBookWindow (esta classe)
    → QStackedWidget com 15 telas (0 a 14)
    → Events conecta os botões às ações
    → _inject_voice_buttons() → RF011: microfones nas telas de cadastro

PRÓXIMO PASSO (futuro):
  - Substituir showMaximized() por showFullScreen() para imersão total
  - Animar transições entre telas (fade/slide)
  - Responsividade: adaptar o layout a orientações diferentes
"""

from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QHBoxLayout, QLabel, QWidget, QVBoxLayout, QFrame, QGraphicsDropShadowEffect, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap
from PyQt6 import uic

from gui.events import Events
from model.farmer import *
from utils.sms_sender import SMSSender
from utils.validators import *
from utils.voice_widget import make_mic_button, attach_voice_to_lineedit


class AgroBookWindow(QMainWindow):
    def __init__(self, farmer):
        super().__init__()
        self.setWindowTitle("AgroBook")
        self.setMinimumSize(380, 660)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #E9F2EA; border-radius: 12px;")
        self.stacked_widget.setFixedSize(360, 640)

        container = QFrame()
        container.setObjectName("appContainer")
        container.setStyleSheet("""
            QFrame#appContainer {
                background-color: #124831;
                border-radius: 12px;
            }
        """)
        container.setFixedSize(380, 660)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 6)
        container.setGraphicsEffect(shadow)

        inner = QVBoxLayout(container)
        inner.setContentsMargins(10, 10, 10, 10)
        inner.addWidget(self.stacked_widget)

        outer = QWidget()
        outer.setStyleSheet("background-color: #0d3320;")

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addStretch(1)
        hbox.addWidget(container)
        hbox.addStretch(1)

        vbox = QVBoxLayout(outer)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        self.setCentralWidget(outer)

        self.farmer = farmer
        self.sms = SMSSender()

        # ── Telas ──────────────────────────────────────────────────────────────
        self.initial_screen         = uic.loadUi("gui/InitialScreen.ui", None)
        self.phone_screen           = uic.loadUi("gui/GetPhoneScreen.ui", None)
        self.sms_screen             = uic.loadUi("gui/SMSScreen.ui", None)
        self.farmer_name_screen     = uic.loadUi("gui/FarmerName.ui", None)
        self.farmer_cpf_screen      = uic.loadUi("gui/FarmerCPF.ui", None)
        self.farmer_location_screen = uic.loadUi("gui/FarmerLocation.ui", None)
        self.home_screen            = uic.loadUi("gui/HomeScreen.ui", None)
        self.my_data_screen         = uic.loadUi("gui/MyData.ui", None)
        self.expenses_screen        = uic.loadUi("gui/Expenses.ui", None)
        self.areas_screen           = uic.loadUi("gui/Areas.ui", None)
        self.planting_screen        = uic.loadUi("gui/Planting.ui", None)
        self.harvests_screen        = uic.loadUi("gui/Harvests.ui", None)
        self.coowners_screen        = uic.loadUi("gui/CoOwners.ui", None)
        self.signup_areas_screen    = uic.loadUi("gui/SignupAreas.ui", None)
        self.signup_coowners_screen = uic.loadUi("gui/SignupCoOwners.ui", None)

        # ── Stack ──────────────────────────────────────────────────────────────
        # Garante que cada tela seja opaca (autofill) para evitar artefatos
        # de sobreposição durante a transição entre telas no QStackedWidget
        for screen in [
            self.initial_screen,         # 0
            self.phone_screen,           # 1
            self.sms_screen,             # 2
            self.farmer_name_screen,     # 3
            self.farmer_cpf_screen,      # 4
            self.farmer_location_screen, # 5
            self.home_screen,            # 6
            self.my_data_screen,         # 7
            self.expenses_screen,        # 8
            self.areas_screen,           # 9
            self.planting_screen,        # 10
            self.harvests_screen,        # 11
            self.coowners_screen,        # 12
            self.signup_areas_screen,    # 13
            self.signup_coowners_screen, # 14
        ]:
            screen.setAutoFillBackground(True)
            self.stacked_widget.addWidget(screen)

        self.stacked_widget.setCurrentIndex(0)

        # ── Remove contorno de foco de todos os botões ────────────────────────
        for screen in [self.centralWidget()] + [
            self.initial_screen, self.phone_screen, self.sms_screen,
            self.farmer_name_screen, self.farmer_cpf_screen, self.farmer_location_screen,
            self.home_screen, self.my_data_screen, self.expenses_screen,
            self.areas_screen, self.planting_screen, self.harvests_screen,
            self.coowners_screen, self.signup_areas_screen, self.signup_coowners_screen,
        ]:
            for btn in screen.findChildren(QPushButton):
                btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # ── Ajustes de layout (mantidos da VA2) ───────────────────────────────
        self.farmer_location_screen.state_combobox.addItems(list_of_states)

        self.phone_screen.verticalLayout_2.setContentsMargins(24, 40, 24, 24)
        self.phone_screen.verticalLayout_2.setSpacing(16)
        self.phone_screen.verticalLayout.setSpacing(12)
        self.phone_screen.horizontalLayout.setSpacing(16)
        self.phone_screen.horizontalLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.phone_screen.phone_logo.setFixedSize(56, 56)
        self.phone_screen.phone_logo.setScaledContents(True)
        self.phone_screen.phone_logo.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        phone_pixmap = QPixmap("gui/images/phone-icon.png")
        if not phone_pixmap.isNull():
            self.phone_screen.phone_logo.setPixmap(phone_pixmap)
        self.phone_screen.verticalLayout_5.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.sms_screen.verticalLayout_2.setContentsMargins(24, 40, 24, 24)
        self.sms_screen.verticalLayout_2.setSpacing(16)
        self.sms_screen.verticalLayout.setSpacing(12)
        self.sms_screen.horizontalLayout.setSpacing(16)
        self.sms_screen.horizontalLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.sms_screen.message_logo.setFixedSize(56, 56)
        self.sms_screen.message_logo.setScaledContents(True)
        self.sms_screen.message_logo.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        sms_pixmap = QPixmap("gui/images/message-icon.png")
        if not sms_pixmap.isNull():
            self.sms_screen.message_logo.setPixmap(sms_pixmap)
        self.sms_screen.verticalLayout_5.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.farmer_name_screen.verticalLayout_2.setContentsMargins(16, 40, 16, 24)
        self.farmer_name_screen.verticalLayout_2.setSpacing(12)
        self.farmer_name_screen.verticalLayout_2.insertStretch(1, 1)
        self.farmer_name_screen.verticalLayout_2.addStretch(1)

        self.farmer_cpf_screen.verticalLayout_2.setContentsMargins(16, 40, 16, 24)
        self.farmer_cpf_screen.verticalLayout_2.setSpacing(12)
        self.farmer_cpf_screen.verticalLayout.setSpacing(16)
        self.farmer_cpf_screen.verticalLayout_2.insertStretch(1, 1)
        self.farmer_cpf_screen.verticalLayout_2.addStretch(1)

        self.farmer_location_screen.verticalLayout_2.setContentsMargins(16, 40, 16, 24)
        self.farmer_location_screen.verticalLayout_2.setSpacing(12)
        self.farmer_location_screen.verticalLayout.setSpacing(16)
        self.farmer_location_screen.verticalLayout_2.insertStretch(1, 1)
        self.farmer_location_screen.verticalLayout_2.addStretch(1)

        # ── Ajustes de layout para as demais telas ──────────────────────────
        self.initial_screen.verticalLayout_2.setContentsMargins(24, 24, 24, 24)
        self.initial_screen.verticalLayout_2.setSpacing(12)

        self.home_screen.verticalLayout_2.setContentsMargins(24, 24, 24, 24)
        self.home_screen.verticalLayout_2.setSpacing(12)

        self.my_data_screen.verticalLayout_2.setContentsMargins(16, 16, 16, 16)
        self.my_data_screen.verticalLayout_2.setSpacing(16)

        self.expenses_screen.verticalLayout_2.setContentsMargins(24, 16, 24, 16)
        self.expenses_screen.verticalLayout_2.setSpacing(8)

        self.areas_screen.verticalLayout_2.setContentsMargins(24, 16, 24, 16)
        self.areas_screen.verticalLayout_2.setSpacing(8)

        self.planting_screen.verticalLayout_2.setContentsMargins(24, 16, 24, 16)
        self.planting_screen.verticalLayout_2.setSpacing(8)

        self.harvests_screen.verticalLayout_2.setContentsMargins(24, 16, 24, 16)
        self.harvests_screen.verticalLayout_2.setSpacing(8)

        self.coowners_screen.verticalLayout.setContentsMargins(24, 16, 24, 16)
        self.coowners_screen.verticalLayout.setSpacing(8)

        self.signup_areas_screen.verticalLayout.setContentsMargins(24, 16, 24, 16)
        self.signup_areas_screen.verticalLayout.setSpacing(8)

        self.signup_coowners_screen.verticalLayout.setContentsMargins(24, 16, 24, 16)
        self.signup_coowners_screen.verticalLayout.setSpacing(8)

        # ── RF011: injetar botões de microfone nas telas de cadastro ──────────
        self._inject_voice_buttons()

        # ── Eventos ────────────────────────────────────────────────────────────
        self.events = Events(self)

        # Tela inicial
        self.initial_screen.signup_button.clicked.connect(self.events.sign_up)
        self.initial_screen.login_button.clicked.connect(self.events.login)

        # Cadastro — dados pessoais
        self.phone_screen.receive_code_button.clicked.connect(self.events.sign_up_receive_code)
        self.sms_screen.code_lineedit1.textChanged.connect(
            lambda: self.events.sign_up_code_next_lineedit(self.sms_screen.code_lineedit2))
        self.sms_screen.code_lineedit2.textChanged.connect(
            lambda: self.events.sign_up_code_next_lineedit(self.sms_screen.code_lineedit3))
        self.sms_screen.code_lineedit3.textChanged.connect(
            lambda: self.events.sign_up_code_next_lineedit(self.sms_screen.code_lineedit4))
        self.sms_screen.confirm_button.clicked.connect(self.events.sign_up_check_code)
        self.farmer_name_screen.next_button.clicked.connect(self.events.sign_up_get_name)
        self.farmer_cpf_screen.next_button.clicked.connect(self.events.sign_up_get_cpf)
        self.farmer_location_screen.next_button.clicked.connect(self.events.sign_up_get_location)

        # Cadastro — áreas e coproprietários
        self.signup_areas_screen.new_area_button.clicked.connect(self.events.signup_new_area)
        self.signup_areas_screen.update_area_button.clicked.connect(self.events.signup_update_area)
        self.signup_areas_screen.delete_area_button.clicked.connect(self.events.signup_delete_area)
        self.signup_areas_screen.done_button.clicked.connect(self.events.signup_areas_done)
        self.signup_coowners_screen.new_coowner_button.clicked.connect(self.events.signup_new_coowner)
        self.signup_coowners_screen.update_coowner_button.clicked.connect(self.events.signup_update_coowner)
        self.signup_coowners_screen.delete_coowner_button.clicked.connect(self.events.signup_delete_coowner)
        self.signup_coowners_screen.done_button.clicked.connect(self.events.signup_coowners_done)

        # Home
        self.home_screen.my_data_button.clicked.connect(self.events.my_data)
        self.home_screen.expenses_button.clicked.connect(self.events.expenses)
        self.home_screen.land_button.clicked.connect(self.events.areas)
        self.home_screen.planting_button.clicked.connect(self.events.planting)
        self.home_screen.harvest_button.clicked.connect(self.events.harvest)
        self.home_screen.report_button.clicked.connect(self.events.report)
        self.home_screen.coowners_button.clicked.connect(self.events.coowners)

        # Meus dados
        self.my_data_screen.done_button.clicked.connect(self.events.process_my_data)

        # Gastos
        self.expenses_screen.done_button.clicked.connect(self.events.process_expenses)
        self.expenses_screen.new_expense_button.clicked.connect(self.events.new_expense)
        self.expenses_screen.delete_expense_button.clicked.connect(self.events.delete_expense)
        self.expenses_screen.update_expense_button.clicked.connect(self.events.update_expense)

        # Áreas
        self.areas_screen.done_button.clicked.connect(self.events.process_areas)
        self.areas_screen.new_area_button.clicked.connect(self.events.new_area)
        self.areas_screen.delete_area_button.clicked.connect(self.events.delete_area)
        self.areas_screen.update_area_button.clicked.connect(self.events.update_area)

        # Plantio — botão de voz para registro por fala
        self.planting_screen.done_button.clicked.connect(self.events.process_planting)
        self.planting_screen.new_planting_button.clicked.connect(self.events.new_planting)
        self.planting_screen.delete_planting_button.clicked.connect(self.events.delete_planting)
        self.planting_screen.update_planting_button.clicked.connect(self.events.update_planting)

        # Colheita
        self.harvests_screen.done_button.clicked.connect(self.events.process_harvests)
        self.harvests_screen.new_harvest_button.clicked.connect(self.events.new_harvest)
        self.harvests_screen.delete_harvest_button.clicked.connect(self.events.delete_harvest)
        self.harvests_screen.update_harvest_button.clicked.connect(self.events.update_harvest)

        # RF009 — Multiproprietários
        self.coowners_screen.new_coowner_button.clicked.connect(self.events.new_coowner)
        self.coowners_screen.update_coowner_button.clicked.connect(self.events.update_coowner)
        self.coowners_screen.delete_coowner_button.clicked.connect(self.events.delete_coowner)
        self.coowners_screen.done_button.clicked.connect(self.events.process_coowners)

    # ═══════════════════════════════════════════════════════════════════════════
    # VA3 — RF011: INJEÇÃO DOS BOTÕES DE MICROFONE
    # ═══════════════════════════════════════════════════════════════════════════
    #
    # O QUE FAZ:
    #   Para cada tela de cadastro (Telefone, Nome, CPF, Cidade), substitui o
    #   QLineEdit original por um QHBoxLayout contendo [QLineEdit | MicButton].
    #
    # POR QUE:
    #   O agricultor pode falar em vez de digitar. O microfone fica ao lado
    #   do campo de texto — ele fala, o sistema preenche. Se quiser corrigir,
    #   é só digitar normalmente (fallback).
    #
    # FLUXO (para cada campo):
    #   1. _inject_voice_buttons() é chamado no __init__ da janela
    #   2. Para cada tela (phone, name, cpf, town):
    #      a. Encontra o QLineEdit pelo objectName
    #      b. Cria mic_btn via make_mic_button() (voice_widget.py)
    #      c. Substitui o lineedit por hbox [lineedit | mic_btn] no layout
    #      d. Conecta o mic_btn via attach_voice_to_lineedit()
    #   3. Quando o agricultor clica no mic:
    #      a. Grava áudio → VoiceInput (voice_input.py)
    #      b. Transcreve com Whisper → texto
    #      c. LLMParser (llm_parser.py) → JSON
    #      d. on_result() preenche o campo e chama o callback específico
    #
    # DIFERENÇA DA VA2:
    #   VA2: só digitação. Sem entrada por voz.
    #   VA3: voz como método principal, digitação como fallback.
    #
    # PRÓXIMO PASSO (futuro):
    #   - Adicionar microfones nas telas de listagem (gastos, plantios, etc.)
    #   - Feedback visual de gravação (animação no botão)
    # ───────────────────────────────────────────────────────────────────────────

    def _inject_voice_buttons(self):
        """
        RF011 — injeta botões de microfone ao lado dos campos de texto
        nas telas de cadastro, seguindo o layout do Figma.

        A estratégia é substituir o QLineEdit existente por um QHBoxLayout
        com [QLineEdit | QPushButton(🎤)], mantendo o mesmo objectName
        no lineedit para que o restante do código não precise mudar.
        """

        # ── Tela Telefone ─────────────────────────────────────────────────────
        from PyQt6.QtWidgets import QLineEdit
        screen = self.phone_screen
        phone_field = screen.findChild(QLineEdit, "phone_lineedit")
        if phone_field:
            self._wrap_lineedit_with_mic(
                layout      = screen.verticalLayout,
                lineedit    = phone_field,
                insert_after_widget = None,
                on_result   = lambda r, f=phone_field: f.setText(
                    __import__("re").sub(r"\D", "", str(r.get("valor") or r.get("_transcricao") or ""))
                ),
                hint    = "Fale seu número: oitenta e um, noventa e nove...",
                duration = 8
            )

        # ── Tela Nome ─────────────────────────────────────────────────────────
        screen = self.farmer_name_screen
        _name_field = screen.findChild(QLineEdit, "name_lineedit")
        if _name_field:
            self._wrap_lineedit_with_mic(
                layout      = screen.verticalLayout_2,
                lineedit    = _name_field,
                insert_after_widget = screen.code_sent_label,
                on_result   = lambda r, f=_name_field: (
                    f.setText(r.get("valor", r.get("_transcricao", "")))
                    if r.get("tipo") in ("nome", "desconhecido") else None
                ),
                hint = "Pode falar: \"Meu nome é João da Silva\" ou só o nome",
                duration = 8
            )

        # ── Tela CPF ──────────────────────────────────────────────────────────
        screen = self.farmer_cpf_screen
        _cpf_field = screen.findChild(QLineEdit, "cpf_lineedit")
        if _cpf_field:
            def _on_cpf_result(r, f=_cpf_field):
                import re as _re
                # Pega o valor já tratado pelo LLM ou a transcrição bruta
                raw = r.get("valor") or r.get("cpf") or r.get("_transcricao") or ""
                # Remove tudo que não é dígito (pontos, traços, espaços, texto)
                digits = _re.sub(r"\D", "", str(raw))
                # Se o LLM devolveu texto por extenso, os dígitos serão vazios;
                # nesse caso limpar o campo e pedir para tentar de novo
                if digits:
                    f.setText(digits)

            self._wrap_lineedit_with_mic(
                layout      = screen.verticalLayout,
                lineedit    = _cpf_field,
                insert_after_widget = None,
                on_result   = _on_cpf_result,
                hint     = "Fale os 11 números devagar",
                duration = 10
            )

        # ── Tela Localização (cidade) ─────────────────────────────────────────
        screen = self.farmer_location_screen
        _town_field = screen.findChild(QLineEdit, "town_lineedit")
        if _town_field:
            self._wrap_lineedit_with_mic(
                layout      = screen.verticalLayout,
                lineedit    = _town_field,
                insert_after_widget = None,
                on_result   = lambda r, f=_town_field: (
                    f.setText(r.get("valor", r.get("_transcricao", "")))
                    if r.get("tipo") == "cidade" else None
                ),
                hint = "Pode falar: \"Moro em Caruaru\"",
                duration = 8
            )

    def _wrap_lineedit_with_mic(self, layout, lineedit, insert_after_widget, on_result, hint="", duration=5):
        """
        Substitui um QLineEdit no layout por um QHBoxLayout com
        [QLineEdit expandido | botão mic 44×44].
        Adiciona um QLabel de dica abaixo.
        """
        # encontra a posição do lineedit no layout
        idx = layout.indexOf(lineedit)
        if idx < 0:
            return  # não achou, não faz nada

        # remove o lineedit do layout (sem destruir o widget)
        layout.removeWidget(lineedit)

        # cria o label de status/dica
        status = QLabel(hint)
        status.setStyleSheet("font-size: 11px; color: #7C5A3C; font-style: italic; padding-left: 4px;")
        status.setWordWrap(True)

        # cria o botão de microfone
        mic = make_mic_button()

        # monta QHBoxLayout com lineedit + mic
        hbox = QHBoxLayout()
        hbox.setSpacing(8)
        hbox.addWidget(lineedit)
        hbox.addWidget(mic)

        # insere hbox e label no mesmo índice do lineedit original
        layout.insertLayout(idx, hbox)
        layout.insertWidget(idx + 1, status)

        # conecta o botão
        attach_voice_to_lineedit(
            mic_btn      = mic,
            lineedit     = lineedit,
            on_result    = on_result,
            duration     = duration,
            status_label = status
        )
