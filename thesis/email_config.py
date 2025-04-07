# Email Configuration
SMTP_SERVER = "smtp.gmail.com"  # Using Gmail SMTP server
SMTP_PORT = 587  # TLS port
EMAIL_USERNAME = "tipqccbds@gmail.com"
EMAIL_PASSWORD = "bbyb jhml uamv ndyy"  # Replace with your app password
EMAIL_FROM = "tipqccbds@gmail.com"  # Replace with your email
EMAIL_SUBJECT = "Password Reset - Cyberbullying Detection System"

# Email Templateyour-email@gmail.com"
RESET_EMAIL_TEMPLATE = """
Dear {username},

You have requested to reset your password for the Cyberbullying Detection System.

To reset your password, please click on the following link:
{reset_link}

This link will expire in 24 hours.

If you did not request this password reset, please ignore this email.

Best regards,
Cyberbullying Detection System Team
""" 