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
from comment_filters import CommentFiltersDialog

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

class SummaryDialog(QDialog):
    """Custom dialog to display summary text and a pie chart."""
    def __init__(self, summary_text, chart_pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analysis Summary")
        self.setStyleSheet(DIALOG_STYLE)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Summary Text - Make font larger
        styled_summary_text = f'<div style="font-size: 14px;">{summary_text}</div>' # Increased font size using HTML
        text_label = QLabel(styled_summary_text)
        text_label.setTextFormat(Qt.RichText) # Allow rich text (bold, and styling)
        text_label.setWordWrap(True)
        layout.addWidget(text_label)

        # Pie Chart Image
        if chart_pixmap:
            chart_label = QLabel()
            chart_label.setAlignment(Qt.AlignCenter)
            # Scale pixmap while maintaining aspect ratio
            scaled_pixmap = chart_pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            chart_label.setPixmap(scaled_pixmap)
            layout.addWidget(chart_label)

        # Close Button
        close_button = QPushButton("Close")
        close_button.setStyleSheet(BUTTON_STYLE)
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)

class UserMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize variables
        self.first_login = True
        self.current_user = None
        self.selected_comments = []  # Change to list of dictionaries
        self.csv_tab_count = 1
        self.url_tab_count = 1
        self.comment_metadata = {}
        self.tabs = {}
        self.tab_states = {}
        self.main_window = None
        self.session_id = None  # Add session ID property
        self.setWindowTitle("Cyberbullying Content Guidance System - User View")
        self.showFullScreen()
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")

        # Set window icon
        base_path = os.path.dirname(os.path.abspath(__file__))
        app_icon = QIcon(os.path.join(base_path, "assets", "applogo.png"))
        self.setWindowIcon(app_icon)

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

        # Initialize input stack
        self.input_stack = QStackedWidget()

        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self)

        # Initialize main UI
        self.init_main_ui()

    def set_current_user(self, username):
        """Set the current user and update the UI to show their name"""
        self.current_user = username
        if hasattr(self, 'app_name_label'):
            self.app_name_label.setText(f"Cyberbullying Content Guidance System - {username}")
        
        # Create or restore session
        self.create_or_restore_session()
        
        # Then restore UI from database
        self.restore_session()
        
        # Log the action
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
            
            # Now restore the UI state - this is called separately in set_current_user
            # self.restore_session()
            
        except Exception as e:
            print(f"Session creation/restoration error: {e}")

    def restore_session(self):
        """Restore tabs and comments from saved session"""
        try:
            # Clear existing tabs first to prevent duplicates
            self.selected_comments = []
            self.comment_metadata = {}
            self.tabs = {}
            
            # Reset tab counters for fresh start
            self.csv_tab_count = 1
            self.url_tab_count = 1
            
            # Remove all tabs from the UI
            while self.tab_widget.count() > 0:
                self.tab_widget.removeTab(0)
            
            conn = get_db_connection()
            cursor = conn.cursor()

            # Get all tabs for this session
            cursor.execute("""
                SELECT tab_id, tab_name, tab_type 
                FROM session_tabs 
                WHERE session_id = ?
            """, (self.session_id,))
            
            tabs = cursor.fetchall()
            
            # Create a dictionary to collect comments for each tab name
            all_tab_comments = {}
            
            # First, collect all comments for all tabs
            for tab_id, tab_name, tab_type in tabs:
                # Get comments for this tab
                cursor.execute("""
                    SELECT comment_text, prediction, confidence,
                           profile_name, profile_picture, comment_date,
                           likes_count, profile_id, is_reply, reply_to, is_selected
                    FROM tab_comments 
                    WHERE tab_id = ?
                """, (tab_id,))
                
                comments = cursor.fetchall()
                
                # Initialize list for this tab name if not exists
                if tab_name not in all_tab_comments:
                    all_tab_comments[tab_name] = []
                
                # Process each comment
                for comment_data in comments:
                    (comment_text, prediction, confidence, profile_name, 
                     profile_picture, comment_date, likes_count, profile_id, 
                     is_reply, reply_to, is_selected) = comment_data
                    
                    # Create comment dictionary
                    comment_dict = {
                        'comment_text': comment_text,
                        'prediction': prediction,
                        'confidence': confidence,
                        'profile_name': profile_name,
                        'profile_picture': profile_picture,
                        'comment_date': comment_date,
                        'likes_count': likes_count,
                        'profile_id': profile_id,
                        'is_reply': is_reply,
                        'reply_to': reply_to
                    }
                    
                    # Add to list for this tab (avoid duplicates)
                    if comment_dict not in all_tab_comments[tab_name]:
                        all_tab_comments[tab_name].append(comment_dict)
                    
                    # Store metadata
                    self.comment_metadata[comment_text] = {
                        'profile_name': profile_name,
                        'profile_picture': profile_picture,
                        'date': comment_date,
                        'likes_count': likes_count,
                        'profile_id': profile_id,
                        'is_reply': is_reply,
                        'reply_to': reply_to,
                        'confidence': confidence  # Store confidence in metadata
                    }
                    
                    # Add to selected comments if selected
                    if is_selected and comment_text not in self.selected_comments:
                        self.selected_comments.append(comment_text)
            
            # Now create tabs and populate them with the collected comments
            for tab_name, comments_data in all_tab_comments.items():
                if not comments_data:  # Skip empty tabs
                    continue
                    
                # Create tab in UI
                table = self.create_empty_tab(tab_name)
                
                # Populate the table with all comments for this tab
                table.setRowCount(0)
                self.populate_table(table, comments_data)
                
                # Log the restored tab
                print(f"Restored tab '{tab_name}' with {len(comments_data)} comments")
            
            conn.close()
            
            # Update tab counters based on existing tabs
            self.update_tab_counters()
            
            # Show/hide appropriate elements based on tab count
            if self.tab_widget.count() > 0:
                self.initial_message.hide()
                self.tab_widget.show()
                self.enable_dataset_operations(True)
            else:
                self.initial_message.show()
                self.tab_widget.hide()
                self.enable_dataset_operations(False)
            
        except Exception as e:
            print(f"Session restoration error: {e}")
            import traceback
            traceback.print_exc()  # Print full stack trace for debugging

    def update_tab_counters(self):
        """Update tab counters based on existing tabs"""
        max_csv_count = 0
        max_url_count = 0
        
        # Check all tab names to find the highest numbers
        for tab_name in self.tabs.keys():
            if tab_name.startswith("CSV "):
                try:
                    # Extract number from format "CSV X: filename"
                    number_part = tab_name.split(" ")[1]
                    if ":" in number_part:
                        number = int(number_part.split(":")[0])
                        max_csv_count = max(max_csv_count, number)
                except (ValueError, IndexError):
                    pass
            elif tab_name.startswith("URL "):
                try:
                    # Extract number from format "URL X: url"
                    number_part = tab_name.split(" ")[1]
                    if ":" in number_part:
                        number = int(number_part.split(":")[0])
                        max_url_count = max(max_url_count, number)
                except (ValueError, IndexError):
                    pass
        
        # Set the counters to one more than the highest found
        self.csv_tab_count = max_csv_count + 1
        self.url_tab_count = max_url_count + 1
        
        print(f"Updated tab counters - CSV: {self.csv_tab_count}, URL: {self.url_tab_count}")

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

    def close_tab(self, index):
        """Close the tab and clean up resources"""
        # Get tab name before removing - this is the truncated version shown in UI
        ui_tab_name = self.tab_widget.tabText(index)
        
        # Get the actual tab widget for this index
        tab_widget = self.tab_widget.widget(index)
        
        # Find the full tab name from the tabs dictionary
        full_tab_name = None
        for name, widget in self.tabs.items():
            if widget == tab_widget:
                full_tab_name = name
                break
        
        # Use full tab name for database operations if found, otherwise use UI tab name
        tab_name = full_tab_name or ui_tab_name
        
        print(f"Closing tab: UI name='{ui_tab_name}', Full name='{tab_name}'")
        
        try:
            # Remove tab data from database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # First get the tab_id
            cursor.execute("""
                SELECT tab_id FROM session_tabs 
                WHERE session_id = ? AND tab_name = ?
            """, (self.session_id, tab_name))
            
            tab_result = cursor.fetchone()
            if tab_result:
                tab_id = tab_result[0]
                
                # Delete comments associated with this tab
                cursor.execute("""
                    DELETE FROM tab_comments 
                    WHERE tab_id = ?
                """, (tab_id,))
                
                # Delete the tab itself
                cursor.execute("""
                    DELETE FROM session_tabs 
                    WHERE tab_id = ?
                """, (tab_id,))
                
                conn.commit()
                print(f"Successfully deleted tab {tab_name} and its comments from database")
            else:
                print(f"Warning: Could not find tab_id for '{tab_name}' in session {self.session_id}")
            
            # Now update session last accessed time
            cursor.execute("""
                UPDATE user_sessions 
                SET last_accessed = GETDATE()
                WHERE session_id = ?
            """, (self.session_id,))
            conn.commit()
            
            conn.close()
            
            # Log the action
            log_user_action(self.current_user, f"Closed tab: {tab_name}")
            
        except Exception as e:
            print(f"Error removing tab data from database: {e}")
            import traceback
            traceback.print_exc()
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        
        # Clean up memory and UI
        if tab_name in self.tabs:
            # Get all comment text in this tab to clean up metadata and selected comments
            comment_texts = []
            table_widget = self.tabs[tab_name].findChild(QTableWidget)
            if table_widget:
                for row in range(table_widget.rowCount()):
                    comment_item = table_widget.item(row, 0)
                    if comment_item:
                        comment_text = comment_item.data(Qt.UserRole) or comment_item.text()
                        comment_texts.append(comment_text)
                        
                        # Remove from selected comments if present
                        if comment_text in self.selected_comments:
                            self.selected_comments.remove(comment_text)
                            
                        # Remove metadata
                        if comment_text in self.comment_metadata:
                            del self.comment_metadata[comment_text]
            
            # Remove tab widget and reference
            self.tabs[tab_name].deleteLater()
            del self.tabs[tab_name]
        
        # Remove tab from UI
        self.tab_widget.removeTab(index)
            
        # If no tabs left, show initial message and disable dataset operations
        if self.tab_widget.count() == 0:
            self.tab_widget.hide()
            self.initial_message.show()
            self.enable_dataset_operations(False)
            self.add_remove_button.setEnabled(False)
            self.export_selected_button.setEnabled(False)
            self.details_text_edit.clear()

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
        self.app_name_label = QLabel("Cyberbullying Content Guidance System")
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

        # --- Start Modification ---
        # Main horizontal layout for inputs
        input_layout = QHBoxLayout(input_container)
        input_layout.setSpacing(15) # Add some spacing between radio buttons and stack
        input_layout.setContentsMargins(0, 0, 0, 0)

        # Left side: Vertical layout for radio buttons
        radio_button_container = QWidget()
        radio_button_layout = QVBoxLayout(radio_button_container)
        radio_button_layout.setSpacing(8)
        radio_button_layout.setContentsMargins(0, 0, 0, 0)

        method_label = QLabel("Choose Input Method:")
        method_label.setFont(FONTS['header'])
        method_label.setStyleSheet(f"color: {COLORS['text']}; margin-bottom: 5px;")
        radio_button_layout.addWidget(method_label)

        self.fb_radio = QRadioButton("Facebook Post")
        self.csv_radio = QRadioButton("CSV File")
        self.direct_radio = QRadioButton("Single Comment")

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

        radio_button_layout.addWidget(self.fb_radio)
        radio_button_layout.addWidget(self.csv_radio)
        radio_button_layout.addWidget(self.direct_radio)
        radio_button_layout.addStretch()

        input_layout.addWidget(radio_button_container, stretch=0) # Give minimum width

        # Middle part: Create stacked widget for different input methods
        self.input_stack = QStackedWidget()

        # --- Create Details Panel ---
        self.details_text_edit = QTextEdit() # Define details panel here
        self.details_text_edit.setReadOnly(True)
        self.details_text_edit.setStyleSheet(TEXT_EDIT_STYLE)
        self.details_text_edit.setMinimumHeight(150) # Give it a reasonable minimum height

        # --- Create Directions Panel ---
        self.directions_panel = QTextEdit()
        self.directions_panel.setReadOnly(True)
        self.directions_panel.setStyleSheet(TEXT_EDIT_STYLE) # Use same style as details
        self.directions_panel.setFixedWidth(500) 
        self.directions_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding) # Fixed width, expanding height

        # --- Modify Connections ---
        # Connect radio buttons to a new handler
        self.fb_radio.toggled.connect(lambda checked: self.handle_input_selection(0) if checked else None)
        self.csv_radio.toggled.connect(lambda checked: self.handle_input_selection(1) if checked else None)
        self.direct_radio.toggled.connect(lambda checked: self.handle_input_selection(2) if checked else None)

        # Set default selection and initial directions
        self.fb_radio.setChecked(True)
        self.update_directions(0) # Show initial directions for FB

        # Add the input stack (middle) and directions panel (right) to the main horizontal layout
        input_layout.addWidget(self.input_stack, stretch=1) # Give it flexible horizontal space
        input_layout.addWidget(self.directions_panel, stretch=0) # Add directions panel to the right
        # --- End Modification ---

        # --- Facebook Post Input section - UPDATED ---
        fb_section = QWidget()
        fb_section.setStyleSheet(SECTION_CONTAINER_STYLE)
        fb_layout = QVBoxLayout(fb_section)
        fb_layout.setSpacing(8)
        fb_layout.setContentsMargins(12, 12, 12, 12)

        fb_title = QLabel("Facebook Post Analysis")
        fb_title.setFont(FONTS['header'])
        fb_title.setStyleSheet(f"color: {COLORS['text']};")
        fb_layout.addWidget(fb_title)

        url_layout = QHBoxLayout()
        self.url_input.setStyleSheet(INPUT_STYLE)
        self.url_input.setPlaceholderText("Paste Facebook post URL here...")
        self.url_input.setToolTip("Enter the full URL of a Facebook post to analyze its comments")
        url_layout.addWidget(self.url_input)
        
        # Replace include_replies checkbox with filter button
        self.filter_button.setFont(FONTS['button'])
        self.filter_button.setStyleSheet(BUTTON_STYLE)
        self.filter_button.setFixedWidth(80)
        self.filter_button.setToolTip("Configure comment scraping options")
        url_layout.addWidget(self.filter_button)
        fb_layout.addLayout(url_layout)

        self.scrape_button.setFont(FONTS['button'])
        self.scrape_button.setStyleSheet(BUTTON_STYLE)
        self.scrape_button.setToolTip("Start analyzing comments from the Facebook post")
        fb_layout.addWidget(self.scrape_button)
        self.input_stack.addWidget(fb_section)

        # --- CSV File Input section (content remains the same, just added to stack) ---
        csv_section = QWidget()
        csv_section.setStyleSheet(SECTION_CONTAINER_STYLE)
        csv_layout = QVBoxLayout(csv_section)
        csv_layout.setSpacing(8)
        csv_layout.setContentsMargins(12, 12, 12, 12)
        
        csv_title = QLabel("CSV File Analysis")
        csv_title.setFont(FONTS['header'])
        csv_title.setStyleSheet(f"color: {COLORS['text']};")
        csv_layout.addWidget(csv_title)

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

        # --- Direct Input section (content remains the same, just added to stack) ---
        direct_section = QWidget()
        direct_section.setStyleSheet(SECTION_CONTAINER_STYLE)
        direct_layout = QVBoxLayout(direct_section)
        direct_layout.setSpacing(8)
        direct_layout.setContentsMargins(12, 12, 12, 12)
        
        direct_title = QLabel("Single Comment Analysis")
        direct_title.setFont(FONTS['header'])
        direct_title.setStyleSheet(f"color: {COLORS['text']};")
        direct_layout.addWidget(direct_title)

        # Add input field directly to the main vertical layout
        self.text_input.setStyleSheet(INPUT_STYLE)
        self.text_input.setPlaceholderText("Type or paste a comment here...")
        self.text_input.setToolTip("Enter a single comment to analyze")
        direct_layout.addWidget(self.text_input)

        # Add button directly to the main vertical layout
        self.analyze_button.setFont(FONTS['button'])
        self.analyze_button.setStyleSheet(BUTTON_STYLE)
        self.analyze_button.setToolTip("Analyze the entered comment")
        direct_layout.addWidget(self.analyze_button)

        self.input_stack.addWidget(direct_section)

        # Explicitly set stretch factor 0 for the input container
        self.content_layout.addWidget(input_container, stretch=0)

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
            (self.export_all_button, "📤 Export Tab", 0, 2),
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

        # Add the splitter to the content layout with a stretch factor
        self.content_layout.addWidget(splitter, stretch=1) 

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

    def truncate_tab_name(self, name, max_length=15):
        """Truncate tab name if it exceeds the maximum length"""
        if len(name) > max_length:
            return name[:max_length-3] + "..."
        return name

    def create_empty_tab(self, tab_type):
        """Create a new empty tab with a table"""
        # Truncate tab name for consistent width
        tab_display_name = self.truncate_tab_name(tab_type)
        
        if tab_type in self.tabs:
            return self.tabs[tab_type].findChild(QTableWidget)

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
            "Sort by Confidence (High to Low)", # Added
            "Sort by Confidence (Low to High)", # Added
            "Show Replies Only"
        ])
        header_layout.addWidget(sort_combo)
        tab_layout.addLayout(header_layout)

        # Create and configure table
        table = QTableWidget()
        table.setSortingEnabled(True)
        table.setStyleSheet(TABLE_ALTERNATE_STYLE)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Comment", "Prediction", "Confidence"])
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Adjust column sizes
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.resizeSection(1, 150)
        header.resizeSection(2, 100)
        table.setColumnWidth(1, 150)
        table.setColumnWidth(2, 100)

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
        # Add tab to widget and store reference - use display name for UI but store full name in dict
        self.tab_widget.addTab(tab, tab_display_name)
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
        comment_item = self.get_current_table().item(row, 0)
        comment = comment_item.data(Qt.UserRole) or comment_item.text()
        prediction = self.get_current_table().item(row, 1).text()
        confidence = self.get_current_table().item(row, 2).text()
        
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
                parent_item = current_table.item(i, 0)
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

    def scrape_comments(self):
        """Scrape and process Facebook comments"""
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
            
            # Use filters instead of just include_replies
            scrape_comments(url, temp_path, self.comment_filters)
            
            end_time = time.time() # Record end time
            duration = end_time - start_time
            print(f"Scraping and initial processing took {duration:.2f} seconds.")
            
            df = pd.read_csv(temp_path)
            
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
            def is_short_comment(text, min_words=3):
                # Split by whitespace and count words
                words = text.strip().split()
                return len(words) < min_words
            
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
            min_word_count = self.comment_filters.get("minWordCount", 3)
            exclude_links = self.comment_filters.get("excludeLinks", True)
            exclude_emojis_only = self.comment_filters.get("excludeEmojisOnly", True)
            
            # Create mask for comments to keep
            keep_mask = pd.Series(True, index=df.index)
            
            # Apply filters
            for idx, row in df.iterrows():
                text = row['Text']
                
                # Check if comment is too short
                if is_short_comment(text, min_word_count):
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
            
            # Initialize metadata and comments data
            self.comment_metadata = {}
            comments_data = []
            
            for _, row in filtered_df.iterrows():
                comment_text = row['Text']
                # Get prediction and confidence from model
                prediction, confidence = classify_comment(comment_text)
                
                # Store metadata
                self.comment_metadata[comment_text] = {
                    'profile_name': row['Profile Name'],
                    'profile_picture': row['Profile Picture'],
                    'date': row['Date'],
                    'likes_count': row['Likes Count'],
                    'profile_id': row['Profile ID'],
                    'is_reply': row['Is Reply'],
                    'reply_to': row['Reply To'],
                    'confidence': confidence
                }
                
                # Prepare comment data
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
            
            # Create a new tab for the results
            tab_name = f"URL {self.url_tab_count}: {url[:30]}..."
            self.url_tab_count += 1
            
            # Create table and populate it
            table = self.create_empty_tab(tab_name)
            self.populate_table(table, comments_data)
            
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
            # Get the first column name
            first_column = df.columns[0]
            
            # Initialize comments list
            comments_data = []
            
            # Process each row
            for _, row in df.iterrows():
                try:
                    # Get comment text from first column, ensuring it's a string
                    comment_text = str(row[first_column]).strip()
                    if not comment_text:  # Skip empty comments
                        continue
                        
                    # Classify the comment
                    prediction, confidence = classify_comment(comment_text)
                    
                    # Store metadata
                    self.comment_metadata[comment_text] = {
                        'profile_name': 'CSV Input',
                        'profile_picture': '',
                        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'likes_count': 'N/A',
                        'profile_id': 'N/A',
                        'confidence': confidence
                    }
                    
                    # Prepare comment data
                    comments_data.append({
                        'comment_text': comment_text,
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
                    
                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue
            
            if not comments_data:
                display_message(self, "Error", "No valid comments found in the CSV file.")
                return
            
            # Create a new tab for the results
            tab_name = f"CSV {self.csv_tab_count}: {file_name}"
            self.csv_tab_count += 1
            
            # Create table and populate it
            table = self.create_empty_tab(tab_name)
            self.populate_table(table, comments_data)
            
            # Save the initial state
            self.save_tab_state(tab_name, comments_data)
            
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
            
            comment_text = self.text_input.text()
            
            # Check if the input is 5 words or less
            word_count = len(comment_text.split())
            is_short_input = word_count <= 5
            
            # Get prediction and confidence from model
            prediction, confidence = classify_comment(comment_text)
            
            # Store metadata
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
            
            # Define the target tab name
            tab_name = "Direct Inputs"
            
            # Get or create the "Direct Inputs" tab and its table
            if tab_name in self.tabs:
                tab_widget = self.tabs[tab_name]
                table = tab_widget.findChild(QTableWidget)
            else:
                table = self.create_empty_tab(tab_name)
            
            # Populate table with the new comment, setting append=True to keep existing comments
            self.populate_table(table, comment_data, append=True)
            
            # Clear the text input
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
            
            log_user_action(self.current_user, "Analyzed single comment")
            
        except Exception as e:
            display_message(self, "Error", f"Error analyzing comment: {e}")
        finally:
            self.show_loading(False)

    def populate_table(self, table, comments, append=False):
        """Populate table with analyzed comments"""
        if not append:
            table.setRowCount(0)
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Comment", "Prediction", "Confidence"])

        # Create a set of existing comments to avoid duplicates
        existing_comments = set()
        if append:
            for row in range(table.rowCount()):
                comment_item = table.item(row, 0)
                if comment_item and comment_item.data(Qt.UserRole):
                    existing_comments.add(comment_item.data(Qt.UserRole))

        for comment in comments:
            # Get the comment text and prediction from the comment dictionary
            comment_text = comment.get('comment_text', '')
            
            # Skip if this comment already exists in the table
            if comment_text in existing_comments:
                continue
                
            existing_comments.add(comment_text)
            
            prediction = comment.get('prediction', '')  # Use pre-classified prediction
            confidence = comment.get('confidence', 0.0)  # Use pre-classified confidence (0.0-1.0)

            # Convert confidence to High/Medium/Low
            # confidence_level = "High" if confidence > 0.8 else "Medium" if confidence > 0.5 else "Low"

            # Get metadata from either dictionary or metadata store
            if isinstance(comment, dict):
                # New format: use metadata directly from dictionary
                metadata = {
                    'profile_name': comment.get('profile_name', 'N/A'),
                    'profile_picture': comment.get('profile_picture', None),
                    'comment_date': comment.get('comment_date', 'N/A'),
                    'likes_count': comment.get('likes_count', 0),
                    'profile_id': comment.get('profile_id', 'N/A'),
                    'is_reply': comment.get('is_reply', False),
                    'reply_to': comment.get('reply_to', None),
                    'confidence': confidence  # Store actual confidence value (0.0-1.0)
                }
                # Also store in comment_metadata for compatibility with other functions
                self.comment_metadata[comment_text] = metadata
            else:
                # Old format: use comment_metadata directly (deprecated)
                metadata = self.comment_metadata.get(comment_text, {})
            
            is_reply = metadata.get('is_reply', False)
            
            # Insert new row
            row_position = table.rowCount()
            table.insertRow(row_position)

            # Set comment cell
            display_text = comment_text
            if is_reply:
                reply_to = metadata.get('reply_to', '')
                comment_item = QTableWidgetItem(display_text)
                comment_item.setData(Qt.UserRole, comment_text)
                comment_item.setData(Qt.DisplayRole, f" [↪ Reply] {display_text}")
                comment_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            else:
                comment_item = QTableWidgetItem(display_text)
                comment_item.setData(Qt.UserRole, comment_text)
                comment_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

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
            else:
                # Fallback for any other value
                prediction_item.setForeground(QColor(COLORS['text']))
            
            # Set confidence cell (formatted 0-100 with %)
            confidence_text = f"{confidence:.2f}%" # Format to 2 decimal places and add %
            confidence_item = QTableWidgetItem(confidence_text)
            confidence_item.setTextAlignment(Qt.AlignCenter)

            # Add data to table
            table.setItem(row_position, 0, comment_item)
            table.setItem(row_position, 1, prediction_item)
            table.setItem(row_position, 2, confidence_item) # Add to 3rd column

            # Resize row to fit content
            table.resizeRowToContents(row_position)

            # Highlight if in selected comments
            if comment_text in self.selected_comments:
                for col in range(table.columnCount()):
                    table.item(row_position, col).setBackground(QColor(COLORS['highlight']))

        # Reset sort dropdown to default (index 0) when replacing table content
        if not append and hasattr(table, 'sort_combo'):
            table.sort_combo.setCurrentIndex(0)
            # Optionally trigger the sort immediately if needed, though setting index might do it
            # self.sort_table(table) 

        # Set the current tab
        try:
            # Get the name/title of the current tab
            if table.parent():
                table_parent = table.parent()
                for tab_name, tab_widget in self.tabs.items():
                    if tab_widget == table_parent:
                        tab_index = self.tab_widget.indexOf(tab_widget)
                        self.tab_widget.setCurrentIndex(tab_index)
                        # Don't save the tab state automatically
                        # self.save_tab_state(tab_name, comments)
                        break
        except Exception as e:
            print(f"Error setting current tab: {e}")

    def show_summary(self):
        """Show summary with counts, ratios, and a pie chart for the three-level guidance system."""
        table = self.get_current_table()
        if not table or table.rowCount() == 0:
            display_message(self, "Info", "No comments to summarize")
            return

        total_comments = table.rowCount()
        potentially_harmful_count = 0
        requires_review_count = 0
        likely_appropriate_count = 0
        confidences = [] # Collect confidences again

        for row in range(total_comments):
            comment_item = table.item(row, 0)
            prediction_item = table.item(row, 1) 
            confidence_item = table.item(row, 2) # Get item from 3rd column
            
            if not comment_item or not prediction_item or not confidence_item:
                continue
            
            # Get prediction label
            prediction = prediction_item.text()

            # Get confidence score (0-100)
            try:
                confidence = float(confidence_item.text().strip('%')) # Read float from table, remove %
                confidences.append(confidence)
            except ValueError:
                 # Handle cases where confidence might not be a valid number
                 pass 

            if prediction == "Potentially Harmful":
                potentially_harmful_count += 1
            elif prediction == "Requires Review":
                requires_review_count += 1
            elif prediction == "Likely Appropriate":
                likely_appropriate_count += 1

        avg_confidence = np.mean(confidences) if confidences else 0
        
        # Calculate ratios
        harmful_ratio = (potentially_harmful_count / total_comments) if total_comments > 0 else 0
        review_ratio = (requires_review_count / total_comments) if total_comments > 0 else 0
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
            labels = ['Potentially Harmful', 'Requires Review', 'Likely Appropriate']
            sizes = [potentially_harmful_count, requires_review_count, likely_appropriate_count]
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
                    fig, ax = plt.subplots(figsize=(5, 3.5)) # Adjusted size
                    ax.pie(filtered_sizes, explode=explode, labels=filtered_labels, colors=filtered_colors,
                           autopct='%1.1f%%', shadow=False, startangle=90,
                           textprops={'color': 'white'}) # White text for better visibility
                    ax.axis('equal')  # Equal aspect ratio ensures a circular pie chart
                    # Ensure background is transparent for better theme integration
                    fig.patch.set_alpha(0.0)
                    ax.patch.set_alpha(0.0)
                    
                    # Add a title noting this is guidance-oriented
                    ax.set_title("Content Guidance Assessment", color='white', pad=20)
                    
                    buf = BytesIO()
                    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, transparent=True)
                    plt.close(fig) # Close the figure to free memory
                    buf.seek(0)
                    
                    image = QImage.fromData(buf.getvalue())
                    chart_pixmap = QPixmap.fromImage(image)
                except Exception as e:
                    print(f"Error generating pie chart: {e}")
                    chart_pixmap = None # Ensure it's None if chart fails
        # --- End Pie Chart --- 

        # Show custom dialog
        dialog = SummaryDialog(summary_text, chart_pixmap, self)
        dialog.exec_()
        
        log_user_action(self.current_user, "Viewed guidance summary")

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

        row = selected_items[0].row()
        comment_item = self.get_current_table().item(row, 0)
        prediction_item = self.get_current_table().item(row, 1)
        confidence_item = self.get_current_table().item(row, 2)
        
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
                for col in range(self.get_current_table().columnCount()):
                    self.get_current_table().item(row, col).setBackground(QColor(COLORS['normal']))
                log_user_action(self.current_user, "Removed comment from list")
                self.update_details_panel()
                return
            elif isinstance(item, str) and item == comment:
                # Found it (old format) - remove it
                self.selected_comments.pop(i)
                display_message(self, "Success", "Comment removed from list")
                # Reset row color
                for col in range(self.get_current_table().columnCount()):
                    self.get_current_table().item(row, col).setBackground(QColor(COLORS['normal']))
                log_user_action(self.current_user, "Removed comment from list")
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
                log_user_action(self.current_user, f"Exported selected comments to: {file_path}")
            except Exception as e:
                display_message(self, "Error", f"Error exporting comments: {e}")

    def export_all(self):
        """Export all analyzed comments from the current tab to CSV"""
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
                log_user_action(self.current_user, f"Exported all comments to {os.path.basename(file_path)}")
            except Exception as e:
                display_message(self, "Error", f"Failed to export data: {e}")

    def generate_report(self):
        """Generate report for user interface"""
        generate_report_user(self)
        log_user_action(self.current_user, "Generated analysis report")

    # --- Add Helper Methods ---
    def handle_input_selection(self, index):
        """Handles radio button selection changes."""
        self.input_stack.setCurrentIndex(index)
        self.update_directions(index)

    def update_directions(self, index):
        """Updates the directions panel based on the selected input type."""
        directions_html = ""
        if index == 0: # Facebook Post
            directions_html = """
            <b style='font-size: 14px;'>Facebook Post Instructions:</b><br><br>
            1. Find the Facebook post you want to analyze.<br>
            2. Copy the full URL from your browser's address bar.<br>
            3. Paste the URL into the input field.<br>
            4. Check "Include Replies" if you want to analyze replies to comments.<br>
            5. Click "Scrape Comments" to begin.<br><br>
            <i>Note: Only public posts can be scraped. Scraping may take some time depending on the number of comments.</i>
            """
        elif index == 1: # CSV File
            directions_html = """
            <b style='font-size: 14px;'>CSV File Instructions:</b><br><br>
            1. Prepare a CSV file.<br>
            2. Ensure the first column contains the comments you want to analyze.<br>
            3. Click "Browse" to locate and select your CSV file.<br>
            4. Click "Process CSV" to analyze the comments.<br><br>
            <i>Note: The system only reads the first column. Ensure text is UTF-8 encoded if you encounter issues.</i>
            """
        elif index == 2: # Single Comment
            directions_html = """
            <b style='font-size: 14px;'>Single Comment Instructions:</b><br><br>
            1. Type or paste the comment text directly into the input field.<br>
            2. Click "Analyze Comment".<br>
            3. The result will be added to the "Direct Inputs" tab in the table below.<br><br>
            <i>Note: This is useful for quickly checking individual comments.</i>
            """
        self.directions_panel.setHtml(f"<div style='color: {COLORS['text']}; font-size: 12px; padding: 5px;'>{directions_html}</div>")

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