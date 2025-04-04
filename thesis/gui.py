from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QTextEdit, QWidget, 
                           QFileDialog, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QSplitter, QGridLayout, QComboBox, QSizePolicy, QStackedWidget, QDialog, QTabWidget, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QFont, QPixmap, QImage, QIcon
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
from scraper import scrape_comments
from model import classify_comment
import pandas as pd
from utils import display_message
from styles import (COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE, TABLE_STYLE, TAB_STYLE, 
                   WELCOME_TITLE_STYLE, WELCOME_SUBTITLE_STYLE, WELCOME_DESCRIPTION_STYLE, 
                   GET_STARTED_BUTTON_STYLE, WELCOME_VERSION_STYLE, CONTAINER_STYLE, 
                   DETAIL_TEXT_STYLE, TABLE_ALTERNATE_STYLE, DIALOG_STYLE, 
                   IMAGE_LABEL_STYLE, ABOUT_BUTTON_STYLE, WELCOME_BACKGROUND_STYLE,
                   WELCOME_CONTAINER_STYLE, WELCOME_TITLE_FONT, WELCOME_TITLE_STYLE_DARK,
                   WELCOME_SUBTITLE_FONT, GET_STARTED_BUTTON_DARK_STYLE, 
                   ABOUT_BUTTON_OUTLINE_STYLE, DETAIL_TEXT_SPAN_STYLE)
