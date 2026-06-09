from gui.dialog import Dialog
from utils.validators import *


class Events:
    def __init__(self, window):
        """
        The events class. The argument is the window.
        """

        self.window = window

        """
        Creating the dialog object, to show dialogs on the screen:
        """
        
        self.dialog = Dialog()

    """
    Events for sign up:
    """

    def sign_up(self):
        self.window.stacked_widget.setCurrentIndex(1)

    def sign_up_receive_code(self):
        if is_valid_phone(self.window.phone_screen.phone_lineedit.text()):
            phone = self.window.phone_screen.phone_lineedit.text()

            self.window.sms.send(phone)
            self.window.farmer.phone_number = phone
            self.window.stacked_widget.setCurrentIndex(2)
        else:
            self.dialog.error_dialog("Telefone inválido!")

    def sign_up_code_next_lineedit(self, lineedit):
        lineedit.setFocus()

    def sign_up_check_code(self):
        user_entry = self.window.sms_screen.code_lineedit1.text() + self.window.sms_screen.code_lineedit2.text() + self.window.sms_screen.code_lineedit3.text() + self.window.sms_screen.code_lineedit4.text()

        if user_entry == self.window.sms.code:
            self.window.stacked_widget.setCurrentIndex(3)
        else:
            self.dialog.error_dialog("Código inválido!")

    def sign_up_get_name(self):
        if is_valid_name(self.window.farmer_name_screen.name_lineedit.text()):
            name = self.window.farmer_name_screen.name_lineedit.text()

            self.window.farmer.name = name
            self.window.stacked_widget.setCurrentIndex(4)
        else:
            self.dialog.error_dialog("Nome inválido!")

    def sign_up_get_cpf(self):
        if is_valid_cpf(self.window.farmer_cpf_screen.cpf_lineedit.text()):
            cpf = self.window.farmer_cpf_screen.cpf_lineedit.text()

            self.window.farmer.cpf = cpf
            self.window.stacked_widget.setCurrentIndex(5)
        else:
            self.dialog.error_dialog("CPF inválido!")

    def sign_up_get_location(self):
        if is_valid_town(self.window.farmer_location_screen.town_lineedit.text()):
            town = self.window.farmer_location_screen.town_lineedit.text()
            self.window.farmer.town = town
            self.window.farmer.state = self.window.farmer_location_screen.state_combobox.currentText()

            self.window.farmer.save() # This is important: all data need to be stored on the JSON files.

            self.window.stacked_widget.setCurrentIndex(6)
        else:
            self.dialog.error_dialog("Cidade inválida!")


    """
    Events for login:
    """

    def login(self):
        self.window.stacked_widget.setCurrentIndex(6)

    def my_data(self):
        self.window.my_data_screen.name_lineedit.setText(self.window.farmer.name)
        self.window.my_data_screen.cpf_lineedit.setText(self.window.farmer.cpf)
        self.window.my_data_screen.phone_lineedit.setText(self.window.farmer.phone_number)
        self.window.my_data_screen.town_lineedit.setText(self.window.farmer.town)
        self.window.my_data_screen.state_combobox.addItems(list_of_states)

        self.window.stacked_widget.setCurrentIndex(7)

    def expenses(self):
        for _id, expense in enumerate(self.window.farmer.expense.list_of_expenses):
            self.window.expenses_screen.expense_listwidget.addItem(expense)

        self.window.stacked_widget.setCurrentIndex(8)

    def areas(self):
        for _id, area in enumerate(self.window.farmer.area.list_of_area):
            text = f"area{'name'}"
            self.window.areas_screen.area_listwidget.addItem(text)

        self.window.stacked_widget.setCurrentIndex(9)

    def planting(self):
        for _id, planting in enumerate(self.window.farmer.planting.list_of_planting):
            text = f"planting{'culture'} | planting{'amount'} | planting{'date'}"
            self.window.planting_screen.planting_listwidget.addItem(text)

        self.window.stacked_widget.setCurrentIndex(10)

    def harvest(self):
        for _id, harvest in enumerate(self.window.farmer.harvest.list_of_harvest):
            text = f"harvest{'culture'} | harvest{'amount'} | harvest{'date'}"
            self.window.harvests_screen.harvest_listwidget.addItem(text)

        self.window.stacked_widget.setCurrentIndex(11)

    def report(self):
        if self.window.farmer.report.gen_report() != 0:
            self.dialog.error_dialog("Erro: não foi possível gerar o relatório!")

        if self.dialog.yes_or_no_dialog("Relatório gerado com sucesso! Deseja abri-lo no navegador?"):
            self.window.farmer.report.open_report()

    def process_my_data(self):
        self.window.farmer.name = self.window.my_data_screen.name_lineedit.text()
        self.window.farmer.cpf = self.window.my_data_screen.cpf_lineedit.text()
        self.window.farmer.phone = self.window.my_data_screen.phone_lineedit.text()
        self.window.farmer.town = self.window.my_data_screen.town_lineedit.text()

        self.window.farmer.save()

        self.window.stacked_widget.setCurrentIndex(6)

    def process_expenses(self):
        self.window.stacked_widget.setCurrentIndex(6)

    def new_expense(self):
        data = self.dialog.form_dialog(["Tipo de gasto (exemplo: adubo, transporte, mão de obra)", "Valor do gasto (exemplo: 100 reais)", "Data do gasto"], [is_valid_name, is_valid_name, is_valid_date])

        text = f"Gasto: {data[0]} | Valor: {data[1]} | Data: {data[2]}"

        self.window.farmer.save()

        self.window.expenses_screen.expense_listwidget.addItem(text)

    def process_areas(self):
        self.window.stacked_widget.setCurrentIndex(6)
    
    def process_planting(self):
        self.window.stacked_widget.setCurrentIndex(6)

    def process_harvests(self):
        self.window.stacked_widget.setCurrentIndex(6)
