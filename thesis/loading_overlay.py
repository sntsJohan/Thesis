from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor
from styles import COLORS, FONTS

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
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
        self.loading_label.setAlignment(Qt.AlignCenter)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {COLORS['primary']};
                border-radius: 5px;
                text-align: center;
                color: {COLORS['text']};
                background-color: {COLORS['surface']};
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['primary']};
                width: 10px;
            }}
        """)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.hide()
        
        layout.addWidget(self.loading_label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
        
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