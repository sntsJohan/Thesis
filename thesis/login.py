from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QApplication, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE
from db_config import get_db_connection, log_user_action
from werkzeug.security import check_password_hash
import os

class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")
        self.setMinimumWidth(400)
        
        # Position window on the right side and center it vertically
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(0, 0, 400, 500)  # Set initial size
        qr = self.frameGeometry()
        qr.moveCenter(screen.center())  # Center the window
        qr.moveRight(screen.right() - 350)  # Move to right side with 200px margin
        self.setGeometry(qr)
        
        # Set window icon
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QIcon(os.path.join(base_path, "assets", "applogo.png")))
        
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

        # Sign Up / Forgot Password Links Container
        links_layout = QHBoxLayout()
        links_layout.setContentsMargins(0, 10, 0, 0) # Add some top margin

        # Forgot Password Link
        self.forgot_password_label = QLabel("Forgot Password?")
        self.forgot_password_label.setFont(FONTS['body'])
        self.forgot_password_label.setStyleSheet(f"color: {COLORS['text_secondary']}; text-decoration: underline; cursor: pointer;") # Use secondary text color
        self.forgot_password_label.setAlignment(Qt.AlignLeft)
        self.forgot_password_label.mousePressEvent = lambda e: self.open_forgot_password()
        links_layout.addWidget(self.forgot_password_label)

        links_layout.addStretch() # Push sign up link to the right

        # Sign Up Text Link
        self.signup_label = QLabel("New User? Create Account")
        self.signup_label.setFont(FONTS['body'])
        self.signup_label.setStyleSheet(f"color: {COLORS['text_secondary']}; text-decoration: underline; cursor: pointer;") # Use secondary text color
        self.signup_label.setAlignment(Qt.AlignRight)
        self.signup_label.mousePressEvent = lambda e: self.open_register()
        links_layout.addWidget(self.signup_label)

        layout.addLayout(links_layout) # Add the horizontal layout for links

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
                "SELECT password, role, is_active FROM users WHERE username=?",
                (username,)
            )
            result = cursor.fetchone()
            
            if result:
                stored_hash, role, is_active = result
                if is_active and check_password_hash(stored_hash, password):
                    self.role = role.strip()
                    self.username = username  # Store username
                    conn.close()
                    # Only log if role is user
                    if self.role.lower() == "user":
                        log_user_action(username, "User Login")
                    self.accept()
                elif not is_active:
                    # Account exists but is disabled
                    self.error_label.setText("Account is disabled. Contact administrator.")
                    conn.close()
                else:
                    # Password doesn't match
                    self.error_label.setText("Invalid username or password")
                    self.password_input.clear()
                    conn.close()
            else:
                # User not found
                self.error_label.setText("Invalid username or password")
                self.password_input.clear()
                if conn:
                    conn.close()
            
        except Exception as e:
            self.error_label.setText("Database connection error")
            print(f"Database error: {str(e)}")

    def open_register(self):
        from register import RegisterWindow
        register_window = RegisterWindow(self)
        if register_window.exec_() == QDialog.Accepted:
            self.username_input.setText(register_window.get_username())

    def open_forgot_password(self):
        from forgot_password import ForgotPasswordDialog
        forgot_password_dialog = ForgotPasswordDialog(self)
        forgot_password_dialog.exec_()

    def get_role(self):
        return self.role

    def get_username(self):  # Add this new method
        return getattr(self, 'username', None)
