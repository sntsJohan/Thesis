from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QWidget, QMessageBox,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QComboBox, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE, DIALOG_STYLE, TABLE_STYLE
from db_config import get_db_connection, log_user_action

class UserManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Management")
        self.setStyleSheet(DIALOG_STYLE)
        self.setMinimumWidth(1200)  # Increased width
        self.setMinimumHeight(800)  # Increased height
        
        # Set window icon
        self.setWindowIcon(QIcon("assets/applogo.png"))
        
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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Username", "Role", "Last Login", "Status", 
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
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        
        self.table.setColumnWidth(0, 150)  # Username
        self.table.setColumnWidth(1, 100)  # Role
        self.table.setColumnWidth(2, 180)  # Last Login
        self.table.setColumnWidth(3, 100)   # Status
        self.table.setColumnWidth(4, 120)  # Action Count
        self.table.setColumnWidth(5, 180)  # Account Created
        
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
                role = user[1]
                last_login = user[2] if user[2] else "Never"
                is_active = user[3]
                action_count = user[4]
                created_at = user[5]

                # Username
                self.table.setItem(i, 0, QTableWidgetItem(username))
                
                # Role
                role_item = QTableWidgetItem(role)
                role_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 1, role_item)
                
                # Last Login
                self.table.setItem(i, 2, QTableWidgetItem(str(last_login)))
                
                # Status
                status_item = QTableWidgetItem("Active" if is_active else "Disabled")
                status_item.setTextAlignment(Qt.AlignCenter)
                if is_active:
                    status_item.setForeground(QColor(COLORS['success']))
                else:
                    status_item.setForeground(QColor(COLORS['error']))
                self.table.setItem(i, 3, status_item)
                
                # Action Count
                count_item = QTableWidgetItem(str(action_count))
                count_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 4, count_item)
                
                # Created At
                self.table.setItem(i, 5, QTableWidgetItem(str(created_at)))
                
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
                
                self.table.setCellWidget(i, 6, actions_widget)
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")

    def show_add_user_dialog(self):
        """Show dialog to add new user"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New User")
        dialog.setStyleSheet(DIALOG_STYLE)
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)  # Increased spacing
        layout.setContentsMargins(20, 20, 20, 20)  # Increased margins
        
        # Username
        username_label = QLabel("Username:")
        username_label.setFont(FONTS['body'])
        username_input = QLineEdit()
        username_input.setStyleSheet(INPUT_STYLE)
        username_input.setFixedHeight(35)  # Consistent height
        layout.addWidget(username_label)
        layout.addWidget(username_input)
        
        # Password
        password_label = QLabel("Password:")
        password_label.setFont(FONTS['body'])
        password_input = QLineEdit()
        password_input.setStyleSheet(INPUT_STYLE)
        password_input.setFixedHeight(35)
        password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_label)
        layout.addWidget(password_input)
        
        # Role
        role_label = QLabel("Role:")
        role_label.setFont(FONTS['body'])
        role_combo = QComboBox()
        role_combo.addItems(["user", "admin"])
        role_combo.setStyleSheet("""
            QComboBox {
                background-color: """ + COLORS['surface'] + """;
                color: """ + COLORS['text'] + """;
                border: 1px solid """ + COLORS['border'] + """;
                border-radius: 4px;
                padding: 8px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(assets/drop.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: """ + COLORS['surface'] + """;
                color: """ + COLORS['text'] + """;
                selection-background-color: """ + COLORS['primary'] + """;
                selection-color: """ + COLORS['text'] + """;
                border: 1px solid """ + COLORS['border'] + """;
            }
        """)
        role_combo.setFixedHeight(35)
        layout.addWidget(role_label)
        layout.addWidget(role_combo)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(BUTTON_STYLE)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(BUTTON_STYLE)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        # Error Label
        error_label = QLabel()
        error_label.setStyleSheet(f"color: {COLORS['error']}")
        error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(error_label)
        
        def save_user():
            username = username_input.text().strip()
            password = password_input.text().strip()
            role = role_combo.currentText()
            
            if not username or not password:
                error_label.setText("Please fill all fields")
                return
                
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Check if username exists
                cursor.execute("SELECT username FROM users WHERE username=?", (username,))
                if cursor.fetchone():
                    error_label.setText("Username already exists")
                    return
                
                # Add new user
                cursor.execute(
                    """INSERT INTO users (username, password, role, is_active, created_at) 
                       VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)""",
                    (username, password, role)
                )
                conn.commit()
                conn.close()
                
                self.load_users()
                dialog.accept()
                
            except Exception as e:
                error_label.setText(f"Error: {str(e)}")
        
        save_btn.clicked.connect(save_user)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()

    def edit_user(self, username):
        """Show dialog to edit user"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE username=?", (username,))
            current_role = cursor.fetchone()[0]
            conn.close()
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Edit User - {username}")
            dialog.setStyleSheet(DIALOG_STYLE)
            dialog.setMinimumWidth(400)
            dialog.setFixedHeight(200)  # Set initial fixed height
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Role
            role_label = QLabel("Role:")
            role_label.setFont(FONTS['body'])
            role_combo = QComboBox()
            role_combo.addItems(["user", "admin"])
            role_combo.setCurrentText(current_role)
            role_combo.setStyleSheet("""
                QComboBox {
                    background-color: """ + COLORS['surface'] + """;
                    color: """ + COLORS['text'] + """;
                    border: 1px solid """ + COLORS['border'] + """;
                    border-radius: 4px;
                    padding: 8px;
                    min-width: 100px;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 30px;
                }
                QComboBox::down-arrow {
                    image: url(assets/drop.png);
                    width: 12px;
                    height: 12px;
                }
                QComboBox QAbstractItemView {
                    background-color: """ + COLORS['surface'] + """;
                    color: """ + COLORS['text'] + """;
                    selection-background-color: """ + COLORS['primary'] + """;
                    selection-color: """ + COLORS['text'] + """;
                    border: 1px solid """ + COLORS['border'] + """;
                }
            """)
            role_combo.setFixedHeight(35)
            layout.addWidget(role_label)
            layout.addWidget(role_combo)
            
            # Reset Password Button
            reset_pwd_btn = QPushButton("Reset Password")
            reset_pwd_btn.setStyleSheet(BUTTON_STYLE)
            reset_pwd_btn.setFixedHeight(35)
            layout.addWidget(reset_pwd_btn)
            
            # Password Reset Section (initially hidden)
            password_section = QWidget()
            password_section.hide()
            password_layout = QVBoxLayout(password_section)
            password_layout.setSpacing(15)
            password_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to prevent layout shifts
            
            # New Password
            password_label = QLabel("New Password:")
            password_label.setFont(FONTS['body'])
            password_input = QLineEdit()
            password_input.setStyleSheet(INPUT_STYLE)
            password_input.setFixedHeight(35)
            password_input.setEchoMode(QLineEdit.Password)
            password_layout.addWidget(password_label)
            password_layout.addWidget(password_input)
            
            # Confirm Password
            confirm_label = QLabel("Confirm Password:")
            confirm_label.setFont(FONTS['body'])
            confirm_input = QLineEdit()
            confirm_input.setStyleSheet(INPUT_STYLE)
            confirm_input.setFixedHeight(35)
            confirm_input.setEchoMode(QLineEdit.Password)
            password_layout.addWidget(confirm_label)
            password_layout.addWidget(confirm_input)
            
            layout.addWidget(password_section)
            
            # Error Label
            error_label = QLabel()
            error_label.setStyleSheet(f"color: {COLORS['error']}")
            error_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(error_label)
            
            # Buttons
            btn_layout = QHBoxLayout()
            save_btn = QPushButton("Save")
            save_btn.setStyleSheet(BUTTON_STYLE)
            save_btn.setFixedHeight(35)
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setStyleSheet(BUTTON_STYLE)
            cancel_btn.setFixedHeight(35)
            
            btn_layout.addWidget(save_btn)
            btn_layout.addWidget(cancel_btn)
            layout.addLayout(btn_layout)
            
            # Toggle password section visibility
            def toggle_password_section():
                if password_section.isHidden():
                    dialog.setFixedHeight(500)  # Expanded height for password section
                    password_section.show()
                    reset_pwd_btn.setText("Cancel Password Reset")
                else:
                    dialog.setFixedHeight(200)  # Original height
                    password_section.hide()
                    reset_pwd_btn.setText("Reset Password")
                    password_input.clear()
                    confirm_input.clear()
            
            reset_pwd_btn.clicked.connect(toggle_password_section)
            
            def save_changes():
                try:
                    new_role = role_combo.currentText()
                    
                    # Validate passwords if section is visible
                    if not password_section.isHidden():
                        password = password_input.text()
                        confirm = confirm_input.text()
                        
                        if not password:
                            error_label.setText("Please enter a new password")
                            return
                        if password != confirm:
                            error_label.setText("Passwords do not match")
                            return
                    
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Update role
                    cursor.execute(
                        "UPDATE users SET role=? WHERE username=?",
                        (new_role, username)
                    )
                    
                    # Update password if reset section is visible
                    if not password_section.isHidden():
                        cursor.execute(
                            "UPDATE users SET password=? WHERE username=?",
                            (password, username)
                        )
                    
                    conn.commit()
                    conn.close()
                    
                    self.load_users()
                    dialog.accept()
                    
                    if not password_section.isHidden():
                        QMessageBox.information(self, "Success", "User information and password updated")
                    else:
                        QMessageBox.information(self, "Success", "User information updated")
                    
                except Exception as e:
                    error_label.setText(f"Error: {str(e)}")
            
            save_btn.clicked.connect(save_changes)
            cancel_btn.clicked.connect(dialog.reject)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit user: {str(e)}")

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