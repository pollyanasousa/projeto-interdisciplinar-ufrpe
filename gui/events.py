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
        self.window.my_data_screen.state_combobox.setCurrentText(self.window.farmer.state)

        self.window.stacked_widget.setCurrentIndex(7)

    def expenses(self):
        self.window.expenses_screen.expense_listwidget.clear()

        for expense in self.window.farmer.expense.list_of_expenses:
            text = f"Tipo: {expense['type']} | Valor: {expense['value']} | Data: {expense['date']}"
            self.window.expenses_screen.expense_listwidget.addItem(text)

        self.window.stacked_widget.setCurrentIndex(8)

    def areas(self):
        self.window.areas_screen.area_listwidget.clear()

        for area in self.window.farmer.area.list_of_area:
            text = f"{area['name']}"
            self.window.areas_screen.area_listwidget.addItem(text)

        self.window.stacked_widget.setCurrentIndex(9)

    def planting(self):
        self.window.planting_screen.planting_listwidget.clear()

        for planting in self.window.farmer.planting.list_of_planting:
            text = f"Cultura: {planting['culture']} | Área: {planting['area']} | Quantidade: {planting['amount']} | Data: {planting['date']} "
            self.window.planting_screen.planting_listwidget.addItem(text)

        self.window.stacked_widget.setCurrentIndex(10)

    def harvest(self):
        self.window.harvests_screen.harvest_listwidget.clear()

        for harvest in self.window.farmer.harvest.list_of_harvest:
            text = f"Cultura: {harvest['culture']} | Quantidade: {harvest['amount']} | Data: {harvest['date']}"
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
        data = self.dialog.form_dialog(["Tipo de gasto (exemplo: adubo, transporte, mão de obra)", "Valor do gasto (exemplo: 100 reais)", "Data do gasto"], [is_valid_name, lambda name: is_valid_name(name, allow_numbers=True), is_valid_date])

        if data:
            text = f"Gasto: {data[0]} | Valor: {data[1]} | Data: {data[2]}"

            self.window.farmer.expense.new_expense(data[0], data[1], data[2])
            self.window.farmer.save()

            self.expenses()
        else:
            self.dialog.error_dialog("Erro ao adicionar gasto! Verifique os dados digitados.")

    def delete_expense(self):
        if self.dialog.yes_or_no_dialog("Deseja remover o gasto selecionado?"):
            line = self.window.expenses_screen.expense_listwidget.currentRow()

            self.window.farmer.expense.delete_expense(line)
            self.window.farmer.save()

            self.expenses()

    def update_expense(self):
        data = self.dialog.form_dialog(["Tipo de gasto (exemplo: adubo, transporte, mão de obra)", "Valor do gasto (exemplo: 100 reais)", "Data do gasto"], [is_valid_name, lambda name: is_valid_name(name, allow_numbers=True), is_valid_date])

        if data:
            line = self.window.expenses_screen.expense_listwidget.currentRow()

            self.window.farmer.expense.update_expense(line, data[0], data[1], data[2])
            self.window.farmer.save()

            self.expenses()
        else:
            self.dialog.error_dialog("Erro ao editar gasto! Verifique os dados digitados.")

    def process_areas(self):
        self.window.stacked_widget.setCurrentIndex(6)
    
    def new_area(self):
        data = self.dialog.form_dialog(["Nome da área (exemplo: roçado do fundo, terra perto do rio)"], [is_valid_name])

        if data:
            text = f"Área: {data[0]}"

            self.window.farmer.area.new_area(data[0])
            self.window.farmer.save()

            self.areas()
        else:
            self.dialog.error_dialog("Erro ao adicionar área! Verifique os dados digitados.")

    def delete_area(self):
        if self.dialog.yes_or_no_dialog("Deseja remover a área selecionada?"):
            line = self.window.expenses_screen.expense_listwidget.currentRow()

            self.window.farmer.area.delete_area(line)
            self.window.farmer.save()

            self.areas()

    def update_area(self):
        data = self.dialog.form_dialog(["Nome da área (exemplo: roçado do fundo, terra perto do rio)"], [is_valid_name])

        if data:
            line = self.window.expenses_screen.expense_listwidget.currentRow()

            self.window.farmer.area.update_area(line, data[0])
            self.window.farmer.save()

            self.areas()
        else:
            self.dialog.error_dialog("Erro ao editar área! Verifique os dados digitados.")
    
    def process_planting(self):
        self.window.stacked_widget.setCurrentIndex(6)

    def new_planting(self):
        data = self.dialog.form_dialog(["Nome da cultura (exemplo: milho, feijão, mandioca)", "Área da cultura", "Quantidade da cultura (exemplo: 3 sacos, 2 caixas)", "Data"], [is_valid_name, lambda name: is_valid_name(name, True), lambda name: is_valid_name(name, True), is_valid_date])

        if data:
            text = f"Cultura: {data[0]} | Área: {data[1]} | Quantidade: {data[2]} | Data: {data[3]}"

            self.window.farmer.planting.new_planting(data[0], data[1], data[2], data[3])
            self.window.farmer.save()

            self.planting()
        else:
            self.dialog.error_dialog("Erro ao adicionar plantio! Verifique os dados digitados.")

    def delete_planting(self):
        if self.dialog.yes_or_no_dialog("Deseja remover o plantio selecionado?"):
            line = line = self.window.planting_screen.planting_listwidget.currentRow()

            self.window.farmer.planting.delete_planting(line)
            self.window.farmer.save()

            self.planting()

    def update_planting(self):
        data = self.dialog.form_dialog(["Nome da cultura (exemplo: milho, feijão, mandioca)", "Área da cultura", "Quantidade da cultura (exemplo: 3 sacos, 2 caixas)"], [is_valid_name, is_valid_name, lambda name: is_valid_name(name, True)])

        if data:
            line = line = self.window.planting_screen.planting_listwidget.currentRow()

            self.window.farmer.planting.update_planting(line, data[0], data[1], data[2], data[3])
            self.window.farmer.save()

            self.planting()
        else:
            self.dialog.error_dialog("Erro ao editar plantio! Verifique os dados digitados.")

    def process_harvests(self):
        self.window.stacked_widget.setCurrentIndex(6)

    def new_harvest(self):
        data = self.dialog.form_dialog(["Nome da cultura (exemplo: milho, feijão, mandioca)", "Quantidade da colheita (exemplo: 10 sacos, 5 caixas)", "Data da colheita"], [is_valid_name, lambda name: is_valid_name(name, True), is_valid_date])

        if data:
            text = f"Cultura: {data[0]} | Quantidade: {data[1]} | Data: {data[2]}"

            self.window.farmer.harvest.new_harvest(data[0], data[1], data[2])
            self.window.farmer.save()

            self.harvest()
        else:
            self.dialog.error_dialog("Erro ao adicionar colheita! Verifique os dados digitados.")

    def delete_harvest(self):
        if self.dialog.yes_or_no_dialog("Deseja remover a colheita selecionada?"):
            line = self.window.harvests_screen.harvest_listwidget.currentRow()

            self.window.farmer.harvest.delete_harvest(line)
            self.window.farmer.save()

            self.harvest()

    def update_harvest(self):
        data = self.dialog.form_dialog(["Nome da cultura (exemplo: milho, feijão, mandioca)", "Quantidade da colheita (exemplo: 10 sacos, 5 caixas)", "Data da colheita"], [is_valid_name, lambda name: is_valid_name(True), is_valid_date])

        if data:
            line = self.window.harvests_screen.harvest_listwidget.currentRow()

            self.window.farmer.harvest.update_harvest(line, data[0], data[1], data[2])
            self.window.farmer.save()

            self.harvest()
        else:
            self.dialog.error_dialog("Erro ao editar colheita! Verifique os dados digitados.")