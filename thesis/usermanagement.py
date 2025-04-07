from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QWidget, QMessageBox,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QComboBox, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE, DIALOG_STYLE, TABLE_STYLE
from db_config import get_db_connection, log_user_action
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re

class UserManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Management")
        self.setStyleSheet(DIALOG_STYLE)
        self.setMinimumWidth(1400)  # Increased width
        self.setMinimumHeight(800)  # Increased height
        
        # Set window icon
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QIcon(os.path.join(base_path, "assets", "applogo.png")))
        
        self.init_ui()
        self.load_users()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("User Management")
        title.setFont(FONTS['header'])
        title.setStyleSheet(f"color: {COLORS['primary']}; font-size: 24px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Actions Container
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        
        # Add User Button
        add_user_btn = QPushButton(" + Add User")
        add_user_btn.setFont(FONTS['button'])
        add_user_btn.setStyleSheet(BUTTON_STYLE)
        add_user_btn.clicked.connect(self.show_add_user_dialog)
        actions_layout.addWidget(add_user_btn)
        
        # Clear Sessions Button
        clear_sessions_btn = QPushButton("🗑️ Clear All Sessions")
        clear_sessions_btn.setFont(FONTS['button'])
        clear_sessions_btn.setStyleSheet(BUTTON_STYLE)
        clear_sessions_btn.clicked.connect(self.clear_all_sessions)
        actions_layout.addWidget(clear_sessions_btn)
        
        # Refresh Button
        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.setFont(FONTS['button'])
        refresh_btn.setStyleSheet(BUTTON_STYLE)
        refresh_btn.clicked.connect(self.load_users)
        actions_layout.addWidget(refresh_btn)
        
        actions_layout.addStretch()
        layout.addWidget(actions_container)

        # Users Table
        self.table = QTableWidget()
        self.table.setStyleSheet(TABLE_STYLE + """

        """)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Username", "Email", "Role", "Last Login", "Status",
            "Action Count", "Account Created", "Actions"
        ])
        
        # Set row height
        self.table.verticalHeader().setDefaultSectionSize(60)  # Reduced row height
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.setSectionResizeMode(7, QHeaderView.Stretch)
        
        self.table.setColumnWidth(0, 150)  # Username
        self.table.setColumnWidth(1, 200)  # Email
        self.table.setColumnWidth(2, 100)  # Role
        self.table.setColumnWidth(3, 180)  # Last Login
        self.table.setColumnWidth(4, 100)  # Status
        self.table.setColumnWidth(5, 120)  # Action Count
        self.table.setColumnWidth(6, 120)  # Account Created
        
        # Make table read-only
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.table.setColumnWidth(7, 120)  # Actions column
        
        layout.addWidget(self.table)

        # Close Button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(BUTTON_STYLE)
        close_btn.setFont(FONTS['button'])
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def load_users(self):
        """Load users from database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get user data with metrics
            cursor.execute("""
                SELECT 
                    u.username,
                    u.email,
                    u.role,
                    (SELECT TOP 1 timestamp FROM user_logs 
                     WHERE username = u.username 
                     ORDER BY timestamp DESC) as last_login,
                    u.is_active,
                    (SELECT COUNT(*) FROM user_logs 
                     WHERE username = u.username) as action_count,
                    u.created_at
                FROM users u
                ORDER BY u.username
            """)
            users = cursor.fetchall()
            
            self.table.setRowCount(len(users))
            for i, user in enumerate(users):
                username = user[0]
                email = user[1] if user[1] else "N/A"
                role = user[2]
                last_login = user[3] if user[3] else "Never"
                is_active = user[4]
                action_count = user[5]
                created_at = user[6]

                # Username
                self.table.setItem(i, 0, QTableWidgetItem(username))
                
                # Email
                self.table.setItem(i, 1, QTableWidgetItem(email))
                
                # Role
                role_item = QTableWidgetItem(role)
                role_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 2, role_item)
                
                # Last Login
                self.table.setItem(i, 3, QTableWidgetItem(str(last_login)))
                
                # Status
                status_item = QTableWidgetItem("Active" if is_active else "Disabled")
                status_item.setTextAlignment(Qt.AlignCenter)
                if is_active:
                    status_item.setForeground(QColor(COLORS['success']))
                else:
                    status_item.setForeground(QColor(COLORS['error']))
                self.table.setItem(i, 4, status_item)
                
                # Action Count
                count_item = QTableWidgetItem(str(action_count))
                count_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 5, count_item)
                
                # Created At
                created_at_str = created_at.strftime('%Y-%m-%d') if created_at else "N/A"
                created_at_item = QTableWidgetItem(created_at_str)
                created_at_item.setTextAlignment(Qt.AlignCenter) # Center align date
                self.table.setItem(i, 6, created_at_item)
                
                # Action Buttons Container
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 0, 4, 0)  # Reduced margins
                actions_layout.setSpacing(4)  # Reduced spacing
                
                # Make buttons smaller with consistent style
                button_style = """
                    QPushButton {
                        padding: 4px 8px;
                        min-width: 90px;
                        max-width: 90px;
                        font-size: 11px;
                        background: transparent;
                        border: 1px solid """ + COLORS['border'] + """;
                    }
                    QPushButton:hover {
                        background-color: """ + COLORS['hover'] + """;
                    }
                """
                
                edit_btn = QPushButton("✏️ Edit")
                edit_btn.setStyleSheet(button_style)
                edit_btn.setFixedHeight(26)  # Smaller height
                edit_btn.clicked.connect(lambda checked, u=username: self.edit_user(u))
                
                toggle_btn = QPushButton("❌ Disable" if is_active else "✓ Enable")
                toggle_btn.setStyleSheet(button_style)
                toggle_btn.setFixedHeight(26)
                toggle_btn.clicked.connect(lambda checked, u=username, a=is_active: self.toggle_user_status(u, a))
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(toggle_btn)
                
                self.table.setCellWidget(i, 7, actions_widget)
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")

    def show_add_user_dialog(self):
        """Show dialog to add new user"""
        dialog = AddEditUserDialog(self)
        if dialog.exec_():
            self.load_users()

    def edit_user(self, username):
        """Show dialog to edit user"""
        dialog = AddEditUserDialog(self, username)
        if dialog.exec_():
            self.load_users()

    def toggle_user_status(self, username, current_status):
        """Toggle user active status"""
        new_status = not current_status
        status_text = "enable" if new_status else "disable"
        
        confirm = QMessageBox.question(
            self,
            "Confirm Status Change",
            f"Are you sure you want to {status_text} user '{username}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET is_active=? WHERE username=?",
                    (new_status, username)
                )
                conn.commit()
                conn.close()
                
                self.load_users()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update user status: {str(e)}")

    def clear_all_sessions(self):
        """Clear all user sessions and their associated data"""
        try:
            # Show confirmation dialog
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Clear All Sessions")
            msg.setText("Are you sure you want to clear all user sessions?")
            msg.setInformativeText("This will delete all session data including comments, predictions, and analysis results. This action cannot be undone.")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            
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
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Delete all session data
                cursor.execute("DELETE FROM tab_comments")
                cursor.execute("DELETE FROM session_tabs")
                cursor.execute("DELETE FROM user_sessions")
                
                # Reset session IDs
                cursor.execute("DBCC CHECKIDENT ('user_sessions', RESEED, 0)")
                cursor.execute("DBCC CHECKIDENT ('session_tabs', RESEED, 0)")
                cursor.execute("DBCC CHECKIDENT ('tab_comments', RESEED, 0)")
                
                conn.commit()
                conn.close()
                
                # Show success message
                QMessageBox.information(self, "Success", "All sessions and their data have been cleared successfully.")
                
                # Log the action
                log_user_action("admin", "Cleared all user sessions and data")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear sessions: {str(e)}")

class AddEditUserDialog(QDialog):
    def __init__(self, parent, username=None):
        super().__init__(parent)
        self.edit_mode = username is not None
        self.existing_username = username

        self.setWindowTitle("Edit User" if self.edit_mode else "Add New User")
        self.setStyleSheet(DIALOG_STYLE)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Username
        username_label = QLabel("Username:")
        username_label.setFont(FONTS['body'])
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(INPUT_STYLE)
        self.username_input.setFixedHeight(35)
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)

        # Email
        email_label = QLabel("Email:")
        email_label.setFont(FONTS['body'])
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet(INPUT_STYLE)
        self.email_input.setFixedHeight(35)
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)

        # Password
        password_label = QLabel("Password (leave blank to keep unchanged in edit mode):")
        password_label.setFont(FONTS['body'])
        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(INPUT_STYLE)
        self.password_input.setFixedHeight(35)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)

        # Role
        role_label = QLabel("Role:")
        role_label.setFont(FONTS['body'])
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        self.role_combo.setStyleSheet("""
            QComboBox {
                background-color: """ + COLORS['surface'] + """;
                color: """ + COLORS['text'] + """;
                border: 1px solid """ + COLORS['border'] + """;
                border-radius: 4px;
                padding: 8px;
                min-width: 100px;
            }
            QComboBox QAbstractItemView { /* Style the dropdown list */
                background-color: """ + COLORS['surface'] + """;
                color: """ + COLORS['text'] + """;
                border: 1px solid """ + COLORS['border'] + """;
                selection-background-color: """ + COLORS['primary'] + """;
            }
        """)
        layout.addWidget(role_label)
        layout.addWidget(self.role_combo)

        # Active Status Checkbox
        self.active_checkbox = QCheckBox("Account Active")
        self.active_checkbox.setFont(FONTS['body'])
        self.active_checkbox.setStyleSheet("QCheckBox { spacing: 5px; }")
        layout.addWidget(self.active_checkbox)

        # Error Label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLORS['error']};")
        layout.addWidget(self.error_label)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setFont(FONTS['button'])
        save_btn.setStyleSheet(BUTTON_STYLE)
        save_btn.clicked.connect(self.save_user)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(FONTS['button'])
        cancel_btn.setStyleSheet(BUTTON_STYLE)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        if self.edit_mode:
            self.load_user_data()
        else:
            # Default for new user
            self.active_checkbox.setChecked(True)

    def load_user_data(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT username, email, role, is_active FROM users WHERE username=?",
                           (self.existing_username,))
            user = cursor.fetchone()
            conn.close()

            if user:
                self.username_input.setText(user[0])
                self.email_input.setText(user[1] if user[1] else "")
                self.role_combo.setCurrentText(user[2])
                self.active_checkbox.setChecked(bool(user[3]))
            else:
                self.error_label.setText("User not found.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load user data: {str(e)}")

    def save_user(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text() # Don't strip password
        role = self.role_combo.currentText()
        is_active = self.active_checkbox.isChecked()

        if not username:
            self.error_label.setText("Username cannot be empty.")
            return
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.error_label.setText("Invalid email format.")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check for username/email conflicts (only if username/email changed or adding new)
            if not self.edit_mode or username != self.existing_username:
                cursor.execute("SELECT username FROM users WHERE username=?", (username,))
                if cursor.fetchone():
                    self.error_label.setText("Username already exists.")
                    conn.close()
                    return
            if email and (not self.edit_mode or email != self.get_original_email()):
                cursor.execute("SELECT email FROM users WHERE email=?", (email,))
                if cursor.fetchone():
                    self.error_label.setText("Email already registered.")
                    conn.close()
                    return

            if self.edit_mode:
                # Update existing user
                if password:
                    # Hash the new password before updating
                    hashed_password = generate_password_hash(password)
                    cursor.execute("""
                        UPDATE users SET username=?, email=?, password=?, role=?, is_active=?
                        WHERE username=?
                    """, (username, email if email else None, hashed_password, role, is_active, self.existing_username))
                else:
                    # Don't update password
                    cursor.execute("""
                        UPDATE users SET username=?, email=?, role=?, is_active=?
                        WHERE username=?
                    """, (username, email if email else None, role, is_active, self.existing_username))
                log_action = "User Edited"
            else:
                # Add new user
                if not password:
                    self.error_label.setText("Password is required for new users.")
                    conn.close()
                    return
                # Hash the password for the new user
                hashed_password = generate_password_hash(password)
                cursor.execute("""
                    INSERT INTO users (username, email, password, role, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, email if email else None, hashed_password, role, is_active))
                log_action = "User Added"

            conn.commit()
            conn.close()
            log_user_action(self.existing_username if self.edit_mode else username, f"{log_action}: {username}")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save user: {str(e)}")

    def get_original_email(self):
        # Helper to get original email for comparison during edit
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM users WHERE username=?", (self.existing_username,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception:
            return None