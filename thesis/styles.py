from PyQt5.QtGui import QColor, QFont

# Enhanced Color scheme (Dark Mode with better contrast)
COLORS = {
    'primary': '#00BCD4',      # Vibrant cyan (brand color)
    'secondary': '#A0A0A0',    # Muted gray for less emphasis
    'background': '#121212',   # Deep dark gray; reduces eye strain
    'surface': '#1E1E1E',      # Slightly lighter for depth
    'error': '#EF5350',        # Red for errors and warnings
    'warning': '#FFB74D',      # Orange for warnings and cautions
    'success': '#66BB6A',      # Green for success messages
    'text': '#E0E0E0',         # Light gray for readability
    'text_secondary': '#A0A0A0',  # Muted gray for less emphasis
    'bullying': '#EF5350',     # Error red
    'normal': '#66BB6A',       # Success green
    'highlight': '#00BCD4',    # Primary color for highlighting
    'border': '#2C2C2C',       # Subtle border color
    'hover': '#26C6DA',        # Lighter shade of accent for hover
    'active': '#00BCD4',       # Primary color for active elements
    'disabled': '#555555',     # Desaturated, low-contrast for disabled states
    # New color definitions for the three prediction levels
    'potentially_harmful': '#EF5350',  # Red - same as error
    'requires_attention': '#FF9800',   # Orange - slightly more vibrant than warning
    'likely_appropriate': '#66BB6A',   # Green - same as success
}

# Enhanced Fonts with better readability
FONTS = {
    'header': QFont('Segoe UI', 13, QFont.Bold),  # Slightly larger header
    'subheader': QFont('Segoe UI', 12, QFont.Bold),  # Medium header for section titles
    'body': QFont('Segoe UI', 11),  # Slightly larger body text
    'button': QFont('Segoe UI', 11, QFont.Medium),  # Consistent with body
    'small': QFont('Segoe UI', 9)  # New option for smaller text
}

# Enhanced Button Style
BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['primary']};
        color: {COLORS['background']};
        border: none;
        padding: 12px 24px;
        border-radius: 6px;
        min-width: 120px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {COLORS['hover']};
        color: black;
    }}
    QPushButton:pressed {{
        background-color: {COLORS['active']};
        color: {COLORS['background']};
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
        color: black;
    }}
    QTableWidget::item:hover:!selected {{
        background-color: {COLORS['hover']};
        color: black;
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
        max-width: 120px;
        font-size: 12px;
        text-align: left;
    }}
    QTabBar::tab:selected {{
        background: {COLORS['primary']};
        color: black;
    }}
    QTabBar::tab:hover:!selected {{
        background: {COLORS['hover']};
        color: black;
    }}
    QTabBar::close-button {{
        color: white;
        background: transparent;
        image: none;
        border: none;
        padding: 4px;
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
        /* border: 1px solid {COLORS['secondary']}; */ /* Removed border for cleaner look */
        border-radius: 4px;
        padding: 15px; /* Add some padding for internal spacing */
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
    color: {COLORS['text']};
    letter-spacing: 1px;
"""

WELCOME_SUBTITLE_STYLE = f"""
    font-size: 24px; 
    color: {COLORS['text']};
    letter-spacing: 0.5px;
"""

WELCOME_DESCRIPTION_STYLE = f"""
    font-size: 15px; 
    color: {COLORS['text_secondary']};
    letter-spacing: 0.2px;
"""

WELCOME_VERSION_STYLE = f"""
    color: {COLORS['text_secondary']}; 
    font-size: 18px;
"""

WELCOME_BACKGROUND_STYLE = f"background-color: {COLORS['background']};"

WELCOME_CONTAINER_STYLE = "background-color: transparent;"

WELCOME_TITLE_FONT = QFont('Segoe UI', 96)
WELCOME_TITLE_FONT.setBold(True)
WELCOME_TITLE_FONT.setStyle(QFont.StyleItalic)

WELCOME_TITLE_STYLE_DARK = f"""
    color: {COLORS['text']};
"""

WELCOME_SUBTITLE_FONT = QFont('Segoe UI', 24)

GET_STARTED_BUTTON_DARK_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['primary']};
        color: {COLORS['background']};
        border: none;
        padding: 12px 24px;
        border-radius: 4px;
        min-width: 150px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {COLORS['hover']};
    }}
"""

ABOUT_BUTTON_OUTLINE_STYLE = f"""
    QPushButton {{
        background-color: transparent;
        color: {COLORS['text']};
        border: 1px solid {COLORS['text']};
        padding: 12px 24px;
        border-radius: 4px;
        min-width: 100px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {COLORS['text']};
        color: {COLORS['background']};
    }}
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

# Shared component styles
SECTION_CONTAINER_STYLE = f"""
    QWidget {{
        background-color: {COLORS['background']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        padding: 12px;
    }}
"""

DETAILS_SECTION_STYLE = f"""
    QWidget {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 15px;
    }}
"""

TEXT_EDIT_STYLE = f"""
    QTextEdit {{
        background-color: {COLORS['background']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        padding: 12px;
        font-size: 14px;
    }}
    QTextEdit:focus {{
        border: 1px solid {COLORS['primary']};
    }}
"""

MENU_BAR_STYLE = f"""
    QWidget {{
        background-color: black;
        padding: 0px;
    }}
    QPushButton {{
        color: {COLORS['text']};
        background-color: transparent;
        border: none;
        padding: 8px 16px;
        font-size: 14px;
        min-width: 100px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['hover']};
    }}
"""

CHECKBOX_REPLY_STYLE = f"""
    QCheckBox {{
        color: {COLORS['text']};
        font-size: 13px;
        padding: 5px;
        margin-left: 5px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid {COLORS['border']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {COLORS['primary']};
        border: 2px solid {COLORS['primary']};
        image: url(check.png);
    }}
"""

# Row operation button style
ROW_OPERATION_BUTTON_STYLE = f"""
    {BUTTON_STYLE}
    QPushButton {{
        padding: 12px 20px;
        min-width: 140px;
    }}
"""