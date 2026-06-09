from PyQt6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget
from PyQt6 import uic

from model.farmer import *
from sms_sender import SMSSender
from utils.validators import *

class Gui(QMainWindow):
    def __init__(self, farmer):
        """
        It represents the GUI. The argument farmer is an object of the class Farmer.
        """

        super().__init__()
        self.setWindowTitle("AgroBook")
        self.setStyleSheet("background-color:#E9F2EA")
        self.setFixedSize(360, 640)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.initial_screen = uic.loadUi("InitialScreen.ui", None)

        """
        Screens for sign up:
        """

        self.phone_screen = uic.loadUi("GetPhoneScreen.ui", None)
        self.sms_screen = uic.loadUi("SMSScreen.ui", None)

        self.farmer_name_screen = uic.loadUi("FarmerName.ui", None)
        self.farmer_cpf_screen = uic.loadUi("FarmerCPF.ui", None)
        self.farmer_location_screen = uic.loadUi("FarmerLocation.ui", None)

        """
        Screens for login:
        """

        self.home_screen = uic.loadUi("HomeScreen.ui", None)
        self.my_data_screen = uic.loadUi("MyData.ui", None)
        self.expenses_screen = uic.loadUi("Expenses.ui", None)
        self.areas_screen = uic.loadUi("Areas.ui", None)
        self.planting_screen = uic.loadUi("Planting.ui", None)
        self.harvests_screen = uic.loadUi("Harvests.ui", None)

        """
        Adding screens on self.stacked_widget:
        """

        self.stacked_widget.addWidget(self.initial_screen)
        self.stacked_widget.addWidget(self.phone_screen)
        self.stacked_widget.addWidget(self.sms_screen)
        self.stacked_widget.addWidget(self.farmer_name_screen)
        self.stacked_widget.addWidget(self.farmer_cpf_screen)
        self.stacked_widget.addWidget(self.farmer_location_screen)
        self.stacked_widget.addWidget(self.home_screen)
        self.stacked_widget.addWidget(self.my_data_screen)
        self.stacked_widget.addWidget(self.expenses_screen)
        self.stacked_widget.addWidget(self.areas_screen)
        self.stacked_widget.addWidget(self.planting_screen)
        self.stacked_widget.addWidget(self.harvests_screen)

        """
        Setting initial screen as current index:
        """

        self.stacked_widget.setCurrentIndex(0)

        """
        Adding events:
        """

        self.initial_screen.signup_button.clicked.connect(self.sign_up)
        self.initial_screen.login_button.clicked.connect(self.login)

        self.phone_screen.receive_code_button.clicked.connect(self.sign_up_receive_code)
        self.sms_screen.confirm_button.clicked.connect(self.sign_up_check_code)
        self.farmer_name_screen.next_button.clicked.connect(self.sign_up_get_name)
        self.farmer_cpf_screen.next_button.clicked.connect(self.sign_up_get_cpf)
        self.farmer_location_screen.next_button.clicked.connect(self.sign_up_get_location)

        self.home_screen.my_data_button.clicked.connect(self.my_data)
        self.home_screen.expenses_button.clicked.connect(self.expenses)
        self.home_screen.land_button.clicked.connect(self.areas)
        self.home_screen.planting_button.clicked.connect(self.planting)
        self.home_screen.harvest_button.clicked.connect(self.harvest)
        self.home_screen.report_button.clicked.connect(self.report)

        self.my_data_screen.done_button.clicked.connect(self.process_my_data)
        self.expenses_screen.done_button.clicked.connect(self.process_expenses)
        self.areas_screen.done_button.clicked.connect(self.process_areas)
        self.planting_screen.done_button.clicked.connect(self.process_planting)
        self.harvests_screen.done_button.clicked.connect(self.process_harvests)

        """
        The farmer:
        """

        self.farmer = farmer

        """
        Creating the SMS object, to handle codes:
        """

        self.sms = SMSSender()

    """
    Functions that deal with PyQt modals:
    """

    def show_error_dialog(self, message):
        """
        It shows an error dialog on the screen, whose message is passed as argument.
        """

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Erro")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        msg_box.exec()

    def ask_dialog(self, message):
        """
        It shows a dialog on the screen, asking a "yes" or "no" question, whose content is passed
        as argument.

        It returns True if the user answered "yes" and False otherwise.
        """

        msg_box = QMessageBox.question(
            self,
            "Pergunta",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        return msg_box == QMessageBox.StandardButton.Yes

    """
    Events for sign up:
    """

    def sign_up(self):
        self.stacked_widget.setCurrentIndex(1)

    def sign_up_receive_code(self):
        if is_valid_phone(self.phone_screen.phone_lineedit.text()):
            phone = self.phone_screen.phone_lineedit.text()

            self.sms.send(phone)
            self.farmer.phone_number = phone
            self.stacked_widget.setCurrentIndex(2)
        else:
            self.show_error_dialog("Telefone inválido!")

    def sign_up_check_code(self):
        user_entry = self.sms_screen.code_lineedit1.text() + self.sms_screen.code_lineedit2.text() + self.sms_screen.code_lineedit3.text() + self.sms_screen.code_lineedit4.text()

        if user_entry == self.sms.code:
            self.stacked_widget.setCurrentIndex(3)
        else:
            self.show_error_dialog("Código inválido!")

    def sign_up_get_name(self):
        if is_valid_name(self.farmer_name_screen.name_lineedit.text()):
            name = self.farmer_name_screen.name_lineedit.text()

            self.farmer.name = name
            self.stacked_widget.setCurrentIndex(4)
        else:
            self.show_error_dialog("Nome inválido!")

    def sign_up_get_cpf(self):
        if is_valid_cpf(self.farmer_cpf_screen.cpf_lineedit.text()):
            cpf = self.farmer_cpf_screen.cpf_lineedit.text()

            self.farmer.cpf = cpf
            self.stacked_widget.setCurrentIndex(5)
        else:
            self.show_error_dialog("CPF inválido!")

    def sign_up_get_location(self):
        if is_valid_town(self.farmer_location_screen.town_lineedit.text()):
            town = self.farmer_location_screen.town_lineedit.text()
            self.farmer.town = town

            self.farmer.save() # This is important: all data need to be stored on the JSON files.

            self.stacked_widget.setCurrentIndex(6)
        else:
            self.show_error_dialog("Cidade inválida!")


    """
    Events for login:
    """

    def login(self):
        self.stacked_widget.setCurrentIndex(6)

    def my_data(self):
        self.my_data_screen.name_lineedit.setText(self.farmer.name)
        self.my_data_screen.cpf_lineedit.setText(self.farmer.cpf)
        self.my_data_screen.phone_lineedit.setText(self.farmer.phone_number)
        self.my_data_screen.town_lineedit.setText(self.farmer.town)

        self.stacked_widget.setCurrentIndex(7)

    def expenses(self):
        for _id, expense in enumerate(self.farmer.expense.list_of_expenses):
            self.expenses_screen.expense_listwidget.addItem(expense)

        self.stacked_widget.setCurrentIndex(8)

    def areas(self):
        for _id, area in enumerate(self.farmer.area.list_of_area):
            self.areas_screen.area_listwidget.addItem(area)

        self.stacked_widget.setCurrentIndex(9)

    def planting(self):
        for _id, planting in enumerate(self.farmer.planting.list_of_planting):
            self.planting_screen.planting_listwidget.addItem(planting)

        self.stacked_widget.setCurrentIndex(10)

    def harvest(self):
        for _id, harvest in enumerate(self.farmer.harvest.list_of_harvest):
            self.harvests_screen.harvest_listwidget.addItem(harvest)

        self.stacked_widget.setCurrentIndex(11)

    def report(self):
        if self.farmer.report.gen_report() != 0:
            self.show_error_dialog("Erro: não foi possível gerar o relatório!")

        if self.ask_dialog("Relatório gerado com sucesso! Deseja abri-lo no navegador?"):
            self.farmer.report.open_report()

    def process_my_data(self):
        self.farmer.name = self.my_data_screen.name_lineedit.text()
        self.farmer.cpf = self.my_data_screen.cpf_lineedit.text()
        self.farmer.phone = self.my_data_screen.phone_lineedit.text()
        self.farmer.town = self.my_data_screen.town_lineedit.text()

        self.farmer.save()

        self.stacked_widget.setCurrentIndex(6)

    def process_expenses(self):
        self.stacked_widget.setCurrentIndex(6)

    def process_areas(self):
        self.stacked_widget.setCurrentIndex(6)
    
    def process_planting(self):
        self.stacked_widget.setCurrentIndex(6)

    def process_harvests(self):
        self.stacked_widget.setCurrentIndex(6)
