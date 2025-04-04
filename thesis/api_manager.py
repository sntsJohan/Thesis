from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QWidget, QMessageBox)
from PyQt5.QtCore import Qt
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE, DIALOG_STYLE
import re

class APIManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Key Management")
        self.setStyleSheet(DIALOG_STYLE)
        self.setMinimumWidth(800)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("API Key Management")
        title.setFont(FONTS['header'])
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # API Input section
        input_container = QWidget()
        input_container.setStyleSheet(f"background-color: {COLORS['surface']}; border-radius: 8px; padding: 20px;")
        input_layout = QVBoxLayout(input_container)

        # Current API display
        current_api_label = QLabel("Current API Key:")
        current_api_label.setFont(FONTS['body'])
        input_layout.addWidget(current_api_label)

        api_display_layout = QHBoxLayout()
        self.api_display = QLineEdit()
        self.api_display.setReadOnly(True)
        self.api_display.setStyleSheet(INPUT_STYLE)
        self.toggle_button = QPushButton("Show")
        self.toggle_button.setStyleSheet(BUTTON_STYLE)
        self.toggle_button.setFixedWidth(100)
        self.toggle_button.clicked.connect(self.toggle_api_visibility)
        
        api_display_layout.addWidget(self.api_display)
        api_display_layout.addWidget(self.toggle_button)
        input_layout.addLayout(api_display_layout)

        # New API input
        new_api_label = QLabel("New API Key:")
        new_api_label.setFont(FONTS['body'])
        input_layout.addWidget(new_api_label)

        self.new_api_input = QLineEdit()
        self.new_api_input.setStyleSheet(INPUT_STYLE)
        self.new_api_input.setPlaceholderText("Enter new API key...")
        input_layout.addWidget(self.new_api_input)

        # Add confirmation field
        confirm_api_label = QLabel("Confirm API Key:")
        confirm_api_label.setFont(FONTS['body'])
        input_layout.addWidget(confirm_api_label)

        self.confirm_api_input = QLineEdit()
        self.confirm_api_input.setStyleSheet(INPUT_STYLE)
        self.confirm_api_input.setPlaceholderText("Confirm new API key...")
        input_layout.addWidget(self.confirm_api_input)

        layout.addWidget(input_container)

        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save Changes")
        save_button.setStyleSheet(BUTTON_STYLE)
        save_button.clicked.connect(self.save_api_key)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet(BUTTON_STYLE)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)

        # Load current API
        self.load_current_api()

    def load_current_api(self):
        try:
            with open('c:\\Users\\johan\\Documents\\GitHub\\Thesis\\thesis\\scraper.py', 'r') as file:
                content = file.read()
                api_match = re.search(r'api = ["\'](.+?)["\']', content)
                if api_match:
                    api_key = api_match.group(1)
                    self.current_api = api_key
                    self.api_display.setText('*' * len(api_key))
                else:
                    self.current_api = ""
                    self.api_display.setText("No API key found")
        except Exception as e:
            self.api_display.setText("Error loading API key")
            self.current_api = ""

    def toggle_api_visibility(self):
        if self.toggle_button.text() == "Show":
            self.api_display.setText(self.current_api)
            self.toggle_button.setText("Hide")
        else:
            self.api_display.setText('*' * len(self.current_api))
            self.toggle_button.setText("Show")

    def save_api_key(self):
        new_api = self.new_api_input.text().strip()
        confirm_api = self.confirm_api_input.text().strip()
        
        if not new_api or not confirm_api:
            from utils import display_message
            display_message(self, "Error", "Please fill in both fields")
            return
            
        if new_api != confirm_api:
            from utils import display_message
            display_message(self, "Error", "API keys do not match")
            return
        
        # Add confirmation dialog
        confirm = QMessageBox.question(
            self,
            "Confirm API Update",
            "Are you sure you want to update the API key? This will affect all operations and may impact existing functionality.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.No:
            return
        
        try:
            with open('c:\\Users\\johan\\Documents\\GitHub\\Thesis\\thesis\\scraper.py', 'r') as file:
                content = file.read()
            
            # Replace API key
            new_content = re.sub(
                r'api = ["\'].+?["\']',
                f'api = "{new_api}"',
                content
            )
            
            with open('c:\\Users\\johan\\Documents\\GitHub\\Thesis\\thesis\\scraper.py', 'w') as file:
                file.write(new_content)
            
            self.current_api = new_api
            self.api_display.setText('*' * len(new_api))
            self.new_api_input.clear()
            self.confirm_api_input.clear()
            self.toggle_button.setText("Show")
            self.accept()
        except Exception as e:
            from utils import display_message
            display_message(self, "Error", f"Failed to save API key: {str(e)}")