import tempfile
import time
from PyQt5.QtWidgets import QApplication
from comment_operations import generate_report_from_window
from user import UserMainWindow
from loading_overlay import LoadingOverlay
from stopwords import TAGALOG_STOP_WORDS
import re
from history import HistoryDialog  # Add at top with other imports

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_comments = [] 
        self.comment_metadata = {}  # Initialize comment_metadata
        
        # Create admin menu bar
        self.admin_buttons_container = QWidget()
        self.admin_buttons_container.setFixedHeight(40)  # Fixed height for menu bar
        self.admin_buttons_container.setStyleSheet(f"""
            QWidget {{
                background-color: black;
                padding: 0px;
            }}
            QPushButton {{
                color: {COLORS['text']};
                background-color: transparent;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
        """)
        
        admin_layout = QHBoxLayout(self.admin_buttons_container)
        admin_layout.setContentsMargins(0, 0, 0, 0)
        admin_layout.setSpacing(0)  # Remove spacing between buttons

        # Add app name to the left
        app_name = QLabel("Cyberbullying Detection System - Admin View")
        app_name.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px; padding: 0 16px;")
        app_name.setFont(FONTS['button'])
        admin_layout.addWidget(app_name)
        
        # Add stretch to push remaining buttons to right
        admin_layout.addStretch()

        # Create buttons - right side
        manage_api_button = QPushButton("🔑 Manage API")
        manage_api_button.clicked.connect(self.show_api)
        manage_api_button.setFont(FONTS['button'])
        
        logs_button = QPushButton("📋 User Logs")
        logs_button.clicked.connect(self.show_history)
        logs_button.setFont(FONTS['button'])
        
        sign_out_button = QPushButton("Sign Out")
        sign_out_button.clicked.connect(self.confirm_sign_out)
        sign_out_button.setFont(FONTS['button'])
        
        # Add right-side buttons
        admin_layout.addWidget(manage_api_button)
        admin_layout.addWidget(logs_button)
        admin_layout.addWidget(sign_out_button)
        
        # Hide by default - will show only for admin
        self.admin_buttons_container.hide()
        
        # Initialize UI elements
        self.url_input = QLineEdit()
        self.include_replies = QCheckBox("Include Replies")
        self.scrape_button = QPushButton("Scrape Comments")
        self.scrape_button.clicked.connect(self.scrape_comments)
        
        self.file_input = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        self.process_csv_button = QPushButton("Process CSV")
        self.process_csv_button.clicked.connect(self.process_csv)
        
        self.text_input = QLineEdit()
        self.analyze_button = QPushButton("Analyze Comment")
        self.analyze_button.clicked.connect(self.analyze_single)
        
        # Initialize operation buttons
        self.show_summary_button = QPushButton()
        self.word_cloud_button = QPushButton()
        self.export_all_button = QPushButton()
        self.generate_report_button = QPushButton()
        self.add_remove_button = QPushButton()
        self.export_selected_button = QPushButton()

        # Connect operation button signals
        self.show_summary_button.clicked.connect(self.show_summary)
        self.word_cloud_button.clicked.connect(self.show_word_cloud)
        self.export_all_button.clicked.connect(self.export_all)
        self.generate_report_button.clicked.connect(self.generate_report)
        self.add_remove_button.clicked.connect(self.toggle_list_status)
        self.export_selected_button.clicked.connect(self.export_selected)

        # Initially disable row operation buttons
        self.add_remove_button.setEnabled(False)
        self.export_selected_button.setEnabled(False)

        # Initialize tab counters
        self.csv_tab_count = 1
        self.url_tab_count = 1
        
        self.setWindowTitle("Cyber Boolean")
        self.showFullScreen()  # Makes the window fullscreen
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")

        # Set window icon
        app_icon = QIcon("assets/applogo.png")
        self.setWindowIcon(app_icon)

        self.central_widget = QStackedWidget()  
        self.setCentralWidget(self.central_widget)

        self.init_welcome_screen()
        self.init_main_ui()

        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self)

    def init_welcome_screen(self):
        welcome_widget = QWidget()
        welcome_widget.setStyleSheet(WELCOME_BACKGROUND_STYLE)
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setSpacing(0)
        welcome_layout.setContentsMargins(90, 0, 90, 0)

        welcome_layout.addStretch(1)

        header_container = QWidget()
        header_container.setStyleSheet(WELCOME_CONTAINER_STYLE)
        header_layout = QVBoxLayout(header_container)
        header_layout.setSpacing(10)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Title parts
        title_label = QLabel("Cyberbullying")
        title_label.setFont(WELCOME_TITLE_FONT)
        title_label.setStyleSheet(WELCOME_TITLE_STYLE_DARK)
        title_label.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(title_label)

        secondary_title = QLabel("Detection")
        secondary_title.setFont(WELCOME_TITLE_FONT)
        secondary_title.setStyleSheet(WELCOME_TITLE_STYLE_DARK)
        secondary_title.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(secondary_title)

        subtitle_label = QLabel("Tagalog and English Cyberbullying Detection System")
        subtitle_label.setFont(WELCOME_SUBTITLE_FONT)
        subtitle_label.setStyleSheet(WELCOME_TITLE_STYLE_DARK)
        subtitle_label.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(subtitle_label)

        welcome_layout.addWidget(header_container)
        welcome_layout.addSpacing(60)

        button_container = QWidget()
        button_container.setStyleSheet(WELCOME_CONTAINER_STYLE)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(20)

        self.get_started_button = QPushButton("Get Started")
        self.get_started_button.setFont(FONTS['button'])
        self.get_started_button.setStyleSheet(GET_STARTED_BUTTON_DARK_STYLE)
        self.get_started_button.clicked.connect(self.show_login)
        button_layout.addWidget(self.get_started_button)

        about_button = QPushButton("About")
        about_button.setFont(FONTS['button'])
        about_button.setStyleSheet(ABOUT_BUTTON_OUTLINE_STYLE)
        about_button.clicked.connect(self.show_about)
        button_layout.addWidget(about_button)
        
        button_layout.addStretch()
        welcome_layout.addWidget(button_container)

        welcome_layout.addStretch(1)
        welcome_layout.addSpacing(40)
        
        version_label = QLabel("Version 1.0")
        version_label.setAlignment(Qt.AlignLeft)
        version_label.setStyleSheet(WELCOME_VERSION_STYLE)
        welcome_layout.addWidget(version_label)
        
        welcome_layout.addSpacing(20)

        self.central_widget.addWidget(welcome_widget)

    def show_login(self):
        """Show login dialog and handle user role"""
        from login import LoginWindow
        login_dialog = LoginWindow(self)
        result = login_dialog.exec_()
        
        if result == QDialog.Accepted:
            role = login_dialog.get_role()
            username = login_dialog.get_username()
            
            if role and role.lower() == "admin":
                self.central_widget.setCurrentIndex(1)  # Switch to main UI
                self.admin_buttons_container.show()  # Show admin buttons
                self.showFullScreen()
            elif role and role.lower() == "user":
                try:
                    self.user_window = UserMainWindow()
                    self.user_window.set_current_user(username)  # Set username first
                    self.user_window.set_main_window(self)      # Set main window reference
                    self.hide()                                 # Hide main window
                    self.user_window.init_main_ui()             # Initialize UI
                    self.user_window.showFullScreen()           # Show window last
                except Exception as e:
                    display_message(self, "Error", f"Error initializing user interface: {e}")
                    self.central_widget.setCurrentIndex(0)
            else:
                display_message(self, "Error", f"Invalid role: {role}")
                self.central_widget.setCurrentIndex(0)
        else:
            self.central_widget.setCurrentIndex(0)

    def show_user_ui(self):
        """Show user interface"""
        try:
            self.user_window = UserMainWindow()
            self.user_window.set_main_window(self)
            self.user_window.show()
            self.hide()
        except Exception as e:
            display_message(self, "Error", f"Error opening user interface: {e}")
            self.show()

    def show_main_ui(self):
        self.central_widget.setCurrentIndex(1)

    def init_main_ui(self):
        main_widget = QWidget()
        self.central_widget.addWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margins completely
        
        # Add admin buttons at the top with no margins
        self.admin_buttons_container.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.admin_buttons_container)
        
        # Add a container for the main content with proper padding
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        # Initialize the rest of the UI in the content container
        self.init_ui()
        
        # Add the content container to the main layout
        self.layout.addWidget(content_container)

    def init_ui(self):
        # Input Container with enhanced styling and better spacing
        input_container = QWidget()
        input_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        input_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        
        # Main vertical layout with improved spacing
        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(20)
        input_layout.setContentsMargins(20, 20, 20, 20)

        # Add responsive grid layout for input sections
        input_grid = QGridLayout()
        input_grid.setSpacing(15)
        input_grid.setContentsMargins(0, 0, 0, 0)

        # Facebook Post Section with enhanced styling
        fb_section = QWidget()
        fb_layout = QVBoxLayout(fb_section)
        fb_layout.setSpacing(10)

        # Enhanced section headers with icons
        fb_header = QHBoxLayout()
        fb_icon = QLabel()
        fb_icon.setPixmap(QIcon("assets/fb_icon.png").pixmap(QSize(20, 20)))
        fb_title = QLabel("Facebook Post")
        fb_title.setFont(FONTS['header'])
        fb_title.setStyleSheet(f"color: {COLORS['text']};")
        fb_header.addWidget(fb_icon)
        fb_header.addWidget(fb_title)
        fb_header.addStretch()
        fb_layout.addLayout(fb_header)

        # Enhanced URL input
        url_container = QWidget()
        url_layout = QVBoxLayout(url_container)
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.setSpacing(5)

        self.url_input.setStyleSheet(INPUT_STYLE)
        self.url_input.setPlaceholderText("Enter Facebook Post URL")
        url_layout.addWidget(self.url_input)

        # Checkbox with better styling
        self.include_replies.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text']};
                font-size: 13px;
                padding: 5px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {COLORS['border']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['primary']};
                border: 2px solid {COLORS['primary']};
            }}
        """)
        url_layout.addWidget(self.include_replies)
        fb_layout.addWidget(url_container)

        # Enhanced scrape button
        self.scrape_button.setFont(FONTS['button'])
        self.scrape_button.setStyleSheet(f"""
            {BUTTON_STYLE}
            QPushButton {{
                padding: 12px;
                border-radius: 6px;
            }}
        """)
        fb_layout.addWidget(self.scrape_button)
        
        # Add Facebook section to grid
        input_grid.addWidget(fb_section, 0, 0)

        # CSV File Section - Made more compact
        csv_section = QWidget()
        csv_section.setStyleSheet(CONTAINER_STYLE)
        csv_layout = QVBoxLayout(csv_section)
        csv_layout.setSpacing(5)  # Reduced spacing
        csv_layout.setContentsMargins(8, 8, 8, 8)  # Reduced padding
        
        csv_title = QLabel("CSV File")
        csv_title.setFont(FONTS['button'])  # Smaller font
        csv_title.setAlignment(Qt.AlignCenter)
        
        file_browse_layout = QHBoxLayout()
        self.file_input = QLineEdit()
        self.file_input.setStyleSheet(INPUT_STYLE)
        self.file_input.setPlaceholderText("Select CSV file")
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.setFont(FONTS['button'])
        self.browse_button.setStyleSheet(BUTTON_STYLE)
        self.browse_button.setFixedWidth(80)
        self.browse_button.clicked.connect(self.browse_file)
        
        file_browse_layout.addWidget(self.file_input)
        file_browse_layout.addWidget(self.browse_button)
        
        self.process_csv_button = QPushButton("Process CSV")
        self.process_csv_button.setFont(FONTS['button'])
        self.process_csv_button.setStyleSheet(BUTTON_STYLE)
        self.process_csv_button.clicked.connect(self.process_csv)
        
        csv_layout.addWidget(csv_title)
        csv_layout.addLayout(file_browse_layout)
        csv_layout.addWidget(self.process_csv_button)
        input_grid.addWidget(csv_section, 0, 1)

        # Direct Input Section - Made more compact
        direct_section = QWidget()
        direct_section.setStyleSheet(CONTAINER_STYLE)
        direct_layout = QVBoxLayout(direct_section)
        direct_layout.setSpacing(5)  # Reduced spacing
        direct_layout.setContentsMargins(8, 8, 8, 8)
        direct_title = QLabel("Direct Input")
        direct_title.setFont(FONTS['button'])  # Smaller font
        direct_title.setAlignment(Qt.AlignCenter)
        self.text_input = QLineEdit()
        self.text_input.setStyleSheet(INPUT_STYLE)
        self.text_input.setPlaceholderText("Enter comment to analyze")
        self.analyze_button = QPushButton("Analyze Comment")
        self.analyze_button.setFont(FONTS['button'])
        self.analyze_button.setStyleSheet(BUTTON_STYLE)
        self.analyze_button.clicked.connect(self.analyze_single)
        direct_layout.addWidget(direct_title)
        direct_layout.addWidget(self.text_input)
        direct_layout.addWidget(self.analyze_button)
        input_grid.addWidget(direct_section, 0, 2)

        # Add input grid to main layout
        input_layout.addLayout(input_grid)
        
        # Add input container to main layout
        self.layout.addWidget(input_container)

        # Create responsive splitter for table and details
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {COLORS['border']};
                margin: 1px;
            }}
            QSplitter::handle:hover {{
                background: {COLORS['hover']};
            }}
        """)

        # Table Container
        table_container = QWidget()
        table_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(TAB_STYLE)
        self.initial_message = QLabel("No analysis performed yet.\nResults will appear here.")
        self.initial_message.setAlignment(Qt.AlignCenter)
        self.initial_message.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px;")
        table_layout.addWidget(self.initial_message)
        
        table_layout.addWidget(self.tab_widget)
        self.tab_widget.hide()  # Hide tab widget initially

        # Initialize tab counters
        self.csv_tab_count = 1
        self.url_tab_count = 1
        
        # Dictionary to store tab references
        self.tabs = {}

        splitter.addWidget(table_container)

        # Details Panel with enhanced styling
        details_container = QWidget()
        details_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        details_layout = QVBoxLayout(details_container)
        details_layout.setSpacing(15)
        details_layout.setContentsMargins(15, 0, 0, 0)

        # Details section with better visual hierarchy
        details_section = QWidget()
        details_section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        details_section_layout = QVBoxLayout(details_section)
        details_section_layout.setSpacing(10)
        details_section_layout.setContentsMargins(15, 15, 15, 15)

        # Details header with icon
        details_header = QHBoxLayout()
        details_title = QLabel("Comment Details")
        details_title.setFont(FONTS['header'])
        details_title.setStyleSheet(f"color: {COLORS['text']};")
        details_header.addWidget(details_title)
        details_header.addStretch()
        details_section_layout.addLayout(details_header)

        # Enhanced details text area
        self.details_text_edit = QTextEdit()
        self.details_text_edit.setReadOnly(True)
        self.details_text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
            }}
            QTextEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """)
        details_section_layout.addWidget(self.details_text_edit)
        details_layout.addWidget(details_section)

        # Row Operations Section - Enhanced styling
        row_ops_section = QWidget()
        row_ops_section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        row_ops_layout = QVBoxLayout(row_ops_section)
        row_ops_layout.setSpacing(12)
        row_ops_layout.setContentsMargins(15, 15, 15, 15)

        row_ops_title = QLabel("Row Operations")
        row_ops_title.setFont(FONTS['header'])
        row_ops_title.setStyleSheet(f"color: {COLORS['text']};")
        row_ops_layout.addWidget(row_ops_title)

        # Row operation buttons grid
        row_grid = QGridLayout()
        row_grid.setSpacing(10)
        row_grid.setContentsMargins(0, 5, 0, 5)

        row_button_configs = [
            (self.add_remove_button, "➕ Add to List", 0, 0),
            (self.export_selected_button, "📋 Export List", 0, 1)
        ]

        for button, text, row, col in row_button_configs:
            button.setText(text)
            button.setFont(FONTS['button'])
            button.setStyleSheet(f"""
                {BUTTON_STYLE}
                QPushButton {{
                    padding: 12px 20px;
                    min-width: 140px;
                }}
            """)
            row_grid.addWidget(button, row, col)

        row_ops_layout.addLayout(row_grid)
        details_layout.addWidget(row_ops_section)

        # Dataset Operations Section - Better organization and spacing
        dataset_ops_section = QWidget()
        dataset_ops_section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        dataset_ops_layout = QVBoxLayout(dataset_ops_section)
        dataset_ops_layout.setSpacing(12)
        dataset_ops_layout.setContentsMargins(15, 15, 15, 15)

        dataset_ops_title = QLabel("Dataset Operations")
        dataset_ops_title.setFont(FONTS['header'])
        dataset_ops_title.setStyleSheet(f"color: {COLORS['text']};")
        dataset_ops_layout.addWidget(dataset_ops_title)

        # Create grid layout for operation buttons with proper spacing
        ops_grid = QGridLayout()
        ops_grid.setSpacing(10)
        ops_grid.setContentsMargins(0, 5, 0, 5)

        # Dataset operation buttons with icons
        button_configs = [
            (self.show_summary_button, "📊 Summary", 0, 0),
            (self.word_cloud_button, "☁️ Word Cloud", 0, 1),
            (self.export_all_button, "📤 Export All", 0, 2),
            (self.generate_report_button, "📝 Generate Report", 1, 0, 3)  # span 3 columns
        ]

        for button, text, row, col, *span in button_configs:
            button.setText(text)
            button.setFont(FONTS['button'])
            button.setStyleSheet(BUTTON_STYLE)
            button.setEnabled(False)  # Initially disabled
            if span:
                ops_grid.addWidget(button, row, col, 1, span[0])  # Use column span if provided
            else:
                ops_grid.addWidget(button, row, col)

        dataset_ops_layout.addLayout(ops_grid)
        details_layout.addWidget(dataset_ops_section)

        splitter.addWidget(details_container)

        # Set initial sizes for the splitter to make them equal
        splitter.setSizes([self.width() // 2, self.width() // 2]) 
        splitter.setStretchFactor(0, 1) 
        splitter.setStretchFactor(1, 1)

        # Add splitter to main layout
        self.layout.addWidget(splitter)

        # Set layout stretch factors
        self.layout.setStretch(0, 0)  
        self.layout.setStretch(1, 1) 

    def show_loading(self, show=True):
        if show:
            self.loading_overlay.show()
        else:
            self.loading_overlay.hide()

    def confirm_sign_out(self):
        """Show confirmation dialog before signing out"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Sign Out")
        msg.setText("Are you sure you want to sign out?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        # Style the message box
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
            }}
            QPushButton {{
                {BUTTON_STYLE}
                min-width: 100px;
            }}
        """)
        
        if msg.exec_() == QMessageBox.Yes:
            self.central_widget.setCurrentIndex(0)

    def scrape_comments(self):
        url = self.url_input.text()
        if not url:
            display_message(self, "Error", "Please enter a URL.")
            return

        try:
            self.show_loading(True)
            QApplication.processEvents()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
                temp_path = temp_file.name
            
            # Pass include_replies flag to scrape_comments
            scrape_comments(url, temp_path, self.include_replies.isChecked())
            df = pd.read_csv(temp_path)
            
            # Filter out replies if not included
            if not self.include_replies.isChecked():
                df = df[~df['Is Reply']]
                
            # Store additional comment metadata
            self.comment_metadata = {}
            for _, row in df.iterrows():
                self.comment_metadata[row['Text']] = {
                    'profile_name': row['Profile Name'],
                    'profile_picture': row['Profile Picture'],
                    'date': row['Date'],
                    'likes_count': row['Likes Count'],
                    'profile_id': row['Profile ID'],
                    'is_reply': row['Is Reply'],
                    'reply_to': row['Reply To']
                }
            
            comments = df['Text'].tolist()
            self.populate_table(comments)
        except Exception as e:
            display_message(self, "Error", f"Error scraping comments: {e}")
        finally:
            self.show_loading(False)  # Hide loading overlay

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.file_input.setText(file_path)

    def process_csv(self):
        if not self.file_input.text():
            display_message(self, "Error", "Please select a CSV file first")
            return
        try:
            self.show_loading(True)  # Show loading overlay
            QApplication.processEvents()  # Ensure the UI updates
            
            df = pd.read_csv(self.file_input.text())
            comments = df.iloc[:, 0].tolist()
            
            # Create metadata for CSV comments
            self.comment_metadata = {}
            for comment in comments:
                self.comment_metadata[comment] = {
                    'profile_name': 'CSV Input',
                    'profile_picture': '',
                    'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'likes_count': 'N/A',
                    'profile_id': 'N/A'
                }
            
            self.populate_table(comments)
        except Exception as e:
            display_message(self, "Error", f"Error reading CSV file: {e}")
        finally:
            self.show_loading(False)  # Hide loading overlay

    def analyze_single(self):
        if not self.text_input.text():
            display_message(self, "Error", "Please enter a comment to analyze")
            return
        
        try:
            self.show_loading(True)  # Show loading overlay
            QApplication.processEvents()  # Ensure the UI updates
            
            # Create metadata for the direct input comment
            comment = self.text_input.text()
            self.comment_metadata = {
                comment: {
                    'profile_name': 'Direct Input',
                    'profile_picture': '',
                    'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'likes_count': 'N/A',
                    'profile_id': 'N/A'
                }
            }
            
            self.populate_table([comment])
        finally:
            self.show_loading(False)  # Hide loading overlay

    def create_empty_tab(self, tab_type):
        """Create a new empty tab with table"""
        if tab_type == "Direct Inputs" and "Direct Inputs" in self.tabs:
            return self.tabs["Direct Inputs"].findChild(QTableWidget)

        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        
        # Header layout with table title, search bar, and sort dropdown
        header_layout = QHBoxLayout()
        table_title = QLabel("Comments")
        table_title.setFont(FONTS['header'])
        header_layout.addWidget(table_title)
        
        # Add search bar
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search comments...")
        search_bar.setStyleSheet(INPUT_STYLE)
        search_bar.setMaximumWidth(300)
        search_layout.addWidget(search_bar)
        
        header_layout.addWidget(search_container)
        header_layout.addStretch()
        
        sort_combo = QComboBox()
        sort_combo.addItems([
            "Sort by Comments (A-Z)",
            "Sort by Comments (Z-A)",
            "Sort by Prediction (A-Z)",
            "Sort by Confidence (High to Low)",
            "Sort by Confidence (Low to High)",
            "Show Replies Only"  # Add this option
        ])
        header_layout.addWidget(sort_combo)
        tab_layout.addLayout(header_layout)

        # Create table
        table = QTableWidget()
        table.setSortingEnabled(True)
        table.setStyleSheet(TABLE_ALTERNATE_STYLE)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Comment", "Prediction", "Confidence"])
        table.setAlternatingRowColors(True)

        # Adjust column sizes
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        table.setColumnWidth(1, 150)
        table.setColumnWidth(2, 100)

        table.setWordWrap(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.itemSelectionChanged.connect(self.update_details_panel)
        
        # Store sort combo and connect it
        table.sort_combo = sort_combo
        sort_combo.currentIndexChanged.connect(lambda: self.sort_table(table))
        
        tab_layout.addWidget(table)
        
        # Connect search functionality
        def filter_table():
            search_text = search_bar.text().lower()
            for row in range(table.rowCount()):
                comment = table.item(row, 0).text().lower()
                table.setRowHidden(row, search_text not in comment)
        
        search_bar.textChanged.connect(filter_table)
        
        # Store search bar reference
        table.search_bar = search_bar
        
        # Add tab to widget and store reference
        self.tab_widget.addTab(tab, tab_type)
        self.tabs[tab_type] = tab
        
        # Enable close buttons for tabs
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Show tab widget and hide initial message when first tab is created
        if (self.tab_widget.isHidden()):
            self.initial_message.hide()
            self.tab_widget.show()
            # Enable dataset operations when first tab is created
            self.enable_dataset_operations(True)
            
        return table

    def close_tab(self, index):
        """Close the tab and clean up resources"""
        # Get tab name before removing
        tab_name = self.tab_widget.tabText(index)
        
        # Remove tab and its reference
        self.tab_widget.removeTab(index)
        if tab_name in self.tabs:
            del self.tabs[tab_name]
            
        # If no tabs left, show initial message and disable dataset operations
        if self.tab_widget.count() == 0:
            self.tab_widget.hide()
            self.initial_message.show()
            self.enable_dataset_operations(False)

    def enable_dataset_operations(self, enable=True):
        """Enable or disable dataset operation buttons"""
        dataset_buttons = [
            self.show_summary_button,
            self.word_cloud_button,
            self.export_all_button,
            self.generate_report_button
        ]
        for btn in dataset_buttons:
            btn.setEnabled(enable)

    def get_current_table(self):
        """Get the table widget from the current tab"""
        current_tab = self.tab_widget.currentWidget()
        return current_tab.findChild(QTableWidget)

    def populate_table(self, comments):
        """Create new tab and populate it based on input type"""
        # Store the input source before clearing
        file_path = self.file_input.text()
        url = self.url_input.text()

        # Clear inputs after checking
        self.file_input.clear()
        self.url_input.clear()

        if len(comments) == 1:  # Direct input
            tab_name = "Direct Inputs"
        elif file_path:  # CSV input
            # Get filename without path and extension
            file_name = file_path.split('/')[-1].split('\\')[-1]  # Handle both Unix and Windows paths
            file_name = file_name.rsplit('.', 1)[0]  # Remove extension
            
            # Truncate if longer than 20 characters
            if len(file_name) > 20:
                file_name = file_name[:17] + "..."
            
            # Check if tab with this name already exists
            if file_name in self.tabs:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Question)
                msg.setWindowTitle("Duplicate File Name")
                msg.setText(f"A tab with name '{file_name}' already exists.")
                msg.setInformativeText("Do you want to replace the existing tab or create a new one?")
                replace_button = msg.addButton("Replace", QMessageBox.YesRole)
                new_tab_button = msg.addButton("Create New", QMessageBox.NoRole)
                msg.addButton("Cancel", QMessageBox.RejectRole)
                
                msg.exec_()
                
                if msg.clickedButton() == replace_button:
                    # Remove existing tab
                    old_tab_index = self.tab_widget.indexOf(self.tabs[file_name])
                    self.tab_widget.removeTab(old_tab_index)
                    del self.tabs[file_name]
                    tab_name = file_name
                elif msg.clickedButton() == new_tab_button:
                    # Find next available number
                    counter = 2
                    while f"{file_name} ({counter})" in self.tabs:
                        counter += 1
                    tab_name = f"{file_name} ({counter})"
                else:
                    # User clicked Cancel
                    return
            else:
                tab_name = file_name
                
        elif url:  # Facebook post
            tab_name = f"Facebook Post {self.url_tab_count}"
            self.url_tab_count += 1
        else:  # Fallback case
            tab_name = f"Analysis {self.csv_tab_count + self.url_tab_count}"

        # Create new tab and get its table
        table = self.create_empty_tab(tab_name)
        
        # Enable dataset operations since we now have data
        self.enable_dataset_operations(True)

        for comment in comments:
            metadata = self.comment_metadata.get(comment, {})
            is_reply = metadata.get('is_reply', False)
            
            prediction, confidence = classify_comment(comment)
            row_position = table.rowCount()
            table.insertRow(row_position)

            # Create display text with reply indicator
            display_text = comment
            if is_reply:
                reply_to = metadata.get('reply_to', '')
                comment_item = QTableWidgetItem(display_text)
                comment_item.setData(Qt.UserRole, comment)  # Store original comment
                comment_item.setData(Qt.DisplayRole, f" [↪ Reply] {display_text}") 
                comment_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            else:
                comment_item = QTableWidgetItem(display_text)
                comment_item.setData(Qt.UserRole, comment)
                comment_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            # Add subtle background color for reply comments
            if is_reply:
                lighter_surface = QColor(COLORS['surface']).lighter(105)
                comment_item.setBackground(lighter_surface)

            prediction_item = QTableWidgetItem(prediction)
            prediction_item.setTextAlignment(Qt.AlignCenter)
            if prediction == "Cyberbullying":
                prediction_item.setForeground(QColor(COLORS['bullying']))
            else:
                prediction_item.setForeground(QColor(COLORS['normal']))

            confidence_item = QTableWidgetItem(f"{confidence:.2%}")
            confidence_item.setTextAlignment(Qt.AlignCenter)

            table.setItem(row_position, 0, comment_item)
            table.setItem(row_position, 1, prediction_item)
            table.setItem(row_position, 2, confidence_item)

            table.resizeRowToContents(row_position)

            if comment in self.selected_comments:
                for col in range(table.columnCount()):
                    table.item(row_position, col).setBackground(QColor(COLORS['highlight']))

        # Switch to the new tab
        tab_index = self.tab_widget.indexOf(self.tabs[tab_name])
        self.tab_widget.setCurrentIndex(tab_index)

    def sort_table(self, table):
        """Sort the specified table based on its combo box selection"""
        sort_combo = table.sort_combo
        index = sort_combo.currentIndex()
        
        # First show all rows when not in "Show Replies Only" mode
        if index != 5:
            for row in range(table.rowCount()):
                table.setRowHidden(row, False)
        
        # Handle the replies filter
        if index == 5:  # "Show Replies Only"
            for row in range(table.rowCount()):
                text = table.item(row, 0).text()
                is_reply = text.startswith(" [↪ Reply]") or text.startswith(" ↪ Reply")
                table.setRowHidden(row, not is_reply)
            return
            
        # Regular sorting
        if index == 0:
            table.sortItems(0, Qt.AscendingOrder)
        elif index == 1:
            table.sortItems(0, Qt.DescendingOrder)
        elif index == 2:
            table.sortItems(1, Qt.AscendingOrder)
        elif index == 3:
            table.sortItems(2, Qt.DescendingOrder)
        elif index == 4:
            table.sortItems(2, Qt.AscendingOrder)

    def update_details_panel(self):
        selected_items = self.get_current_table().selectedItems()
        if not selected_items:
            self.details_text_edit.clear()
            # Disable row operations
            self.add_remove_button.setEnabled(False)
            self.export_selected_button.setEnabled(False)
            
            # Keep dataset operations enabled if there's data
            has_data = self.tab_widget.count() > 0
            self.enable_dataset_operations(has_data)
            return

        # Enable row operation buttons when row is selected
        self.add_remove_button.setEnabled(True)
        self.export_selected_button.setEnabled(True)

        # Make sure dataset operations are enabled when there's data
        self.enable_dataset_operations(True)

        row = selected_items[0].row()
        comment = self.get_current_table().item(row, 0).text()
        prediction = self.get_current_table().item(row, 1).text()
        confidence = self.get_current_table().item(row, 2).text()
        
        # Get metadata for the comment if available
        metadata = self.comment_metadata.get(comment, {
            'profile_name': 'N/A',
            'profile_picture': '',
            'date': 'N/A',
            'likes_count': 'N/A',
            'profile_id': 'N/A',
            'is_reply': False,
            'reply_to': ''
        })
        
        commenter = metadata.get('profile_name', 'N/A')
        date = metadata.get('date', 'N/A')
        likes = metadata.get('likes_count', 'N/A')
        is_reply = metadata.get('is_reply', False)
        reply_to = metadata.get('reply_to', '')

        # Update add/remove button text based on list status
        if comment in self.selected_comments:
            self.add_remove_button.setText("➖ Remove from List")
        else:
            self.add_remove_button.setText("➕ Add to List")

        # Rules text
        rules_broken = ["Harassment", "Hate Speech", "Threatening Language"] if prediction == "Cyberbullying" else []

        # Set text contents with additional metadata and larger font size
        self.details_text_edit.clear()
        
        # Create spans with larger font size
        def make_text(label, value):
            return f'<span style="{DETAIL_TEXT_SPAN_STYLE}"><b>{label}</b>{value}</span>'

        self.details_text_edit.append(make_text("Comment:\n", f"{comment}\n"))
        self.details_text_edit.append(make_text("Commenter: ", f"{commenter}\n"))
        self.details_text_edit.append(make_text("Date: ", f"{date}\n"))
        self.details_text_edit.append(make_text("Likes: ", f"{likes}\n"))
        
        # Add reply information if it's a reply
        if is_reply and reply_to:
            # Find row number and parent comment details
            current_table = self.get_current_table()
            for i in range(current_table.rowCount()):
                parent_text = current_table.item(i, 0).data(Qt.UserRole)
                if parent_text == reply_to:
                    parent_metadata = self.comment_metadata.get(reply_to, {})
                    parent_name = parent_metadata.get('profile_name', 'Unknown')
                    parent_date = parent_metadata.get('date', 'N/A')
                    
                    self.details_text_edit.append("\n" + make_text("Reply Information:\n", ""))
                    self.details_text_edit.append(make_text("Row #", f"{i+1}\n"))
                    self.details_text_edit.append(make_text("Replying to: ", f"{parent_name}\n"))
                    self.details_text_edit.append(make_text("Original Comment: ", f"{reply_to}\n"))
                    self.details_text_edit.append(make_text("Date: ", f"{parent_date}\n"))
                    break
            else:
                self.details_text_edit.append("\n" + make_text("Reply Information:\n", ""))
                self.details_text_edit.append(make_text("Replying to: ", f"{reply_to}\n"))

        self.details_text_edit.append(make_text("Classification: ", f"{prediction}\n"))
        self.details_text_edit.append(make_text("Confidence: ", f"{confidence}\n"))
        self.details_text_edit.append(make_text("Status: ", f"{'In List' if comment in self.selected_comments else 'Not in List'}\n"))
        self.details_text_edit.append(make_text("Rules Broken:", ""))

        cursor = self.details_text_edit.textCursor()
        for rule in rules_broken:
            cursor.insertHtml(f'<span style="font-size: 16px; background-color: {COLORS["secondary"]}; border-radius: 4px; padding: 2px 4px; margin: 2px; display: inline-block;">{rule}</span> ')
        self.details_text_edit.setTextCursor(cursor)

    def show_summary(self):
        total_comments = self.get_current_table().rowCount()
        if total_comments == 0:
            display_message(self, "Error", "No comments to summarize")
            return

        cyberbullying_count = 0
        normal_count = 0
        high_confidence_count = 0  # Comments with confidence > 90%

        for row in range(total_comments):
            prediction = self.get_current_table().item(row, 1).text()
            confidence = float(self.get_current_table().item(row, 2).text().strip('%')) / 100

            if prediction == "Cyberbullying":
                cyberbullying_count += 1
            else:
                normal_count += 1

            if confidence > 0.9:
                high_confidence_count += 1

        summary_text = (
            f"Analysis Summary:\n\n"
            f"Total Comments Analyzed: {total_comments}\n"
            f"Cyberbullying Comments: {cyberbullying_count} ({(cyberbullying_count/total_comments)*100:.1f}%)\n"
            f"Normal Comments: {normal_count} ({(normal_count/total_comments)*100:.1f}%)\n"
            f"High Confidence Predictions: {high_confidence_count} ({(high_confidence_count/total_comments)*100:.1f}%)\n"
            f"Comments in Selection List: {len(self.selected_comments)}"
        )
        
        # Display summary in a simple dialog
        display_message(self, "Results Summary", summary_text)

    def show_word_cloud(self):
        """Generate and display word cloud visualization"""
        total_comments = self.get_current_table().rowCount()
        if total_comments == 0:
            display_message(self, "Error", "No comments to visualize")
            return

        all_comments = []
        for row in range(total_comments):
            comment = self.get_current_table().item(row, 0).text()
            all_comments.append(comment)

        try:
            # Preprocess comments
            def preprocess_text(text):
                text = text.lower()
                text = re.sub(r'http\S+|www\S+|https\S+', '', text)
                text = re.sub(r'[^\w\s]', '', text)
                text = ' '.join(text.split())
                return text

            processed_comments = [preprocess_text(comment) for comment in all_comments]
            
            wordcloud = WordCloud(
                width=800, 
                height=400,
                background_color='white',
                max_words=100,
                stopwords=TAGALOG_STOP_WORDS,
                collocations=False
            ).generate(' '.join(processed_comments))

            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            
            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
            plt.close()
            buf.seek(0)
            
            image = QImage.fromData(buf.getvalue())
            pixmap = QPixmap.fromImage(image)

            # Create dialog for word cloud
            dialog = QDialog(self)
            dialog.setWindowTitle("Word Cloud Visualization")
            dialog.setMinimumWidth(800)
            dialog.setStyleSheet(DIALOG_STYLE)
            layout = QVBoxLayout(dialog)

            # Add word cloud
            image_label = QLabel()
            image_label.setStyleSheet(IMAGE_LABEL_STYLE)
            scaled_pixmap = pixmap.scaled(700, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(image_label)

            # Add close button
            close_button = QPushButton("Close")
            close_button.setStyleSheet(BUTTON_STYLE)
            close_button.clicked.connect(dialog.close)
            layout.addWidget(close_button, alignment=Qt.AlignCenter)

            dialog.exec_()

        except Exception as e:
            display_message(self, "Error", f"Error generating word cloud: {e}")

    def toggle_list_status(self):
        selected_items = self.get_current_table().selectedItems()
        if not selected_items:
            display_message(self, "Error", "Please select a comment to add or remove")
            return

        comment = self.get_current_table().item(selected_items[0].row(), 0).text()
        row = selected_items[0].row()
        if comment in self.selected_comments:
            self.selected_comments.remove(comment)
            display_message(self, "Success", "Comment removed from list")
            # Reset row color
            for col in range(self.get_current_table().columnCount()):
                self.get_current_table().item(row, col).setBackground(QColor(COLORS['normal']))
        else:
            self.selected_comments.append(comment)
            display_message(self, "Success", "Comment added to list")
            # Highlight row color
            for col in range(self.get_current_table().columnCount()):
                self.get_current_table().item(row, col).setBackground(QColor(COLORS['highlight']))
        self.update_details_panel()

    def export_selected(self):
        if not self.selected_comments:
            display_message(self, "Error", "No comments selected for export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Selected Comments", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                df = pd.DataFrame(self.selected_comments, columns=['Comment'])
                df.to_csv(file_path, index=False)
                display_message(self, "Success", "Selected comments exported successfully")
            except Exception as e:
                display_message(self, "Error", f"Error exporting comments: {e}")

    def export_all(self):
        if self.get_current_table().rowCount() == 0:
            display_message(self, "Error", "No comments to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export All Comments", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                comments = []
                predictions = []
                confidences = []

                for row in range(self.get_current_table().rowCount()):
                    comments.append(self.get_current_table().item(row, 0).text())
                    predictions.append(self.get_current_table().item(row, 1).text())
                    confidences.append(self.get_current_table().item(row, 2).text())

                df = pd.DataFrame({
                    'Comment': comments,
                    'Prediction': predictions,
                    'Confidence': confidences
                })
                df.to_csv(file_path, index=False)
                display_message(self, "Success", "All comments exported successfully")
            except Exception as e:
                display_message(self, "Error", f"Error exporting comments: {e}")

    def generate_report(self):
        """Generate report by calling the report generation function"""
        generate_report_from_window(self)

    def show_history(self):
        """Show the history dialog"""
        dialog = HistoryDialog(self)
        dialog.exec_()

    def show_api(self):
        """Show the API manager dialog"""
        from api_manager import APIManagerDialog
        dialog = APIManagerDialog(self)
        dialog.exec_()

    def show_about(self):
        """Show the About dialog"""
        from about import AboutDialog
        about_dialog = AboutDialog(self)
        about_dialog.exec_()