from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QTextEdit, QWidget, 
                           QFileDialog, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QSplitter, QGridLayout, QComboBox, 
                           QSizePolicy, QStackedWidget, QFrame, QTabWidget, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QTextCursor, QImage, QPixmap, QIcon
from scraper import scrape_comments
from model import classify_comment
import pandas as pd
from utils import display_message
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE, TABLE_STYLE, TAB_STYLE, DIALOG_STYLE, CONTAINER_STYLE, TITLELESS_CONTAINER_STYLE, TABLE_ALTERNATE_STYLE, DETAIL_TEXT_STYLE, HEADER_STYLE, TAG_STYLE
import tempfile
import time
from PyQt5.QtWidgets import QApplication
from comment_operations import generate_report_from_window, generate_report_user
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
from io import BytesIO
from stopwords import TAGALOG_STOP_WORDS
from PyQt5.QtWidgets import QDialog

# Reuse the LoadingOverlay from the main GUI
from loading_overlay import LoadingOverlay
from db_config import log_user_action  # Add this import

class UserMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyber Boolean - Simple View")
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
        
        # Add stretch to push sign out button to right
        menu_layout.addStretch()
        
        # Create sign out button
        sign_out_button = QPushButton("🚪 Sign Out")
        sign_out_button.setFont(FONTS['button'])
        sign_out_button.clicked.connect(self.confirm_sign_out)
        menu_layout.addWidget(sign_out_button)
        
        # Initialize rest of UI
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.init_main_ui()
        
        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self)

        # Store reference to main window
        self.main_window = None

        # Initialize current user
        self.current_user = None

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
        main_widget = QWidget()
        self.central_widget.addWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margins completely
        
        # Add menu bar at the top with no margins
        self.menu_bar.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.menu_bar)
        
        # Add a container for the main content with proper padding
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Move existing content initialization here
        # Top header section with sign out button and title in one row
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title in center
        title = QLabel("Cyberbullying Detection Tool")
        title.setFont(FONTS['header'])
        title.setStyleSheet(HEADER_STYLE)
        title.setAlignment(Qt.AlignCenter)
        
        # Add invisible spacer on left to match button width
        header_layout.addSpacing(100)
        
        # Add title
        header_layout.addWidget(title, 1)  # Title takes remaining space
        
        # Sign Out button on right
        sign_out_button = QPushButton("Sign Out")
        sign_out_button.setFont(FONTS['button'])
        sign_out_button.setStyleSheet(BUTTON_STYLE)
        sign_out_button.setFixedWidth(100)
        sign_out_button.clicked.connect(self.confirm_sign_out)
        header_layout.addWidget(sign_out_button)
        
        content_layout.addWidget(header_widget)
        
        # Collapsible input section
        input_container = QWidget()
        input_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)  # Limit vertical size
        input_layout = QHBoxLayout(input_container)  # Changed to horizontal for space efficiency
        input_layout.setSpacing(10)
        input_layout.setContentsMargins(0, 0, 0, 0)

        # Facebook Post Section - Made more compact
        fb_section = QWidget()
        fb_section.setStyleSheet(CONTAINER_STYLE)
        fb_layout = QVBoxLayout(fb_section)
        fb_layout.setSpacing(5)  # Reduced spacing
        fb_layout.setContentsMargins(8, 8, 8, 8)  # Reduced padding
        
        fb_title = QLabel("Facebook Post")
        fb_title.setFont(FONTS['button'])  # Smaller font
        fb_title.setAlignment(Qt.AlignCenter)
        self.url_input = QLineEdit()
        self.url_input.setStyleSheet(INPUT_STYLE)
        self.url_input.setPlaceholderText("Enter Facebook Post URL")

        # Add checkbox for including replies
        self.include_replies = QCheckBox("Include Replies")
        self.include_replies.setStyleSheet(f"color: {COLORS['text']};")
        self.include_replies.setFont(FONTS['button'])
        self.include_replies.setChecked(True)  # Default to including replies
        
        self.scrape_button = QPushButton("Scrape Comments")
        self.scrape_button.setFont(FONTS['button'])
        self.scrape_button.setStyleSheet(BUTTON_STYLE)
        self.scrape_button.clicked.connect(self.scrape_comments)
        
        fb_layout.addWidget(fb_title)
        fb_layout.addWidget(self.url_input)
        fb_layout.addWidget(self.include_replies)  # Add checkbox to layout
        fb_layout.addWidget(self.scrape_button)
        input_layout.addWidget(fb_section)

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
        self.browse_button.setFixedWidth(80)  # Smaller button
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
        input_layout.addWidget(csv_section)

        # Direct Input Section - Made more compact
        direct_section = QWidget()
        direct_section.setStyleSheet(CONTAINER_STYLE)
        direct_layout = QVBoxLayout(direct_section)
        direct_layout.setSpacing(5)  # Reduced spacing
        direct_layout.setContentsMargins(8, 8, 8, 8)  # Reduced padding
        
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
        input_layout.addWidget(direct_section)

        # Add input container to main layout with fixed height
        content_layout.addWidget(input_container)
        
        # Make a line separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"background-color: {COLORS['border']};")
        content_layout.addWidget(separator)
        
        # Results section with tab widget - Modified to match input containers
        results_container = QWidget()
        results_container.setStyleSheet(CONTAINER_STYLE)
        results_layout = QVBoxLayout(results_container)
        results_layout.setContentsMargins(8, 8, 8, 8)  # Match input section padding

        # Create a container for the title with proper alignment
        title_container = QWidget()
        title_container.setStyleSheet(TITLELESS_CONTAINER_STYLE)
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        table_title = QLabel("Results")
        table_title.setFont(FONTS['header'])
        table_title.setAlignment(Qt.AlignLeft)
        title_layout.addWidget(table_title)
        title_layout.addStretch()

        # Add the title container to the results layout
        results_layout.addWidget(title_container)

        # Initial message widget with styled container
        message_container = QWidget()
        message_container.setStyleSheet(TITLELESS_CONTAINER_STYLE)
        message_layout = QVBoxLayout(message_container)
        message_layout.setContentsMargins(5, 10, 5, 10)  # Better padding for message

        self.initial_message = QLabel("No analysis performed yet.\nResults will appear here.")
        self.initial_message.setAlignment(Qt.AlignCenter)
        self.initial_message.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px;")
        message_layout.addWidget(self.initial_message)

        # Tab widget styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(TAB_STYLE)

        # Add initial message to tab widget area
        results_layout.addWidget(message_container)
        results_layout.addWidget(self.tab_widget)
        self.tab_widget.hide()  

        # Operations section - Created as a boxed container like input sections with fixed height
        operations_container = QWidget()
        operations_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)  
        operations_container.setStyleSheet(CONTAINER_STYLE)
        operations_layout = QVBoxLayout(operations_container)
        operations_layout.setSpacing(5)  # Reduced spacing
        operations_layout.setContentsMargins(8, 8, 8, 8)  # Reduced padding

        # Operations title with fixed height and compact layout
        operations_title = QLabel("Operations")
        operations_title.setFont(FONTS['button'])  # Same font as input section titles
        operations_title.setAlignment(Qt.AlignCenter)
        operations_title.setFixedHeight(20)  # Set fixed height for title to minimize space
        operations_layout.addWidget(operations_title)

        # Add buttons for summary, word cloud, and report generation in a row
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to make more compact
        self.show_summary_button = QPushButton("📊 Show Summary")
        self.word_cloud_button = QPushButton("☁️ Word Cloud")
        self.generate_report_button = QPushButton("📝 Generate Report")

        # Connect the buttons
        self.show_summary_button.clicked.connect(self.show_summary)
        self.word_cloud_button.clicked.connect(self.show_word_cloud)
        self.generate_report_button.clicked.connect(self.generate_report)

        # Style the buttons
        for btn in [self.show_summary_button, self.word_cloud_button, self.generate_report_button]:
            btn.setStyleSheet(BUTTON_STYLE)
            btn.setFont(FONTS['button'])

        buttons_layout.addWidget(self.show_summary_button)
        buttons_layout.addWidget(self.word_cloud_button)
        buttons_layout.addWidget(self.generate_report_button)
        operations_layout.addLayout(buttons_layout)

        # Add operations container below the results
        results_layout.addWidget(operations_container)

        # Initialize tab counters
        self.csv_tab_count = 1
        self.url_tab_count = 1

        # Dictionary to store tab references
        self.tabs = {}

        # Add results container to main layout with stretch factor
        content_layout.addWidget(results_container, 1)  # Give it maximum stretch
            
        # Set stretch factors
        content_layout.setStretch(0, 0)  # Header
        content_layout.setStretch(1, 0)  # Input - minimal height
        content_layout.setStretch(2, 0)  # Separator - minimal height
        content_layout.setStretch(3, 1)  # Results - takes all remaining space
        
        self.layout.addWidget(content_container)
    
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