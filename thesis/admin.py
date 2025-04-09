from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QLabel, QPushButton, QDialog, QLineEdit, QTextEdit,
                             QFileDialog, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QSplitter, QGridLayout, QComboBox, QSizePolicy,
                             QStackedWidget, QTabWidget, QMessageBox, QCheckBox, QTabBar)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QFont, QPixmap, QImage, QIcon, QPainter
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd
import tempfile
import time
import re
import os

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
        self.selected_comments = []  # List for selected comments
        self.comment_metadata = {}  # Comment metadata storage
        self.csv_tab_count = 1
        self.url_tab_count = 1
        self.tabs = {}  # Dictionary to store tab references
        
        # Set window properties
        self.setWindowTitle("Cyberbullying Detection System - Admin")
        self.showFullScreen()
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")
        
        # Set window icon
        app_icon = QIcon("./assets/applogo.png")
        self.setWindowIcon(app_icon)
        
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
        self.app_name_label = QLabel("Cyberbullying Detection System - Admin View")
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
        
        self.include_replies = QCheckBox("Include Replies")
        self.include_replies.setStyleSheet(CHECKBOX_REPLY_STYLE)
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
        self.export_all_button = QPushButton("📤 Export All")
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
        dialog = APIManagerDialog(self)
        dialog.exec_()
        
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

    def create_empty_tab(self, tab_type):
        """Create a new empty tab with table"""
        # Truncate tab name for consistent width
        tab_display_name = self.truncate_tab_name(tab_type)
        
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

        # Create and configure table
        table = QTableWidget()
        table.setSortingEnabled(True)
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
        
        # Add tab to widget and store reference - use display name for UI but store full name in dict
        self.tab_widget.addTab(tab, tab_display_name)
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
            self.add_remove_button.setEnabled(False)  # Disable row operations
            self.export_selected_button.setEnabled(False) # Disable row operations
            self.details_text_edit.clear() # Clear details panel
    
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
            self.show_loading(True)
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
                temp_path = temp_file.name
            
            # Pass include_replies flag to scrape_comments
            scrape_comments(url, temp_path, self.include_replies.isChecked())
            df = pd.read_csv(temp_path)
            
            # Filter out replies if not included
            if not self.include_replies.isChecked():
                df = df[~df['Is Reply']]

            # Initialize counters for excluded comments
            short_comment_count = 0
            name_only_count = 0
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
            
            # Function to check if comment has 3 or fewer words
            def is_short_comment(text):
                # Split by whitespace and count words
                words = text.strip().split()
                return len(words) <= 3
            
            # Filter the dataframe
            filtered_df = df.copy()
            
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
            
            # Apply the mask to keep only valid comments
            filtered_df = df[keep_mask]
            
            # Store additional comment metadata
            self.comment_metadata = {}
            for _, row in filtered_df.iterrows():
                self.comment_metadata[row['Text']] = {
                    'profile_name': row['Profile Name'],
                    'profile_picture': row['Profile Picture'],
                    'date': row['Date'],
                    'likes_count': row['Likes Count'],
                    'profile_id': row['Profile ID'],
                    'is_reply': row['Is Reply'],
                    'reply_to': row['Reply To']
                }
            
            comments = filtered_df['Text'].tolist()
            self.populate_table(comments)
            
            # Show summary dialog with exclusion statistics
            excluded_count = short_comment_count + name_only_count
            if excluded_count > 0:
                message = (
                    f"Comments Filter Summary:\n\n"
                    f"Total comments found: {total_comments}\n"
                    f"Comments excluded: {excluded_count}\n"
                    f"• Short comments (3 words or less): {short_comment_count}\n"
                    f"• Name-only comments: {name_only_count}\n\n"
                    f"Comments displayed: {len(comments)}"
                )
                QMessageBox.information(self, "Comment Filtering Results", message)
            
        except Exception as e:
            display_message(self, "Error", f"Error scraping comments: {e}")
        finally:
            self.show_loading(False)  # Hide loading overlay
    
    def process_csv(self):
        if not self.file_input.text():
            display_message(self, "Error", "Please select a CSV file first")
            return
        try:
            self.show_loading(True)  # Show loading overlay
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()  # Ensure the UI updates
            
            df = pd.read_csv(self.file_input.text())
            # Convert all values to strings to handle numeric values
            comments = df.iloc[:, 0].astype(str).tolist()
            
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
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()  # Ensure the UI updates
            
            # Create metadata for the direct input comment
            comment = self.text_input.text()
            
            # Check if the comment already exists in metadata (might be from previous input)
            if comment not in self.comment_metadata:
                self.comment_metadata[comment] = {
                    'profile_name': 'Direct Input',
                    'profile_picture': '',
                    'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'likes_count': 'N/A',
                    'profile_id': 'N/A'
                }
            
            # Call populate_table with append=True
            self.populate_table([comment], append=True)
            
            # Clear the input field after processing
            self.text_input.clear()
            
        finally:
            self.show_loading(False)  # Hide loading overlay
    
    def populate_table(self, comments, append=False):
        """Create new tab and populate it based on input type"""
        # Store the input source before clearing
        file_path = self.file_input.text()
        url = self.url_input.text()

        # Clear inputs after checking
        self.file_input.clear()
        self.url_input.clear()

        if len(comments) == 1 and not file_path and not url:  # Check if it's truly direct input
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
        else:  # Fallback case (shouldn't happen with current logic)
            tab_name = f"Analysis {self.csv_tab_count + self.url_tab_count}"
            append = False

        # Get or create the table
        if append and tab_name in self.tabs:
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

        for comment in comments:
             # Skip if appending and comment already exists
            if append and comment in existing_comments_in_table:
                continue
            
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

            # Set prediction cell
            prediction_item = QTableWidgetItem(prediction)
            prediction_item.setTextAlignment(Qt.AlignCenter)
            if prediction == "Cyberbullying":
                prediction_item.setForeground(QColor(COLORS['bullying']))
            else:
                prediction_item.setForeground(QColor(COLORS['normal']))

            # Display confidence (0-100) in the third column with %
            confidence_text = f"{confidence:.2f}%" # Format to 2 decimal places and add %
            confidence_item = QTableWidgetItem(confidence_text)
            confidence_item.setTextAlignment(Qt.AlignCenter)

            table.setItem(row_position, 0, comment_item)
            table.setItem(row_position, 1, prediction_item)
            table.setItem(row_position, 2, confidence_item) # Add to 3rd column

            table.resizeRowToContents(row_position)

            if comment in self.selected_comments:
                for col in range(table.columnCount()):
                    table.item(row_position, col).setBackground(QColor(COLORS['highlight']))

        # Switch to the correct tab
        if tab_name in self.tabs:
             tab_index = self.tab_widget.indexOf(self.tabs[tab_name])
             if tab_index != -1:
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
        """Show summary with counts, ratios, and a pie chart."""
        table = self.get_current_table()
        if not table or table.rowCount() == 0:
            display_message(self, "Info", "No comments to summarize")
            return

        total_comments = table.rowCount()
        cyberbullying_count = 0
        normal_count = 0
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

            if prediction == "Cyberbullying":
                cyberbullying_count += 1
            elif prediction == "Normal":
                normal_count += 1

        avg_confidence = np.mean(confidences) if confidences else 0

        # Calculate ratios
        bully_ratio = (cyberbullying_count / total_comments) if total_comments > 0 else 0
        normal_ratio = (normal_count / total_comments) if total_comments > 0 else 0

        summary_text = (
            f"<b>Summary of Current Tab</b><br><br>"
            f"Total Comments: {total_comments}<br>"
            f"Cyberbullying: {cyberbullying_count} ({bully_ratio:.1%})<br>"
            f"Normal: {normal_count} ({normal_ratio:.1%})<br>"
            f"Average Confidence: {avg_confidence:.2f}<br>" # Display avg confidence (0-100)
        )

        # --- Generate Pie Chart --- 
        chart_pixmap = None
        # Only generate pie chart if both classes are present
        if total_comments > 0 and cyberbullying_count > 0 and normal_count > 0:
            labels = ['Cyberbullying', 'Normal']
            sizes = [cyberbullying_count, normal_count]
            colors = [COLORS.get('bullying', '#FF6347'), COLORS.get('normal', '#90EE90')] 
            explode = (0.1, 0) if cyberbullying_count > 0 else (0, 0) 

            try:
                fig, ax = plt.subplots(figsize=(5, 3.5))
                ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                       autopct='%1.1f%%', shadow=False, startangle=90,
                       textprops={'color': 'white'}) # Changed text color to white
                ax.axis('equal')
                fig.patch.set_alpha(0.0)
                ax.patch.set_alpha(0.0)
                
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
