from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6 import uic

from gui.events import Events
from model.farmer import *
from utils.sms_sender import SMSSender
from utils.validators import *


class AgroBookWindow(QMainWindow):
    def __init__(self, farmer):
        super().__init__()
        self.setWindowTitle("AgroBook")
        self.setStyleSheet("background-color:#E9F2EA")
        self.setFixedSize(360, 640)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.farmer = farmer
        self.sms = SMSSender()

        # ── Telas ──────────────────────────────────────────────────────────────
        # idx 0
        self.initial_screen = uic.loadUi("gui/InitialScreen.ui", None)
        # idx 1-5 — cadastro
        self.phone_screen           = uic.loadUi("gui/GetPhoneScreen.ui", None)
        self.sms_screen             = uic.loadUi("gui/SMSScreen.ui", None)
        self.farmer_name_screen     = uic.loadUi("gui/FarmerName.ui", None)
        self.farmer_cpf_screen      = uic.loadUi("gui/FarmerCPF.ui", None)
        self.farmer_location_screen = uic.loadUi("gui/FarmerLocation.ui", None)
        # idx 6 — home
        self.home_screen    = uic.loadUi("gui/HomeScreen.ui", None)   # 6
        # idx 7-13 — funcionalidades
        self.my_data_screen  = uic.loadUi("gui/MyData.ui", None)       # 7
        self.expenses_screen = uic.loadUi("gui/Expenses.ui", None)     # 8
        self.areas_screen    = uic.loadUi("gui/Areas.ui", None)        # 9
        self.planting_screen = uic.loadUi("gui/Planting.ui", None)    # 10
        self.harvests_screen = uic.loadUi("gui/Harvests.ui", None)    # 11
        self.coowners_screen = uic.loadUi("gui/CoOwners.ui", None)    # 12
        # idx 14-15 — cadastro obrigatório de área e coproprietários
        self.signup_areas_screen    = uic.loadUi("gui/SignupAreas.ui", None)    # 13
        self.signup_coowners_screen = uic.loadUi("gui/SignupCoOwners.ui", None) # 14

        # ── Stack ──────────────────────────────────────────────────────────────
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
            self.stacked_widget.addWidget(screen)

        self.stacked_widget.setCurrentIndex(0)

        # ── Ajustes iniciais ───────────────────────────────────────────────────
        self.farmer_location_screen.state_combobox.addItems(list_of_states)

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

        # Cadastro — áreas obrigatórias (idx 14)
        self.signup_areas_screen.new_area_button.clicked.connect(self.events.signup_new_area)
        self.signup_areas_screen.update_area_button.clicked.connect(self.events.signup_update_area)
        self.signup_areas_screen.delete_area_button.clicked.connect(self.events.signup_delete_area)
        self.signup_areas_screen.done_button.clicked.connect(self.events.signup_areas_done)

        # Cadastro — coproprietários (idx 15)
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

        # Plantio
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
