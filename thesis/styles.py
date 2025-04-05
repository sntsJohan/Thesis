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

# Table Style with better borders and hover effects
TABLE_STYLE = f"""
    QTableWidget {{
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        gridline-color: {COLORS['border']};
        outline: none;
        padding: 8px;
    }}
    QHeaderView::section {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        border: none;
        border-bottom: 2px solid {COLORS['border']};
        padding: 12px 16px;
        font-weight: bold;
        font-size: 13px;
    }}
    QHeaderView::section:vertical {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        border: none;
        border-right: 2px solid {COLORS['border']};
        padding: 12px;
    }}
    QTableCornerButton::section {{
        background-color: {COLORS['surface']};
        border: none;
        border-right: 2px solid {COLORS['border']};
        border-bottom: 2px solid {COLORS['border']};
    }}
    QTableWidget::item {{
        padding: 12px;
        border: none;
        border-bottom: 1px solid {COLORS['border']};
    }}
    QTableWidget::item:selected {{
        background-color: {COLORS['primary']};
        color: {COLORS['text']};
    }}
    QTableWidget::item:hover:!selected {{
        background-color: {COLORS['hover']};
        color: {COLORS['text']};
    }}
"""

# Add new tab styles
TAB_STYLE = f"""
    QTabWidget::pane {{
        border: 1px solid {COLORS['border']};
        background: {COLORS['surface']};
        border-radius: 8px;
    }}
    QTabBar::tab {{
        background: {COLORS['surface']};
        color: {COLORS['text']};
        padding: 8px 12px;
        border: 1px solid {COLORS['border']};
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        min-width: 80px;
    }}
    QTabBar::tab:selected {{
        background: {COLORS['primary']};
        color: {COLORS['text']};
    }}
    QTabBar::tab:hover:!selected {{
        background: {COLORS['hover']};
    }}
    QTabBar::close-button {{
        image: url(assets/close.png);
        subcontrol-position: right;
        subcontrol-origin: padding;
        margin-right: 4px;
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

# Dialog and Message Box Style
DIALOG_STYLE = f"""
    QDialog {{
        background-color: {COLORS['background']};
        color: {COLORS['text']};
    }}
    QPushButton {{
        {BUTTON_STYLE}
        min-width: 100px;
    }}
"""

# Image Label Style
IMAGE_LABEL_STYLE = f"""
    QLabel {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        padding: 10px;
        border-radius: 4px;
    }}
"""

# Loading Overlay Style
LOADING_OVERLAY_STYLE = f"""
    QWidget {{
        background-color: rgba(0, 0, 0, 0.5);
        border-radius: 8px;
    }}
"""

# Container Styles
CONTAINER_STYLE = f"""
    QWidget {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['secondary']};
        border-radius: 4px;
    }}
"""

TITLELESS_CONTAINER_STYLE = f"""
    QWidget {{
        background-color: {COLORS['surface']};
        border: none;
    }}
"""

# Alternative Table Style with alternating row colors
TABLE_ALTERNATE_STYLE = f"""
    {TABLE_STYLE}
    QTableWidget::item:alternate {{
        background-color: {COLORS['surface']};
    }}
    QTableWidget::item {{
        background-color: {COLORS['background']};
    }}
    QTableWidget::item:selected {{
        background-color: {COLORS['primary']};
    }}
"""

# Welcome Screen Styles
WELCOME_TITLE_STYLE = f"""
    font-size: 42px; 
    color: {COLORS['primary']};
    letter-spacing: 1px;
"""

WELCOME_SUBTITLE_STYLE = f"""
    font-size: 24px; 
    color: {COLORS['text']};
    letter-spacing: 0.5px;
"""

WELCOME_DESCRIPTION_STYLE = f"""
    font-size: 15px; 
    color: {COLORS['secondary']};
    letter-spacing: 0.2px;
"""

WELCOME_VERSION_STYLE = f"""
    color: {COLORS['secondary']}; 
    font-size: 18px;
    opacity: 0.8;
"""

WELCOME_BACKGROUND_STYLE = f"background-color: {COLORS['primary']};"

WELCOME_CONTAINER_STYLE = "background-color: transparent;"

WELCOME_TITLE_FONT = QFont('Times New Roman', 96)
WELCOME_TITLE_FONT.setBold(True)
WELCOME_TITLE_FONT.setStyle(QFont.StyleItalic)

WELCOME_TITLE_STYLE_DARK = """
    color: #222222;
"""

WELCOME_SUBTITLE_FONT = QFont('Segoe UI', 24)

GET_STARTED_BUTTON_DARK_STYLE = """
    QPushButton {
        background-color: #222222;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 4px;
        min-width: 150px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #333333;
    }
"""

ABOUT_BUTTON_OUTLINE_STYLE = """
    QPushButton {
        background-color: transparent;
        color: #222222;
        border: 1px solid #222222;
        padding: 12px 24px;
        border-radius: 4px;
        min-width: 100px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: rgba(34, 34, 34, 0.1);
    }
"""

DETAIL_TEXT_SPAN_STYLE = "font-size: 16px;"

# Header Title Style
HEADER_STYLE = f"""
    font-size: 15px;
    color: {COLORS['text']};
    padding: 0px;
"""

# Enhanced Details Panel Style
DETAIL_TEXT_STYLE = f"""
    QTextEdit {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 12px;
        font-size: 14px;
        selection-background-color: {COLORS['primary']};
    }}
    QTextEdit:focus {{
        border: 1px solid {COLORS['primary']};
    }}
"""

# Disabled Button Style
BUTTON_DISABLED_STYLE = f"""
    {BUTTON_STYLE}
    QPushButton:disabled {{
        background-color: {COLORS['surface']};
        color: {COLORS['secondary']};
        border: 1px solid {COLORS['secondary']};
        opacity: 0.7;
    }}
"""

# Get Started Button Style
GET_STARTED_BUTTON_STYLE = f"""
    {BUTTON_STYLE}
    padding: 12px 30px;
    font-size: 16px;
    border-radius: 6px;
"""

# about Button Style
ABOUT_BUTTON_STYLE = f"""
    {BUTTON_STYLE}
    padding: 12px 30px;
    font-size: 16px;
    border-radius: 6px;
"""

# Tag Style for rules in details panel
TAG_STYLE = f"""
    font-size: 16px; 
    background-color: {COLORS['secondary']}; 
    border-radius: 4px; 
    padding: 2px 4px; 
    margin: 2px; 
    display: inline-block;
"""