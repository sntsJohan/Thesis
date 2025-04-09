from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPixmap, QIcon
from styles import COLORS, FONTS
import os

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        
        # Main layout for the overlay (centers the content container)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Create the content container
        self.content_container = QWidget()
        self.content_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['primary']};
                border-radius: 10px;
                padding: 20px 40px;
            }}
        """)
        
        # Layout for the content inside the container
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setAlignment(Qt.AlignCenter)
        content_layout.setSpacing(15) # Adjust spacing inside the container
        
        # Add the application logo to the container layout
        base_path = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_path, "assets", "applogo.png")
        self.logo_label = QLabel()
        pixmap = QPixmap(logo_path)
        self.logo_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("border: none;") # Remove border from logo
        content_layout.addWidget(self.logo_label)
        
        # Create loading label (styling removed, handled by container)
        self.loading_label = QLabel("Loading...")
        self.loading_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                background-color: transparent; /* Remove individual background */
                border: none; /* Remove individual border */
                padding: 0; /* Remove individual padding */
                font: {FONTS['header'].family()};
                font-size: 16px;
            }}
        """)
        self.loading_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.loading_label)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {COLORS['primary']};
                border-radius: 5px;
                text-align: center;
                color: {COLORS['text']};
                background-color: {COLORS['surface']}; /* Match container slightly */
                height: 15px; /* Slightly smaller height */
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['primary']};
                width: 10px;
            }}
        """)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.hide()
        content_layout.addWidget(self.progress_bar)
        
        # Add the content container to the main layout
        main_layout.addWidget(self.content_container)
        self.setLayout(main_layout)
        
        # Create animation dots
        self.dots = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_dots)
        self.timer.start(500)  # Update every 500ms
        
        self.hide()

    def animate_dots(self):
        self.dots = (self.dots + 1) % 4
        current_text = self.loading_label.text().split("...")[0]
        self.loading_label.setText(current_text + "." * self.dots)

    def show(self, message="Loading..."):
        self.loading_label.setText(message)
        self.progress_bar.hide()
        self.resize(self.parent().size())
        super().show()
        
    def show_with_progress(self, message="Loading..."):
        self.loading_label.setText(message)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.resize(self.parent().size())
        super().show()
        
    def set_progress(self, value):
        self.progress_bar.setValue(value)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 150))
        
    def resizeEvent(self, event):
        self.resize(self.parent().size())
        super().resizeEvent(event) 