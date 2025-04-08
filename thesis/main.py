import sys
from PyQt5.QtWidgets import QApplication
from gui import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()   
    window.show()
    sys.exit(app.exec_())
    