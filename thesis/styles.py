from PyQt5.QtGui import QColor, QFont

# Color scheme (Dark Mode)
COLORS = {
    'primary': '#6200EE',      # More modern purple
    'secondary': '#424242',    # Dark gray
    'background': '#121212',   # Darker background for better contrast
    'surface': '#1E1E1E',      # Slightly lighter than background
    'error': '#CF6679',        # Soft red
    'success': '#03DAC6',      # Teal
    'text': '#FFFFFF',         # White text
    'text_secondary': '#B3B3B3',  # Light gray text
    'bullying': '#FF1744',     # Red
    'normal': '#00E676',       # Green
    'highlight': '#311B92',    # Deeper purple for highlighting
    'border': '#303030',       # New color for borders
    'hover': '#7B1FA2',        # New hover color for buttons
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
        padding: 10px 20px;
        border-radius: 6px;
        min-width: 120px;
        font-weight: 600;
        transition: background-color 0.3s;
    }}
    QPushButton:hover {{
        background-color: {COLORS['hover']};
    }}
    QPushButton:pressed {{
        background-color: {COLORS['secondary']};
    }}
    QPushButton:disabled {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text_secondary']};
    }}
"""

INPUT_STYLE = f"""
    QLineEdit {{
        padding: 12px;
        border: 2px solid {COLORS['border']};
        border-radius: 6px;
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        font-size: 14px;
    }}
    QLineEdit:focus {{
        border: 2px solid {COLORS['primary']};
        background-color: {COLORS['background']};
    }}
    QLineEdit::placeholder {{
        color: {COLORS['text_secondary']};
    }}
"""

TABLE_STYLE = f"""
    QTableWidget {{
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        gridline-color: {COLORS['border']};
        outline: none;
        padding: 5px;
    }}
    QHeaderView::section {{
        background-color: {COLORS['background']};
        color: {COLORS['text']};
        padding: 12px;
        border: none;
        border-bottom: 2px solid {COLORS['border']};
        font-weight: bold;
        font-size: 14px;
    }}
    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {COLORS['border']};
    }}
    QTableWidget::item:selected {{
        background-color: {COLORS['primary']};
        color: {COLORS['text']};
    }}
    QScrollBar:vertical {{
        background: {COLORS['background']};
        width: 14px;
        margin: 0px;
        border-radius: 7px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS['secondary']};
        border-radius: 7px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLORS['primary']};
    }}
    QScrollBar:horizontal {{
        background: {COLORS['background']};
        height: 14px;
        margin: 0px;
        border-radius: 7px;
    }}
    QScrollBar::handle:horizontal {{
        background: {COLORS['secondary']};
        border-radius: 7px;
        min-width: 30px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {COLORS['primary']};
    }}
"""
