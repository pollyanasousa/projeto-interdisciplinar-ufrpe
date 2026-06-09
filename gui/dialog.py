from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QMessageBox, QVBoxLayout

class Dialog:
    def __init__(self):
        pass

    def error_dialog(self, message):
        """
        It shows an error dialog on the screen, whose message is passed as argument.
        """

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Erro")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        msg_box.exec()

    def yes_or_no_dialog(self, message):
        """
        It shows a dialog on the screen, asking a "yes" or "no" question, whose content is passed
        as argument.

        It returns True if the user answered "yes" and False otherwise.
        """

        msg_box = QMessageBox.question(
            None,
            "Pergunta",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        return msg_box == QMessageBox.StandardButton.Yes
    
    def form_dialog(self, entries, validations):
        """
        It shows a form dialog on the screen. The "entries" argument is a list of strings that
        indicate the input data and "validations" argument is a list of functions that check if
        the data are in the right format, where validations[n] refers to entries[n].

        The function returns a list containing the user input, where the n-th element refers 
        to entries[n]. But it returns None if at least an input was invalid.
        """

        dialog = QDialog()
        dialog.setWindowTitle("AgroBook")
        
        form_layout = QFormLayout()
        
        lineedits = [QLineEdit() for i in range(len(entries))]
        
        for i, entry in enumerate(entries):
            form_layout.addRow(entry, lineedits[i])
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        
        vbox_layout = QVBoxLayout()
        vbox_layout.addLayout(form_layout)
        vbox_layout.addWidget(buttons)

        dialog.setLayout(vbox_layout)

        if dialog.exec():
            result = []

            for i in range(len(entries)):
                if validations[i](lineedits[i].text()):
                    result.append(lineedits[i].text())
                else:
                    return None

            return result