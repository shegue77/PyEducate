from sys import argv, exit as sys_exit
from PySide6.QtWidgets import QApplication
from gui.client.ui_loader import MainWindow


if __name__ == "__main__":
    app = QApplication(argv)
    window = MainWindow()
    window.setWindowTitle("PyEducate")
    window.showMaximized()
    window.show()
    sys_exit(app.exec())
