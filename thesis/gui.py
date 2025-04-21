from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QWidget, QStackedWidget, QDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from utils import display_message, get_resource_path
from styles import (WELCOME_BACKGROUND_STYLE, WELCOME_CONTAINER_STYLE, WELCOME_TITLE_FONT, 
                   WELCOME_TITLE_STYLE_DARK, WELCOME_SUBTITLE_FONT, GET_STARTED_BUTTON_DARK_STYLE, 
                   ABOUT_BUTTON_OUTLINE_STYLE, WELCOME_VERSION_STYLE, COLORS, FONTS)
from user import UserMainWindow
from admin import AdminWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.admin_window = None
        self.user_window = None
        
        # Set window properties
        self.setWindowTitle("Cyberbullying Detection System")
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")

        # Set window icon using the resource path
        icon_path = get_resource_path("assets/applogo.png")
        app_icon = QIcon(icon_path)
        self.setWindowIcon(app_icon)

        # Create central stacked widget
        self.central_widget = QStackedWidget()  
        self.setCentralWidget(self.central_widget)

        # Initialize welcome screen
        self.init_welcome_screen()
        
        # Show fullscreen after setup
        self.showFullScreen()

    def init_welcome_screen(self):
        """Initialize the welcome screen"""
        welcome_widget = QWidget()
        welcome_widget.setStyleSheet(WELCOME_BACKGROUND_STYLE)
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setSpacing(0)
        welcome_layout.setContentsMargins(90, 0, 90, 0)

        welcome_layout.addStretch(1)

        header_container = QWidget()
        header_container.setStyleSheet(WELCOME_CONTAINER_STYLE)
        header_layout = QVBoxLayout(header_container)
        header_layout.setSpacing(10)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Title parts
        title_label = QLabel("Cyberbullying")
        title_label.setFont(WELCOME_TITLE_FONT)
        title_label.setStyleSheet(WELCOME_TITLE_STYLE_DARK)
        title_label.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(title_label)

        secondary_title = QLabel("Detection")
        secondary_title.setFont(WELCOME_TITLE_FONT)
        secondary_title.setStyleSheet(WELCOME_TITLE_STYLE_DARK)
        secondary_title.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(secondary_title)

        subtitle_label = QLabel("Tagalog and English Cyberbullying Detection System")
        subtitle_label.setFont(WELCOME_SUBTITLE_FONT)
        subtitle_label.setStyleSheet(WELCOME_TITLE_STYLE_DARK)
        subtitle_label.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(subtitle_label)

        welcome_layout.addWidget(header_container)
        welcome_layout.addSpacing(60)

        button_container = QWidget()
        button_container.setStyleSheet(WELCOME_CONTAINER_STYLE)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(20)

        self.get_started_button = QPushButton("Get Started")
        self.get_started_button.setFont(FONTS['button'])
        self.get_started_button.setStyleSheet(GET_STARTED_BUTTON_DARK_STYLE)
        self.get_started_button.clicked.connect(self.show_login)
        button_layout.addWidget(self.get_started_button)

        about_button = QPushButton("About")
        about_button.setFont(FONTS['button'])
        about_button.setStyleSheet(ABOUT_BUTTON_OUTLINE_STYLE)
        about_button.clicked.connect(self.show_about)
        button_layout.addWidget(about_button)
        
        button_layout.addStretch()
        welcome_layout.addWidget(button_container)

        welcome_layout.addStretch(1)
        welcome_layout.addSpacing(40)
        
        version_label = QLabel("Version 1.0")
        version_label.setAlignment(Qt.AlignLeft)
        version_label.setStyleSheet(WELCOME_VERSION_STYLE)
        welcome_layout.addWidget(version_label)
        
        welcome_layout.addSpacing(20)

        self.central_widget.addWidget(welcome_widget)

    def show_login(self):
        """Show login dialog and handle user role"""
        from login import LoginWindow
        login_dialog = LoginWindow(self)
        result = login_dialog.exec_()
        
        if result == QDialog.Accepted:
            role = login_dialog.get_role()
            username = login_dialog.get_username()
            
            if role and role.lower() == "admin":
                try:
                    # Create admin window
                    self.admin_window = AdminWindow(self)
                    # Set current user for the admin window
                    self.admin_window.set_current_user(username)
                    self.hide()
                    self.admin_window.showFullScreen()
                except Exception as e:
                    display_message(self, "Error", f"Error initializing admin interface: {e}")
                    import traceback
                    traceback.print_exc()
            elif role and role.lower() == "user":
                try:
                    # Create new user window instance
                    self.user_window = UserMainWindow()
                    # Set references
                    self.user_window.main_window = self
                    self.user_window.username_label.setText(f"👤 {username}")
                    # Initialize session first
                    self.user_window.set_current_user(username)
                    # Show user window
                    self.hide()
                    self.user_window.showFullScreen()
                except Exception as e:
                    display_message(self, "Error", f"Error initializing user interface: {e}")
            else:
                display_message(self, "Error", f"Invalid role: {role}")
        
    def confirm_sign_out(self):
        """Confirm sign out from the admin/user interface"""
        reply = QMessageBox.question(
            self, 
            "Confirm Sign Out", 
            "Are you sure you want to sign out?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # If admin window exists and is visible, close it
            if self.admin_window:
                self.admin_window.close()
                self.admin_window = None
            
            # If user window exists and is visible, close it  
            if self.user_window:
                self.user_window.close()
                self.user_window = None
                
            # Show the welcome screen
            self.show()
            
    def show_about(self):
        """Show the About dialog"""
        from about import AboutDialog
        about_dialog = AboutDialog(self)
        about_dialog.exec_()