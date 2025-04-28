import sys
from PyQt5.QtWidgets import QApplication
from gui import MainWindow
from model import initialize_models

def main():
    """Main application entry point"""
    print("Application starting, initializing models...")
    try:
        initialize_models()
        print("Model initialization successful.")
    except Exception as e:
        print(f"CRITICAL: Model initialization failed: {e}")
        # Depending on requirements, you might want to exit or show an error message
        # For now, we'll print the error and continue, but classification will likely fail.
        # Consider adding a user-friendly error dialog here.
        # sys.exit(1) # Optional: Exit if models are critical

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    