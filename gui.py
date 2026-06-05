from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6 import uic

class Gui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AgroBook")
        self.setFixedSize(360, 640)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.initial_screen = uic.loadUi("InitialScreen.ui", None)

        self.stacked_widget.addWidget(self.initial_screen)

        self.stacked_widget.setCurrentIndex(0)
