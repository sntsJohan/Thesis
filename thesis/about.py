from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QWidget, QScrollArea, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from styles import COLORS, FONTS, DIALOG_STYLE, CONTAINER_STYLE

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setStyleSheet(DIALOG_STYLE)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Set window icon
        self.setWindowIcon(QIcon("assets/applogo.png"))
        
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
        logo_pixmap = QPixmap("assets/applogo.png")
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
        
        description = QLabel(
            "A sophisticated system designed to detect and analyze cyberbullying content "
            "in both Tagalog and English languages. This tool uses advanced natural language "
            "processing and machine learning techniques to identify potentially harmful content "
            "across social media platforms."
        )
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
            {"name": "Anioay, Kenneth", "role": "Project Lead & ML Engineer", "image": "assets/placeholder.png"},
            {"name": "De Vera, Nathan", "role": "Backend Developer", "image": "assets/placeholder.png"},
            {"name": "Evangelista, Danielle", "role": "Frontend Developer", "image": "assets/placeholder.png"},
            {"name": "Santos, Johan", "role": "Frontend Developer", "image": "assets/placeholder.png"}
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
            pixmap = QPixmap(member["image"])
            image.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            image.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(image)
            
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