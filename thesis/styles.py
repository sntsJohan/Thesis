from PyQt5.QtGui import QColor, QFont

# Enhanced Color scheme (Dark Mode with better contrast)
COLORS = {
    'primary': '#8A2BE2',      # Brighter purple for better visibility
    'secondary': '#555555',    # Lighter gray for better contrast
    'background': '#1A1A1A',   # Slightly lighter background
    'surface': '#252525',      # More distinct from background
    'error': '#FF5252',        # Brighter red for better visibility
    'success': '#00E676',      # Kept the bright green
    'text': '#FFFFFF',         # White text
    'text_secondary': '#CCCCCC',  # Lighter gray text for better readability
    'bullying': '#FF1744',     # Bright red
    'normal': '#00E676',       # Bright green
    'highlight': '#673AB7',    # Lighter purple for highlighting
    'border': '#3D3D3D',       # Lighter border for better definition
    'hover': '#9C27B0',        # Brighter hover color
    'active': '#B39DDB',       # New color for active elements
    'disabled': '#757575',     # New distinct color for disabled elements
}

# Enhanced Fonts with better readability
FONTS = {
    'header': QFont('Segoe UI', 13, QFont.Bold),  # Slightly larger header
    'body': QFont('Segoe UI', 11),  # Slightly larger body text
    'button': QFont('Segoe UI', 11, QFont.Medium),  # Consistent with body
    'small': QFont('Segoe UI', 9)  # New option for smaller text
}

# Enhanced Button Style
BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['primary']};
        color: {COLORS['text']};
        border: none;
        padding: 12px 24px;
        border-radius: 6px;
        min-width: 120px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {COLORS['hover']};
    }}
    QPushButton:pressed {{
        background-color: {COLORS['active']};
        color: #121212;
    }}
    QPushButton:disabled {{
        background-color: {COLORS['disabled']};
        color: {COLORS['text_secondary']};
    }}
"""

# Enhanced Input Style
INPUT_STYLE = f"""
    QLineEdit {{
        padding: 14px;
        border: 2px solid {COLORS['border']};
        border-radius: 6px;
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        font-size: 14px;
        selection-background-color: {COLORS['primary']};
    }}
    QLineEdit:focus {{
        border: 2px solid {COLORS['primary']};
        background-color: #2A2A2A;
    }}
    QLineEdit::placeholder {{
        color: {COLORS['text_secondary']};
    }}
"""

# Enhanced Table Style
TABLE_STYLE = f"""
    QTableWidget {{
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        gridline-color: {COLORS['border']};
        outline: none;
        padding: 6px;
    }}
    QHeaderView::section {{
        background-color: #383838;
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        padding: 15px;
        font-weight: bold;
        font-size: 13px;
    }}
    QTableWidget::item {{
        padding: 13px;
        border: none;
        border-bottom: 1px solid {COLORS['border']};
    }}
    QTableWidget::item:selected {{
        background-color: {COLORS['primary']};
        color: {COLORS['text']};
    }}
    QTableWidget::item:hover:!selected {{
        background-color: #353535;
    }}
    QTableWidget QTableCornerButton::section {{
        background-color: #383838;
        border: 1px solid {COLORS['border']};
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS['secondary']};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLORS['primary']};
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 10px;
        margin: 2px;
    }}
    QScrollBar::handle:horizontal {{
        background: {COLORS['secondary']};
        border-radius: 5px;
        min-width: 30px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {COLORS['primary']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        border: none;
        background: none;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
    }}
"""

# New styles for additional elements

# Dropdown/Combo Box Style
COMBOBOX_STYLE = f"""
    QComboBox {{
        padding: 12px;
        border: 2px solid {COLORS['border']};
        border-radius: 6px;
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        min-width: 120px;
        font-size: 14px;
    }}
    QComboBox:hover {{
        border: 2px solid {COLORS['hover']};
    }}
    QComboBox:focus {{
        border: 2px solid {COLORS['primary']};
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 30px;
        border-left: none;
    }}
    QComboBox::down-arrow {{
        image: url(down_arrow.png);
        width: 14px;
        height: 14px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        selection-background-color: {COLORS['primary']};
        selection-color: {COLORS['text']};
    }}
"""

# Checkbox Style
CHECKBOX_STYLE = f"""
    QCheckBox {{
        spacing: 10px;
        color: {COLORS['text']};
    }}
    QCheckBox::indicator {{
        width: 20px;
        height: 20px;
        border-radius: 4px;
        border: 2px solid {COLORS['border']};
    }}
    QCheckBox::indicator:unchecked {{
        background-color: {COLORS['surface']};
    }}
    QCheckBox::indicator:unchecked:hover {{
        border: 2px solid {COLORS['hover']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {COLORS['primary']};
        border: 2px solid {COLORS['primary']};
        image: url(checkmark.png);
    }}
"""

# Label Style
LABEL_STYLE = f"""
    QLabel {{
        color: {COLORS['text']};
        font-size: 14px;
    }}
    QLabel[labelType="title"] {{
        font-size: 18px;
        font-weight: bold;
        color: {COLORS['text']};
    }}
    QLabel[labelType="subtitle"] {{
        font-size: 16px;
        color: {COLORS['text_secondary']};
    }}
    QLabel[labelType="error"] {{
        color: {COLORS['error']};
    }}
    QLabel[labelType="success"] {{
        color: {COLORS['success']};
    }}
"""