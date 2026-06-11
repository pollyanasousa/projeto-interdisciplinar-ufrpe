from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QMessageBox, QVBoxLayout, QComboBox
)

# Sentinel: distingue "usuário cancelou" de "dado inválido"
CANCELLED = object()


class Dialog:
    def __init__(self):
        pass

    def error_dialog(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Erro")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def yes_or_no_dialog(self, message):
        msg_box = QMessageBox.question(
            None,
            "Pergunta",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        return msg_box == QMessageBox.StandardButton.Yes

    def form_dialog(self, entries, validations, prefill=None):
        """
        Formulário genérico com campos de texto.
        Retorna:
          - lista de valores  → OK e dados válidos
          - CANCELLED         → usuário clicou Cancelar
          - None              → OK mas dado inválido
        """
        dialog = QDialog()
        dialog.setWindowTitle("AgroBook")

        form_layout = QFormLayout()
        lineedits = [QLineEdit() for _ in range(len(entries))]

        if prefill:
            for i, val in enumerate(prefill):
                if i < len(lineedits) and val:
                    lineedits[i].setText(str(val))

        for i, entry in enumerate(entries):
            form_layout.addRow(entry, lineedits[i])

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        vbox_layout = QVBoxLayout()
        vbox_layout.addLayout(form_layout)
        vbox_layout.addWidget(buttons)
        dialog.setLayout(vbox_layout)

        if not dialog.exec():
            return CANCELLED  # usuário cancelou

        result = []
        for i in range(len(entries)):
            if validations[i](lineedits[i].text()):
                result.append(lineedits[i].text())
            else:
                return None  # dado inválido
        return result

    def expense_dialog(self, cultures, prefill=None):
        """
        Formulário de gasto com combobox de culturas do plantio.
        cultures: lista de nomes de cultura (+ "Geral")
        prefill: dict com type, value, date, culture
        Retorna dict {type, value, date, culture} ou CANCELLED ou None.
        """
        dialog = QDialog()
        dialog.setWindowTitle("AgroBook")

        form_layout = QFormLayout()

        type_edit = QLineEdit()
        value_edit = QLineEdit()
        date_edit = QLineEdit()
        culture_combo = QComboBox()
        culture_combo.addItems(["Geral"] + cultures)

        if prefill:
            type_edit.setText(prefill.get("type", ""))
            value_edit.setText(prefill.get("value", ""))
            date_edit.setText(prefill.get("date", ""))
            idx = culture_combo.findText(prefill.get("culture", "Geral"))
            if idx >= 0:
                culture_combo.setCurrentIndex(idx)

        form_layout.addRow("Tipo de gasto (ex: adubo, transporte)", type_edit)
        form_layout.addRow("Valor (ex: 100 reais)", value_edit)
        form_layout.addRow("Data (ex: hoje, ontem, 15/06/2025)", date_edit)
        form_layout.addRow("Plantio/Cultura", culture_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        vbox = QVBoxLayout()
        vbox.addLayout(form_layout)
        vbox.addWidget(buttons)
        dialog.setLayout(vbox)

        if not dialog.exec():
            return CANCELLED

        from utils.validators import is_valid_name, is_valid_date
        _type = type_edit.text().strip()
        value = value_edit.text().strip()
        date = date_edit.text().strip()
        culture = culture_combo.currentText()
        value_ok = len(value) > 0 and len(value) <= 100
        if is_valid_name(_type) and value_ok and is_valid_date(date):
            return {"type": _type, "value": value, "date": date, "culture": culture}
        return None


    def harvest_dialog(self, cultures, prefill=None):
        """
        Formulário de colheita com combobox de culturas do plantio.
        cultures: lista de nomes de cultura cadastrados
        prefill: dict com culture, amount, date
        Retorna dict {culture, amount, date} ou CANCELLED ou None.
        """
        dialog = QDialog()
        dialog.setWindowTitle("AgroBook")

        form_layout = QFormLayout()

        culture_combo = QComboBox()
        culture_combo.addItems(cultures)
        amount_edit = QLineEdit()
        date_edit = QLineEdit()

        if prefill:
            idx = culture_combo.findText(prefill.get("culture", ""))
            if idx >= 0:
                culture_combo.setCurrentIndex(idx)
            amount_edit.setText(prefill.get("amount", ""))
            date_edit.setText(prefill.get("date", ""))

        form_layout.addRow("Cultura colhida", culture_combo)
        form_layout.addRow("Quantidade (ex: 10 sacos, 5 arrobas, 300 kg)", amount_edit)
        form_layout.addRow("Data da colheita (ex: hoje, ontem, há 15 dias)", date_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        vbox = QVBoxLayout()
        vbox.addLayout(form_layout)
        vbox.addWidget(buttons)
        dialog.setLayout(vbox)

        if not dialog.exec():
            return CANCELLED

        from utils.validators import is_valid_name, is_valid_date
        culture = culture_combo.currentText()
        amount = amount_edit.text().strip()
        date = date_edit.text().strip()
        if is_valid_name(amount, allow_numbers=True) and is_valid_date(date):
            return {"culture": culture, "amount": amount, "date": date}
        return None

    def planting_dialog(self, areas, prefill=None):
        """
        Formulário de plantio com combobox de áreas.
        Retorna:
          - dict {culture, area, amount, date} → OK e dados válidos
          - CANCELLED                          → usuário clicou Cancelar
          - None                               → OK mas dado inválido
        """
        dialog = QDialog()
        dialog.setWindowTitle("AgroBook")

        form_layout = QFormLayout()

        culture_edit = QLineEdit()
        area_combo = QComboBox()
        area_combo.addItems(areas)
        amount_edit = QLineEdit()
        date_edit = QLineEdit()

        if prefill:
            culture_edit.setText(prefill.get("culture", ""))
            idx = area_combo.findText(prefill.get("area", ""))
            if idx >= 0:
                area_combo.setCurrentIndex(idx)
            amount_edit.setText(prefill.get("amount", ""))
            date_edit.setText(prefill.get("date", ""))

        form_layout.addRow("Nome da cultura (ex: milho, feijão)", culture_edit)
        form_layout.addRow("Área", area_combo)
        form_layout.addRow("Quantidade (ex: 3 sacos, 2 arrobas)", amount_edit)
        form_layout.addRow("Data (ex: hoje, ontem, 15/06/2025)", date_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        vbox = QVBoxLayout()
        vbox.addLayout(form_layout)
        vbox.addWidget(buttons)
        dialog.setLayout(vbox)

        if not dialog.exec():
            return CANCELLED  # usuário cancelou

        from utils.validators import is_valid_name, is_valid_date
        culture = culture_edit.text().strip()
        area = area_combo.currentText()
        amount = amount_edit.text().strip()
        date = date_edit.text().strip()
        if is_valid_name(culture) and is_valid_name(amount, allow_numbers=True) and is_valid_date(date):
            return {"culture": culture, "area": area, "amount": amount, "date": date}
        return None  # dado inválido