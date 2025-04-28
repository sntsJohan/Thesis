from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QWidget, QScrollArea, QGridLayout, QSizePolicy, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from styles import COLORS, FONTS, DIALOG_STYLE, CONTAINER_STYLE
import os
# Import the resource path helper
from utils import get_resource_path 

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setStyleSheet(DIALOG_STYLE)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
         # Position window on the right side and center it vertically
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(0, 0, 400, 500)  # Set initial size
        qr = self.frameGeometry()
        qr.moveCenter(screen.center())  # Center the window
        qr.moveRight(screen.right() - 200)  # Move to right side with 200px margin
        self.setGeometry(qr)
        
        # Set window icon using helper
        # base_path = os.path.dirname(os.path.abspath(__file__))
        # self.setWindowIcon(QIcon(os.path.join(base_path, "assets", "applogo.png")))
        app_icon_path = get_resource_path(os.path.join("assets", "applogo.png"))
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))
        
        self.init_ui()

    def init_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: {COLORS['background']}; border: none; }}")
        
        # Container widget for scroll area
        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setSpacing(30)
        
        # System Information Section
        system_container = QWidget()
        system_container.setStyleSheet(CONTAINER_STYLE)
        system_layout = QVBoxLayout(system_container)
        
        # Title with logo
        title_layout = QHBoxLayout()
        logo = QLabel()
        # base_path = os.path.dirname(os.path.abspath(__file__))
        # logo_pixmap = QPixmap(os.path.join(base_path, "assets", "applogo.png"))
        logo_path = get_resource_path(os.path.join("assets", "applogo.png"))
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo.setPixmap(logo_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_layout.addWidget(logo)
        
        title = QLabel("Tagalog-English Cyberbullying Detection System")
        title.setFont(FONTS['header'])
        title.setStyleSheet(f"color: {COLORS['primary']};")
        title_layout.addWidget(title)
        title_layout.addStretch()
        system_layout.addLayout(title_layout)
        
        # Version and description
        version = QLabel("Version 1.0")
        version.setFont(FONTS['body'])
        system_layout.addWidget(version)
        
        # Updated, user-friendly description
        description_text = (
            "This tool helps identify potential cyberbullying in Tagalog and English comments. "
            "You can analyze comments from Facebook posts, upload a CSV file, or type in a single comment. "
            "The system uses mBERT + SVM to read the comment and predict if it's 'Cyberbullying' or 'Normal'. "
            "Results are shown in a table with a confidence score, and you can generate reports and visualizations like word clouds."
        )
        description = QLabel(description_text)
        description.setWordWrap(True)
        description.setFont(FONTS['body'])
        system_layout.addWidget(description)
        
        scroll_layout.addWidget(system_container)
        
        # Team Section
        team_container = QWidget()
        team_container.setStyleSheet(CONTAINER_STYLE)
        team_layout = QVBoxLayout(team_container)
        
        team_title = QLabel("Development Team")
        team_title.setFont(FONTS['header'])
        team_title.setStyleSheet(f"color: {COLORS['primary']};")
        team_layout.addWidget(team_title)
        
        # Grid for team members
        team_grid = QGridLayout()
        team_grid.setSpacing(20)
        
        # Team member data
        team_members = [
            # Use get_resource_path for images
            {"name": "Anioay, Kenneth", "role": "Project Lead & ML Engineer", "image": get_resource_path(os.path.join("assets", "kenneth.png"))},
            {"name": "De Vera, Nathan", "role": "Researcher", "image": get_resource_path(os.path.join("assets", "nathan.jpg"))},
            {"name": "Evangelista, Danielle", "role": "Researcher", "image": get_resource_path(os.path.join("assets", "daniel.jpg"))},
            {"name": "Santos, Johan", "role": "Fullstack Developer", "image": get_resource_path(os.path.join("assets", "johan.jpg"))}
        ]
        
        # Create team member cards
        for i, member in enumerate(team_members):
            card = QWidget()
            card.setStyleSheet(f"""
                QWidget {{
                    background-color: {COLORS['surface']};
                    border-radius: 8px;
                    padding: 10px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            
            # Member image
            image = QLabel()
            # Set a fixed size for the QLabel to ensure layout consistency
            image.setFixedSize(120, 120) 
            image.setAlignment(Qt.AlignCenter)
            
            # Check if image path exists before creating Pixmap
            member_image_path = member["image"]
            if os.path.exists(member_image_path):
                 pixmap = QPixmap(member_image_path)
                 # Scale pixmap to fit within the QLabel, keeping aspect ratio
                 scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                 image.setPixmap(scaled_pixmap)
            else:
                 image.setText("(Image not found)") # Placeholder if image missing
                 image.setStyleSheet("color: grey;") # Style the placeholder text
            
            # Center the QLabel within the card's layout
            card_layout.addWidget(image, alignment=Qt.AlignCenter) 
            
            # Member name
            name = QLabel(member["name"])
            name.setFont(FONTS['button'])
            name.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(name)
            
            # Member role
            role = QLabel(member["role"])
            role.setFont(FONTS['body'])
            role.setStyleSheet(f"color: {COLORS['text_secondary']};")
            role.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(role)
            
            # Add card to grid
            team_grid.addWidget(card, i // 2, i % 2)
        
        team_layout.addLayout(team_grid)
        scroll_layout.addWidget(team_container)
        
        # Technologies Used Section
        tech_container = QWidget()
        tech_container.setStyleSheet(CONTAINER_STYLE)
        tech_layout = QVBoxLayout(tech_container)
        
        tech_title = QLabel("Technologies Used")
        tech_title.setFont(FONTS['header'])
        tech_title.setStyleSheet(f"color: {COLORS['primary']};")
        tech_layout.addWidget(tech_title)
        
        technologies = QLabel(
            "• Python with PyQt5 for the user interface\n"
            "• Natural Language Processing (NLP) for text analysis\n"
            "• Machine Learning for classification\n"
            "• SQL for data storage\n"
            "• Matplotlib and WordCloud for data visualization"
        )
        technologies.setFont(FONTS['body'])
        tech_layout.addWidget(technologies)
        
        scroll_layout.addWidget(tech_container)
        
        # Add scroll area to main layout
        scroll.setWidget(container)
        layout.addWidget(scroll)