from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QCheckBox, 
                             QPushButton, QHBoxLayout, QScrollArea, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import os
from styles import COLORS, FONTS, BUTTON_STYLE, DIALOG_STYLE

class DisclaimerDialog(QDialog):
    """Disclaimer dialog shown at application startup"""
    
    # Signal emitted when user accepts the disclaimer
    accepted = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Important Disclaimer")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet(DIALOG_STYLE)
        self.setMinimumSize(750, 600)  # Increased size for better readability
        
        # Set window icon
        base_path = os.path.dirname(os.path.abspath(__file__))
        app_icon = QIcon(os.path.join(base_path, "assets", "applogo.png"))
        self.setWindowIcon(app_icon)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)  # Increased spacing
        main_layout.setContentsMargins(30, 30, 30, 30)  # Increased margins
        
        # Title
        title_label = QLabel("Ethical Considerations and Disclaimer")
        title_label.setFont(QFont(FONTS['header'].family(), 18, QFont.Bold))  # Larger font
        title_label.setStyleSheet(f"color: {COLORS['primary']}; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Scroll area for disclaimer text
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QScrollBar:vertical {{
                background: {COLORS['surface']};
                width: 14px;
                border-radius: 7px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['secondary']};
                min-height: 30px;
                border-radius: 7px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        disclaimer_widget = QWidget()
        disclaimer_widget.setStyleSheet(f"background-color: {COLORS['background']};")
        disclaimer_layout = QVBoxLayout(disclaimer_widget)
        disclaimer_layout.setSpacing(25)  # Increased spacing between sections
        disclaimer_layout.setContentsMargins(25, 25, 25, 25)  # Increased padding
        
        # Disclaimer sections
        sections = [
            {
                "title": "Purpose of the Tool",
                "content": "The Cyberbullying Content Guidance System is designed to assist in identifying potentially problematic content in online communications sourced *only from public Facebook posts*. This tool provides an assessment based on its underlying model and is not a definitive judgment about the nature of the content. All assessments should be reviewed by a human moderator."
            },
            {
                "title": "Privacy and Data Usage (Facebook Posts)",
                "content": "When using this tool with content from public Facebook posts:\n\n• Comment text and related metadata (commenter name, date, etc.) are processed but not stored permanently by this tool beyond your current session.\n• All data analysis is conducted locally on your device.\n• This tool should not be used to target specific individuals.\n• You must comply with Facebook's Terms of Service when collecting data."
            },
            {
                "title": "Limitations and Potential Biases",
                "content": "Be aware of the following limitations:\n\n• The assessment is probabilistic, based on patterns learned by the model, not a deterministic judgment.\n• False positives and false negatives can occur.\n• Cultural and linguistic nuances may not be fully captured.\n• Results should be interpreted cautiously, particularly for content with lower confidence scores.\n• The underlying model may reflect biases present in its training data.\n• Context and intent are often not fully captured by automated analysis."
            },
            {
                "title": "Ethical Usage Guidelines",
                "content": "By using this tool, you agree to:\n\n• Use the technology responsibly and ethically.\n• Not rely solely on automated assessments for moderation decisions.\n• Consider context and intent when reviewing flagged content.\n• Respect the privacy of individuals whose content is being analyzed.\n• Not use this tool to discriminate against individuals or groups.\n• Obtain appropriate consent when required by law or platform terms.\n• Use the tool as an aid for human judgment, not as a replacement."
            },
            {
                "title": "Research Context",
                "content": "This application was developed as part of academic research. The labels and assessments it provides are based on a machine learning model and are designed to guide human reviewers, not to provide conclusive determinations about whether content constitutes cyberbullying or harmful speech."
            }
        ]
        
        # Add each section to the layout with improved styling
        for section in sections:
            # Create section container with background but NO BORDER
            section_container = QWidget()
            section_container.setStyleSheet(f"""
                background-color: {COLORS['surface']};
                border-radius: 8px;
                /* border: 1px solid {COLORS['border']}; */ /* Border removed */
                padding: 10px;
            """)
            section_container_layout = QVBoxLayout(section_container)
            section_container_layout.setContentsMargins(15, 15, 15, 15)
            section_container_layout.setSpacing(10)
            
            # Section title
            section_title = QLabel(section["title"])
            section_title.setFont(QFont(FONTS['header'].family(), 14, QFont.Bold))  # Larger font
            section_title.setStyleSheet(f"color: {COLORS['primary']}; background: transparent;")
            section_container_layout.addWidget(section_title)
            
            # Section content
            section_content = QLabel(section["content"])
            section_content.setFont(QFont(FONTS['body'].family(), 12))  # Larger font
            section_content.setStyleSheet(f"color: {COLORS['text']}; background: transparent; line-height: 150%;")
            section_content.setWordWrap(True)
            section_content.setTextFormat(Qt.RichText)
            # Convert bullet points to HTML for better formatting
            formatted_content = section["content"].replace("• ", "<br>• ").replace("\n\n", "<br><br>")
            section_content.setText(formatted_content)
            section_container_layout.addWidget(section_content)
            
            disclaimer_layout.addWidget(section_container)
        
        # Add some spacing at the bottom for better scrolling
        disclaimer_layout.addStretch(1)
        
        scroll_area.setWidget(disclaimer_widget)
        main_layout.addWidget(scroll_area)
        
        # Checkbox for agreement with better styling
        self.agreement_checkbox = QCheckBox("I have read and understand the disclaimer and ethical considerations")
        self.agreement_checkbox.setFont(QFont(FONTS['body'].family(), 12))  # Larger font
        self.agreement_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text']};
                spacing: 10px;
                padding: 5px;
                background-color: {COLORS['surface']};
                border-radius: 5px;
            }}
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border: 2px solid {COLORS['border']};
                border-radius: 4px;
                background-color: {COLORS['background']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['primary']};
            }}
        """)
        self.agreement_checkbox.stateChanged.connect(self.update_button_state)
        main_layout.addWidget(self.agreement_checkbox)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Continue button
        self.continue_button = QPushButton("Continue")
        self.continue_button.setFont(FONTS['button'])
        self.continue_button.setStyleSheet(f"""
            {BUTTON_STYLE}
            QPushButton {{
                padding: 10px 20px;
                font-size: 13px;
            }}
        """)
        self.continue_button.setEnabled(False)
        self.continue_button.setFixedWidth(150)
        self.continue_button.clicked.connect(self.accept_disclaimer)
        
        # Exit button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setFont(FONTS['button'])
        self.exit_button.setStyleSheet(f"""
            {BUTTON_STYLE}
            QPushButton {{
                background-color: {COLORS['error']};
                padding: 10px 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #c62828;
            }}
            QPushButton:pressed {{
                background-color: #b71c1c;
            }}
        """)
        self.exit_button.setFixedWidth(150)
        self.exit_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.exit_button)
        button_layout.addWidget(self.continue_button)
        
        main_layout.addLayout(button_layout)
    
    def update_button_state(self, state):
        """Enable/disable continue button based on checkbox state"""
        self.continue_button.setEnabled(state == Qt.Checked)
    
    def accept_disclaimer(self):
        """Handle user accepting the disclaimer"""
        self.accepted.emit()
        self.accept() 