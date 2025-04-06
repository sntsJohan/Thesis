from PyQt5.QtWidgets import (QDialog, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QTextEdit, QWidget, 
                           QFileDialog, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QSplitter, QGridLayout, QComboBox, 
                           QSizePolicy, QStackedWidget, QTabWidget, QMessageBox, 
                           QCheckBox, QApplication)
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
from comment_operations import generate_report_user
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE, DIALOG_STYLE, TABLE_ALTERNATE_STYLE, TABLE_STYLE, TAB_STYLE, CONTAINER_STYLE
import tempfile
import time
import re
from stopwords import TAGALOG_STOP_WORDS

# Reuse the LoadingOverlay from the main GUI
from loading_overlay import LoadingOverlay
from db_config import log_user_action  # Add this import

class UserMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyber Bullying Detection System - User View")
        self.showFullScreen()
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")
        
        # Set window icon
        self.setWindowIcon(QIcon("assets/applogo.png"))
        
        # Create top menu bar
        self.menu_bar = QWidget()
        self.menu_bar.setFixedHeight(40)
        self.menu_bar.setStyleSheet(f"""
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
        
        # Create menu bar layout
        menu_layout = QHBoxLayout(self.menu_bar)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)
        
        # Add app name on the left
        app_name = QLabel("Cyberbullying Detection System - User View")
        app_name.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px; padding: 0 16px;")
        app_name.setFont(FONTS['button'])
        menu_layout.addWidget(app_name)
        
        # Add stretch to push sign out button to right
        menu_layout.addStretch()
        
        # Create sign out button - right side
        sign_out_button = QPushButton("Sign Out")
        sign_out_button.clicked.connect(self.confirm_sign_out)
        sign_out_button.setFont(FONTS['button'])
        menu_layout.addWidget(sign_out_button)
        
        # Initialize central widget but don't set up UI yet
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self)

        # Store reference to main window
        self.main_window = None

        # Initialize current user
        self.current_user = None

        # Initialize tab counters
        self.csv_tab_count = 1
        self.url_tab_count = 1
        
        # Dictionary to store tab references
        self.tabs = {}

    def set_main_window(self, main_window):
        self.main_window = main_window

    def sign_out(self):
        """Sign out and return to main GUI"""
        try:
            if self.current_user:  # Only log if we have a valid username
                try:
                    log_user_action(self.current_user, "Signed out")
                except Exception as log_error:
                    print(f"Logging error: {log_error}")
            else:
                print("Warning: Cannot log sign out - no current user")

            from gui import MainWindow
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        except Exception as e:
            display_message(self, "Error", f"Error during sign out: {e}")
    
    def confirm_sign_out(self):
        """Show confirmation dialog before signing out"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Sign Out")
        msg.setText("Are you sure you want to sign out?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setStyleSheet(DIALOG_STYLE)
        
        if msg.exec_() == QMessageBox.Yes:
            self.sign_out()
    
    def set_current_user(self, username):
        """Set current user and ensure it's not None"""
        if username:
            self.current_user = username
            try:
                log_user_action(username, "Logged in as user")
            except Exception as log_error:
                print(f"Logging error: {log_error}")
        else:
            print("Warning: Attempted to set None as current user")
            self.current_user = None
    
    def show_main_ui(self):
        self.central_widget.setCurrentIndex(1)
    
    def init_main_ui(self):
        # Create and set up main widget that will contain everything
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(0, 0, 0, 0) 
        
        # Add menu bar at the top with no margins
        self.menu_bar.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.menu_bar)
        
        # Add a container for the main content with proper padding
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(25, 25, 25, 25)  #

        # Input Container with enhanced styling and better spacing
        input_container = QWidget()
        input_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        input_container.setStyleSheet("background: transparent;")  
        
        # Main horizontal layout with improved spacing
        input_layout = QHBoxLayout(input_container)
        input_layout.setSpacing(20)
        input_layout.setContentsMargins(0, 0, 0, 0)        

        # Facebook Post Section with enhanced styling
        fb_section = QWidget()
        fb_section.setFixedHeight(200)  # Set fixed height
        fb_section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        fb_layout = QVBoxLayout(fb_section)
        fb_layout.setSpacing(8)
        fb_layout.setContentsMargins(12, 12, 12, 12)

        # Simple label
        fb_title = QLabel("Facebook Post")
        fb_title.setFont(FONTS['header'])
        fb_title.setStyleSheet(f"color: {COLORS['text']};")
        fb_title.setContentsMargins(0, 0, 0, 5)
        fb_layout.addWidget(fb_title)

        # URL input horizontal layout with checkbox
        url_layout = QHBoxLayout()
        url_layout.setSpacing(12)  # Increased spacing between URL input and checkbox
        url_layout.setContentsMargins(0, 0, 0, 0)

        self.url_input = QLineEdit()
        self.url_input.setStyleSheet(INPUT_STYLE)
        self.url_input.setPlaceholderText("Enter Facebook Post URL")
        
        self.include_replies = QCheckBox("Include Replies")
        self.include_replies.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text']};
                font-size: 13px;
                padding: 5px;
                margin-left: 5px;  # Added margin to separate from URL input
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
        self.include_replies.setChecked(True)
        
        url_layout.addWidget(self.url_input, 1)  # Give URL input stretch factor of 1
        url_layout.addWidget(self.include_replies, 0)  # Don't stretch checkbox
        fb_layout.addLayout(url_layout)

        self.scrape_button = QPushButton("Scrape Comments")
        self.scrape_button.setFont(FONTS['button'])
        self.scrape_button.setStyleSheet(f"""
            {BUTTON_STYLE}
            QPushButton {{
                padding: 12px;
                border-radius: 6px;
            }}
        """)
        self.scrape_button.clicked.connect(self.scrape_comments)
        fb_layout.addWidget(self.scrape_button)

        input_layout.addWidget(fb_section)

        # CSV File Section with matching styling
        csv_section = QWidget()
        csv_section.setFixedHeight(200)  # Set fixed height
        csv_section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        csv_layout = QVBoxLayout(csv_section)
        csv_layout.setSpacing(8)
        csv_layout.setContentsMargins(12, 12, 12, 12)
        
        # Simple CSV label
        csv_title = QLabel("CSV File")
        csv_title.setFont(FONTS['header'])
        csv_title.setStyleSheet(f"color: {COLORS['text']};")
        csv_title.setContentsMargins(0, 0, 0, 5)
        csv_layout.addWidget(csv_title)

        # File input with browse button
        file_browse_layout = QHBoxLayout()
        file_browse_layout.setContentsMargins(0, 0, 0, 0)
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
        csv_layout.addLayout(file_browse_layout)
        
        self.process_csv_button = QPushButton("Process CSV")
        self.process_csv_button.setFont(FONTS['button'])
        self.process_csv_button.setStyleSheet(BUTTON_STYLE)
        self.process_csv_button.clicked.connect(self.process_csv)
        csv_layout.addWidget(self.process_csv_button)
        
        input_layout.addWidget(csv_section)

        # Direct Input Section with matching styling
        direct_section = QWidget()
        direct_section.setFixedHeight(200)  # Set fixed height
        direct_section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        direct_layout = QVBoxLayout(direct_section)
        direct_layout.setSpacing(8)
        direct_layout.setContentsMargins(12, 12, 12, 12)
        
        # Simple direct input label
        direct_title = QLabel("Direct Input")
        direct_title.setFont(FONTS['header'])
        direct_title.setStyleSheet(f"color: {COLORS['text']};")
        direct_title.setContentsMargins(0, 0, 0, 5)
        direct_layout.addWidget(direct_title)
        
        self.text_input = QLineEdit()
        self.text_input.setStyleSheet(INPUT_STYLE)
        self.text_input.setPlaceholderText("Enter comment to analyze")
        
        self.analyze_button = QPushButton("Analyze Comment")
        self.analyze_button.setFont(FONTS['button'])
        self.analyze_button.setStyleSheet(BUTTON_STYLE)
        self.analyze_button.clicked.connect(self.analyze_single)
        
        direct_layout.addWidget(self.text_input)
        direct_layout.addWidget(self.analyze_button)
        
        input_layout.addWidget(direct_section)

        # Add input container to main layout
        content_layout.addWidget(input_container)

        # Results Container with enhanced styling
        results_container = QWidget()
        results_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        results_container.setStyleSheet(CONTAINER_STYLE)
        results_layout = QVBoxLayout(results_container)
        results_layout.setSpacing(8)  

        # Tab widget with styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(TAB_STYLE)
        self.initial_message = QLabel("No analysis performed yet.\nResults will appear here.")
        self.initial_message.setAlignment(Qt.AlignCenter)
        self.initial_message.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px;")
        results_layout.addWidget(self.initial_message)
        
        results_layout.addWidget(self.tab_widget)
        self.tab_widget.hide()

        # Operations section with enhanced styling but more compact
        operations_container = QWidget()
        operations_container.setStyleSheet("background: transparent;") 
        operations_container.setMaximumHeight(95)  
        operations_layout = QVBoxLayout(operations_container)
        operations_layout.setSpacing(5)  # Reduced spacing
        operations_layout.setContentsMargins(0, 0, 0, 0)

        # Title section with fixed height
        title_container = QWidget()
        title_container.setFixedHeight(30)  # Reduced height for title
        title_container.setStyleSheet("background: transparent;")
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        operations_title = QLabel("Dataset Operations")
        operations_title.setFont(FONTS['header'])
        operations_title.setStyleSheet(f"color: {COLORS['text']};")
        title_layout.addWidget(operations_title)
        operations_layout.addWidget(title_container)

        # Operation buttons with icons in a single row
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.show_summary_button = QPushButton("📊 Summary")
        self.word_cloud_button = QPushButton("☁️ Word Cloud")
        self.generate_report_button = QPushButton("📝 Generate Report")

        # Connect buttons
        self.show_summary_button.clicked.connect(self.show_summary)
        self.word_cloud_button.clicked.connect(self.show_word_cloud)
        self.generate_report_button.clicked.connect(self.generate_report)

        # Style the buttons
        for btn in [self.show_summary_button, self.word_cloud_button, self.generate_report_button]:
            btn.setStyleSheet(f"""
                {BUTTON_STYLE}
                QPushButton {{
                    padding: 12px 20px;
                    min-width: 140px;
                }}
            """)
            btn.setFont(FONTS['button'])
            buttons_layout.addWidget(btn)

        operations_layout.addLayout(buttons_layout)
        results_layout.addWidget(operations_container)

        # Add results container to main layout
        content_layout.addWidget(results_container)

        # Set content layout stretching
        content_layout.setStretch(0, 0)  # Input container - fixed height
        content_layout.setStretch(1, 1)  # Results container - takes remaining space

        # Add content container to main layout
        main_layout.addWidget(content_container)

        # CRITICAL: Set the main widget as the central widget's current widget
        self.central_widget.addWidget(main_widget)
        self.central_widget.setCurrentWidget(main_widget)
    
    def show_loading(self, show=True):
        if show:
            self.loading_overlay.show()
        else:
            self.loading_overlay.hide()
    
    def scrape_comments(self):
        url = self.url_input.text()
        if not url:
            display_message(self, "Error", "Please enter a URL.")
            return

        try:
            self.show_loading(True)
            QApplication.processEvents()
            
            if self.current_user:  # Only log if we have a valid user
                try:
                    # Truncate URL if too long
                    short_url = url[:30] + "..." if len(url) > 30 else url
                    log_user_action(self.current_user, f"Scraped FB post: {short_url}")
                except Exception as log_error:
                    print(f"Logging error: {log_error}")
            
            from scraper import scrape_comments
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
                    'is_reply': row.get('Is Reply', False),
                    'reply_to': row.get('Reply To', '')
                }
            
            comments = df['Text'].tolist()
            self.populate_table(comments)
        except Exception as e:
            display_message(self, "Error", f"Error scraping comments: {e}")
        finally:
            self.show_loading(False)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.file_input.setText(file_path)

    def process_csv(self):
        if not self.file_input.text():
            display_message(self, "Error", "Please select a CSV file first")
            return
        try:
            self.show_loading(True)
            file_path = self.file_input.text()
            
            if self.current_user:  # Only log if we have a valid user
                try:
                    # Get just the filename without full path
                    file_name = file_path.split('/')[-1].split('\\')[-1]
                    log_user_action(self.current_user, f"Processed CSV: {file_name}")
                except Exception as log_error:
                    print(f"Logging error: {log_error}")
            
            QApplication.processEvents()
            
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
                    'profile_id': 'N/A',
                    'is_reply': False,
                    'reply_to': ''
                }
            
            self.populate_table(comments)
        except Exception as e:
            display_message(self, "Error", f"Error reading CSV file: {e}")
        finally:
            self.show_loading(False)

    def analyze_single(self):
        if not self.text_input.text():
            display_message(self, "Error", "Please enter a comment to analyze")
            return
        
        try:
            self.show_loading(True)
            comment = self.text_input.text()
            
            if self.current_user:  # Only log if we have a valid user
                try:
                    log_user_action(self.current_user, "Analyzed single comment")
                except Exception as log_error:
                    print(f"Logging error: {log_error}")
            
            QApplication.processEvents()
            
            # Create metadata for the direct input comment
            self.comment_metadata = {
                comment: {
                    'profile_name': 'Direct Input',
                    'profile_picture': '',
                    'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'likes_count': 'N/A',
                    'profile_id': 'N/A',
                    'is_reply': False,
                    'reply_to': ''
                }
            }
            
            self.populate_table([comment])
        finally:
            self.show_loading(False)

    def create_empty_tab(self, tab_type):
        """Create a new empty tab with table"""
        if tab_type == "Direct Inputs" and "Direct Inputs" in self.tabs:
            # Return existing Direct Inputs table
            return self.tabs["Direct Inputs"].findChild(QTableWidget)

        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        
        # Header layout with table title and sort dropdown
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

        # Enable better table behavior
        table.setWordWrap(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        
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
        
        # Show tab widget and hide initial message when first tab is created
        if self.tab_widget.isHidden():
            self.initial_message.hide()
            self.tab_widget.show()
        
        self.tab_widget.setTabsClosable(True)  # Enable close buttons
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        return table

    def close_tab(self, index):
        """Close the tab and clean up resources"""
        tab_name = self.tab_widget.tabText(index)
        
        if self.current_user:  # Only log if we have a valid user
            try:
                log_user_action(self.current_user, f"Closed tab: {tab_name}")
            except Exception as log_error:
                print(f"Logging error: {log_error}")
        
        # Remove tab and its reference
        self.tab_widget.removeTab(index)
        if tab_name in self.tabs:
            del self.tabs[tab_name]
            
        # If no tabs left, show initial message
        if self.tab_widget.count() == 0:
            self.tab_widget.hide()
            self.initial_message.show()

    def get_current_table(self):
        """Get the table widget from the current tab"""
        current_tab = self.tab_widget.currentWidget()
        return current_tab.findChild(QTableWidget)

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

    def populate_table(self, comments):
        """Create new tab and populate it based on input type"""
        # Store the input source before clearing
        file_path = self.file_input.text()
        url = self.url_input.text()

        # Clear inputs after checking
        self.file_input.clear()
        self.url_input.clear()
        self.text_input.clear()  # Also clear the text input field

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
        
        for comment in comments:
            metadata = self.comment_metadata.get(comment, {})
            is_reply = metadata.get('is_reply', False)
            reply_to = metadata.get('reply_to', '')
            
            prediction, confidence = classify_comment(comment)
            row_position = table.rowCount()
            table.insertRow(row_position)

            # Create display text with reply indicator
            if is_reply:
                comment_item = QTableWidgetItem()
                comment_item.setData(Qt.UserRole, comment)  # Store original comment
                comment_item.setData(Qt.DisplayRole, f" [↪ Reply] {comment}")
                comment_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                # Add subtle background color for replies
                lighter_surface = QColor(COLORS['surface']).lighter(105)
                comment_item.setBackground(lighter_surface)
            else:
                comment_item = QTableWidgetItem(comment)
                comment_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
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

        # Resize rows after all data is added for better performance
        table.resizeRowsToContents()
        
        # Switch to the new tab
        tab_index = self.tab_widget.indexOf(self.tabs[tab_name])
        self.tab_widget.setCurrentIndex(tab_index)
        
        # Ensure we're focusing on the table part of the window
        # by scrolling to top
        table.scrollToTop()
    
    def update_details_panel(self):
        # This is a simplified version that doesn't show detailed information
        # but keeps the function to avoid errors when selecting table rows
        pass

    def export_results(self):
        current_table = self.get_current_table()
        if not current_table or current_table.rowCount() == 0:
            display_message(self, "Error", "No comments to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                comments = []
                predictions = []
                confidences = []

                for row in range(current_table.rowCount()):
                    comments.append(current_table.item(row, 0).text())
                    predictions.append(current_table.item(row, 1).text())
                    confidences.append(current_table.item(row, 2).text())

                df = pd.DataFrame({
                    'Comment': comments,
                    'Prediction': predictions,
                    'Confidence': confidences
                })
                df.to_csv(file_path, index=False)
                
                if self.current_user:  # Only log if we have a valid user
                    try:
                        log_user_action(self.current_user, f"Exported results to: {file_path}")
                    except Exception as log_error:
                        print(f"Logging error: {log_error}")
                
                display_message(self, "Success", "Results exported successfully")
            except Exception as e:
                display_message(self, "Error", f"Error exporting results: {e}")

    def show_word_cloud(self):
        """Generate and display word cloud visualization"""
        total_comments = self.get_current_table().rowCount()
        if total_comments == 0:
            display_message(self, "Error", "No comments to visualize")
            return

        all_comments = []
        for row in range(total_comments):
            if not self.get_current_table().isRowHidden(row):
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
            layout = QVBoxLayout(dialog)

            # Add word cloud
            image_label = QLabel()
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

    def show_summary(self):
        """Show summary of comments analysis"""
        total_comments = 0
        cyberbullying_count = 0
        normal_count = 0
        high_confidence_count = 0

        table = self.get_current_table()
        for row in range(table.rowCount()):
            if not table.isRowHidden(row):
                total_comments += 1
                prediction = table.item(row, 1).text()
                confidence = float(table.item(row, 2).text().strip('%')) / 100

                if prediction == "Cyberbullying":
                    cyberbullying_count += 1
                else:
                    normal_count += 1

                if confidence > 0.9:
                    high_confidence_count += 1

        if total_comments == 0:
            display_message(self, "Error", "No visible comments to summarize")
            return

        summary_text = (
            f"Analysis Summary:\n\n"
            f"Total Comments: {total_comments}\n"
            f"Cyberbullying Comments: {cyberbullying_count} ({(cyberbullying_count/total_comments)*100:.1f}%)\n"
            f"Normal Comments: {normal_count} ({(normal_count/total_comments)*100:.1f}%)\n"
            f"High Confidence Predictions: {high_confidence_count} ({(high_confidence_count/total_comments)*100:.1f}%)"
        )

        display_message(self, "Results Summary", summary_text)

    def generate_report(self):
        """Generate report by calling the report generation function"""
        generate_report_user(self)