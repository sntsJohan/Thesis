import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from gui import MainWindow
from model import initialize_models
from setup_db import setup_database
from db_config import test_connection
from disclaimer import DisclaimerDialog
import traceback

def show_error_dialog(message, details=None):
    """Show an error dialog with the given message"""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("Error")
    msg_box.setText("Application Error")
    msg_box.setInformativeText(message)
    if details:
        msg_box.setDetailedText(details)
    else:
        msg_box.setDetailedText(traceback.format_exc())
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()

def show_warning_dialog(message, details=None):
    """Show a warning dialog with the given message"""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle("Warning")
    msg_box.setText("Application Warning")
    msg_box.setInformativeText(message)
    if details:
        msg_box.setDetailedText(details)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()

def main():
    """Main application entry point"""
    print("Application starting...")
    
    # Create application instance
    app = QApplication(sys.argv)
    
    # Show disclaimer dialog before proceeding
    disclaimer = DisclaimerDialog()
    if disclaimer.exec_() != DisclaimerDialog.Accepted:
        print("User declined disclaimer. Exiting application.")
        sys.exit(0)
    
    print("Disclaimer accepted. Proceeding with application startup.")
    
    # First, check database connectivity
    connected, error_message = test_connection()
    if not connected:
        print(f"DATABASE ERROR: {error_message}")
        show_warning_dialog(
            "Database connection failed. Some features like API management will not work.",
            f"Error details: {error_message}"
        )
    else:
        print("Database connection successful.")
        
        # Set up database tables
        try:
            setup_success = setup_database()
            if setup_success:
                print("Database setup successful.")
            else:
                print("Database setup failed.")
                show_warning_dialog(
                    "Database setup failed. Some features like API management will not work.",
                    "Check the application logs for details."
                )
        except Exception as e:
            error_msg = f"CRITICAL: Database setup failed: {e}"
            print(error_msg)
            print(traceback.format_exc())
            show_warning_dialog(
                "Database setup failed. Some features like API management will not work.",
                str(e)
            )
    
    # Initialize models
    try:
        initialize_models()
        print("Model initialization successful.")
    except Exception as e:
        error_msg = f"CRITICAL: Model initialization failed: {e}"
        print(error_msg)
        print(traceback.format_exc())
        show_warning_dialog(
            "Model initialization failed. Classification features will not work properly.",
            str(e)
        )

    # Start the application
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        error_msg = f"CRITICAL: Application failed to start: {e}"
        print(error_msg)
        print(traceback.format_exc())
        show_error_dialog(error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
    