from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QLabel, QPushButton, QDialog, QLineEdit, QTextEdit,
                             QFileDialog, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QSplitter, QGridLayout, QComboBox, QSizePolicy,
                             QStackedWidget, QTabWidget, QMessageBox, QCheckBox, QTabBar,
                             QApplication)
from PyQt5.QtCore import Qt, QSize, QRect, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPixmap, QImage, QIcon, QPainter, QPen
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd
import tempfile
import time
import re
import os
import hashlib # Add near other imports at the top of admin.py

from model import classify_comment
from scraper import scrape_comments
from styles import (COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE, TABLE_STYLE, TAB_STYLE, 
                   DETAIL_TEXT_STYLE, TABLE_ALTERNATE_STYLE, DIALOG_STYLE, 
                   IMAGE_LABEL_STYLE, MENU_BAR_STYLE, CHECKBOX_REPLY_STYLE, 
                   ROW_OPERATION_BUTTON_STYLE, SECTION_CONTAINER_STYLE, 
                   DETAILS_SECTION_STYLE, TEXT_EDIT_STYLE)
from utils import display_message
from history import HistoryDialog
from api_manager import APIManagerDialog
from usermanagement import UserManagementDialog
from about import AboutDialog
from user import SummaryDialog
from loading_overlay import LoadingOverlay
from stopwords import TAGALOG_STOP_WORDS
from comment_operations import generate_report
from db_config import log_user_action, get_db_connection
from comment_filters import CommentFiltersDialog

def admin_classify_comment(text):
    """
    Admin interface for classifying a comment using the model.
    This is a wrapper around classify_comment that can be extended with
    admin-specific functionality like logging or enhanced reporting.
    
    Args:
        text (str): The comment text to classify
        
    Returns:
        tuple: (prediction_label, confidence_score)
    """
    # Call the main classification function from model.py
    prediction, confidence = classify_comment(text)
    
    # Could add admin-specific functionality here:
    # - Enhanced logging 
    # - Additional processing
    # - Store results in admin-specific database, etc.
    
    return prediction, confidence

def batch_classify_comments(comments_list):
    """
    Process a batch of comments for admin analysis
    
    Args:
        comments_list (list): List of comment strings to classify
        
    Returns:
        list: List of dictionaries with comment text, prediction and confidence
    """
    results = []
    
    for comment in comments_list:
        prediction, confidence = admin_classify_comment(comment)
        results.append({
            'comment_text': comment,
            'prediction': prediction,
            'confidence': confidence
        })
    
    return results

class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDrawBase(True)
        
    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        size.setWidth(size.width() + 35)  # Add more space for X
        return size
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set font for X
        font = QFont("Arial", 8, QFont.Bold)
        painter.setFont(font)
        
        for index in range(self.count()):
            rect = self.tabRect(index)
            if not rect.isValid():
                continue
                
            # Draw X text in white
            painter.setPen(QColor('white'))
            x_rect = rect.adjusted(rect.width() - 25, 0, 0, 0)
            painter.drawText(x_rect, Qt.AlignCenter, "×")

