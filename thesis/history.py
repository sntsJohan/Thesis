from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
                           QHeaderView, QPushButton, QLabel, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from styles import COLORS, FONTS, BUTTON_STYLE, TABLE_STYLE
from db_config import get_db_connection
from datetime import datetime
import os

class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Logs")
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")
        self.resize(800, 600)
        
        # Set window icon
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QIcon(os.path.join(base_path, "assets", "applogo.png")))
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with title and refresh button
        header_layout = QHBoxLayout()
        
        # Add title
        title = QLabel("User Activity Logs")
        title.setFont(FONTS['header'])
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        
        # Add refresh button
        refresh_button = QPushButton("↻ Refresh")
        refresh_button.setStyleSheet(BUTTON_STYLE)
        refresh_button.setFixedWidth(100)
        refresh_button.clicked.connect(self.load_logs)
        header_layout.addWidget(refresh_button)
        
        layout.addLayout(header_layout)
        
        # Create table
        self.table = QTableWidget()
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Timestamp", "User", "Action"])
        
        # Set column sizes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Timestamp
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # User
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Action
        
        self.table.setColumnWidth(0, 200)  # Timestamp
        self.table.setColumnWidth(1, 150)  # User
        
        layout.addWidget(self.table)
        
        # Add buttons container
        buttons_layout = QHBoxLayout()
        
        # Add clear logs button
        clear_button = QPushButton("🗑️ Clear Logs")
        clear_button.setStyleSheet(BUTTON_STYLE)
        clear_button.setFixedWidth(120)
        clear_button.clicked.connect(self.confirm_clear_logs)
        buttons_layout.addWidget(clear_button)
        
        # Add spacer to separate buttons
        buttons_layout.addStretch()
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet(BUTTON_STYLE)
        close_button.setFixedWidth(100)
        close_button.clicked.connect(self.close)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        
        # Load logs initially
        self.load_logs()
    
    def confirm_clear_logs(self):
        """Show confirmation dialog before clearing logs"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Clear Logs")
        msg_box.setText("Are you sure you want to clear all user logs?")
        msg_box.setInformativeText("This action cannot be undone.")
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Style the message box
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
            }}
            QPushButton {{
                {BUTTON_STYLE}
                min-width: 100px;
            }}
        """)
        
        # Show the dialog and check result
        if msg_box.exec_() == QMessageBox.Yes:
            self.clear_logs()
    
    def clear_logs(self):
        """Clear all logs from the database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Delete all logs
            cursor.execute("DELETE FROM user_logs")
            conn.commit()
            
            # Also clear sessions data if needed
            clear_sessions = QMessageBox.question(
                self, 
                "Clear Sessions Too?", 
                "Do you also want to clear all user sessions data?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if clear_sessions == QMessageBox.Yes:
                # First delete all tab comments (due to foreign key constraints)
                cursor.execute("""
                    DELETE FROM tab_comments 
                    WHERE tab_id IN (SELECT tab_id FROM session_tabs)
                """)
                
                # Then delete all session tabs
                cursor.execute("DELETE FROM session_tabs")
                
                # Finally delete all sessions
                cursor.execute("DELETE FROM user_sessions")
                conn.commit()
                
                # Show additional confirmation
                QMessageBox.information(self, "Sessions Cleared", "All user sessions have been cleared.")
            
            conn.close()
            
            # Reload the now-empty table
            self.load_logs()
            
            # Show success message
            QMessageBox.information(self, "Success", "All logs have been cleared successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear logs: {str(e)}")
            import traceback
            traceback.print_exc()  # Print stack trace for debugging
    
    def load_logs(self):
        """Load logs from SQL database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get logs ordered by timestamp descending (most recent first)
            cursor.execute("""
                SELECT timestamp, username, action 
                FROM user_logs 
                ORDER BY timestamp DESC
            """)
            
            logs = cursor.fetchall()
            
            # Clear existing rows
            self.table.setRowCount(0)
            
            if logs:
                self.table.setRowCount(len(logs))
                for i, (timestamp, username, action) in enumerate(logs):
                    # Format timestamp
                    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Add items to table
                    self.table.setItem(i, 0, QTableWidgetItem(formatted_time))
                    self.table.setItem(i, 1, QTableWidgetItem(username))
                    self.table.setItem(i, 2, QTableWidgetItem(action))
            else:
                self.table.setRowCount(1)
                self.table.setSpan(0, 0, 1, 3)  # Merge cells for message
                self.table.setItem(0, 0, QTableWidgetItem("No logs available"))
            
            conn.close()
            
        except Exception as e:
            self.table.setRowCount(1)
            self.table.setSpan(0, 0, 1, 3)  # Merge cells for error message
            self.table.setItem(0, 0, QTableWidgetItem(f"Error loading logs: {str(e)}"))
