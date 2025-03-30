from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE

class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")
        self.setMinimumWidth(400)
        self.role = None  # Store the user role
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("Login")
        title.setFont(FONTS['header'])
        title.setStyleSheet(f"color: {COLORS['primary']}; font-size: 24px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Username
        username_label = QLabel("Username")
        username_label.setFont(FONTS['body'])
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(INPUT_STYLE)
        self.username_input.setPlaceholderText("Enter your username")
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)

        # Password
        password_label = QLabel("Password")
        password_label.setFont(FONTS['body'])
        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(INPUT_STYLE)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)

        # Login Button
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet(BUTTON_STYLE)
        self.login_button.setFont(FONTS['button'])
        self.login_button.clicked.connect(self.validate_login)
        layout.addWidget(self.login_button)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLORS['error']};")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

    def validate_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Define user credentials
        credentials = {
            "admin": {"password": "admin123", "role": "admin"},
            "user": {"password": "user123", "role": "user"}
        }

        if username in credentials and password == credentials[username]["password"]:
            self.role = credentials[username]["role"]
            self.accept()
        else:
            self.error_label.setText("Invalid username or password")
            self.password_input.clear()

    def get_role(self):
        return self.role
