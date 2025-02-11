from PyQt5.QtGui import QColor, QFont

# Color scheme (Dark Mode)
COLORS = {
    'primary': '#2962FF',      # Blue
    'secondary': '#424242',    # Dark gray
    'background': '#1E1E1E',   # Dark background
    'surface': '#2D2D2D',      # Slightly lighter dark
    'error': '#CF6679',        # Soft red
    'success': '#03DAC6',      # Teal
    'text': '#FFFFFF',         # White text
    'text_secondary': '#B3B3B3',  # Light gray text
    'bullying': '#FF1744',     # Red
    'normal': '#00E676'        # Green
}

# Fonts
FONTS = {
    'header': QFont('Segoe UI', 12, QFont.Bold),
    'body': QFont('Segoe UI', 10),
    'button': QFont('Segoe UI', 10, QFont.Medium)
}

# Styles
BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['primary']};
        color: {COLORS['text']};
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        min-width: 100px;
    }}
    QPushButton:hover {{
        background-color: #3D74FF;
    }}
    QPushButton:pressed {{
        background-color: #2255D8;
    }}
"""

INPUT_STYLE = f"""
    QLineEdit {{
        padding: 8px;
        border: 1px solid {COLORS['secondary']};
        border-radius: 4px;
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
    }}
    QLineEdit:focus {{
        border: 2px solid {COLORS['primary']};
    }}
"""

TABLE_STYLE = f"""
    QTableWidget {{
        border: 1px solid {COLORS['secondary']};
        border-radius: 4px;
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        gridline-color: {COLORS['secondary']};
        outline: none;
    }}
    QHeaderView::section {{
        background-color: {COLORS['background']};
        color: {COLORS['text']};
        padding: 8px;
        border: none;
        border-right: 1px solid {COLORS['secondary']};
        border-bottom: 1px solid {COLORS['secondary']};
        font-weight: bold;
    }}
    QTableWidget::item {{
        padding: 5px;
    }}
    QTableWidget::item:selected {{
        background-color: {COLORS['primary']};
    }}
    QScrollBar:vertical {{
        background: {COLORS['surface']};
        width: 12px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS['secondary']};
        border-radius: 6px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        background: none;
    }}
    QScrollBar:horizontal {{
        background: {COLORS['surface']};
        height: 12px;
        margin: 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: {COLORS['secondary']};
        border-radius: 6px;
        min-width: 20px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        background: none;
    }}
"""
