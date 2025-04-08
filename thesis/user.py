from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QTextEdit, QWidget, 
                           QFileDialog, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QSplitter, QGridLayout, QComboBox, 
                           QSizePolicy, QStackedWidget, QDialog, QTabWidget, QTabBar,
                           QMessageBox, QCheckBox, QApplication, QRadioButton)
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QColor, QFont, QPixmap, QImage, QIcon, QPainter, QPen
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
                   ABOUT_BUTTON_OUTLINE_STYLE, DETAIL_TEXT_SPAN_STYLE,
                   SECTION_CONTAINER_STYLE, DETAILS_SECTION_STYLE, TEXT_EDIT_STYLE,
                   MENU_BAR_STYLE, CHECKBOX_REPLY_STYLE, ROW_OPERATION_BUTTON_STYLE)
import tempfile
import time
from comment_operations import generate_report_user
from loading_overlay import LoadingOverlay
from stopwords import TAGALOG_STOP_WORDS
import re
from db_config import log_user_action, get_db_connection
import os

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

class UserMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_comments = []
        self.comment_metadata = {}
        self.current_user = None
        self.main_window = None
        self.session_id = None  # Add session ID property
        self.setWindowTitle("Cyberbullying Detection - User View")
        self.showFullScreen()
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")

        # Set window icon
        base_path = os.path.dirname(os.path.abspath(__file__))
        app_icon = QIcon(os.path.join(base_path, "assets", "applogo.png"))
        self.setWindowIcon(app_icon)

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

        # Initialize input stack
        self.input_stack = QStackedWidget()

        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self)

        # Initialize main UI
        self.init_main_ui()

    def set_current_user(self, username):
        """Set the current user and create or restore their session"""
        self.current_user = username
        self.app_name_label.setText(f"Cyberbullying Detection System - {username}")
        self.create_or_restore_session()
        log_user_action(username, "User login")

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
            
            # Now restore the UI state
            self.restore_session()
            
        except Exception as e:
            print(f"Session creation/restoration error: {e}")

    def restore_session(self):
        """Restore tabs and comments from saved session"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Get all tabs for this session
            cursor.execute("""
                SELECT tab_id, tab_name, tab_type 
                FROM session_tabs 
                WHERE session_id = ?
            """, (self.session_id,))
            
            tabs = cursor.fetchall()
            
            for tab_id, tab_name, tab_type in tabs:
                # Create tab in UI
                table = self.create_empty_tab(tab_name)
                
                # Get comments for this tab
                cursor.execute("""
                    SELECT comment_text, prediction, confidence,
                           profile_name, profile_picture, comment_date,
                           likes_count, profile_id, is_reply, reply_to, is_selected
                    FROM tab_comments 
                    WHERE tab_id = ?
                """, (tab_id,))
                
                comments = cursor.fetchall()
                
                for comment_data in comments:
                    (comment_text, prediction, confidence, profile_name, 
                     profile_picture, comment_date, likes_count, profile_id, 
                     is_reply, reply_to, is_selected) = comment_data
                    
                    # Store metadata
                    self.comment_metadata[comment_text] = {
                        'profile_name': profile_name,
                        'profile_picture': profile_picture,
                        'date': comment_date,
                        'likes_count': likes_count,
                        'profile_id': profile_id,
                        'is_reply': is_reply,
                        'reply_to': reply_to
                    }
                    
                    # Add to selected comments if selected
                    if is_selected:
                        self.selected_comments.append(comment_text)
                    
                    # Add row to table
                    row_position = table.rowCount()
                    table.insertRow(row_position)
                    
                    display_text = f" [↪ Reply] {comment_text}" if is_reply else comment_text
                    
                    comment_item = QTableWidgetItem(display_text)
                    comment_item.setData(Qt.UserRole, comment_text)
                    
                    prediction_item = QTableWidgetItem(prediction)
                    prediction_item.setTextAlignment(Qt.AlignCenter)
                    
                    if prediction == "Cyberbullying":
                        prediction_item.setForeground(QColor(COLORS['bullying']))
                    else:
                        prediction_item.setForeground(QColor(COLORS['normal']))
                    
                    table.setItem(row_position, 0, comment_item)
                    table.setItem(row_position, 1, prediction_item)
                    
                    if is_selected:
                        for col in range(table.columnCount()):
                            table.item(row_position, col).setBackground(QColor(COLORS['highlight']))
                    
                    table.resizeRowToContents(row_position)
            
            conn.close()
            
        except Exception as e:
            print(f"Session restoration error: {e}")

    def save_tab_state(self, tab_name, comments):
        """Save tab and its comments to the database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Create tab record
            cursor.execute("""
                INSERT INTO session_tabs (session_id, tab_name, tab_type)
                VALUES (?, ?, ?)
            """, (self.session_id, tab_name, "analysis"))
            
            tab_id = cursor.execute("SELECT @@IDENTITY").fetchval()
            
            # Save each comment
            for comment in comments:
                try:
                    row = self.get_row_by_comment(comment)
                    if row is None:
                        continue
                    
                    metadata = self.comment_metadata.get(comment, {})
                    
                    # Get table values
                    prediction = self.get_current_table().item(row, 1).text()
                    confidence_text = self.get_current_table().item(row, 2).text().strip('%')
                    confidence_value = float(confidence_text) / 100
                    
                    # Handle likes_count - ensure it's a valid float or NULL
                    likes_count = metadata.get('likes_count')
                    try:
                        likes_count = float(likes_count) if likes_count not in ('N/A', '', None) else None
                    except (ValueError, TypeError):
                        likes_count = None
                    
                    # Clean up text fields to handle emojis and special characters
                    # Ensure values are strings before encoding
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
                    
                    clean_comment = clean_text(comment)
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
                        confidence_value,
                        clean_profile_name,
                        clean_profile_picture,
                        metadata.get('date'),
                        likes_count,
                        metadata.get('profile_id'),
                        float(bool(metadata.get('is_reply', False))),
                        clean_reply_to,
                        comment in self.selected_comments
                    ))
                    
                except Exception as e:
                    print(f"Error saving comment {comment}: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Tab save error: {e}")

    def get_row_by_comment(self, comment_text):
        """Helper function to find row number by comment text"""
        table = self.get_current_table()
        if not table:
            return None
            
        for row in range(table.rowCount()):
            # Check both display text and stored data
            item = table.item(row, 0)
            if not item:
                continue
                
            stored_text = item.data(Qt.UserRole)
            if stored_text == comment_text:
                return row
                
        return None

    def confirm_sign_out(self):
        """Show confirmation dialog before signing out and close session"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Sign Out")
        msg.setText("Are you sure you want to sign out?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
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
            self.close_session()
            log_user_action(self.current_user, "User signed out")
            self.main_window.show()
            self.close()

    def close_session(self):
        """Close the current session"""
        if self.session_id:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_sessions 
                    SET is_active = 0, last_accessed = GETDATE()
                    WHERE session_id = ?
                """, (self.session_id,))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Session close error: {e}")

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
            
        # Clean up the widget
        if tab_name in self.tabs:
            tab_widget = self.tabs[tab_name]
            tab_widget.deleteLater()
            del self.tabs[tab_name]
            
        # Update UI state if no tabs left
        if self.tab_widget.count() == 0:
            self.tab_widget.hide()
            self.initial_message.show()
            self.enable_dataset_operations(False)
            
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
        self.app_name_label = QLabel("Cyberbullying Detection System")
        self.app_name_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px; padding: 0 16px;")
        self.app_name_label.setFont(FONTS['button'])
        menu_layout.addWidget(self.app_name_label)
        
        # Add stretch to push remaining buttons to right
        menu_layout.addStretch()
        
        # Add Username label (hidden)
        self.username_label = QLabel()
        self.username_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px; padding: 0 16px;")
        self.username_label.setFont(FONTS['button'])
        self.username_label.hide()  # Hide the label instead of removing it
        menu_layout.addWidget(self.username_label)
        
        # Create sign out button
        sign_out_button = QPushButton("Sign Out")
        sign_out_button.clicked.connect(self.confirm_sign_out)
        sign_out_button.setFont(FONTS['button'])
        menu_layout.addWidget(sign_out_button)
        
        main_layout.addWidget(menu_bar)

        # Create content container
        content_container = QWidget()
        self.content_layout = QVBoxLayout(content_container)
        self.content_layout.setSpacing(15)
        self.content_layout.setContentsMargins(25, 25, 25, 35)
        
        # Initialize the rest of the UI
        self.init_ui()
        
        main_layout.addWidget(content_container)
        
        # Create the central widget
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.addWidget(main_widget)
        
        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self)

    def init_ui(self):
        """Initialize the detailed UI components"""
        # Add tab widget with custom tab bar
        self.tab_widget = QTabWidget()
        custom_tab_bar = CustomTabBar()
        self.tab_widget.setTabBar(custom_tab_bar)
        self.tab_widget.setStyleSheet(TAB_STYLE)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Create initial message
        self.initial_message = QLabel("No analysis performed yet.\nResults will appear here.")
        self.initial_message.setAlignment(Qt.AlignCenter)
        self.initial_message.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px;")
        
        # Initialize tabs dictionary
        self.tabs = {}
        
        # Initialize tab counters
        self.csv_tab_count = 1
        self.url_tab_count = 1
        
        # Main input container with better organization
        input_container = QWidget()
        input_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        input_container.setStyleSheet("background: transparent;")

        # Main vertical layout for inputs
        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(10)
        input_layout.setContentsMargins(0, 0, 0, 0)

        # Input method selection
        method_label = QLabel("Choose Input Method:")
        method_label.setFont(FONTS['header'])
        method_label.setStyleSheet(f"color: {COLORS['text']}; margin-bottom: 5px;")
        input_layout.addWidget(method_label)

        # Create radio button group for input selection
        radio_group = QWidget()
        radio_layout = QHBoxLayout(radio_group)
        radio_layout.setSpacing(20)
        radio_layout.setContentsMargins(0, 0, 0, 10)

        # Create radio buttons
        self.fb_radio = QRadioButton("Facebook Post")
        self.csv_radio = QRadioButton("CSV File")
        self.direct_radio = QRadioButton("Single Comment")

        # Style the radio buttons
        radio_style = f"""
            QRadioButton {{
                color: {COLORS['text']};
                font-size: 14px;
                padding: 8px;
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
            }}
            QRadioButton::indicator:unchecked {{
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                background-color: {COLORS['surface']};
            }}
            QRadioButton::indicator:checked {{
                border: 2px solid {COLORS['highlight']};
                border-radius: 8px;
                background-color: {COLORS['highlight']};
            }}
        """
        self.fb_radio.setStyleSheet(radio_style)
        self.csv_radio.setStyleSheet(radio_style)
        self.direct_radio.setStyleSheet(radio_style)

        # Add radio buttons to layout
        radio_layout.addWidget(self.fb_radio)
        radio_layout.addWidget(self.csv_radio)
        radio_layout.addWidget(self.direct_radio)
        radio_layout.addStretch()

        # Connect radio buttons to stack widget
        self.fb_radio.toggled.connect(lambda checked: self.input_stack.setCurrentIndex(0) if checked else None)
        self.csv_radio.toggled.connect(lambda checked: self.input_stack.setCurrentIndex(1) if checked else None)
        self.direct_radio.toggled.connect(lambda checked: self.input_stack.setCurrentIndex(2) if checked else None)

        # Set default selection
        self.fb_radio.setChecked(True)

        input_layout.addWidget(radio_group)

        # Create stacked widget for different input methods
        self.input_stack = QStackedWidget()
        input_layout.addWidget(self.input_stack)

        # Facebook Post Input
        fb_section = QWidget()
        fb_section.setStyleSheet(SECTION_CONTAINER_STYLE)
        fb_layout = QVBoxLayout(fb_section)
        fb_layout.setSpacing(8)
        fb_layout.setContentsMargins(12, 12, 12, 12)

        fb_title = QLabel("Facebook Post Analysis")
        fb_title.setFont(FONTS['header'])
        fb_title.setStyleSheet(f"color: {COLORS['text']};")
        fb_layout.addWidget(fb_title)

        fb_description = QLabel("Enter a Facebook post URL to analyze its comments")
        fb_description.setStyleSheet(f"color: {COLORS['text']}; font-size: 12px; margin-bottom: 5px;")
        fb_layout.addWidget(fb_description)

        url_layout = QHBoxLayout()
        self.url_input.setStyleSheet(INPUT_STYLE)
        self.url_input.setPlaceholderText("Paste Facebook post URL here...")
        self.url_input.setToolTip("Enter the full URL of a Facebook post to analyze its comments")
        url_layout.addWidget(self.url_input)
        
        self.include_replies.setStyleSheet(CHECKBOX_REPLY_STYLE)
        self.include_replies.setToolTip("Include reply comments in the analysis")
        url_layout.addWidget(self.include_replies)
        fb_layout.addLayout(url_layout)

        self.scrape_button.setFont(FONTS['button'])
        self.scrape_button.setStyleSheet(BUTTON_STYLE)
        self.scrape_button.setToolTip("Start analyzing comments from the Facebook post")
        fb_layout.addWidget(self.scrape_button)
        self.input_stack.addWidget(fb_section)

        # CSV File Input
        csv_section = QWidget()
        csv_section.setStyleSheet(SECTION_CONTAINER_STYLE)
        csv_layout = QVBoxLayout(csv_section)
        csv_layout.setSpacing(8)
        csv_layout.setContentsMargins(12, 12, 12, 12)
        
        csv_title = QLabel("CSV File Analysis")
        csv_title.setFont(FONTS['header'])
        csv_title.setStyleSheet(f"color: {COLORS['text']};")
        csv_layout.addWidget(csv_title)

        csv_description = QLabel("Upload a CSV file containing comments to analyze")
        csv_description.setStyleSheet(f"color: {COLORS['text']}; font-size: 12px; margin-bottom: 5px;")
        csv_layout.addWidget(csv_description)

        file_browse_layout = QHBoxLayout()
        self.file_input.setStyleSheet(INPUT_STYLE)
        self.file_input.setPlaceholderText("Select CSV file...")
        self.file_input.setToolTip("Choose a CSV file containing comments to analyze")
        file_browse_layout.addWidget(self.file_input)
        
        self.browse_button.setFont(FONTS['button'])
        self.browse_button.setStyleSheet(BUTTON_STYLE)
        self.browse_button.setFixedWidth(80)
        self.browse_button.setToolTip("Browse for a CSV file")
        file_browse_layout.addWidget(self.browse_button)
        csv_layout.addLayout(file_browse_layout)
        
        self.process_csv_button.setFont(FONTS['button'])
        self.process_csv_button.setStyleSheet(BUTTON_STYLE)
        self.process_csv_button.setToolTip("Start analyzing comments from the CSV file")
        csv_layout.addWidget(self.process_csv_button)
        self.input_stack.addWidget(csv_section)

        # Direct Input
        direct_section = QWidget()
        direct_section.setStyleSheet(SECTION_CONTAINER_STYLE)
        direct_layout = QVBoxLayout(direct_section)
        direct_layout.setSpacing(8)
        direct_layout.setContentsMargins(12, 12, 12, 12)
        
        direct_title = QLabel("Single Comment Analysis")
        direct_title.setFont(FONTS['header'])
        direct_title.setStyleSheet(f"color: {COLORS['text']};")
        direct_layout.addWidget(direct_title)

        direct_description = QLabel("Enter a single comment to analyze")
        direct_description.setStyleSheet(f"color: {COLORS['text']}; font-size: 12px; margin-bottom: 5px;")
        direct_layout.addWidget(direct_description)
        
        self.text_input.setStyleSheet(INPUT_STYLE)
        self.text_input.setPlaceholderText("Type or paste a comment here...")
        self.text_input.setToolTip("Enter a single comment to analyze")
        direct_layout.addWidget(self.text_input)
        
        self.analyze_button.setFont(FONTS['button'])
        self.analyze_button.setStyleSheet(BUTTON_STYLE)
        self.analyze_button.setToolTip("Analyze the entered comment")
        direct_layout.addWidget(self.analyze_button)
        self.input_stack.addWidget(direct_section)

        self.content_layout.addWidget(input_container)

        # Create responsive splitter for table and details
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(0)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: none;
                width: 0px;
            }}
        """)
        splitter.setChildrenCollapsible(False)

        # Table Container
        table_container = QWidget()
        table_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)

        # Add tab widget
        table_layout.addWidget(self.initial_message)
        table_layout.addWidget(self.tab_widget)
        self.tab_widget.hide()

        splitter.addWidget(table_container)

        # Details Panel
        details_container = QWidget()
        details_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        details_layout = QVBoxLayout(details_container)
        details_layout.setSpacing(15)
        details_layout.setContentsMargins(15, 0, 0, 0)

        # Details section
        details_section = QWidget()
        details_section.setStyleSheet(DETAILS_SECTION_STYLE)
        details_section_layout = QVBoxLayout(details_section)
        details_section_layout.setSpacing(10)
        details_section_layout.setContentsMargins(15, 15, 15, 15)

        details_header = QHBoxLayout()
        details_title = QLabel("Comment Details")
        details_title.setFont(FONTS['header'])
        details_title.setStyleSheet(f"color: {COLORS['text']};")
        details_header.addWidget(details_title)
        details_header.addStretch()
        details_section_layout.addLayout(details_header)

        self.details_text_edit = QTextEdit()
        self.details_text_edit.setReadOnly(True)
        self.details_text_edit.setStyleSheet(TEXT_EDIT_STYLE)
        details_section_layout.addWidget(self.details_text_edit)
        details_layout.addWidget(details_section)

        # Row Operations Section
        row_ops_section = QWidget()
        row_ops_section.setStyleSheet(DETAILS_SECTION_STYLE)
        row_ops_layout = QVBoxLayout(row_ops_section)
        row_ops_layout.setSpacing(12)
        row_ops_layout.setContentsMargins(15, 15, 15, 15)

        row_ops_title = QLabel("Row Operations")
        row_ops_title.setFont(FONTS['header'])
        row_ops_title.setStyleSheet(f"color: {COLORS['text']};")
        row_ops_layout.addWidget(row_ops_title)

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
            button.setStyleSheet(ROW_OPERATION_BUTTON_STYLE)
            row_grid.addWidget(button, row, col)

        row_ops_layout.addLayout(row_grid)
        details_layout.addWidget(row_ops_section)

        # Dataset Operations Section
        dataset_ops_section = QWidget()
        dataset_ops_section.setStyleSheet(DETAILS_SECTION_STYLE)
        dataset_ops_layout = QVBoxLayout(dataset_ops_section)
        dataset_ops_layout.setSpacing(12)
        dataset_ops_layout.setContentsMargins(15, 15, 15, 15)

        dataset_ops_title = QLabel("Dataset Operations")
        dataset_ops_title.setFont(FONTS['header'])
        dataset_ops_title.setStyleSheet(f"color: {COLORS['text']};")
        dataset_ops_layout.addWidget(dataset_ops_title)

        ops_grid = QGridLayout()
        ops_grid.setSpacing(10)
        ops_grid.setContentsMargins(0, 5, 0, 5)

        button_configs = [
            (self.show_summary_button, "📊 Summary", 0, 0),
            (self.word_cloud_button, "☁️ Word Cloud", 0, 1),
            (self.export_all_button, "📤 Export All", 0, 2),
            (self.generate_report_button, "📝 Generate Report", 1, 0, 3)
        ]

        for button, text, row, col, *span in button_configs:
            button.setText(text)
            button.setFont(FONTS['button'])
            button.setStyleSheet(BUTTON_STYLE)
            button.setEnabled(False)
            if span:
                ops_grid.addWidget(button, row, col, 1, span[0])
            else:
                ops_grid.addWidget(button, row, col)

        dataset_ops_layout.addLayout(ops_grid)
        details_layout.addWidget(dataset_ops_section)

        splitter.addWidget(details_container)
        
        splitter.setSizes([900, 100])
        splitter.setStretchFactor(0, 9)
        splitter.setStretchFactor(1, 1)

        self.content_layout.addWidget(splitter)

    def show_about(self):
        """Show About dialog and log the action"""
        from about import AboutDialog
        about_dialog = AboutDialog(self)
        about_dialog.exec_()
        log_user_action(self.current_user, "Viewed About dialog")

    def show_loading(self, show=True):
        """Show or hide the loading overlay"""
        if show:
            self.loading_overlay.show()
        else:
            self.loading_overlay.hide()

    def create_empty_tab(self, tab_type):
        """Create a new empty tab with a table"""
        if tab_type == "Direct Inputs" and "Direct Inputs" in self.tabs:
            return self.tabs["Direct Inputs"].findChild(QTableWidget)

        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        
        # Header section with title and controls
        header_layout = QHBoxLayout()
        table_title = QLabel("Comments")
        table_title.setFont(FONTS['header'])
        header_layout.addWidget(table_title)
        
        # Search container
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
        
        # Sort dropdown
        sort_combo = QComboBox()
        sort_combo.addItems([
            "Sort by Comments (A-Z)",
            "Sort by Comments (Z-A)",
            "Sort by Prediction (A-Z)",
            "Show Replies Only"
        ])
        header_layout.addWidget(sort_combo)
        tab_layout.addLayout(header_layout)

        # Create and configure table
        table = QTableWidget()
        table.setSortingEnabled(True)
        table.setStyleSheet(TABLE_ALTERNATE_STYLE)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Comment", "Prediction"])
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Adjust column sizes
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.resizeSection(1, 150)  # Increased width for prediction column
        table.setColumnWidth(1, 150)

        table.setWordWrap(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.itemSelectionChanged.connect(self.update_details_panel)
        
        # Store references to controls
        table.sort_combo = sort_combo
        sort_combo.currentIndexChanged.connect(lambda: self.sort_table(table))
        
        tab_layout.addWidget(table)
        
        # Configure search functionality
        def filter_table():
            search_text = search_bar.text().lower()
            for row in range(table.rowCount()):
                comment = table.item(row, 0).text().lower()
                table.setRowHidden(row, search_text not in comment)
        
        search_bar.textChanged.connect(filter_table)
        # Add tab to widget and store reference
        self.tab_widget.addTab(tab, tab_type)
        self.tabs[tab_type] = tab

        # Show table widget and enable operations
        if self.tab_widget.isHidden():
            self.initial_message.hide()
            self.tab_widget.show()
            self.enable_dataset_operations(True)
            
        return table

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

    def sort_table(self, table):
        """Sort table based on selected criteria"""
        sort_combo = table.sort_combo
        index = sort_combo.currentIndex()
        
        # Show all rows when not filtering replies
        if index != 3:
            for row in range(table.rowCount()):
                table.setRowHidden(row, False)
        
        # Handle replies filter
        if index == 3:  # "Show Replies Only"
            for row in range(table.rowCount()):
                text = table.item(row, 0).text()
                is_reply = text.startswith(" [↪ Reply]")
                table.setRowHidden(row, not is_reply)
            return
            
        # Handle other sorting options
        if index == 0:  # A-Z
            table.sortItems(0, Qt.AscendingOrder)
        elif index == 1:  # Z-A
            table.sortItems(0, Qt.DescendingOrder)
        elif index == 2:  # Prediction A-Z
            table.sortItems(1, Qt.AscendingOrder)

    def update_details_panel(self):
        """Update the details panel with selected comment information"""
        selected_items = self.get_current_table().selectedItems()
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
        comment = self.get_current_table().item(row, 0).data(Qt.UserRole) or self.get_current_table().item(row, 0).text()
        prediction = self.get_current_table().item(row, 1).text()
        
        metadata = self.comment_metadata.get(comment, {})
        
        # Update add/remove button text
        if comment in self.selected_comments:
            self.add_remove_button.setText("➖ Remove from List")
        else:
            self.add_remove_button.setText("➕ Add to List")
        
        # Update details text
        self.details_text_edit.clear()
        def make_text(label, value):
            return f'<span style="{DETAIL_TEXT_SPAN_STYLE}"><b>{label}</b>{value}</span>'

        # Add comment details
        self.details_text_edit.append(make_text("Comment:\n", f"{comment}\n"))
        self.details_text_edit.append(make_text("Commenter: ", f"{metadata.get('profile_name', 'N/A')}\n"))
        self.details_text_edit.append(make_text("Date: ", f"{metadata.get('date', 'N/A')}\n"))
        self.details_text_edit.append(make_text("Likes: ", f"{metadata.get('likes_count', 'N/A')}\n"))
        
        # Add reply information if applicable
        if metadata.get('is_reply', False) and metadata.get('reply_to'):
            current_table = self.get_current_table()
            for i in range(current_table.rowCount()):
                parent_text = current_table.item(i, 0).data(Qt.UserRole)
                if parent_text == metadata['reply_to']:
                    parent_metadata = self.comment_metadata.get(metadata['reply_to'], {})
                    self.details_text_edit.append("\n" + make_text("Reply Information:\n", ""))
                    self.details_text_edit.append(make_text("Row #", f"{i+1}\n"))
                    self.details_text_edit.append(make_text("Replying to: ", f"{parent_metadata.get('profile_name', 'Unknown')}\n"))
                    self.details_text_edit.append(make_text("Original Comment: ", f"{metadata['reply_to']}\n"))
                    self.details_text_edit.append(make_text("Date: ", f"{parent_metadata['date']}\n"))
                    break
            else:
                self.details_text_edit.append("\n" + make_text("Reply Information:\n", ""))
                self.details_text_edit.append(make_text("Replying to: ", f"{metadata['reply_to']}\n"))

        # Add classification details
        self.details_text_edit.append(make_text("Classification: ", f"{prediction}\n"))
        self.details_text_edit.append(make_text("Status: ", f"{'In List' if comment in self.selected_comments else 'Not in List'}\n"))

    def scrape_comments(self):
        """Scrape and process Facebook comments"""
        url = self.url_input.text()
        if not url:
            display_message(self, "Error", "Please enter a URL.")
            return

        try:
            self.show_loading(True)
            QApplication.processEvents()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
                temp_path = temp_file.name
            
            scrape_comments(url, temp_path, self.include_replies.isChecked())
            df = pd.read_csv(temp_path)
            
            if not self.include_replies.isChecked():
                df = df[~df['Is Reply']]
                
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
            
            try:
                # Truncate URL if too long
                short_url = url[:30] + "..." if len(url) > 30 else url
                log_user_action(self.current_user, f"Scraped FB post: {short_url}")
            except Exception as log_error:
                print(f"Logging error: {log_error}")
            
        except Exception as e:
            display_message(self, "Error", f"Error scraping comments: {e}")
        finally:
            self.show_loading(False)

    def browse_file(self):
        """Open file dialog to select a CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.file_input.setText(file_path)

    def process_csv(self):
        """Process selected CSV file"""
        if not self.file_input.text():
            display_message(self, "Error", "Please select a CSV file first")
            return
            
        file_path = self.file_input.text()
        try:
            # Get just the filename without path and log at the start
            file_name = file_path.split('/')[-1].split('\\')[-1]
            log_user_action(self.current_user, f"Started processing CSV file: {file_name}")
            
            self.show_loading(True)
            QApplication.processEvents()
            
            df = pd.read_csv(file_path)
            # Convert all values to strings to handle numeric values
            comments = df.iloc[:, 0].astype(str).tolist()
            
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
            
            # Log successful completion
            log_user_action(self.current_user, f"Successfully processed CSV file: {file_name}")
            
        except Exception as e:
            # Log failure
            if 'file_name' in locals():
                log_user_action(self.current_user, f"Failed to process CSV file: {file_name}")
            display_message(self, "Error", f"Error reading CSV file: {e}")
        finally:
            self.show_loading(False)

    def analyze_single(self):
        """Analyze a single comment from direct input"""
        if not self.text_input.text():
            display_message(self, "Error", "Please enter a comment to analyze")
            return
        
        try:
            self.show_loading(True)
            QApplication.processEvents()
            
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
            
            log_user_action(self.current_user, "Analyzed single comment")
            
        finally:
            self.show_loading(False)

    def populate_table(self, comments):
        """Populate table with analyzed comments"""
        file_path = self.file_input.text()
        url = self.url_input.text()

        self.file_input.clear()
        self.url_input.clear()
        self.text_input.clear()

        if len(comments) == 1:
            tab_name = "Direct Inputs"
        elif file_path:
            file_name = file_path.split('/')[-1].split('\\')[-1]
            file_name = file_name.rsplit('.', 1)[0]
            
            if len(file_name) > 20:
                file_name = file_name[:17] + "..."
            
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
                    old_tab_index = self.tab_widget.indexOf(self.tabs[file_name])
                    self.tab_widget.removeTab(old_tab_index)
                    del self.tabs[file_name]
                    tab_name = file_name
                elif msg.clickedButton() == new_tab_button:
                    counter = 2
                    while f"{file_name} ({counter})" in self.tabs:
                        counter += 1
                    tab_name = f"{file_name} ({counter})"
                else:
                    return
            else:
                tab_name = file_name
                
        elif url:
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
        else:
            tab_name = f"Analysis {self.csv_tab_count + self.url_tab_count}"

        table = self.create_empty_tab(tab_name)

        for comment in comments:
            metadata = self.comment_metadata.get(comment, {})
            is_reply = metadata.get('is_reply', False)
            
            prediction, confidence = classify_comment(comment)
            row_position = table.rowCount()
            table.insertRow(row_position)

            display_text = comment
            if is_reply:
                reply_to = metadata.get('reply_to', '')
                comment_item = QTableWidgetItem(display_text)
                comment_item.setData(Qt.UserRole, comment)
                comment_item.setData(Qt.DisplayRole, f" [↪ Reply] {display_text}")
                comment_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            else:
                comment_item = QTableWidgetItem(display_text)
                comment_item.setData(Qt.UserRole, comment)
                comment_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            if is_reply:
                lighter_surface = QColor(COLORS['surface']).lighter(105)
                comment_item.setBackground(lighter_surface)

            prediction_item = QTableWidgetItem(prediction)
            prediction_item.setTextAlignment(Qt.AlignCenter)
            if prediction == "Cyberbullying":
                prediction_item.setForeground(QColor(COLORS['bullying']))
            else:
                prediction_item.setForeground(QColor(COLORS['normal']))

            table.setItem(row_position, 0, comment_item)
            table.setItem(row_position, 1, prediction_item)

            table.resizeRowToContents(row_position)

            if comment in self.selected_comments:
                for col in range(table.columnCount()):
                    table.item(row_position, col).setBackground(QColor(COLORS['highlight']))

        tab_index = self.tab_widget.indexOf(self.tabs[tab_name])
        self.tab_widget.setCurrentIndex(tab_index)

        # Save the tab state after populating
        self.save_tab_state(tab_name, comments)

    def show_summary(self):
        """Show summary of comment analysis"""
        total_comments = self.get_current_table().rowCount()
        if total_comments == 0:
            display_message(self, "Error", "No comments to summarize")
            return

        cyberbullying_count = 0
        normal_count = 0
        high_confidence_count = 0

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
        
        display_message(self, "Results Summary", summary_text)
        log_user_action(self.current_user, "Viewed analysis summary")

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

            dialog = QDialog(self)
            dialog.setWindowTitle("Word Cloud Visualization")
            dialog.setMinimumWidth(800)
            dialog.setStyleSheet(DIALOG_STYLE)
            layout = QVBoxLayout(dialog)

            image_label = QLabel()
            image_label.setStyleSheet(IMAGE_LABEL_STYLE)
            scaled_pixmap = pixmap.scaled(700, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(image_label)

            close_button = QPushButton("Close")
            close_button.setStyleSheet(BUTTON_STYLE)
            close_button.clicked.connect(dialog.close)
            layout.addWidget(close_button, alignment=Qt.AlignCenter)

            dialog.exec_()
            log_user_action(self.current_user, "Generated word cloud visualization")

        except Exception as e:
            display_message(self, "Error", f"Error generating word cloud: {e}")

    def toggle_list_status(self):
        """Add or remove selected comment from list"""
        selected_items = self.get_current_table().selectedItems()
        if not selected_items:
            display_message(self, "Error", "Please select a comment to add or remove")
            return

        comment = self.get_current_table().item(selected_items[0].row(), 0).text()
        row = selected_items[0].row()
        if comment in self.selected_comments:
            self.selected_comments.remove(comment)
            display_message(self, "Success", "Comment removed from list")
            for col in range(self.get_current_table().columnCount()):
                self.get_current_table().item(row, col).setBackground(QColor(COLORS['normal']))
            log_user_action(self.current_user, "Removed comment from list")
        else:
            self.selected_comments.append(comment)
            display_message(self, "Success", "Comment added to list")
            for col in range(self.get_current_table().columnCount()):
                self.get_current_table().item(row, col).setBackground(QColor(COLORS['highlight']))
            log_user_action(self.current_user, "Added comment to list")
        self.update_details_panel()

    def export_selected(self):
        """Export selected comments to CSV file"""
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
                log_user_action(self.current_user, f"Exported selected comments to: {file_path}")
            except Exception as e:
                display_message(self, "Error", f"Error exporting comments: {e}")

    def export_all(self):
        """Export all comments to CSV file"""
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
                log_user_action(self.current_user, f"Exported all comments to: {file_path}")
            except Exception as e:
                display_message(self, "Error", f"Error exporting comments: {e}")

    def generate_report(self):
        """Generate report for user interface"""
        generate_report_user(self)
        log_user_action(self.current_user, "Generated analysis report")