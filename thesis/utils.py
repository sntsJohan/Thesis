from PyQt5.QtWidgets import QMessageBox
import smtplib
from email.mime.text import MIMEText
from email_config import SMTP_SERVER, SMTP_PORT, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_FROM

def display_message(parent, title, message):
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.exec_()

def send_email(recipient_email, subject, body):
    """Sends an email using the configured SMTP settings."""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, [recipient_email], msg.as_string())
        print(f"Email sent successfully to {recipient_email}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
        raise  # Re-raise the exception to be caught by the caller
    except smtplib.SMTPConnectError as e:
        print(f"SMTP Connection Error: {e}")
        raise
    except smtplib.SMTPServerDisconnected as e:
        print(f"SMTP Server Disconnected: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred while sending email: {e}")
        raise
