from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE
import json
import os
from db_config import get_db_connection, log_user_action

class RegisterWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register")
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
        self.setWindowIcon(QIcon("assets/applogo.png"))
        
        self.username = ""
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("Create Account")
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

        # Confirm Password
        confirm_label = QLabel("Confirm Password")
        confirm_label.setFont(FONTS['body'])
        self.confirm_input = QLineEdit()
        self.confirm_input.setStyleSheet(INPUT_STYLE)
        self.confirm_input.setPlaceholderText("Confirm your password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(confirm_label)
        layout.addWidget(self.confirm_input)

        # Register Button
        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet(BUTTON_STYLE)
        self.register_button.setFont(FONTS['button'])
        self.register_button.clicked.connect(self.register_user)
        layout.addWidget(self.register_button)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLORS['error']};")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

    def register_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not username or not password:
            self.error_label.setText("Please fill in all fields")
            return

        if password != confirm:
            self.error_label.setText("Passwords do not match")
            self.password_input.clear()
            self.confirm_input.clear()
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if username exists
            cursor.execute("SELECT username FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                self.error_label.setText("Username already exists")
                conn.close()
                return

            # Add new user
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, "user")
            )
            conn.commit()
            conn.close()
            
            # Add logging
            log_user_action(username, "User Registration")
            
            self.username = username
            self.accept()
            
        except Exception as e:
            self.error_label.setText("Database error occurred")
            print(f"Database error: {str(e)}")

    def get_username(self):
        return self.username
