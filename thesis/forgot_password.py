from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE
from db_config import get_db_connection
import os
import secrets
import string
from datetime import datetime, timedelta
from smtplib import SMTPException
from utils import send_email  # Assuming send_email utility exists in utils.py
from reset_password import ResetPasswordDialog # Import the reset dialog

class ForgotPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reset Password")
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
        title = QLabel("Reset Password")
        title.setFont(FONTS['header'])
        title.setStyleSheet(f"color: {COLORS['primary']}; font-size: 24px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Description
        description = QLabel("Enter your username to receive a verification code.")
        description.setFont(FONTS['body'])
        description.setStyleSheet(f"color: {COLORS['text_secondary']};")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)

        # Username input
        username_label = QLabel("Username")
        username_label.setFont(FONTS['body'])
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(INPUT_STYLE)
        self.username_input.setPlaceholderText("Enter your username")
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)

        # Email input
        email_label = QLabel("Email")
        email_label.setFont(FONTS['body'])
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet(INPUT_STYLE)
        self.email_input.setPlaceholderText("Enter your email address")
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)

        # Submit button
        self.submit_button = QPushButton("Send Verification Code")
        self.submit_button.setStyleSheet(BUTTON_STYLE)
        self.submit_button.setFont(FONTS['button'])
        self.submit_button.clicked.connect(self.request_reset)
        layout.addWidget(self.submit_button)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLORS['error']};")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

    def request_reset(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()

        if not username or not email:
            self.error_label.setText("Please enter both username and email")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if username and email match
            cursor.execute(
                "SELECT email FROM users WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()

            if not result:
                self.error_label.setText("Username not found")
                return

            stored_email = result[0]
            if stored_email.lower() != email.lower():
                self.error_label.setText("Email does not match our records")
                return

            # Generate 6-digit verification code
            verification_code = ''.join(secrets.choice(string.digits) for _ in range(6))
            expires_at = datetime.now() + timedelta(minutes=15)  # Code expires in 15 minutes

            # Store verification code in token_hash column
            cursor.execute("""
                DELETE FROM password_resets WHERE username = ?
            """, (username,)) # Delete any existing codes for the user
            cursor.execute("""
                INSERT INTO password_resets (username, token_hash, expires_at) -- Use token_hash
                VALUES (?, ?, ?)
            """, (username, verification_code, expires_at))
            conn.commit()

            # Send email with verification code
            subject = "Your Password Reset Code"
            body = f"Hello {username},\n\nPlease find your password reset verification code below:\n\nVerification Code: {verification_code}\n\nThis code will expire in 15 minutes.\n\nIf you did not request this, please ignore this email.\n\nBest regards,\nYour Application Name" # Added app name
            
            try:
                send_email(email, subject, body) # Use the utility function
                QMessageBox.information(
                    self,
                    "Verification Code Sent",
                    "A verification code has been sent to your email address.\n"
                    "Please check your inbox (and spam/junk folder) and enter the code in the next step."
                )
                # Open the ResetPasswordDialog, passing the username
                self.accept() # Close the current dialog first
                reset_dialog = ResetPasswordDialog(username=username, parent=self.parent()) # Pass username
                reset_dialog.exec_() # Show the reset dialog modally

            except SMTPException as smtp_e:
                 self.error_label.setText("Failed to send email. Check configuration.")
                 print(f"SMTP error during password reset: {str(smtp_e)}")
            except Exception as mail_e:
                 self.error_label.setText("An error occurred sending the email.")
                 print(f"Email sending error during password reset: {str(mail_e)}")


        except Exception as e:
            self.error_label.setText("An database error occurred. Please try again later.") # More specific error
            print(f"Password reset DB error: {str(e)}")
        finally:
            if 'conn' in locals() and conn: # Check if conn exists and is not None
                conn.close() 