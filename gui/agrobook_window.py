from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6 import uic

from gui.events import Events
from model.farmer import *
from utils.sms_sender import SMSSender
from utils.validators import *

class AgroBookWindow(QMainWindow):
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

        """
        The farmer:
        """

        self.farmer = farmer

        """
        Creating the SMS object, to handle codes:
        """

        self.sms = SMSSender()

        """
        Screen for the beginning:
        """

        self.initial_screen = uic.loadUi("gui/InitialScreen.ui", None)

        """
        Screens for sign up:
        """

        self.phone_screen = uic.loadUi("gui/GetPhoneScreen.ui", None)
        self.sms_screen = uic.loadUi("gui/SMSScreen.ui", None)

        self.farmer_name_screen = uic.loadUi("gui/FarmerName.ui", None)
        self.farmer_cpf_screen = uic.loadUi("gui/FarmerCPF.ui", None)
        self.farmer_location_screen = uic.loadUi("gui/FarmerLocation.ui", None)

        """
        Screens for login:
        """

        self.home_screen = uic.loadUi("gui/HomeScreen.ui", None)
        self.my_data_screen = uic.loadUi("gui/MyData.ui", None)
        self.expenses_screen = uic.loadUi("gui/Expenses.ui", None)
        self.areas_screen = uic.loadUi("gui/Areas.ui", None)
        self.planting_screen = uic.loadUi("gui/Planting.ui", None)
        self.harvests_screen = uic.loadUi("gui/Harvests.ui", None)

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
        Initial adjustments:
        """

        self.stacked_widget.setCurrentIndex(0)

        self.farmer_location_screen.state_combobox.addItems(list_of_states)

        """
        Adding events:
        """

        self.events = Events(self)

        self.initial_screen.signup_button.clicked.connect(self.events.sign_up)
        self.initial_screen.login_button.clicked.connect(self.events.login)

        self.phone_screen.receive_code_button.clicked.connect(self.events.sign_up_receive_code)
        self.sms_screen.code_lineedit1.textChanged.connect(lambda: self.events.sign_up_code_next_lineedit(self.sms_screen.code_lineedit2))
        self.sms_screen.code_lineedit2.textChanged.connect(lambda: self.events.sign_up_code_next_lineedit(self.sms_screen.code_lineedit3))
        self.sms_screen.code_lineedit3.textChanged.connect(lambda: self.events.sign_up_code_next_lineedit(self.sms_screen.code_lineedit4))
        self.sms_screen.confirm_button.clicked.connect(self.events.sign_up_check_code)
        self.farmer_name_screen.next_button.clicked.connect(self.events.sign_up_get_name)
        self.farmer_cpf_screen.next_button.clicked.connect(self.events.sign_up_get_cpf)
        self.farmer_location_screen.next_button.clicked.connect(self.events.sign_up_get_location)

        self.home_screen.my_data_button.clicked.connect(self.events.my_data)
        self.home_screen.expenses_button.clicked.connect(self.events.expenses)
        self.home_screen.land_button.clicked.connect(self.events.areas)
        self.home_screen.planting_button.clicked.connect(self.events.planting)
        self.home_screen.harvest_button.clicked.connect(self.events.harvest)
        self.home_screen.report_button.clicked.connect(self.events.report)

        self.my_data_screen.done_button.clicked.connect(self.events.process_my_data)

        self.expenses_screen.done_button.clicked.connect(self.events.process_expenses)
        self.expenses_screen.new_expense_button.clicked.connect(self.events.new_expense)
        self.expenses_screen.delete_expense_button.clicked.connect(self.events.delete_expense)

        self.areas_screen.done_button.clicked.connect(self.events.process_areas)
        self.areas_screen.new_area_button.clicked.connect(self.events.new_area)
        self.areas_screen.delete_area_button.clicked.connect(self.events.delete_area)

        self.planting_screen.done_button.clicked.connect(self.events.process_planting)
        self.planting_screen.new_planting_button.clicked.connect(self.events.new_planting)
        self.planting_screen.delete_planting_button.clicked.connect(self.events.delete_planting)

        self.harvests_screen.done_button.clicked.connect(self.events.process_harvests)
        self.harvests_screen.new_harvest_button.clicked.connect(self.events.new_harvest)
        self.harvests_screen.delete_harvest_button.clicked.connect(self.events.delete_harvest)