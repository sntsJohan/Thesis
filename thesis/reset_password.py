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
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        
        self.setWindowTitle("Set New Password")
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")
        self.setMinimumWidth(400)
        
        # Set window icon
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QIcon(os.path.join(base_path, "assets", "applogo.png")))
        
        self.setup_ui()

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

        # Verification Code input
        code_label = QLabel("Verification Code")
        code_label.setFont(FONTS['body'])
        self.code_input = QLineEdit()
        self.code_input.setStyleSheet(INPUT_STYLE)
        self.code_input.setPlaceholderText("Enter the 6-digit code from your email")
        self.code_input.setMaxLength(6)
        layout.addWidget(code_label)
        layout.addWidget(self.code_input)

        # Password requirements
        # Use HTML for more reliable line breaks in QLabel
        requirements_text = (
            "<b>Password must:</b><br>"
            "&bull; Be at least 8 characters long<br>"
            "&bull; Contain at least one uppercase letter<br>"
            "&bull; Contain at least one lowercase letter<br>"
            "&bull; Contain at least one number<br>"
            "&bull; Contain at least one special character"
        )
        requirements = QLabel(requirements_text)
        requirements.setTextFormat(Qt.RichText) # Tell QLabel to interpret as HTML
        requirements.setFont(FONTS['body'])
        requirements.setStyleSheet(f"color: {COLORS['text_secondary']};")
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
        """Handle password reset submission after code verification"""
        code = self.code_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not code:
            self.error_label.setText("Please enter the verification code")
            return
            
        if len(code) != 6 or not code.isdigit():
             self.error_label.setText("Invalid verification code format")
             return

        if password != confirm:
            self.error_label.setText("Passwords do not match")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # 1. Validate the verification code (stored in token_hash)
            cursor.execute("""
                SELECT TOP 1 token_hash, expires_at
                FROM password_resets 
                WHERE username = ?  -- Removed used = 0 condition
                ORDER BY created_at DESC
            """, (self.username,))
            result = cursor.fetchone()

            if not result:
                self.error_label.setText("Invalid or expired verification code. Please request again.")
                conn.close()
                return

            stored_code, expires_at = result
            
            # Check if token is expired
            if expires_at < datetime.now():
                self.error_label.setText("Verification code has expired. Please request again.")
                conn.close()
                return

            if stored_code != code:
                self.error_label.setText("Incorrect verification code.")
                conn.close()
                return

            # 2. If code is valid, proceed to update password
            hashed_password = generate_password_hash(password)
            
            # Update the user's password
            cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (hashed_password, self.username)
            )
            
            # Delete the used verification code instead of marking it as used
            cursor.execute(
                "DELETE FROM password_resets WHERE username = ? AND token_hash = ?",
                (self.username, code)
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
            if 'conn' in locals() and conn.is_connected():
                conn.close() 