from PyQt5.QtWidgets import QMessageBox

def display_message(parent, title, message):
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.exec_()

def classify_comments():
    pass