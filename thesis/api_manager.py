from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QWidget, QMessageBox,
                           QComboBox, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE, DIALOG_STYLE
import os
from api_db import get_api_key, set_api_key, get_all_api_keys, delete_api_key, test_api_table_connection
from utils import display_message
import traceback

class APIManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Key Management")
        self.setStyleSheet(DIALOG_STYLE)
        self.setMinimumWidth(700)
        
        # Always use 'apify' as the key name
        self.api_key_name = 'apify'
        
        # Initialize api_table to None - this will be set later
        self.api_table = None
        self.table_container = None
        
        # Test database connection before proceeding
        self.db_connected, self.db_error = test_api_table_connection()
        
        # Set window icon
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            self.setWindowIcon(QIcon(os.path.join(base_path, "assets", "applogo.png")))
        except Exception as e:
            print(f"Error setting window icon: {str(e)}")
        
        self.init_ui()

    def init_ui(self):
        try:
            layout = QVBoxLayout(self)
            layout.setSpacing(20)
            
            # Title
            title = QLabel("API Key Management")
            title.setFont(FONTS['header'])
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)
            
            # Show database status
            status_container = QWidget()
            status_layout = QHBoxLayout(status_container)
            status_layout.setContentsMargins(10, 5, 10, 5)
            
            status_label = QLabel("Database Status:")
            status_label.setFont(FONTS['body'])
            status_layout.addWidget(status_label)
            
            if self.db_connected:
                status_text = QLabel("Connected")
                status_text.setStyleSheet(f"color: {COLORS['success']}; font-weight: bold;")
            else:
                status_text = QLabel("Disconnected - " + self.db_error)
                status_text.setStyleSheet(f"color: {COLORS['error']}; font-weight: bold;")
                status_text.setWordWrap(True)
            
            status_layout.addWidget(status_text)
            layout.addWidget(status_container)

            # Only create API table if database is connected
            if self.db_connected:
                # API keys table
                self.create_api_table()
                if self.table_container:
                    layout.addWidget(self.table_container)

            # API Input section
            input_container = QWidget()
            input_container.setStyleSheet(f"background-color: {COLORS['surface']}; border-radius: 8px; padding: 20px;")
            input_layout = QVBoxLayout(input_container)

            # API key title
            api_label = QLabel("Apify API Key")
            api_label.setFont(FONTS['subheader'])
            input_layout.addWidget(api_label)

            # API Key Description
            description = QLabel("Enter your Apify API key below. This key will be used for all scraping operations.")
            description.setFont(FONTS['body'])
            description.setWordWrap(True)
            input_layout.addWidget(description)
            
            # Add some spacing
            input_layout.addSpacing(10)

            # API key layout
            api_key_layout = QHBoxLayout()
            api_key_label = QLabel("API Key:")
            api_key_label.setFont(FONTS['body'])
            api_key_label.setFixedWidth(80)
            
            self.api_key_input = QLineEdit()
            self.api_key_input.setStyleSheet(INPUT_STYLE)
            self.api_key_input.setPlaceholderText("Enter your Apify API key...")
            
            api_key_layout.addWidget(api_key_label)
            api_key_layout.addWidget(self.api_key_input)
            input_layout.addLayout(api_key_layout)

            # Current API key
            current_key = get_api_key(self.api_key_name) if self.db_connected else None
            if current_key:
                current_key_layout = QHBoxLayout()
                current_key_label = QLabel("Current Key:")
                current_key_label.setFont(FONTS['body'])
                current_key_label.setFixedWidth(80)
                
                masked_key = f"{current_key[:4]}...{current_key[-4:]}" if len(current_key) > 8 else "****"
                current_key_value = QLabel(masked_key)
                current_key_value.setFont(FONTS['body'])
                current_key_value.setStyleSheet(f"color: {COLORS['text_secondary']};")
                
                current_key_layout.addWidget(current_key_label)
                current_key_layout.addWidget(current_key_value)
                input_layout.addLayout(current_key_layout)

            # Add some spacing
            input_layout.addSpacing(10)

            # Add or update button
            save_button = QPushButton("Save API Key")
            save_button.setStyleSheet(BUTTON_STYLE)
            save_button.clicked.connect(self.save_api_key)
            # Disable the button if database is not connected
            if not self.db_connected:
                save_button.setEnabled(False)
                save_button.setToolTip("Database connection is required to save API keys")
                
            input_layout.addWidget(save_button)

            layout.addWidget(input_container)

            # Close button
            close_button = QPushButton("Close")
            close_button.setStyleSheet(BUTTON_STYLE)
            close_button.clicked.connect(self.accept)
            layout.addWidget(close_button)
            
            # Add a retry button if database is not connected
            if not self.db_connected:
                retry_button = QPushButton("Retry Connection")
                retry_button.setStyleSheet(BUTTON_STYLE)
                retry_button.clicked.connect(self.retry_connection)
                layout.addWidget(retry_button)
                
        except Exception as e:
            print(f"Error initializing API Manager UI: {str(e)}")
            print(traceback.format_exc())
            # Show a basic error message
            error_layout = QVBoxLayout(self)
            error_label = QLabel(f"Error initializing API Manager: {str(e)}")
            error_label.setWordWrap(True)
            error_layout.addWidget(error_label)
            
            close_button = QPushButton("Close")
            close_button.clicked.connect(self.accept)
            error_layout.addWidget(close_button)
    
    def retry_connection(self):
        """Retry the database connection"""
        try:
            # Test database connection
            self.db_connected, self.db_error = test_api_table_connection()
            
            if self.db_connected:
                display_message(self, "Success", "Database connection successful. Please close and reopen the API Manager.")
            else:
                display_message(self, "Error", f"Database connection failed: {self.db_error}")
        except Exception as e:
            print(f"Error retrying connection: {str(e)}")
            display_message(self, "Error", f"Failed to retry connection: {str(e)}")

    def create_api_table(self):
        try:
            self.table_container = QWidget()
            self.table_container.setStyleSheet(f"background-color: {COLORS['surface']}; border-radius: 8px; padding: 20px;")
            table_layout = QVBoxLayout(self.table_container)
            
            # Table header
            header_label = QLabel("API Key History")
            # Use body font instead of subheader if it's not defined
            if 'subheader' in FONTS:
                header_label.setFont(FONTS['subheader'])
            else:
                header_label.setFont(FONTS['body'])
                header_label.setStyleSheet("font-weight: bold;")
                
            table_layout.addWidget(header_label)
            
            # Create table
            self.api_table = QTableWidget(0, 3)
            self.api_table.setHorizontalHeaderLabels(["Date Updated", "API Key", "Actions"])
            self.api_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.api_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            self.api_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            
            # Load table data
            self.load_api_table()
            
            table_layout.addWidget(self.api_table)
            
            # Refresh button
            refresh_button = QPushButton("Refresh History")
            refresh_button.setStyleSheet(BUTTON_STYLE)
            refresh_button.clicked.connect(self.load_api_table)
            table_layout.addWidget(refresh_button)
        except Exception as e:
            print(f"Error creating API table: {str(e)}")
            print(traceback.format_exc())
            # Create a basic container with error message
            self.table_container = QWidget()
            error_layout = QVBoxLayout(self.table_container)
            error_label = QLabel(f"Error loading API keys: {str(e)}")
            error_label.setWordWrap(True)
            error_layout.addWidget(error_label)
            
            # Create an empty table so methods that use api_table don't fail
            self.api_table = QTableWidget(0, 3)

    def load_api_table(self):
        try:
            if not hasattr(self, 'api_table') or self.api_table is None:
                print("Error: api_table not initialized")
                return
                
            # Clear table
            self.api_table.setRowCount(0)
            
            # Get all API keys
            api_keys = get_all_api_keys()
            
            # Populate table with only 'apify' keys
            apify_keys = [k for k in api_keys if k['key_name'] == self.api_key_name]
            
            for i, key_data in enumerate(apify_keys):
                self.api_table.insertRow(i)
                
                # Date (we'll use updated_at or a placeholder)
                date_item = QTableWidgetItem(str(key_data.get('updated_at', 'Unknown')))
                date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                self.api_table.setItem(i, 0, date_item)
                
                # API key (masked)
                api_key = key_data['api_key']
                masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"
                key_item = QTableWidgetItem(masked_key)
                key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                self.api_table.setItem(i, 1, key_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 4, 4, 4)
                
                edit_button = QPushButton("Use This Key")
                edit_button.setStyleSheet(BUTTON_STYLE)
                edit_button.clicked.connect(lambda checked, key=key_data['api_key']: self.edit_api_key(key))
                
                actions_layout.addWidget(edit_button)
                
                self.api_table.setCellWidget(i, 2, actions_widget)
        except Exception as e:
            print(f"Error loading API keys: {str(e)}")
            print(traceback.format_exc())
            
            if hasattr(self, 'api_table') and self.api_table:
                # Show error in the table
                self.api_table.setRowCount(1)
                error_item = QTableWidgetItem(f"Error loading API keys: {str(e)}")
                self.api_table.setItem(0, 0, error_item)
                self.api_table.setSpan(0, 0, 1, 3)  # Span all columns
    
    def edit_api_key(self, api_key):
        try:
            # Set input field with the selected API key
            self.api_key_input.setText(api_key)
        except Exception as e:
            print(f"Error setting API key: {str(e)}")
            display_message(self, "Error", f"Failed to set API key: {str(e)}")

    def save_api_key(self):
        try:
            api_key = self.api_key_input.text().strip()
            
            if not api_key:
                display_message(self, "Error", "Please enter an API key value")
                return
            
            # Save to database - always use 'apify' as the key name
            success = set_api_key(self.api_key_name, api_key)
            
            if success:
                display_message(self, "Success", "API key saved successfully")
                self.api_key_input.clear()
                
                # Reload the table if it exists
                if hasattr(self, 'api_table') and self.api_table:
                    self.load_api_table()
            else:
                display_message(self, "Error", "Failed to save API key")
        except Exception as e:
            print(f"Error saving API key: {str(e)}")
            print(traceback.format_exc())
            display_message(self, "Error", f"An error occurred while saving: {str(e)}")
