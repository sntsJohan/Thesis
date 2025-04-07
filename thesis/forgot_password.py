from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE
from db_config import get_db_connection
import os
import secrets
import string
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
from email_config import (SMTP_SERVER, SMTP_PORT, EMAIL_USERNAME, 
                          EMAIL_APP_PASSWORD, SENDER_EMAIL, EMAIL_SUBJECT, 
                          EMAIL_TEMPLATE)

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
        description = QLabel("Enter your username to receive a password reset link.")
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
        self.submit_button = QPushButton("Request Reset Link")
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

        conn = None # Initialize conn to None
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
                conn.close()
                return

            stored_email = result[0]
            if not stored_email or stored_email.lower() != email.lower():
                self.error_label.setText("Email does not match our records")
                conn.close()
                return

            # Generate reset token
            token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            expires_at = datetime.now() + timedelta(hours=24)  # Token expires in 24 hours

            # Store reset token
            cursor.execute("""
                INSERT INTO password_resets (username, reset_token, expires_at)
                VALUES (?, ?, ?)
            """, (username, token, expires_at))
            conn.commit()

            # --- Send Email ---
            try:
                # Create the reset link (adjust URL as needed)
                # Assuming your app handles this URL scheme, e.g., myapp://reset?token=...
                # For now, we'll just include the token in the email body.
                # A better approach would be a web link like http://yourdomain.com/reset?token=...
                reset_link = f"Your reset token is: {token}" # Placeholder - replace with actual link logic if applicable

                # Format the email body
                email_body = EMAIL_TEMPLATE.format(username=username, reset_link=reset_link)

                # Create email message
                msg = EmailMessage()
                msg.set_content(email_body)
                msg['Subject'] = EMAIL_SUBJECT
                msg['From'] = SENDER_EMAIL
                msg['To'] = email # Send to the user's provided email

                # Send the email
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                    server.starttls()  # Secure the connection
                    server.login(EMAIL_USERNAME, EMAIL_APP_PASSWORD)
                    server.send_message(msg)
                    
                QMessageBox.information(
                    self,
                    "Reset Link Sent",
                    "A password reset link has been sent to your email address.\\n"
                    "Please check your inbox and follow the instructions."
                )
                self.accept()

            except smtplib.SMTPAuthenticationError:
                self.error_label.setText("Email login failed. Check config.")
                print("SMTP Authentication Error: Check EMAIL_USERNAME and EMAIL_APP_PASSWORD.")
            except smtplib.SMTPConnectError:
                self.error_label.setText("Could not connect to email server.")
                print(f"SMTP Connect Error: Could not connect to {SMTP_SERVER}:{SMTP_PORT}.")
            except Exception as email_error:
                self.error_label.setText("Failed to send reset email.")
                print(f"Email sending error: {str(email_error)}")
                # Optionally rollback token insertion or notify admin
                # For now, we proceed but the user won't get the email

        except Exception as e:
            self.error_label.setText("An error occurred. Please try again later.")
            print(f"Password reset error: {str(e)}")
        finally:
            if conn: # Check if conn was successfully assigned
                conn.close() 