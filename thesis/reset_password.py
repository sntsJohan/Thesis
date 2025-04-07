from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE
from db_config import get_db_connection
from werkzeug.security import generate_password_hash
import os
from datetime import datetime
import re

class ResetPasswordDialog(QDialog):
    def __init__(self, token, parent=None):
        super().__init__(parent)
        self.token = token
        self.username = None  # Will be set after validating token
        
        self.setWindowTitle("Reset Password")
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")
        self.setMinimumWidth(400)
        
        # Set window icon
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QIcon(os.path.join(base_path, "assets", "applogo.png")))
        
        if not self.validate_token():
            self.reject()
            return
            
        self.setup_ui()

    def validate_token(self):
        """Validate the reset token and get associated username"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if token exists and is not expired or used
            cursor.execute("""
                SELECT username, expires_at 
                FROM password_resets 
                WHERE reset_token = ? AND used = 0
            """, (self.token,))
            
            result = cursor.fetchone()
            if not result:
                QMessageBox.critical(
                    self,
                    "Invalid Token",
                    "This password reset link is invalid or has already been used."
                )
                return False
                
            username, expires_at = result
            
            # Check if token is expired
            if expires_at < datetime.now():
                QMessageBox.critical(
                    self,
                    "Expired Token",
                    "This password reset link has expired. Please request a new one."
                )
                return False
                
            self.username = username
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                "An error occurred while validating your reset token."
            )
            print(f"Token validation error: {str(e)}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("Reset Your Password")
        title.setFont(FONTS['header'])
        title.setStyleSheet(f"color: {COLORS['primary']}; font-size: 24px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Password requirements
        requirements = QLabel(
            "Password must:\n"
            "• Be at least 8 characters long\n"
            "• Contain at least one uppercase letter\n"
            "• Contain at least one lowercase letter\n"
            "• Contain at least one number\n"
            "• Contain at least one special character"
        )
        requirements.setFont(FONTS['body'])
        requirements.setStyleSheet(f"color: {COLORS['text_secondary']};")
        requirements.setWordWrap(True)
        layout.addWidget(requirements)

        # New password input
        password_label = QLabel("New Password")
        password_label.setFont(FONTS['body'])
        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(INPUT_STYLE)
        self.password_input.setPlaceholderText("Enter your new password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)

        # Confirm password input
        confirm_label = QLabel("Confirm Password")
        confirm_label.setFont(FONTS['body'])
        self.confirm_input = QLineEdit()
        self.confirm_input.setStyleSheet(INPUT_STYLE)
        self.confirm_input.setPlaceholderText("Confirm your new password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(confirm_label)
        layout.addWidget(self.confirm_input)

        # Submit button
        self.submit_button = QPushButton("Reset Password")
        self.submit_button.setStyleSheet(BUTTON_STYLE)
        self.submit_button.setFont(FONTS['button'])
        self.submit_button.clicked.connect(self.reset_password)
        layout.addWidget(self.submit_button)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLORS['error']};")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

    def validate_password(self, password):
        """Validate password meets requirements"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number"
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character"
        return True, ""

    def reset_password(self):
        """Handle password reset submission"""
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if password != confirm:
            self.error_label.setText("Passwords do not match")
            return

        # Validate password
        is_valid, message = self.validate_password(password)
        if not is_valid:
            self.error_label.setText(message)
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Hash the new password
            hashed_password = generate_password_hash(password)
            
            # Update the user's password
            cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (hashed_password, self.username)
            )
            
            # Mark the reset token as used
            cursor.execute(
                "UPDATE password_resets SET used = 1 WHERE reset_token = ?",
                (self.token,)
            )
            
            conn.commit()
            
            QMessageBox.information(
                self,
                "Success",
                "Your password has been reset successfully.\nYou can now log in with your new password."
            )
            self.accept()
            
        except Exception as e:
            self.error_label.setText("An error occurred. Please try again later.")
            print(f"Password reset error: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close() 