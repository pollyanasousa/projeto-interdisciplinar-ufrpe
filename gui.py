from PyQt6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget
from PyQt6 import uic

import os
import json

from model.farmer import *
from sms_sender import SMSSender
from utils.validators import *

class Gui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AgroBook")
        self.setStyleSheet("background-color:#E9F2EA")
        self.setFixedSize(360, 640)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.initial_screen = uic.loadUi("InitialScreen.ui", None)
        self.phone_screen = uic.loadUi("GetPhoneScreen.ui", None)
        self.sms_screen = uic.loadUi("SMSScreen.ui", None)

        self.farmer_name_screen = uic.loadUi("FarmerName.ui", None)
        self.farmer_cpf_screen = uic.loadUi("FarmerCPF.ui", None)
        self.farmer_location_screen = uic.loadUi("FarmerLocation.ui", None)

        self.home_screen = uic.loadUi("HomeScreen.ui", None)

        self.stacked_widget.addWidget(self.initial_screen)
        self.stacked_widget.addWidget(self.phone_screen)
        self.stacked_widget.addWidget(self.sms_screen)
        self.stacked_widget.addWidget(self.farmer_name_screen)
        self.stacked_widget.addWidget(self.farmer_cpf_screen)
        self.stacked_widget.addWidget(self.farmer_location_screen)
        self.stacked_widget.addWidget(self.home_screen)

        self.stacked_widget.setCurrentIndex(0)

        self.initial_screen.signup_button.clicked.connect(self.sign_up)
        self.initial_screen.login_button.clicked.connect(self.login)

        self.phone_screen.receive_code_button.clicked.connect(self.receive_code)
        self.sms_screen.confirm_button.clicked.connect(self.next3)
        self.farmer_name_screen.next_button.clicked.connect(self.next4)
        self.farmer_cpf_screen.next_button.clicked.connect(self.next5)
        self.farmer_location_screen.next_button.clicked.connect(self.next6)

        self.home_screen.my_data_button.clicked.connect(self.my_data)
        self.home_screen.expenses_button.clicked.connect(self.expenses)
        self.home_screen.land_button.clicked.connect(self.areas)
        self.home_screen.planting_button.clicked.connect(self.planting)
        self.home_screen.harvest_button.clicked.connect(self.harvest)
        self.home_screen.report_button.clicked.connect(self.report)

        self.sms = SMSSender()

    def show_dialog(self, message):
        """
        It shows a dialog on the screen, whose message is passed as argument.
        """

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Erro")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        msg_box.exec()

    """
    Events for sign up:
    """

    def sign_up(self):
        self.stacked_widget.setCurrentIndex(1)

    def receive_code(self):
        if is_valid_phone(self.phone_screen.phone_lineedit.text()):
            self.sms.send(self.phone_screen.phone_lineedit.text())
            self.stacked_widget.setCurrentIndex(2)
        else:
            self.show_dialog("Telefone inválido!")

    def next3(self):
        user_entry = self.sms_screen.code_lineedit1.text() + self.sms_screen.code_lineedit2.text() + self.sms_screen.code_lineedit3.text() + self.sms_screen.code_lineedit4.text()

        if user_entry == self.sms.code:
            self.stacked_widget.setCurrentIndex(3)
        else:
            self.show_dialog("Código inválido!")

    def next4(self):
        if is_valid_name(self.farmer_name_screen.name_lineedit.text()):
            self.stacked_widget.setCurrentIndex(4)
        else:
            self.show_dialog("Nome inválido!")

    def next5(self):
        if is_valid_cpf(self.farmer_cpf_screen.cpf_lineedit.text()):
            self.stacked_widget.setCurrentIndex(5)
        else:
            self.show_dialog("CPF inválido!")

    def next6(self):
        if is_valid_town(self.farmer_location_screen.town_lineedit.text()):
            self.stacked_widget.setCurrentIndex(6)
        else:
            self.show_dialog("Cidade inválida!")


    """
    Events for login:
    """

    def login(self):
        self.stacked_widget.setCurrentIndex(6)

    def my_data(self):
        pass

    def expenses(self):
        pass

    def areas(self):
        pass

    def planting(self):
        pass

    def harvest(self):
        pass

    def report(self):
        pass