class AdminWindow(QMainWindow):
    """Admin interface window with administrative functionality"""
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        
        # Initialize variables
        self.current_user = None
        self.selected_comments = []  # Track selected comments
        self.url_tab_count = 1
        self.csv_tab_count = 1
        self.comment_metadata = {}  # Store metadata for each comment
        self.session_id = None
        self.tabs = {}
        
        # Define base path for assets
        base_path = os.path.dirname(os.path.abspath(__file__))

        # Set window properties
        self.setStyleSheet("background-color: #2b2b2b;")
        self.app_icon = QIcon(os.path.join(base_path, "assets", "applogo.png"))
        self.setWindowIcon(self.app_icon) 
        self.setWindowTitle("Cyberbullying Content Guidance System - Admin")
        self.showMaximized()
        
        # Initialize UI elements
        self.url_input = QLineEdit()
        # Initialize filter settings
        self.comment_filters = {
            "includeReplies": True,
            "maxComments": 100,
            "resultsLimit": 50,  # Keep for compatibility with scraper
            "viewOption": "RANKED_UNFILTERED",  # Keep for compatibility with scraper
            "timelineOption": "CHRONOLOGICAL",  # Keep for compatibility with scraper
            "minWordCount": 3,
            "excludeLinks": True,
            "excludeEmojisOnly": True
        }
        self.filter_button = QPushButton("Filters")
        self.filter_button.clicked.connect(self.show_filters_dialog)
        
        self.file_input = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        self.process_csv_button = QPushButton("Process CSV")
        self.process_csv_button.clicked.connect(self.process_csv)
        
        self.text_input = QLineEdit()
        self.analyze_button = QPushButton("Analyze Comment")
        self.analyze_button.clicked.connect(self.analyze_single)
        
        self.scrape_button = QPushButton("Scrape Comments")
        self.scrape_button.clicked.connect(self.scrape_comments)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Initialize main UI first (this creates the top bar)
        self.init_main_ui()
        
        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self)
        
    def init_main_ui(self):
        """Initialize the main user interface"""
        # Create main widget
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create menu bar
        menu_bar = QWidget()
        menu_bar.setFixedHeight(40)
        menu_bar.setStyleSheet(MENU_BAR_STYLE)
        
        menu_layout = QHBoxLayout(menu_bar)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)

        # Add app name to the left
        self.app_name_label = QLabel("Cyberbullying Content Guidance System - Admin View")
        self.app_name_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px; padding: 0 16px;")
        self.app_name_label.setFont(FONTS['button'])
        menu_layout.addWidget(self.app_name_label)
        
        # Add stretch to push remaining buttons to right
        menu_layout.addStretch()
        
        # Create admin action buttons
        self.manage_api_button = QPushButton("🔑 Manage API")
        self.manage_users_button = QPushButton("👥 Users Management")
        self.logs_button = QPushButton("📋 User Logs")
        self.sign_out_button = QPushButton("Sign Out")
        
        # Set fonts for buttons
        self.manage_api_button.setFont(FONTS['button'])
        self.manage_users_button.setFont(FONTS['button'])
        self.logs_button.setFont(FONTS['button'])
        self.sign_out_button.setFont(FONTS['button'])
        
        # Connect button signals
        self.manage_api_button.clicked.connect(self.show_api_manager)
        self.manage_users_button.clicked.connect(self.show_user_management)
        self.logs_button.clicked.connect(self.show_history)
        self.sign_out_button.clicked.connect(self.confirm_sign_out)
        
        # Add right-side buttons to layout
        menu_layout.addWidget(self.manage_api_button)
        menu_layout.addWidget(self.manage_users_button)
        menu_layout.addWidget(self.logs_button)
        menu_layout.addWidget(self.sign_out_button)
        
        main_layout.addWidget(menu_bar)

        # Create content container
        content_container = QWidget()
        self.content_layout = QVBoxLayout(content_container)
        self.content_layout.setSpacing(15)
        self.content_layout.setContentsMargins(25, 50, 25, 35)
        
        # Initialize the rest of the UI
        self.init_ui()
        
        main_layout.addWidget(content_container)
        
        # Set the created widget as central
        self.setCentralWidget(main_widget)
        
    def init_ui(self):
        """Initialize UI components for the admin dashboard"""
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
        fb_section.setStyleSheet(SECTION_CONTAINER_STYLE)
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
        
        # Connect filter button that was already initialized in __init__
        self.filter_button.setFont(FONTS['button'])
        self.filter_button.setStyleSheet(BUTTON_STYLE)
        self.filter_button.setFixedWidth(80)
        self.filter_button.setToolTip("Configure comment scraping options")
        self.filter_button.clicked.connect(self.show_filters_dialog)
        
        url_layout.addWidget(self.url_input, 1)  # Give URL input stretch factor of 1
        url_layout.addWidget(self.filter_button, 0)  # Don't stretch filter button
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
        csv_section.setStyleSheet(SECTION_CONTAINER_STYLE)
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
        direct_section.setStyleSheet(SECTION_CONTAINER_STYLE)
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

        # Add input container to content layout
        self.content_layout.addWidget(input_container)
        
        # Create responsive splitter for table and details
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(0)  # Make handle invisible
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: none;
                width: 0px;
            }}
        """)
        # Make splitter immovable
        splitter.setChildrenCollapsible(False)

        # Table Container
        table_container = QWidget()
        table_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add tab widget with custom tab bar for consistent appearance with user.py
        self.tab_widget = QTabWidget()
        custom_tab_bar = CustomTabBar()
        self.tab_widget.setTabBar(custom_tab_bar)
        self.tab_widget.setStyleSheet(TAB_STYLE)
        self.initial_message = QLabel("No analysis performed yet.\nResults will appear here.")
        self.initial_message.setAlignment(Qt.AlignCenter)
        self.initial_message.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px;")
        table_layout.addWidget(self.initial_message)
        
        table_layout.addWidget(self.tab_widget)
        self.tab_widget.hide()  # Hide tab widget initially

        splitter.addWidget(table_container)

        # Details Panel with enhanced styling
        details_container = QWidget()
        details_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        details_layout = QVBoxLayout(details_container)
        details_layout.setSpacing(15)
        details_layout.setContentsMargins(15, 0, 0, 0)

        # Details section with better visual hierarchy
        details_section = QWidget()
        details_section.setStyleSheet(DETAILS_SECTION_STYLE)
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
        self.details_text_edit.setStyleSheet(TEXT_EDIT_STYLE)
        details_section_layout.addWidget(self.details_text_edit)
        details_layout.addWidget(details_section)

        # Row Operations Section - Enhanced styling
        row_ops_section = QWidget()
        row_ops_section.setStyleSheet(DETAILS_SECTION_STYLE)
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

        self.add_remove_button = QPushButton("➕ Add to List")
        self.export_selected_button = QPushButton("📋 Export List")
        
        # Initially disable row operation buttons
        self.add_remove_button.setEnabled(False)
        self.export_selected_button.setEnabled(False)
        
        # Connect the buttons
        self.add_remove_button.clicked.connect(self.toggle_list_status)
        self.export_selected_button.clicked.connect(self.export_selected)

        row_button_configs = [
            (self.add_remove_button, "➕ Add to List", 0, 0),
            (self.export_selected_button, "📋 Export List", 0, 1)
        ]

        for button, text, row, col in row_button_configs:
            button.setText(text)
            button.setFont(FONTS['button'])
            button.setStyleSheet(ROW_OPERATION_BUTTON_STYLE)
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

        # Initialize operation buttons
        self.show_summary_button = QPushButton("📊 Summary")
        self.word_cloud_button = QPushButton("☁️ Word Cloud")
        self.export_all_button = QPushButton("📤 Export Tab")
        self.generate_report_button = QPushButton("📝 Generate Report")
        
        # Connect operation button signals
        self.show_summary_button.clicked.connect(self.show_summary)
        self.word_cloud_button.clicked.connect(self.show_word_cloud)
        self.export_all_button.clicked.connect(self.export_all)
        self.generate_report_button.clicked.connect(self.generate_report)

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

        splitter.setSizes([900, 100])
        splitter.setStretchFactor(0, 9)  
        splitter.setStretchFactor(1, 1)

        # Add splitter to content layout
        self.content_layout.addWidget(splitter)

        # Set content layout stretch factors
        self.content_layout.setStretch(0, 0)  # Input container - fixed height
        self.content_layout.setStretch(1, 1)  # Results container - takes remaining space
        
    # --- Additional methods will be added in subsequent edits --- #
    
    def show_loading(self, show=True):
        if show:
            self.loading_overlay.show()
        else:
            self.loading_overlay.hide()
    
    def show_api_manager(self):
        """Show API manager dialog"""
        try:
            dialog = APIManagerDialog(self)
            dialog.exec_()
        except Exception as e:
            print(f"Error showing API Manager: {str(e)}")
            from utils import display_message
            display_message(self, "Error", f"Could not open API Manager: {str(e)}")
        
    def show_user_management(self):
        """Show user management dialog"""
        dialog = UserManagementDialog(self)
        dialog.exec_()
        
    def show_history(self):
        """Show user logs/history dialog"""
        dialog = HistoryDialog(self)
        dialog.exec_()
        
    def show_about(self):
        """Show the About dialog"""
        about_dialog = AboutDialog(self)
        about_dialog.exec_()
        
    def confirm_sign_out(self):
        """Confirm sign out and return to login screen"""
        reply = QMessageBox.question(
            self, 
            "Confirm Sign Out", 
            "Are you sure you want to sign out?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close_session()
            log_user_action(self.current_user, "Admin signed out")
            self.close()
            if self.main_window:
                self.main_window.show()

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.file_input.setText(file_path)

    def truncate_tab_name(self, name, max_length=15):
        """Truncate tab name if it exceeds the maximum length"""
        if len(name) > max_length:
            return name[:max_length-3] + "..."
        return name

    def create_empty_tab(self, tab_type, is_restoring=False):
        """Create a new empty tab with table"""
        # Truncate tab name for consistent width in the UI tab bar
        tab_display_name = self.truncate_tab_name(tab_type, max_length=20) # Slightly longer truncation

        # Important: During restoration, we *always* create a new tab widget,
        # even if a tab with the same name was somehow left over or handled incorrectly before.
        # The restore_session loop is responsible for generating unique names passed as tab_type.
        # If *not* restoring, and the tab_type key exists in our internal dict, reuse/focus it.
        if not is_restoring and tab_type in self.tabs:
            # If not restoring, and tab exists, switch to it and return its table
            existing_tab_widget = self.tabs[tab_type]
            index = self.tab_widget.indexOf(existing_tab_widget)
            if index != -1:
                self.tab_widget.setCurrentIndex(index)
            # Return the table from the existing tab
            table = existing_tab_widget.findChild(QTableWidget)
            print(f"Switched to existing tab '{tab_type}'")
            return table

        # --- Create New Tab Widget ---
        # If restoring OR if tab_type not in self.tabs dictionary, create a new tab widget
        tab = QWidget()
        # Give the tab widget an object name for easier debugging/identification
        tab.setObjectName(f"tab_{tab_type.replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_')}") # Sanitize name for object name
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(5, 5, 5, 5) # Add some margins

        # Header layout with table title, search bar, and sort dropdown
        header_layout = QHBoxLayout()
        table_title = QLabel("Comments") # Title could be dynamic if needed
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
            "Show Replies Only"
        ])
        sort_combo.setStyleSheet(f"""
            QComboBox {{
                {INPUT_STYLE}
                padding: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                selection-background-color: {COLORS['highlight']};
            }}
        """)
        header_layout.addWidget(sort_combo)
        tab_layout.addLayout(header_layout)

        # Create and configure table
        table = QTableWidget()
        table.setObjectName(f"table_{tab_type.replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_')}") # Sanitize name
        table.setSortingEnabled(False) # Disable Qt sorting, use custom sort
        table.setStyleSheet(TABLE_ALTERNATE_STYLE)
        table.setColumnCount(3) # Set to 3 columns
        table.setHorizontalHeaderLabels(["Comment", "Prediction", "Confidence"]) # Update headers
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Adjust column sizes
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed) # Add resize mode for confidence
        header.resizeSection(1, 150)  # Width for prediction
        header.resizeSection(2, 100)  # Width for confidence
        # table.setColumnWidth(1, 150) # setSectionResizeMode is preferred
        # table.setColumnWidth(2, 100)

        table.setWordWrap(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        # Disconnect first to avoid multiple connections if called repeatedly
        try: table.itemSelectionChanged.disconnect(self.update_details_panel)
        except TypeError: pass
        table.itemSelectionChanged.connect(self.update_details_panel)

        # Store sort combo and connect it using a lambda specific to *this* table instance
        table.sort_combo = sort_combo
        # Disconnect first to avoid multiple connections
        try: sort_combo.currentIndexChanged.disconnect() # Disconnect all slots
        except TypeError: pass
        # Use lambda to pass the specific table instance
        sort_combo.currentIndexChanged.connect(lambda index, tbl=table: self.sort_table(tbl))

        tab_layout.addWidget(table)

        # Configure search functionality specific to *this* table instance
        def filter_table(text, tbl=table): # Pass table instance
            search_text = text.lower()
            for row in range(tbl.rowCount()):
                comment_item = tbl.item(row, 0)
                # Check if item exists and has text
                if comment_item and comment_item.text():
                     comment_content = comment_item.text().lower()
                     # Use UserRole data as well if available
                     user_data = comment_item.data(Qt.UserRole)
                     if user_data:
                          comment_content += user_data.lower()
                     tbl.setRowHidden(row, search_text not in comment_content)
                else:
                     # Hide rows with missing comment items
                     tbl.setRowHidden(row, True)

        # Store search bar reference on the table itself
        table.search_bar = search_bar
        # Disconnect first to avoid multiple connections
        try: search_bar.textChanged.disconnect()
        except TypeError: pass
        # Use lambda to pass text and table instance
        search_bar.textChanged.connect(lambda text, tbl=table: filter_table(text, tbl))


        # Store tab reference using the unique `tab_type` name (e.g., "data.csv (2)")
        # This MUST use the name generated by restore_session to ensure uniqueness check works
        self.tabs[tab_type] = tab
        print(f"Added tab to self.tabs dictionary with key: '{tab_type}'")


        # Add the new tab widget to the tab bar using the (potentially truncated) display name
        # This adds the QWidget `tab` to the QTabWidget
        self.tab_widget.addTab(tab, tab_display_name)
        print(f"Added tab to QTabWidget with display name: '{tab_display_name}'")

        # Ensure close buttons are enabled (usually set once)
        if not self.tab_widget.tabsClosable():
             self.tab_widget.setTabsClosable(True)
             # Connect the close signal *once* (maybe in __init__ or init_ui)
             # If connecting here, ensure it's disconnected first
             try: self.tab_widget.tabCloseRequested.disconnect(self.close_tab)
             except TypeError: pass # Not connected yet
             self.tab_widget.tabCloseRequested.connect(self.close_tab)


        # Show tab widget and hide initial message when first tab is created
        if self.tab_widget.isHidden() and self.tab_widget.count() > 0:
            self.initial_message.hide()
            self.tab_widget.show()
            # Only enable if not already enabled - avoid redundant calls
            if not self.show_summary_button.isEnabled():
                self.enable_dataset_operations(True)

        # Set the newly added tab as the current one, especially during restoration
        # This ensures the UI shows the tab being processed
        new_index = self.tab_widget.indexOf(tab)
        if new_index != -1:
            self.tab_widget.setCurrentIndex(new_index)


        return table # Return the newly created table


    def close_tab(self, index, delete_from_db=True):
        """Close the tab and clean up resources. Optionally skip DB deletion."""
        # Get the widget *at the provided index*
        tab_to_close = self.tab_widget.widget(index)
        if not tab_to_close:
            print(f"Error: Could not find widget at index {index} to close.")
            return

        # Find the *actual current index* of this widget right before removal
        current_index = self.tab_widget.indexOf(tab_to_close)
        if current_index == -1:
            print(f"Error: Widget {tab_to_close} no longer found in tab widget.")
            return

        # Get the tab name using the *current index*
        # Find the key in self.tabs that corresponds to this widget
        tab_name = None
        for name, widget in self.tabs.items():
            if widget == tab_to_close:
                tab_name = name
                break

        if not tab_name:
             # Fallback if not found in self.tabs (shouldn't happen ideally)
             tab_name = self.tab_widget.tabText(current_index)
             print(f"Warning: Widget not found in self.tabs keys, using tabText: {tab_name}")

        print(f"Attempting to close tab: Name='{tab_name}', Index={current_index}, DeleteDB={delete_from_db}")

        # --- Database Operations (Conditional) ---
        if delete_from_db:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()

                # Find tab_id based on session_id and tab_name
                cursor.execute("""
                    SELECT tab_id FROM session_tabs
                    WHERE session_id = ? AND tab_name = ?
                """, (self.session_id, tab_name))
                tab_result = cursor.fetchone()

                if tab_result:
                    tab_id = tab_result[0]
                    print(f"  Found tab_id {tab_id} for DB deletion.")
                    # Delete comments associated with this tab
                    cursor.execute("DELETE FROM tab_comments WHERE tab_id = ?", (tab_id,))
                    # Delete the tab entry itself
                    cursor.execute("DELETE FROM session_tabs WHERE tab_id = ?", (tab_id,))
                    conn.commit()
                    print(f"  Successfully deleted comments and tab entry for tab_id {tab_id}")

                    # Now update session last accessed time
                    cursor.execute("""
                        UPDATE user_sessions
                        SET last_accessed = GETDATE()
                        WHERE session_id = ?
                    """, (self.session_id,))
                    conn.commit()
                else:
                    print(f"  Warning: Could not find tab_id for '{tab_name}' in session {self.session_id} for DB deletion.")

                conn.close()
                log_user_action(self.current_user, f"Closed tab (with DB delete): {tab_name}")

            except Exception as e:
                print(f"Error removing tab data from database for '{tab_name}': {e}")
                # Add proper rollback and connection closing in case of error
                try: conn.rollback()
                except: pass
                try: conn.close()
                except: pass
        else:
             print("  Skipping database deletion as requested.")
             # Still log the UI action
             log_user_action(self.current_user, f"Closed duplicate tab (UI only): {tab_name}")


        # --- UI and Internal State Cleanup ---
        if tab_name in self.tabs:
            # Clean up metadata and selected comments associated with this tab_name
            # (Ensure this doesn't break things if called during deduplication)
            # Maybe skip this part if delete_from_db is False? Or make it safe.
            # Let's assume metadata/selection cleanup is okay even if DB isn't deleted.
            table_widget = self.tabs[tab_name].findChild(QTableWidget)
            if table_widget:
                comments_in_tab = set()
                for row in range(table_widget.rowCount()):
                     comment_item = table_widget.item(row, 0)
                     if comment_item:
                          comment_text = comment_item.data(Qt.UserRole) or comment_item.text()
                          comments_in_tab.add(comment_text)

                # Remove associated metadata
                for comment_text in comments_in_tab:
                     if comment_text in self.comment_metadata:
                          del self.comment_metadata[comment_text]

                # Remove from selected list
                self.selected_comments = [
                    item for item in self.selected_comments
                    if not ((isinstance(item, dict) and item.get('comment') in comments_in_tab) or
                            (isinstance(item, str) and item in comments_in_tab))
                ]

            # Remove reference from internal tabs dictionary using the tab_name
            del self.tabs[tab_name]
            print(f"Removed '{tab_name}' from internal tabs dictionary.")
        else:
             print(f"Warning: Tab name '{tab_name}' not found in self.tabs dictionary during cleanup.")


        # --- Remove from Tab Widget ---
        self.tab_widget.removeTab(current_index)
        print(f"Removed tab at index {current_index} from QTabWidget.")

        # Schedule the closed widget for deletion
        tab_to_close.deleteLater()
        print(f"Scheduled widget for deletion: {tab_to_close}")

        # Update UI if no tabs are left
        if self.tab_widget.count() == 0:
            self.tab_widget.hide()
            self.initial_message.show()
            self.enable_dataset_operations(False)
            self.add_remove_button.setEnabled(False)
            self.export_selected_button.setEnabled(False)
            self.details_text_edit.clear()
            print("Last tab closed, updating UI.")
        # Don't automatically select another tab when closing duplicates,
        # as it might interfere with the deduplication loop. Selection can be handled
        # after deduplication is complete if needed.


    # Add the new deduplication method
    def deduplicate_restored_tabs(self):
        print("\nStarting post-restore tab deduplication...")
        content_signatures = {} # hash -> list of (tab_widget, original_tab_id, index)

        # 1. Calculate content signatures for all tabs
        for i in range(self.tab_widget.count()):
            tab_widget = self.tab_widget.widget(i)
            if not tab_widget: continue

            table = tab_widget.findChild(QTableWidget)
            if not table: continue

            original_tab_id = tab_widget.property("original_tab_id")
            if original_tab_id is None:
                 print(f"Warning: Tab at index {i} is missing 'original_tab_id' property.")
                 # Assign a low number to prioritize keeping tabs with valid IDs
                 original_tab_id = -1

            comments = []
            for row in range(table.rowCount()):
                item = table.item(row, 0)
                if item:
                    # Use UserRole data preferentially as it's the original comment
                    comment_text = item.data(Qt.UserRole)
                    if comment_text is None:
                         comment_text = item.text()
                         # Strip potential reply prefix if UserRole wasn't used
                         if isinstance(comment_text, str) and comment_text.startswith(" [↪ Reply] "):
                              comment_text = comment_text[len(" [↪ Reply] "):]
                    comments.append(str(comment_text)) # Ensure string conversion

            if not comments: # Skip empty tabs
                 continue

            # Create a consistent signature
            comments.sort()
            content_string = "|".join(comments)
            hasher = hashlib.sha256()
            hasher.update(content_string.encode('utf-8'))
            content_hash = hasher.hexdigest()

            if content_hash not in content_signatures:
                content_signatures[content_hash] = []
            content_signatures[content_hash].append((tab_widget, original_tab_id, i))
            print(f"  Tab index {i} (ID: {original_tab_id}): Content hash {content_hash[:8]}...")

        # 2. Identify tabs to remove
        tabs_to_remove_indices = set()
        for content_hash, tab_list in content_signatures.items():
            if len(tab_list) > 1:
                print(f"  Found duplicate content (Hash: {content_hash[:8]}...): {len(tab_list)} tabs.")
                # Sort by original_tab_id (descending) to keep the one saved most recently
                # Tabs without a valid ID (assigned -1) will be sorted last (less likely to be kept)
                tab_list.sort(key=lambda x: x[1], reverse=True)

                tab_to_keep_widget, id_to_keep, index_to_keep = tab_list[0]
                print(f"    Keeping Tab ID: {id_to_keep}, Index: {index_to_keep}")

                # Mark others for removal
                for i in range(1, len(tab_list)):
                    tab_to_remove_widget, id_to_remove, index_to_remove = tab_list[i]
                    # We need the index *at the time of removal*, store the index
                    tabs_to_remove_indices.add(index_to_remove)
                    print(f"    Marking Tab ID: {id_to_remove}, Index: {index_to_remove} for removal.")

        # 3. Remove duplicates (iterate by index in reverse order to avoid index shifting issues)
        if tabs_to_remove_indices:
            print(f"  Removing {len(tabs_to_remove_indices)} duplicate tabs...")
            sorted_indices_to_remove = sorted(list(tabs_to_remove_indices), reverse=True)

            for index in sorted_indices_to_remove:
                print(f"    Closing duplicate tab at index {index} (UI only)...")
                self.close_tab(index, delete_from_db=False)
            print("  Finished removing duplicate tabs.")
        else:
            print("  No duplicate tab content found.")

        print("Tab deduplication complete.\n")

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
        if current_tab:
            return current_tab.findChild(QTableWidget)
        return None

    def scrape_comments(self):
        url = self.url_input.text()
        if not url:
            display_message(self, "Error", "Please enter a URL.")
            return

        try:
            start_time = time.time() # Record start time
            self.show_loading(True)
            QApplication.processEvents()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
                temp_path = temp_file.name
            
            # Use filters instead of include_replies flag
            scrape_comments(url, temp_path, self.comment_filters)
            
            end_time = time.time() # Record end time
            duration = end_time - start_time
            print(f"Admin Scraping and initial processing took {duration:.2f} seconds.")

            df = pd.read_csv(temp_path)
            
            # Filter out replies if not included
            if not self.comment_filters.get("includeReplies", True):
                df = df[~df['Is Reply']]

            # Initialize counters for excluded comments
            short_comment_count = 0
            name_only_count = 0
            link_comment_count = 0
            emoji_only_count = 0
            total_comments = len(df)
            
            # Function to check if a comment is likely a name-only comment
            def is_name_only(text):
                # Convert to lowercase for better comparison
                text = text.lower()
                
                # Check common name patterns
                name_patterns = [
                    # Pattern: First Second Third
                    r"^[A-Za-z]+ [A-Za-z]+ [A-Za-z]+$",
                    # Pattern: Name @ Name
                    r"^[A-Za-z]+ @ [A-Za-z]+$",
                    # Pattern: First Last
                    r"^[A-Za-z]+ [A-Za-z]+$",
                    # Tag pattern
                    r"^@[A-Za-z0-9_]+$"
                ]
                
                # Common Filipino name markers
                name_markers = [
                    "kuya", "ate", "tita", "tito", "lola", "lolo", "nanay", "tatay", 
                    "mommy", "daddy", "mama", "papa", "inay", "itay", "sis", "bro"
                ]
                
                # Check if any word in the comment is a common name marker
                words = text.split()
                has_name_marker = any(marker in words for marker in name_markers)
                
                # Check against regex patterns
                matches_pattern = any(re.search(pattern, text, re.IGNORECASE) for pattern in name_patterns)
                
                return matches_pattern or has_name_marker
            
            # Function to check if comment has fewer words than minimum
            def is_short_comment(text):
                # Split by whitespace and count words
                words = text.strip().split()
                min_word_count = self.comment_filters.get("minWordCount", 3)
                return len(words) < min_word_count
            
            # Function to check if comment contains links
            def contains_link(text):
                # Simple regex to detect URLs
                url_pattern = r'https?://\S+|www\.\S+'
                return bool(re.search(url_pattern, text))
            
            # Function to check if comment only contains emojis
            def is_emoji_only(text):
                # Strip whitespace
                text = text.strip()
                if not text:
                    return False
                
                # Check if all characters are emojis or whitespace
                emoji_pattern = re.compile(
                    "["
                    "\U0001F600-\U0001F64F"  # emoticons
                    "\U0001F300-\U0001F5FF"  # symbols & pictographs
                    "\U0001F680-\U0001F6FF"  # transport & map symbols
                    "\U0001F700-\U0001F77F"  # alchemical symbols
                    "\U0001F780-\U0001F7FF"  # Geometric Shapes
                    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                    "\U0001FA00-\U0001FA6F"  # Chess Symbols
                    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                    "\U00002702-\U000027B0"  # Dingbats
                    "\U000024C2-\U0001F251" 
                    "]+|[\u2600-\u26FF\u2700-\u27BF]"
                )
                
                # Replace all emojis with empty string
                text_without_emojis = emoji_pattern.sub('', text)
                
                # If after removing emojis and whitespace there's nothing left, it's emoji-only
                return len(text_without_emojis.strip()) == 0
            
            # Get filter settings with defaults
            exclude_links = self.comment_filters.get("excludeLinks", True)
            exclude_emojis_only = self.comment_filters.get("excludeEmojisOnly", True)
            
            # Create mask for comments to keep
            keep_mask = pd.Series(True, index=df.index)
            
            # Apply filters
            for idx, row in df.iterrows():
                text = row['Text']
                
                # Check if comment is too short
                if is_short_comment(text):
                    keep_mask[idx] = False
                    short_comment_count += 1
                    continue
                
                # Check if comment is likely just a name
                if is_name_only(text):
                    keep_mask[idx] = False
                    name_only_count += 1
                    continue
                
                # Check if comment contains links and we want to exclude them
                if exclude_links and contains_link(text):
                    keep_mask[idx] = False
                    link_comment_count += 1
                    continue
                
                # Check if comment is emoji-only and we want to exclude them
                if exclude_emojis_only and is_emoji_only(text):
                    keep_mask[idx] = False
                    emoji_only_count += 1
                    continue
            
            # Apply the mask to keep only valid comments
            filtered_df = df[keep_mask]
            
            # Prepare comments data with all needed information
            comments_data = []
            
            for _, row in filtered_df.iterrows():
                comment_text = row['Text']
                
                # Store metadata
                self.comment_metadata[comment_text] = {
                    'profile_name': row['Profile Name'],
                    'profile_picture': row['Profile Picture'],
                    'date': row['Date'],
                    'likes_count': row['Likes Count'],
                    'profile_id': row['Profile ID'],
                    'is_reply': row['Is Reply'],
                    'reply_to': row['Reply To']
                }
                
                # Get prediction and confidence
                prediction, confidence = classify_comment(comment_text)
                
                # Add to comments data array
                comments_data.append({
                    'comment_text': comment_text,
                    'prediction': prediction,
                    'confidence': confidence,
                    'profile_name': row['Profile Name'],
                    'profile_picture': row['Profile Picture'],
                    'comment_date': row['Date'],
                    'likes_count': row['Likes Count'],
                    'profile_id': row['Profile ID'],
                    'is_reply': row['Is Reply'],
                    'reply_to': row['Reply To']
                })
            
            # Create a tab name based on URL
            tab_name = f"Facebook Post {self.url_tab_count}"
            self.url_tab_count += 1
            
            # Create table and populate it
            table = self.create_empty_tab(tab_name)
            self.populate_table(comments_data, append=False, target_table=table)
            
            # Save the initial state
            self.save_tab_state(tab_name, comments_data)
            
            # Show summary dialog with exclusion statistics and duration
            excluded_count = short_comment_count + name_only_count + link_comment_count + emoji_only_count
            filter_summary = ""
            if excluded_count > 0:
                min_word_count = self.comment_filters.get("minWordCount", 3)
                filter_summary = (
                    f"<b>Comments Filter Summary:</b><br>"
                    f"Total comments found: {total_comments}<br>"
                    f"Comments excluded: {excluded_count}<br>"
                    f"&nbsp;&nbsp;• Short comments (&lt; {min_word_count} words): {short_comment_count}<br>"
                    f"&nbsp;&nbsp;• Name-only comments: {name_only_count}<br>"
                    f"&nbsp;&nbsp;• Comments with links: {link_comment_count}<br>"
                    f"&nbsp;&nbsp;• Emoji-only comments: {emoji_only_count}<br><br>"
                    f"Comments displayed: {len(comments_data)}"
                )
            
            duration_summary = f"<b>Processing Time:</b><br>Scraping and analysis took {duration:.2f} seconds."            
            
            final_message = filter_summary + ("<br><br>" if filter_summary else "") + duration_summary
            
            QMessageBox.information(self, "Scraping Results", final_message)
            
            # Log the action
            log_user_action(self.current_user, f"Scraped FB post: {url[:30]}..." if len(url) > 30 else url)
            
        except Exception as e:
            display_message(self, "Error", f"Error scraping comments: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.show_loading(False)  # Hide loading overlay
    
    def process_csv(self):
        if not self.file_input.text():
            display_message(self, "Error", "Please select a CSV file first")
            return
        try:
            self.show_loading(True)  # Show loading overlay
            QApplication.processEvents()  # Ensure the UI updates
            
            file_path = self.file_input.text()
            
            # Get just the filename without path and extension for tab naming
            file_name = os.path.basename(file_path)
            file_name = os.path.splitext(file_name)[0]
            
            log_user_action(self.current_user, f"Started processing CSV file: {file_name}")
            
            df = pd.read_csv(file_path)
            # Get the first column for comments
            comments = df.iloc[:, 0].astype(str).tolist()
            
            # Create metadata for CSV comments
            for comment in comments:
                if comment not in self.comment_metadata:  # Only add if not already present
                    self.comment_metadata[comment] = {
                        'profile_name': 'CSV Input',
                        'profile_picture': '',
                        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'likes_count': 'N/A',
                        'profile_id': 'N/A'
                    }
            
            # Create comment data array with all needed information
            comments_data = []
            for comment in comments:
                prediction, confidence = classify_comment(comment)
                comments_data.append({
                    'comment_text': comment,
                    'prediction': prediction,
                    'confidence': confidence,
                    'profile_name': 'CSV Input',
                    'profile_picture': '',
                    'comment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'likes_count': 'N/A',
                    'profile_id': 'N/A',
                    'is_reply': False,
                    'reply_to': None
                })
            
            # Create tab name based on CSV file
            tab_name = f"CSV {self.csv_tab_count}: {file_name}"
            self.csv_tab_count += 1
            
            # Create table and populate it - explicitly passing the tab_name
            table = self.create_empty_tab(tab_name)
            
            # Always use append=False for new CSV data to replace any existing content
            self.populate_table(comments_data, append=False, target_table=table)
            
            # Save the state
            self.save_tab_state(tab_name, comments_data)
            
            log_user_action(self.current_user, f"Successfully processed CSV file: {file_name}")
            
        except Exception as e:
            display_message(self, "Error", f"Error reading CSV file: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.show_loading(False)  # Hide loading overlay

    def analyze_single(self):
        if not self.text_input.text():
            display_message(self, "Error", "Please enter a comment to analyze")
            return
        
        try:
            self.show_loading(True)  # Show loading overlay
            QApplication.processEvents()  # Ensure the UI updates
            
            # Get the comment text
            comment_text = self.text_input.text()
            
            # Check if the input is 5 words or less
            word_count = len(comment_text.split())
            is_short_input = word_count <= 5
            
            # Get prediction and confidence
            prediction, confidence = classify_comment(comment_text)
            
            # Store metadata for this comment
            self.comment_metadata[comment_text] = {
                'profile_name': 'Direct Input',
                'profile_picture': '',
                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'likes_count': 'N/A',
                'profile_id': 'N/A',
                'confidence': confidence
            }
            
            # Prepare comment data
            comment_data = [{
                'comment_text': comment_text,
                'prediction': prediction,
                'confidence': confidence,
                'profile_name': 'Direct Input',
                'profile_picture': '',
                'comment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'likes_count': 'N/A',
                'profile_id': 'N/A',
                'is_reply': False,
                'reply_to': None
            }]
            
            # Define tab name for direct inputs
            tab_name = "Direct Inputs"
            
            # Create or get the existing Direct Inputs tab
            table = self.create_empty_tab(tab_name)
            
            # Append the new comment to the existing table
            self.populate_table(comment_data, append=True, target_table=table)
            
            # Clear the input field
            self.text_input.clear()
            
            # Show warning if input is too short
            if is_short_input:
                warning_text = ("Input has 5 words or less. Prediction accuracy may be reduced for very short inputs, "
                                "especially if they are names, gibberish, or not in English/Tagalog.")
                display_message(self, "Warning", warning_text)

            # Now gather ALL comments from the Direct Inputs tab to save the complete state
            all_comments_data = []
            
            # Iterate through all rows in the table
            for row in range(table.rowCount()):
                row_comment_item = table.item(row, 0)
                row_prediction_item = table.item(row, 1)
                row_confidence_item = table.item(row, 2)
                
                if row_comment_item and row_prediction_item and row_confidence_item:
                    # Get the stored comment text (using UserRole if available)
                    row_comment_text = row_comment_item.data(Qt.UserRole) or row_comment_item.text()
                    row_prediction = row_prediction_item.text()
                    
                    # Get confidence - strip "%" and convert to float
                    try:
                        row_confidence_text = row_confidence_item.text()
                        row_confidence = float(row_confidence_text.strip('%'))
                    except:
                        row_confidence = 0.0
                    
                    # Get metadata for this comment
                    metadata = self.comment_metadata.get(row_comment_text, {})
                    
                    # Create data dictionary for this row
                    row_data = {
                        'comment_text': row_comment_text,
                        'prediction': row_prediction,
                        'confidence': row_confidence,
                        'profile_name': metadata.get('profile_name', 'Direct Input'),
                        'profile_picture': metadata.get('profile_picture', ''),
                        'comment_date': metadata.get('date', time.strftime('%Y-%m-%d %H:%M:%S')),
                        'likes_count': metadata.get('likes_count', 'N/A'),
                        'profile_id': metadata.get('profile_id', 'N/A'),
                        'is_reply': metadata.get('is_reply', False),
                        'reply_to': metadata.get('reply_to', None)
                    }
                    
                    all_comments_data.append(row_data)
            
            # Save the complete tab state with ALL comments
            self.save_tab_state(tab_name, all_comments_data)
            
            # Log the action
            log_user_action(self.current_user, "Analyzed single comment")
            
        except Exception as e:
            display_message(self, "Error", f"Error analyzing comment: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.show_loading(False)  # Hide loading overlay
    
    def populate_table(self, comments, append=False, target_table=None):
        """Create new tab and populate it based on input type"""
        # Store the input source before clearing
        file_path = self.file_input.text()
        url = self.url_input.text()

        # Clear inputs after checking
        self.file_input.clear()
        self.url_input.clear()

        if isinstance(comments, list) and len(comments) == 1 and isinstance(comments[0], dict) and not file_path and not url:
            # Direct input with comment dictionary
            tab_name = "Direct Inputs"
            comment_data = comments
        elif len(comments) == 1 and not file_path and not url:  # Check if it's truly direct input
            tab_name = "Direct Inputs"
            # Create comment data with prediction and confidence
            comment_data = []
            for comment in comments:
                if not isinstance(comment, dict):
                    prediction, confidence = classify_comment(comment)
                    comment_data.append({
                        'comment_text': comment,
                        'prediction': prediction,
                        'confidence': confidence,
                        'profile_name': 'Direct Input',
                        'profile_picture': '',
                        'comment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'likes_count': 'N/A',
                        'profile_id': 'N/A',
                        'is_reply': False,
                        'reply_to': None
                    })
                else:
                    comment_data.append(comment)
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
                    # Remove existing tab widget reference (don't remove from tab_widget yet)
                    if file_name in self.tabs:
                        self.tabs[file_name].deleteLater() # Clean up old widget
                        del self.tabs[file_name]
                        # Find the actual index to remove
                        for i in range(self.tab_widget.count()):
                            if self.tab_widget.tabText(i) == file_name:
                                self.tab_widget.removeTab(i)
                                break
                    tab_name = file_name
                    append = False # Ensure replacement
                elif msg.clickedButton() == new_tab_button:
                    # Find next available number
                    counter = 2
                    while f"{file_name} ({counter})" in self.tabs:
                        counter += 1
                    tab_name = f"{file_name} ({counter})"
                    append = False # Creating new tab
                else:
                    # User clicked Cancel
                    return
            else:
                tab_name = file_name
                append = False # Creating new tab
            
            # Create comment data with prediction and confidence
            comment_data = []
            for comment in comments:
                if not isinstance(comment, dict):
                    prediction, confidence = classify_comment(comment)
                    comment_data.append({
                        'comment_text': comment,
                        'prediction': prediction,
                        'confidence': confidence,
                        'profile_name': 'CSV Input',
                        'profile_picture': '',
                        'comment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'likes_count': 'N/A',
                        'profile_id': 'N/A',
                        'is_reply': False,
                        'reply_to': None
                    })
                else:
                    comment_data.append(comment)
                
        elif url:  # Facebook post
            # Find highest existing Facebook Post number
            highest_num = 0
            for existing_tab in self.tabs.keys():
                if existing_tab.startswith("Facebook Post "):
                    try:
                        num = int(existing_tab.split("Facebook Post ")[1])
                        highest_num = max(highest_num, num)
                    except (ValueError, IndexError):
                        continue
            
            # Set counter to next available number
            self.url_tab_count = highest_num + 1
            tab_name = f"Facebook Post {self.url_tab_count}"
            append = False # Creating new tab
            
            # Create comment data with prediction and confidence
            comment_data = []
            for comment in comments:
                if not isinstance(comment, dict):
                    prediction, confidence = classify_comment(comment)
                    metadata = self.comment_metadata.get(comment, {})
                    comment_data.append({
                        'comment_text': comment,
                        'prediction': prediction,
                        'confidence': confidence,
                        'profile_name': metadata.get('profile_name', 'FB Comment'),
                        'profile_picture': metadata.get('profile_picture', ''),
                        'comment_date': metadata.get('date', time.strftime('%Y-%m-%d %H:%M:%S')),
                        'likes_count': metadata.get('likes_count', 'N/A'),
                        'profile_id': metadata.get('profile_id', 'N/A'),
                        'is_reply': metadata.get('is_reply', False),
                        'reply_to': metadata.get('reply_to', None)
                    })
                else:
                    comment_data.append(comment)
                    
        else:  # Fallback case (shouldn't happen with current logic)
            # Find an appropriate name if other methods failed
            # Look for any source information in the comments
            source_found = False
            source_type = "Analysis"
            
            if comments and len(comments) > 0:
                # If the comments contain metadata, try to determine source
                first_comment = comments[0]
                if isinstance(first_comment, dict) and 'profile_name' in first_comment:
                    profile_name = first_comment.get('profile_name', '')
                    if profile_name == 'CSV Input':
                        source_type = "CSV Data"
                        source_found = True
                    elif profile_name == 'Direct Input':
                        source_type = "Direct Input"
                        tab_name = "Direct Inputs"
                        source_found = True
                    elif 'FB' in profile_name:
                        source_type = "Facebook Post"
                        source_found = True
            
            if not source_found:
                # Find highest existing Analysis number
                highest_num = 0
                for existing_tab in self.tabs.keys():
                    if existing_tab.startswith(f"{source_type} "):
                        try:
                            num = int(existing_tab.split(f"{source_type} ")[1])
                            highest_num = max(highest_num, num)
                        except (ValueError, IndexError):
                            continue
                
                tab_name = f"{source_type} {highest_num + 1}"
            elif source_type == "Direct Input":
                tab_name = "Direct Inputs"
            else:
                # Find highest existing Source type number
                highest_num = 0
                for existing_tab in self.tabs.keys():
                    if existing_tab.startswith(f"{source_type} "):
                        try:
                            num = int(existing_tab.split(f"{source_type} ")[1])
                            highest_num = max(highest_num, num)
                        except (ValueError, IndexError):
                            continue
                
                tab_name = f"{source_type} {highest_num + 1}"
            
            append = False
            
            # Create comment data with prediction and confidence
            comment_data = []
            for comment in comments:
                if not isinstance(comment, dict):
                    prediction, confidence = classify_comment(comment)
                    comment_data.append({
                        'comment_text': comment,
                        'prediction': prediction,
                        'confidence': confidence,
                        'profile_name': 'Input',
                        'profile_picture': '',
                        'comment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'likes_count': 'N/A',
                        'profile_id': 'N/A',
                        'is_reply': False,
                        'reply_to': None
                    })
                else:
                    comment_data.append(comment)

        # Get or create the table
        if target_table:
            # If a specific table is provided, use it
            table = target_table
        elif append and tab_name in self.tabs:
             # If appending and tab exists, get its table
             table = self.tabs[tab_name].findChild(QTableWidget)
        else:
             # Otherwise, create a new tab/table (handles replacement logic internally if name exists)
             table = self.create_empty_tab(tab_name)
        
        # Enable dataset operations since we now have data
        self.enable_dataset_operations(True)

        # Clear existing rows ONLY if not appending
        if not append:
            table.setRowCount(0)
        
        # Create a set of existing comments in the table if appending
        existing_comments_in_table = set()
        if append:
            for row in range(table.rowCount()):
                item = table.item(row, 0)
                if item:
                    existing_comments_in_table.add(item.data(Qt.UserRole) or item.text())

        for comment in comment_data:
            # Skip if appending and comment already exists
            comment_text = comment.get('comment_text', '')
            if append and comment_text in existing_comments_in_table:
                continue
            
            metadata = self.comment_metadata.get(comment_text, {})
            is_reply = metadata.get('is_reply', False)
            
            prediction = comment.get('prediction', '')
            confidence = comment.get('confidence', 0.0)
            
            row_position = table.rowCount()
            table.insertRow(row_position)

            # Create display text with reply indicator
            display_text = comment_text
            if is_reply:
                reply_to = metadata.get('reply_to', '')
                comment_item = QTableWidgetItem(display_text)
                comment_item.setData(Qt.UserRole, comment_text)  # Store original comment
                comment_item.setData(Qt.DisplayRole, f" [↪ Reply] {display_text}") 
                comment_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            else:
                comment_item = QTableWidgetItem(display_text)
                comment_item.setData(Qt.UserRole, comment_text)
                comment_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            # Add subtle background color for reply comments
            if is_reply:
                lighter_surface = QColor(COLORS['surface']).lighter(105)
                comment_item.setBackground(lighter_surface)

            # Set prediction cell
            prediction_item = QTableWidgetItem(prediction)
            prediction_item.setTextAlignment(Qt.AlignCenter)
            if prediction == "Potentially Harmful":
                prediction_item.setForeground(QColor(COLORS['potentially_harmful']))
            elif prediction == "Requires Review":
                prediction_item.setForeground(QColor(COLORS['requires_attention']))
            elif prediction == "Likely Appropriate":
                prediction_item.setForeground(QColor(COLORS['likely_appropriate']))

            # Display confidence (0-100) in the third column with %
            confidence_text = f"{confidence:.2f}%" # Format to 2 decimal places and add %
            confidence_item = QTableWidgetItem(confidence_text)
            confidence_item.setTextAlignment(Qt.AlignCenter)

            table.setItem(row_position, 0, comment_item)
            table.setItem(row_position, 1, prediction_item)
            table.setItem(row_position, 2, confidence_item) # Add to 3rd column

            table.resizeRowToContents(row_position)

            if comment_text in self.selected_comments:
                for col in range(table.columnCount()):
                    table.item(row_position, col).setBackground(QColor(COLORS['highlight']))

        # Reset sort dropdown to default (index 0) when replacing table content
        if not append and hasattr(table, 'sort_combo'):
            table.sort_combo.setCurrentIndex(0)
            # Optionally trigger the sort immediately if needed
            # self.sort_table(table)

        # Switch to the correct tab
        if tab_name in self.tabs:
             tab_index = self.tab_widget.indexOf(self.tabs[tab_name])
             if tab_index != -1:
                 self.tab_widget.setCurrentIndex(tab_index)
        
        # Save the tab state to the database
        if self.session_id:
            self.save_tab_state(tab_name, comment_data)
            
        # Log the action
        if self.current_user:
            action_type = "Loaded" if append else "Created"
            log_user_action(self.current_user, f"{action_type} tab: {tab_name}")

    def sort_table(self, table):
        """Sort table based on selected criteria using custom logic."""
        sort_combo = table.sort_combo
        index = sort_combo.currentIndex()
        
        # Disable sorting during the process
        table.setSortingEnabled(False)

        # --- Reply Filtering --- 
        if index == 5:  # "Show Replies Only"
            for row in range(table.rowCount()):
                comment_item = table.item(row, 0)
                # Check UserRole first for original text
                is_reply = False
                if comment_item:
                    metadata = self.comment_metadata.get(comment_item.data(Qt.UserRole) or comment_item.text(), {})
                    is_reply = metadata.get('is_reply', False)
                table.setRowHidden(row, not is_reply)
            # Re-enable sorting after filtering
            # table.setSortingEnabled(True) # Keep disabled, manual sort below
            return # Exit after filtering
        else:
            # Ensure all rows are visible if not filtering replies
            for row in range(table.rowCount()):
                table.setRowHidden(row, False)

        # --- Custom Sorting Logic --- 
        # Get data for sorting
        all_rows_data = []
        for row in range(table.rowCount()):
            comment_item = table.item(row, 0)
            prediction_item = table.item(row, 1)
            confidence_item = table.item(row, 2)
            
            if not (comment_item and prediction_item and confidence_item):
                # Skip rows with missing items to avoid errors
                continue 

            # Get original comment text (prefer UserRole)
            comment_text = comment_item.data(Qt.UserRole) or comment_item.text()
            # Clean potential display prefix if fallback to text() was used
            if comment_text.startswith(" [↪ Reply] "):
                 comment_text = comment_text[len(" [↪ Reply] "):]
            
            prediction_text = prediction_item.text()
            
            # Get numerical confidence
            confidence_value = 0.0
            try:
                # Use UserRole for confidence if available (safer)
                conf_data = confidence_item.data(Qt.UserRole)
                if conf_data is not None:
                     confidence_value = float(conf_data)
                else:
                     # Fallback: parse text, removing %
                     confidence_value = float(confidence_item.text().strip('%'))
            except (ValueError, TypeError):
                pass # Keep 0.0 if parsing fails
                
            all_rows_data.append((row, comment_text, prediction_text, confidence_value))

        # Define sort key based on index
        sort_key = None
        reverse_sort = False
        
        if index == 0: # Comment A-Z
            sort_key = lambda item: item[1].lower() # item[1] is comment_text
        elif index == 1: # Comment Z-A
            sort_key = lambda item: item[1].lower()
            reverse_sort = True
        elif index == 2: # Prediction A-Z
            sort_key = lambda item: item[2] # item[2] is prediction_text
        elif index == 3: # Confidence High-Low
            sort_key = lambda item: item[3] # item[3] is confidence_value
            reverse_sort = True
        elif index == 4: # Confidence Low-High
            sort_key = lambda item: item[3]
            
        # Perform the sort if a key is defined
        if sort_key:
            all_rows_data.sort(key=sort_key, reverse=reverse_sort)

        # --- Reorder Table Rows --- 
        # This part can be slow for large tables, but is necessary for custom sort
        current_row_mapping = {data[0]: data for data in all_rows_data}
        
        # Temporarily block signals to avoid triggering updates during move
        table.blockSignals(True)
        
        # Move rows according to the sorted order
        target_row = 0
        processed_original_rows = set()
        
        # Iterate through the desired sorted order
        for original_row_index, _, _, _ in all_rows_data:
            if original_row_index in processed_original_rows:
                 continue # Skip if this original row was already moved
            
            # Find the current visual position of the original row
            current_visual_row = -1
            for r in range(table.rowCount()):
                item = table.item(r, 0)
                if item and (item.data(Qt.UserRole) or item.text()) == current_row_mapping[original_row_index][1]:
                    current_visual_row = r
                    break
            
            if current_visual_row != -1 and current_visual_row != target_row:
                # Insert a new row at the target position
                table.insertRow(target_row)
                
                # Move items from the current visual row to the target row
                for col in range(table.columnCount()):
                    item_to_move = table.takeItem(current_visual_row + 1, col) # +1 because we inserted a row
                    table.setItem(target_row, col, item_to_move)
                    
                # Remove the now empty original row (which shifted down)
                table.removeRow(current_visual_row + 1)
                
            processed_original_rows.add(original_row_index)
            target_row += 1
            
        # Unblock signals
        table.blockSignals(False)
        
        # Optional: re-enable default sorting if desired, but manual sort is done
        # table.setSortingEnabled(True)

    def update_details_panel(self):
        """Update the details panel with selected comment information"""
        table = self.get_current_table()
        if not table:
            return
            
        selected_items = table.selectedItems()
        if not selected_items:
            self.details_text_edit.clear()
            self.add_remove_button.setEnabled(False)
            self.export_selected_button.setEnabled(False)
            has_data = self.tab_widget.count() > 0
            self.enable_dataset_operations(has_data)
            return

        self.add_remove_button.setEnabled(True)
        self.export_selected_button.setEnabled(True)
        self.enable_dataset_operations(True)

        row = selected_items[0].row()
        comment_item = table.item(row, 0)
        comment = comment_item.data(Qt.UserRole) or comment_item.text()
        prediction = table.item(row, 1).text()
        confidence = table.item(row, 2).text()
        
        metadata = self.comment_metadata.get(comment, {})
        
        # Check if this comment is in the selected list and update add/remove button text
        in_selected_list = False
        for item in self.selected_comments:
            if (isinstance(item, dict) and item.get('comment') == comment) or (isinstance(item, str) and item == comment):
                in_selected_list = True
                break
                
        if in_selected_list:
            self.add_remove_button.setText("➖ Remove from List")
        else:
            self.add_remove_button.setText("➕ Add to List")
        
        # Update details text
        self.details_text_edit.clear()
        def make_text(label, value):
            return f'<span style="{DETAIL_TEXT_STYLE}"><b>{label}</b>{value}</span>'

        # Add comment details
        self.details_text_edit.append(make_text("Comment:\n", f"{comment}\n"))
        self.details_text_edit.append(make_text("Commenter: ", f"{metadata.get('profile_name', 'N/A')}\n"))
        self.details_text_edit.append(make_text("Date: ", f"{metadata.get('date', 'N/A')}\n"))
        self.details_text_edit.append(make_text("Likes: ", f"{metadata.get('likes_count', 'N/A')}\n"))
        
        # Add reply information if applicable
        if metadata.get('is_reply', False) and metadata.get('reply_to'):
            for i in range(table.rowCount()):
                parent_item = table.item(i, 0)
                if parent_item:
                    parent_text = parent_item.data(Qt.UserRole) or parent_item.text()
                    if parent_text == metadata['reply_to']:
                        parent_metadata = self.comment_metadata.get(metadata['reply_to'], {})
                        self.details_text_edit.append("\n" + make_text("Reply Information:\n", ""))
                        self.details_text_edit.append(make_text("Row #", f"{i+1}\n"))
                        self.details_text_edit.append(make_text("Replying to: ", f"{parent_metadata.get('profile_name', 'Unknown')}\n"))
                        self.details_text_edit.append(make_text("Original Comment: ", f"{metadata['reply_to']}\n"))
                        self.details_text_edit.append(make_text("Date: ", f"{parent_metadata.get('date', 'N/A')}\n"))
                        break
            else:
                self.details_text_edit.append("\n" + make_text("Reply Information:\n", ""))
                self.details_text_edit.append(make_text("Replying to: ", f"{metadata['reply_to']}\n"))

        # Add classification details
        self.details_text_edit.append(make_text("Classification: ", f"{prediction}\n"))
        self.details_text_edit.append(make_text("Confidence: ", f"{confidence}\n"))
        self.details_text_edit.append(make_text("Status: ", f"{'In List' if in_selected_list else 'Not in List'}\n"))

    def toggle_list_status(self):
        selected_items = self.get_current_table().selectedItems()
        if not selected_items:
            display_message(self, "Error", "Please select a comment to add or remove")
            return

        row = selected_items[0].row()
        table = self.get_current_table()
        comment_item = table.item(row, 0)
        prediction_item = table.item(row, 1)
        confidence_item = table.item(row, 2)
        
        comment = comment_item.data(Qt.UserRole) or comment_item.text()
        prediction = prediction_item.text()
        confidence = confidence_item.text()
        
        # Check if this comment is already in the selected comments list
        for i, item in enumerate(self.selected_comments):
            if isinstance(item, dict) and item.get('comment') == comment:
                # Found it - remove it
                self.selected_comments.pop(i)
                display_message(self, "Success", "Comment removed from list")
                # Reset row color
                for col in range(table.columnCount()):
                    table.item(row, col).setBackground(QColor(COLORS['normal']))
                self.update_details_panel()
                return
            elif isinstance(item, str) and item == comment:
                # Found it (old format) - remove it
                self.selected_comments.pop(i)
                display_message(self, "Success", "Comment removed from list")
                # Reset row color
                for col in range(table.columnCount()):
                    table.item(row, col).setBackground(QColor(COLORS['normal']))
                self.update_details_panel()
                return
                
        # If we got here, the comment isn't in the list - add it with prediction and confidence
        self.selected_comments.append({
            'comment': comment,
            'prediction': prediction,
            'confidence': confidence
        })
        display_message(self, "Success", "Comment added to list")
        # Highlight row color
        for col in range(table.columnCount()):
            table.item(row, col).setBackground(QColor(COLORS['highlight']))
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
                # Prepare data for export depending on format of selected_comments
                export_data = []
                
                for item in self.selected_comments:
                    if isinstance(item, dict):
                        # New format with prediction and confidence
                        export_data.append([
                            item.get('comment', ''),
                            item.get('prediction', ''),
                            item.get('confidence', '')
                        ])
                    else:
                        # Legacy format (just strings)
                        comment = item
                        # Try to find prediction and confidence from current table
                        prediction = "Unknown"
                        confidence = "Unknown"
                        
                        # Look for this comment in current table
                        table = self.get_current_table()
                        for row in range(table.rowCount()):
                            comment_item = table.item(row, 0)
                            if comment_item and (comment_item.data(Qt.UserRole) == comment or comment_item.text() == comment):
                                prediction = table.item(row, 1).text()
                                confidence = table.item(row, 2).text()
                                break
                        
                        export_data.append([comment, prediction, confidence])
                
                df = pd.DataFrame(export_data, columns=['Comment', 'Prediction', 'Confidence'])
                df.to_csv(file_path, index=False)
                display_message(self, "Success", "Selected comments exported successfully")
            except Exception as e:
                display_message(self, "Error", f"Error exporting comments: {e}")

    def export_all(self):
        table = self.get_current_table()
        if not table or table.rowCount() == 0:
            display_message(self, "Info", "No comments to export")
            return

        # Prepare data for export
        export_data = []
        header = ["Comment", "Prediction", "Confidence", "Commenter", "Date", "Likes", "Profile ID", "Is Reply", "Reply To"]

        for row in range(table.rowCount()):
            comment_item = table.item(row, 0)
            prediction_item = table.item(row, 1)
            confidence_item = table.item(row, 2)
            
            if not comment_item or not prediction_item or not confidence_item:
                continue
                
            comment_text = comment_item.data(Qt.UserRole) or comment_item.text()
            prediction = prediction_item.text()
            confidence = confidence_item.text() # Get confidence string (e.g., "85.00%")

            # Get metadata
            metadata = self.comment_metadata.get(comment_text, {})
            
            export_data.append([
                comment_text,
                prediction,
                confidence, # Use the formatted string directly
                metadata.get('profile_name', 'N/A'),
                metadata.get('date', 'N/A'),
                metadata.get('likes_count', 'N/A'),
                metadata.get('profile_id', 'N/A'),
                "Yes" if metadata.get('is_reply') else "No",
                metadata.get('reply_to', 'N/A')
            ])

        # Show file dialog to save
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if file_path:
            try:
                df = pd.DataFrame(export_data, columns=header)
                df.to_csv(file_path, index=False)
                display_message(self, "Success", f"Successfully exported all comments to {file_path}")
            except Exception as e:
                display_message(self, "Error", f"Failed to export data: {e}")
                
    def show_summary(self):
        """Show summary with counts, ratios, and a pie chart for the three-level guidance system."""
        table = self.get_current_table()
        if not table or table.rowCount() == 0:
            display_message(self, "Info", "No comments to summarize")
            return

        total_comments = table.rowCount()
        potentially_harmful_count = 0
        requires_review_count = 0 # Changed from needs_review_count
        likely_appropriate_count = 0
        confidences = [] # Collect confidences

        for row in range(total_comments):
            comment_item = table.item(row, 0)
            prediction_item = table.item(row, 1)
            confidence_item = table.item(row, 2) # Get confidence item from 3rd column
            
            if not comment_item or not prediction_item or not confidence_item:
                continue
            
            # Get prediction label from 2nd column
            prediction = prediction_item.text()
            
            # Get confidence score (0-100) from 3rd column
            try:
                confidence = float(confidence_item.text().strip('%')) # Read float, remove %
                confidences.append(confidence)
            except ValueError:
                pass # Ignore if not a valid float

            if prediction == "Potentially Harmful":
                potentially_harmful_count += 1
            elif prediction == "Requires Review": # Changed from Needs Review
                requires_review_count += 1
            elif prediction == "Likely Appropriate":
                likely_appropriate_count += 1

        avg_confidence = np.mean(confidences) if confidences else 0

        # Calculate ratios
        harmful_ratio = (potentially_harmful_count / total_comments) if total_comments > 0 else 0
        review_ratio = (requires_review_count / total_comments) if total_comments > 0 else 0 # Changed from needs_review_count
        appropriate_ratio = (likely_appropriate_count / total_comments) if total_comments > 0 else 0

        summary_text = (
            f"<b>Guidance Summary of Current Tab</b><br><br>"
            f"Total Comments: {total_comments}<br>"
            f"<span style='color:{COLORS['potentially_harmful']}'>Potentially Harmful: {potentially_harmful_count} ({harmful_ratio:.1%})</span><br>"
            f"<span style='color:{COLORS['requires_attention']}'>Requires Review: {requires_review_count} ({review_ratio:.1%})</span><br>"
            f"<span style='color:{COLORS['likely_appropriate']}'>Likely Appropriate: {likely_appropriate_count} ({appropriate_ratio:.1%})</span><br>"
            f"Average Confidence: {avg_confidence:.2f}%<br>" # Display avg confidence with % sign
            f"<br><i>Note: This assessment is guidance-oriented and not a definitive judgment.</i>"
        )

        # --- Generate Pie Chart --- 
        chart_pixmap = None
        # Only generate pie chart if there are comments to display
        if total_comments > 0:
            labels = ['Potentially Harmful', 'Requires Review', 'Likely Appropriate'] # Changed label
            sizes = [potentially_harmful_count, requires_review_count, likely_appropriate_count] # Changed variable
            colors = [
                COLORS.get('potentially_harmful', '#EF5350'), 
                COLORS.get('requires_attention', '#FF9800'), # Still use the 'requires_attention' color key
                COLORS.get('likely_appropriate', '#66BB6A')
            ]
            
            # Only add segments with non-zero values
            non_zero_indices = [i for i, size in enumerate(sizes) if size > 0]
            if non_zero_indices:
                filtered_labels = [labels[i] for i in non_zero_indices]
                filtered_sizes = [sizes[i] for i in non_zero_indices]
                filtered_colors = [colors[i] for i in non_zero_indices]
                
                # Create explode tuple with slight emphasis on "Potentially Harmful" if it exists
                explode = [0.1 if label == 'Potentially Harmful' else 0 for label in filtered_labels]

                try:
                    fig, ax = plt.subplots(figsize=(5, 3.5))
                    ax.pie(filtered_sizes, explode=explode, labels=filtered_labels, colors=filtered_colors,
                           autopct='%1.1f%%', shadow=False, startangle=90,
                           textprops={'color': 'white'}) # White text for better visibility
                    ax.axis('equal')
                    fig.patch.set_alpha(0.0)
                    ax.patch.set_alpha(0.0)
                    
                    # Add a title noting this is guidance-oriented
                    ax.set_title("Content Guidance Assessment", color='white', pad=20)
                    
                    buf = BytesIO()
                    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, transparent=True)
                    plt.close(fig)
                    buf.seek(0)
                    
                    image = QImage.fromData(buf.getvalue())
                    chart_pixmap = QPixmap.fromImage(image)
                except Exception as e:
                    print(f"Error generating pie chart: {e}")
                    chart_pixmap = None
        # --- End Pie Chart --- 

        # Show custom dialog
        dialog = SummaryDialog(summary_text, chart_pixmap, self)
        dialog.exec_()
        
        log_user_action(self.current_user, "Viewed guidance summary")
    
    def show_word_cloud(self):
        """Generate and display word cloud visualization"""
        table = self.get_current_table()
        if not table or table.rowCount() == 0:
            display_message(self, "Error", "No comments to visualize")
            return

        all_comments = []
        for row in range(table.rowCount()):
            comment_item = table.item(row, 0)
            if comment_item:
                comment = comment_item.data(Qt.UserRole) or comment_item.text()
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
    
    def generate_report(self):
        """Generate report by calling the report generation function"""
        generate_report(self)

    def set_current_user(self, username):
        """Set the current user and create or restore their session"""
        self.current_user = username
        self.app_name_label.setText(f"Cyberbullying Content Guidance System - Admin View - {username}")
        
        # First create/copy session data in database
        self.create_or_restore_session()
        
        # Then restore UI from database
        self.restore_session()
        
        # Log the action
        log_user_action(username, "Admin login")

    def create_or_restore_session(self):
        """Create a new session or restore the last active one"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # First deactivate any existing active sessions
            cursor.execute("""
                UPDATE user_sessions 
                SET is_active = 0 
                WHERE username = ? AND is_active = 1
            """, (self.current_user,))
            
            # Create new session
            cursor.execute("""
                INSERT INTO user_sessions (username, is_active)
                VALUES (?, 1)
            """, (self.current_user,))
            conn.commit()
            
            # Get the new session ID
            self.session_id = cursor.execute("SELECT @@IDENTITY").fetchval()
            
            # Get the most recent session's tabs and comments
            cursor.execute("""
                SELECT TOP 1 session_id 
                FROM user_sessions 
                WHERE username = ? AND session_id != ?
                ORDER BY created_at DESC
            """, (self.current_user, self.session_id))
            
            last_session = cursor.fetchone()
            
            if last_session:
                # Copy tabs and comments from the last session
                old_session_id = last_session[0]
                
                # Check if we need to copy data
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM session_tabs
                    WHERE session_id = ?
                """, (old_session_id,))
                
                tab_count = cursor.fetchone()[0]
                
                if tab_count > 0:
                    # Copy tabs
                    cursor.execute("""
                        INSERT INTO session_tabs (session_id, tab_name, tab_type)
                        SELECT ?, tab_name, tab_type
                        FROM session_tabs
                        WHERE session_id = ?
                    """, (self.session_id, old_session_id))
                    
                    # Get the mapping of old tab_ids to new tab_ids
                    cursor.execute("""
                        SELECT t1.tab_id as old_tab_id, t2.tab_id as new_tab_id
                        FROM session_tabs t1
                        JOIN session_tabs t2 ON t1.tab_name = t2.tab_name
                        WHERE t1.session_id = ? AND t2.session_id = ?
                    """, (old_session_id, self.session_id))
                    
                    tab_mapping = {old: new for old, new in cursor.fetchall()}
                    
                    # Copy comments for each tab
                    for old_tab_id, new_tab_id in tab_mapping.items():
                        cursor.execute("""
                            INSERT INTO tab_comments (
                                tab_id, comment_text, prediction, confidence,
                                profile_name, profile_picture, comment_date,
                                likes_count, profile_id, is_reply, reply_to, is_selected
                            )
                            SELECT 
                                ?, comment_text, prediction, confidence,
                                profile_name, profile_picture, comment_date,
                                likes_count, profile_id, is_reply, reply_to, is_selected
                            FROM tab_comments
                            WHERE tab_id = ?
                        """, (new_tab_id, old_tab_id))
                    
                    conn.commit()
            
            conn.close()
            
        except Exception as e:
            print(f"Session creation/restoration error: {e}")

    def restore_session(self):
        """Restore tabs and comments from saved session"""
        try:
            # Clear existing UI tabs and self.tabs dictionary
            print("Starting session restore. Clearing UI tabs.")
            while self.tab_widget.count() > 0:
                 widget = self.tab_widget.widget(0)
                 self.tab_widget.removeTab(0)
                 if widget:
                      widget.deleteLater()
            self.tabs = {}
            # Prepare data structures: clear selected_comments, comment_metadata
            self.selected_comments = []
            self.comment_metadata = {}

            conn = get_db_connection()
            cursor = conn.cursor()
            # Fetch tabs from DB
            cursor.execute("""
                SELECT tab_id, tab_name, tab_type
                FROM session_tabs
                WHERE session_id = ?
                ORDER BY tab_id
            """, (self.session_id,))
            tabs_from_db = cursor.fetchall()
            print(f"Found {len(tabs_from_db)} tabs in database for session {self.session_id}")

            # Process tabs one by one
            for tab_id, original_tab_name, tab_type in tabs_from_db:
                print(f"Processing tab_id: {tab_id}, original_name: '{original_tab_name}'")
                # Fetch comments for tab_id
                cursor.execute("""
                    SELECT comment_text, prediction, confidence,
                           profile_name, profile_picture, comment_date,
                           likes_count, profile_id, is_reply, reply_to, is_selected
                    FROM tab_comments
                    WHERE tab_id = ?
                """, (tab_id,))
                comments_for_tab = cursor.fetchall()
                print(f"  Found {len(comments_for_tab)} comments for this tab.")
                if not comments_for_tab:
                     print(f"  Skipping tab '{original_tab_name}' - no comments found.")
                     continue

                # --- Handle potential duplicate tab names ---
                base_name = original_tab_name
                final_tab_name = base_name
                counter = 1
                while final_tab_name in self.tabs:
                     counter += 1
                     final_tab_name = f"{base_name} ({counter})"
                if final_tab_name != base_name:
                     print(f"  Duplicate UI name detected. Using new name: '{final_tab_name}'")

                # Process comments into list and update metadata/selected
                comments_data_list = []
                for db_row_index, comment_data in enumerate(comments_for_tab):
                    # ... (Existing logic to parse comment_data into comment_dict) ...
                    (comment_text, prediction, confidence, profile_name,
                     profile_picture, comment_date, likes_count, profile_id,
                     is_reply, reply_to, is_selected) = comment_data
                    # ... (Validation/cleaning) ...
                    comment_text = str(comment_text) if comment_text is not None else ""
                    prediction = str(prediction) if prediction is not None else ""
                    try:
                        confidence = float(confidence) if confidence is not None else 0.0
                    except (ValueError, TypeError):
                        confidence = 0.0
                    comment_dict = {
                        'comment_text': comment_text,
                        'prediction': prediction,
                        'confidence': confidence,
                        'profile_name': profile_name,
                        'profile_picture': profile_picture,
                        'comment_date': comment_date,
                        'likes_count': likes_count,
                        'profile_id': profile_id,
                        'is_reply': bool(is_reply),
                        'reply_to': reply_to
                    }
                    comments_data_list.append(comment_dict)
                    # ... (Update self.comment_metadata and self.selected_comments) ...
                    if comment_text and comment_text not in self.comment_metadata:
                        self.comment_metadata[comment_text] = {
                            'profile_name': profile_name,
                            'profile_picture': profile_picture,
                            'date': comment_date,
                            'likes_count': likes_count,
                            'profile_id': profile_id,
                            'is_reply': bool(is_reply),
                            'reply_to': reply_to,
                            'confidence': confidence
                        }
                    if is_selected:
                         is_already_selected = any(
                              (isinstance(item, dict) and item.get('comment') == comment_text) or \
                              (isinstance(item, str) and item == comment_text)
                              for item in self.selected_comments
                         )
                         if not is_already_selected:
                              self.selected_comments.append({
                                   'comment': comment_text,
                                   'prediction': prediction,
                                   'confidence': confidence
                              })
                # Create tab in UI using the final name
                print(f"  Calling create_empty_tab with name: '{final_tab_name}' (is_restoring=True)")
                table = self.create_empty_tab(final_tab_name, is_restoring=True)

                if table:
                    # *** STORE ORIGINAL TAB ID ON THE PARENT TAB WIDGET ***
                    # Navigate up from QTableWidget -> Layout -> QWidget (the actual tab page)
                    parent_widget = table.parentWidget()
                    tab_widget = parent_widget.parentWidget() if parent_widget else None

                    if isinstance(tab_widget, QWidget) and self.tab_widget.indexOf(tab_widget) != -1:
                         tab_widget.setProperty("original_tab_id", tab_id)
                         print(f"  Stored original_tab_id ({tab_id}) on tab widget: {tab_widget.objectName()}")
                    else:
                         print(f"  Warning: Could not find parent tab widget for table in '{final_tab_name}' to store original_tab_id.")

                    # Populate the table
                    print(f"  Populating table for tab '{final_tab_name}' with {len(comments_data_list)} comments.")
                    self.populate_table_directly(table, comments_data_list)
                    print(f"  Finished populating table for '{final_tab_name}'.")
                else:
                    print(f"  Warning: create_empty_tab did not return a table for '{final_tab_name}'.")

                print(f"Restored tab '{final_tab_name}' (Original DB ID: {tab_id}, Name: '{original_tab_name}') with {len(comments_data_list)} comments")

            conn.close()
            print("Finished processing all tabs from database.")

            # *** CALL DEDUPLICATION AFTER PROCESSING ALL TABS ***
            self.deduplicate_restored_tabs()

            # --- Final UI State Update ---
            if self.tab_widget.count() > 0:
                 print("Tabs exist after deduplication. Finalizing UI.")
                 self.initial_message.hide()
                 self.tab_widget.show()
                 self.enable_dataset_operations(True)
                 if self.tab_widget.currentIndex() == -1: # Select first tab if none is selected
                      self.tab_widget.setCurrentIndex(0)
                 self.update_details_panel() # Update details for the currently selected tab
            else:
                 print("No tabs remaining after deduplication. Showing initial message.")
                 self.initial_message.show()
                 self.tab_widget.hide()
                 self.enable_dataset_operations(False)
                 self.details_text_edit.clear()
                 self.add_remove_button.setEnabled(False)
                 self.export_selected_button.setEnabled(False)

            print("Session restore complete.")

        except Exception as e:
            print(f"Session restoration error: {e}")
            import traceback
            traceback.print_exc()

    def populate_table_directly(self, table, comments):
        """Directly populate table with comment data - used for restoring session. Assumes table might already have content from previous restores in the same session, so checks for duplicates."""
        # Create a set of existing comments IN THIS SPECIFIC TABLE to avoid duplicates within the same restore call
        existing_comments_in_this_table = set()
        for row in range(table.rowCount()):
            comment_item = table.item(row, 0)
            if comment_item:
                # Use UserRole first, then text as fallback
                text = comment_item.data(Qt.UserRole) or comment_item.text()
                # Handle potential prefix if it's already displayed
                if text.startswith(" [↪ Reply] "):
                    text = text[len(" [↪ Reply] "):]
                existing_comments_in_this_table.add(text)

        for comment in comments:
            # Skip if already in table
            comment_text = comment.get('comment_text', '')
            if not comment_text or comment_text in existing_comments_in_this_table:
                continue
                
            existing_comments_in_this_table.add(comment_text) # Add to set after check
            
            prediction = comment.get('prediction', '')
            # Ensure confidence is float before formatting
            confidence_val = comment.get('confidence', 0.0)
            try:
                confidence = float(confidence_val)
            except (ValueError, TypeError):
                confidence = 0.0
            
            # Use metadata stored during the restore loop, falling back if needed
            metadata = self.comment_metadata.get(comment_text, {}) 
            is_reply = metadata.get('is_reply', False)

            # Insert new row
            row_position = table.rowCount()
            table.insertRow(row_position)

            # Set comment cell
            display_text = comment_text
            comment_item = QTableWidgetItem() # Create item first
            comment_item.setData(Qt.UserRole, comment_text) # Store original text
            if is_reply:
                reply_to = metadata.get('reply_to', '')
                comment_item.setData(Qt.DisplayRole, f" [↪ Reply] {display_text}")
            else:
                comment_item.setData(Qt.DisplayRole, display_text)
                
            comment_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            # Apply subtle background for replies AFTER setting data
            if is_reply:
                lighter_surface = QColor(COLORS['surface']).lighter(105)
                comment_item.setBackground(lighter_surface)

            # Set prediction cell
            prediction_item = QTableWidgetItem(prediction)
            prediction_item.setTextAlignment(Qt.AlignCenter)
            if prediction == "Cyberbullying":
                prediction_item.setForeground(QColor(COLORS['bullying']))
            elif prediction == "Likely Appropriate":
                prediction_item.setForeground(QColor(COLORS['likely_appropriate']))
            elif prediction == "Requires Review":
                prediction_item.setForeground(QColor(COLORS['requires_attention']))
            else:
                prediction_item.setForeground(QColor(COLORS['potentially_harmful']))
            
            # Set confidence cell (formatted 0-100 with %)
            confidence_text = f"{confidence:.2f}%" # Format to 2 decimal places and add %
            confidence_item = QTableWidgetItem(confidence_text)
            # Store actual float value for potential sorting
            confidence_item.setData(Qt.UserRole, confidence) 
            confidence_item.setTextAlignment(Qt.AlignCenter)

            # Add data to table
            table.setItem(row_position, 0, comment_item)
            table.setItem(row_position, 1, prediction_item)
            table.setItem(row_position, 2, confidence_item) # Add to 3rd column

            # Resize row to fit content
            table.resizeRowToContents(row_position)

            # Highlight if in selected comments (check against the potentially updated self.selected_comments)
            is_selected_in_list = False
            for item in self.selected_comments:
                 if isinstance(item, dict) and item.get('comment') == comment_text:
                     is_selected_in_list = True
                     break
                 elif isinstance(item, str) and item == comment_text:
                     # Handle legacy string format if still present
                     is_selected_in_list = True
                     break
                     
            if is_selected_in_list:
                highlight_color = QColor(COLORS['highlight'])
                for col in range(table.columnCount()):
                    current_item = table.item(row_position, col)
                    if current_item: # Check if item exists before setting background
                         # Preserve reply background if highlighting
                         original_bg = current_item.background()
                         if is_reply and original_bg.isValid() and original_bg != QColor(Qt.transparent):
                              # Blend highlight with reply color (simple alpha blend)
                              blended_color = QColor.fromRgbF(
                                   (highlight_color.redF() * 0.3 + original_bg.redF() * 0.7),
                                   (highlight_color.greenF() * 0.3 + original_bg.greenF() * 0.7),
                                   (highlight_color.blueF() * 0.3 + original_bg.blueF() * 0.7)
                              )
                              current_item.setBackground(blended_color)
                         else:
                              current_item.setBackground(highlight_color)

    def save_tab_state(self, tab_name, comments):
        """Save tab and its comments to the database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if tab already exists for this session
            cursor.execute("""
                SELECT tab_id FROM session_tabs 
                WHERE session_id = ? AND tab_name = ?
            """, (self.session_id, tab_name))
            
            tab_result = cursor.fetchone()
            
            if tab_result:
                # Tab exists, get its ID
                tab_id = tab_result[0]
                
                # Delete existing comments for this tab to avoid duplicates
                cursor.execute("""
                    DELETE FROM tab_comments 
                    WHERE tab_id = ?
                """, (tab_id,))
            else:
                # Create new tab record
                cursor.execute("""
                    INSERT INTO session_tabs (session_id, tab_name, tab_type)
                    VALUES (?, ?, ?)
                """, (self.session_id, tab_name, "analysis"))
                
                tab_id = cursor.execute("SELECT @@IDENTITY").fetchval()
            
            # Save each comment
            for comment in comments:
                try:
                    metadata = self.comment_metadata.get(comment.get('comment_text', ''), {})
                    
                    # Get prediction and confidence from the comment data
                    prediction = comment.get('prediction', '')
                    confidence = comment.get('confidence', 0.0)
                    
                    # Handle likes_count - ensure it's a valid float or NULL
                    likes_count = metadata.get('likes_count')
                    try:
                        likes_count = float(likes_count) if likes_count not in ('N/A', '', None) else None
                    except (ValueError, TypeError):
                        likes_count = None
                    
                    # Clean up text fields to handle emojis and special characters
                    def clean_text(value):
                        if value is None:
                            return ''
                        # Convert float/int to string if needed
                        if isinstance(value, (float, int)):
                            value = str(value)
                        # Handle string encoding
                        try:
                            return value.encode('ascii', 'ignore').decode()
                        except AttributeError:
                            return str(value)
                    
                    clean_comment = clean_text(comment.get('comment_text', ''))
                    clean_profile_name = clean_text(metadata.get('profile_name', ''))
                    clean_profile_picture = clean_text(metadata.get('profile_picture', ''))
                    clean_reply_to = clean_text(metadata.get('reply_to', ''))
                    
                    cursor.execute("""
                        INSERT INTO tab_comments (
                            tab_id, comment_text, prediction, confidence,
                            profile_name, profile_picture, comment_date,
                            likes_count, profile_id, is_reply, reply_to, is_selected
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        tab_id,
                        clean_comment,
                        prediction,
                        confidence,  # Store actual confidence value
                        clean_profile_name,
                        clean_profile_picture,
                        metadata.get('date'),
                        likes_count,
                        metadata.get('profile_id'),
                        float(bool(metadata.get('is_reply', False))),
                        clean_reply_to,
                        clean_comment in self.selected_comments
                    ))
                    
                except Exception as e:
                    print(f"Error saving comment {comment}: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Tab save error: {e}")

    def close_session(self):
        """Close the current session"""
        if self.session_id:
            try:
                # First, we need to ensure all tab state is saved
                for tab_name, tab_widget in self.tabs.items():
                    try:
                        # Get the table from this tab
                        table = tab_widget.findChild(QTableWidget)
                        if not table:
                            continue
                            
                        # Gather all comments from this tab
                        tab_comments = []
                        for row in range(table.rowCount()):
                            row_comment_item = table.item(row, 0)
                            row_prediction_item = table.item(row, 1)
                            row_confidence_item = table.item(row, 2)
                            
                            if row_comment_item and row_prediction_item and row_confidence_item:
                                # Get the stored comment text (using UserRole if available)
                                row_comment_text = row_comment_item.data(Qt.UserRole) or row_comment_item.text()
                                row_prediction = row_prediction_item.text()
                                
                                # Get confidence
                                try:
                                    row_confidence_text = row_confidence_item.text()
                                    row_confidence = float(row_confidence_text.strip('%'))
                                except:
                                    row_confidence = 0.0
                                
                                # Get metadata
                                metadata = self.comment_metadata.get(row_comment_text, {})
                                
                                # Create data dictionary
                                row_data = {
                                    'comment_text': row_comment_text,
                                    'prediction': row_prediction,
                                    'confidence': row_confidence,
                                    'profile_name': metadata.get('profile_name', 'Direct Input'),
                                    'profile_picture': metadata.get('profile_picture', ''),
                                    'comment_date': metadata.get('date', time.strftime('%Y-%m-%d %H:%M:%S')),
                                    'likes_count': metadata.get('likes_count', 'N/A'),
                                    'profile_id': metadata.get('profile_id', 'N/A'),
                                    'is_reply': metadata.get('is_reply', False),
                                    'reply_to': metadata.get('reply_to', None)
                                }
                                
                                tab_comments.append(row_data)
                        
                        # Save this tab's state
                        if tab_comments:
                            self.save_tab_state(tab_name, tab_comments)
                            print(f"Saved state for tab '{tab_name}' with {len(tab_comments)} comments")
                    
                    except Exception as tab_error:
                        print(f"Error saving tab '{tab_name}' before session close: {tab_error}")
                        import traceback
                        traceback.print_exc()
                
                # Now mark the session as inactive
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_sessions 
                    SET is_active = 0, last_accessed = GETDATE()
                    WHERE session_id = ?
                """, (self.session_id,))
                conn.commit()
                conn.close()
                
                print(f"Successfully closed session {self.session_id}")
            except Exception as e:
                print(f"Session close error: {e}")
                import traceback
                traceback.print_exc()

    def show_filters_dialog(self):
        """Show the filters dialog"""
        dialog = CommentFiltersDialog(self.comment_filters, self)
        dialog.filtersUpdated.connect(self.update_filters)
        dialog.exec_()
    
    def update_filters(self, new_filters):
        """Update filter settings when dialog emits filtersUpdated signal"""
        self.comment_filters = new_filters
        try:
            # Log filter changes
            log_user_action(self.current_user, f"Updated comment filters: Max comments={new_filters['maxComments']}, Include Replies={new_filters['includeReplies']}")
        except Exception as log_error:
            print(f"Logging error: {log_error}")
