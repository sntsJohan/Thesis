from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE
from db_config import get_db_connection, log_user_action

class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")
        self.setMinimumWidth(400)
        self.role = None  # Store the user role
        self.username = None  # Store the username
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

        # Sign Up Text Link
        self.signup_label = QLabel("New User? Create Account.")
        self.signup_label.setFont(FONTS['body'])
        self.signup_label.setStyleSheet("text-decoration: underline; color: blue; cursor: pointer;")
        self.signup_label.setAlignment(Qt.AlignCenter)
        self.signup_label.mousePressEvent = lambda e: self.open_register()
        layout.addWidget(self.signup_label)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLORS['error']};")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

    def validate_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role FROM users WHERE username=? AND password=?",
                (username, password)
            )
            result = cursor.fetchone()
            
            if result:
                self.role = result[0].strip()
                self.username = username  # Store username
                conn.close()
                # Only log if role is user
                if self.role.lower() == "user":
                    log_user_action(username, "User Login")
                self.accept()
            else:
                self.error_label.setText("Invalid username or password")
                self.password_input.clear()
            
        except Exception as e:
            self.error_label.setText("Database connection error")
            print(f"Database error: {str(e)}")

    def open_register(self):
        from register import RegisterWindow
        register_window = RegisterWindow(self)
        if register_window.exec_() == QDialog.Accepted:
            self.username_input.setText(register_window.get_username())

    def get_role(self):
        return self.role

    def get_username(self):  # Add this new method
        return getattr(self, 'username', None)
