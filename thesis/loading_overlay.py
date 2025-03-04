from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from styles import COLORS, FONTS

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(parent.size())
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Create loading label with custom styling
        self.loading_label = QLabel("Loading...")
        self.loading_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['primary']};
                border-radius: 10px;
                padding: 20px 40px;
                font: {FONTS['header'].family()};
                font-size: 16px;
            }}
        """)
        layout.addWidget(self.loading_label)
        
        # Create animation dots
        self.dots = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_dots)
        self.timer.start(500)  # Update every 500ms
        
        # Semi-transparent background
        self.setStyleSheet(f"""
            LoadingOverlay {{
                background-color: rgba(0, 0, 0, 150);
            }}
        """)
        
        self.hide()

    def animate_dots(self):
        self.dots = (self.dots + 1) % 4
        self.loading_label.setText("Loading" + "." * self.dots)

    def resizeEvent(self, event):
        self.setFixedSize(self.parent().size())
        super().resizeEvent(event) 