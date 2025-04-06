from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
                           QHeaderView, QPushButton, QLabel, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from styles import COLORS, FONTS, BUTTON_STYLE, TABLE_STYLE
from db_config import get_db_connection
from datetime import datetime

class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Logs")
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")
        self.resize(800, 600)
        
        # Set window icon
        self.setWindowIcon(QIcon("assets/applogo.png"))
        
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
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet(BUTTON_STYLE)
        close_button.setFixedWidth(100)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)
        
        # Load logs initially
        self.load_logs()
    
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
