from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QApplication, QHBoxLayout, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QPalette, QColor
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE
from werkzeug.security import generate_password_hash
import json
import os
import re
from db_config import get_db_connection, log_user_action

class RegisterWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register")
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")
        self.setMinimumWidth(400)
        
        # Set tooltip style
        self.setStyleSheet(f"""
            QToolTip {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                padding: 5px;
                border-radius: 4px;
                font-size: 12px;
            }}
        """)
        
        # Position window on the right side and center it vertically
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(0, 0, 400, 600)
        qr = self.frameGeometry()
        qr.moveCenter(screen.center())
        qr.moveRight(screen.right() - 350)
        self.setGeometry(qr)
        
        # Set window icon
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QIcon(os.path.join(base_path, "assets", "applogo.png")))
        
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

        # Email
        email_label = QLabel("Email")
        email_label.setFont(FONTS['body'])
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet(INPUT_STYLE)
        self.email_input.setPlaceholderText("Enter your email address")
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)

        # Password
        password_label = QLabel("Password")
        password_label.setFont(FONTS['body'])
        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(INPUT_STYLE)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        # Set tooltip with password requirements
        self.password_input.setToolTip(
            "<b>Password Requirements:</b><br>"
            "• At least 8 characters<br>"
            "• One uppercase letter<br>"
            "• One lowercase letter<br>"
            "• One number<br>"
            "• One special character (!@#$%^&*(),.?\":{}|<>)"
        )
        
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

    def show_status_container(self, event):
        """Show the status container when password field is focused"""
        QLineEdit.focusInEvent(self.password_input, event)
        self.status_container.show()

    def hide_status_container(self, event):
        """Hide the status container when password field loses focus"""
        QLineEdit.focusOutEvent(self.password_input, event)
        self.status_container.hide()

    def update_password_requirements(self, password):
        """Update the visual status of password requirements"""
        # Length requirement
        length_icon, length_label = self.requirement_labels['length']
        if len(password) >= 8:
            length_icon.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['success']};
                    border-radius: 8px;
                }}
            """)
        else:
            length_icon.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['error']};
                    border-radius: 8px;
                }}
            """)

        # Uppercase requirement
        upper_icon, upper_label = self.requirement_labels['uppercase']
        if re.search(r"[A-Z]", password):
            upper_icon.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['success']};
                    border-radius: 8px;
                }}
            """)
        else:
            upper_icon.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['error']};
                    border-radius: 8px;
                }}
            """)

        # Lowercase requirement
        lower_icon, lower_label = self.requirement_labels['lowercase']
        if re.search(r"[a-z]", password):
            lower_icon.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['success']};
                    border-radius: 8px;
                }}
            """)
        else:
            lower_icon.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['error']};
                    border-radius: 8px;
                }}
            """)

        # Number requirement
        number_icon, number_label = self.requirement_labels['number']
        if re.search(r"\d", password):
            number_icon.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['success']};
                    border-radius: 8px;
                }}
            """)
        else:
            number_icon.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['error']};
                    border-radius: 8px;
                }}
            """)

        # Special character requirement
        special_icon, special_label = self.requirement_labels['special']
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            special_icon.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['success']};
                    border-radius: 8px;
                }}
            """)
        else:
            special_icon.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['error']};
                    border-radius: 8px;
                }}
            """)

    def validate_password(self, password):
        if len(password) < 8:
            return "Password must be at least 8 characters long"
        if not re.search(r"[A-Z]", password):
            return "Password must contain at least one uppercase letter"
        if not re.search(r"[a-z]", password):
            return "Password must contain at least one lowercase letter"
        if not re.search(r"\d", password):
            return "Password must contain at least one number"
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return "Password must contain at least one special character"
        return None

    def register_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        email = self.email_input.text()

        if not username or not password or not email:
            self.error_label.setText("Please fill in all fields")
            return

        # Simple email format validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.error_label.setText("Invalid email format")
            return

        # Validate password requirements
        password_error = self.validate_password(password)
        if password_error:
            self.error_label.setText(password_error)
            self.password_input.clear()
            self.confirm_input.clear()
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

            # Check if email exists
            cursor.execute("SELECT email FROM users WHERE email=?", (email,))
            if cursor.fetchone():
                self.error_label.setText("Email already registered")
                conn.close()
                return

            # Add new user with email
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                (username, hashed_password, email, "user")
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
