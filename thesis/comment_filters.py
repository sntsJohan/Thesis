from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QCheckBox, QPushButton, QSlider, QSpinBox,
                              QGroupBox, QMessageBox, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPainter, QColor
from styles import (COLORS, FONTS, BUTTON_STYLE, DIALOG_STYLE, 
                   CHECKBOX_REPLY_STYLE, INPUT_STYLE)
import os

class CommentFiltersDialog(QDialog):
    """Dialog for configuring Facebook comments scraper filters"""
    
    # Signal to emit when filter settings are updated
    filtersUpdated = pyqtSignal(dict)
    
    def __init__(self, current_filters=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Comment Filters")
        self.setStyleSheet(DIALOG_STYLE)
        self.setMinimumWidth(500)
        self.setMinimumHeight(450)
        
        # Set window icon
        base_path = os.path.dirname(os.path.abspath(__file__))
        app_icon = QIcon(os.path.join(base_path, "assets", "applogo.png"))
        self.setWindowIcon(app_icon)
        
        # Initialize with default filters if none provided
        self.filters = current_filters or {
            "includeReplies": True,
            "maxComments": 50,
            "minWordCount": 3,
            "excludeLinks": True,
            "excludeEmojisOnly": True
        }
        
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Custom style for group boxes without borders
        groupbox_style = f"""
            QGroupBox {{
                color: {COLORS['text']};
                font-weight: bold;
                font-size: 14px;
                margin-top: 12px;
                border: none;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }}
        """
        
        # Comments Scope Section
        scope_group = QGroupBox("Comments Options")
        scope_group.setStyleSheet(groupbox_style)
        scope_layout = QVBoxLayout(scope_group)
        scope_layout.setSpacing(15)
        scope_layout.setContentsMargins(10, 20, 10, 10)
        
        # Larger checkbox style
        larger_checkbox_style = f"""
            QCheckBox {{
                color: {COLORS['text']};
                spacing: 10px;
                font-size: 13px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {COLORS['border']};
                border-radius: 4px;
                background-color: {COLORS['surface']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['highlight']};
                border: 2px solid {COLORS['highlight']};
                image: url(checkmark.png);
            }}
        """
        
        # Include Replies checkbox
        self.include_replies = QCheckBox("Include Replies")
        self.include_replies.setStyleSheet(larger_checkbox_style)
        self.include_replies.setChecked(self.filters.get("includeReplies", True))
        scope_layout.addWidget(self.include_replies)
        
        # Exclude links checkbox
        self.exclude_links = QCheckBox("Exclude Comments with Links")
        self.exclude_links.setStyleSheet(larger_checkbox_style)
        self.exclude_links.setChecked(self.filters.get("excludeLinks", True))
        scope_layout.addWidget(self.exclude_links)
        
        # Exclude emoji-only comments
        self.exclude_emojis = QCheckBox("Exclude Emoji-only Comments")
        self.exclude_emojis.setStyleSheet(larger_checkbox_style)
        self.exclude_emojis.setChecked(self.filters.get("excludeEmojisOnly", True))
        scope_layout.addWidget(self.exclude_emojis)
        
        # Minimum word count
        min_word_layout = QHBoxLayout()
        min_word_label = QLabel("Minimum Word Count:")
        min_word_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px;")
        
        self.min_word_spin = QSpinBox()
        self.min_word_spin.setMinimum(1)
        self.min_word_spin.setMaximum(10)
        self.min_word_spin.setValue(self.filters.get("minWordCount", 3))
        self.min_word_spin.setStyleSheet(INPUT_STYLE + "font-size: 13px; padding: 5px;")
        self.min_word_spin.setFixedWidth(80)
        
        min_word_layout.addWidget(min_word_label)
        min_word_layout.addWidget(self.min_word_spin)
        min_word_layout.addStretch()
        scope_layout.addLayout(min_word_layout)
        
        # Comments Limit Section
        limit_group = QGroupBox("Maximum Comments")
        limit_group.setStyleSheet(groupbox_style)
        limit_layout = QVBoxLayout(limit_group)
        limit_layout.setSpacing(15)
        limit_layout.setContentsMargins(10, 20, 10, 10)
        
        # Label to show current value
        slider_value_layout = QHBoxLayout()
        slider_value_label = QLabel("Number of comments to scrape:")
        slider_value_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px;")
        slider_value_layout.addWidget(slider_value_label)
        slider_value_layout.addStretch()
        limit_layout.addLayout(slider_value_layout)
        
        # Max comments slider with spin box
        limit_control_layout = QHBoxLayout()
        
        self.max_comments_slider = QSlider(Qt.Horizontal)
        self.max_comments_slider.setMinimum(10)
        self.max_comments_slider.setMaximum(500)
        self.max_comments_slider.setValue(self.filters.get("maxComments", 50))
        # Add ticks to slider
        self.max_comments_slider.setTickPosition(QSlider.TicksBelow)
        self.max_comments_slider.setTickInterval(50)
        self.max_comments_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {COLORS['border']};
                height: 8px;
                background: {COLORS['surface']};
                margin: 0 0;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['highlight']};
                border: 1px solid {COLORS['highlight']};
                width: 22px;
                height: 22px;
                margin: -8px 0;
                border-radius: 11px;
            }}
            QSlider::sub-page:horizontal {{
                background: {COLORS['highlight']};
                border-radius: 4px;
            }}
            QSlider::tick-mark:horizontal {{
                color: {COLORS['text']};
                width: 1px;
                height: 5px;
                margin-top: 5px;
                background: {COLORS['text_secondary']};
            }}
        """)
        
        self.max_comments_spin = QSpinBox()
        self.max_comments_spin.setMinimum(10)
        self.max_comments_spin.setMaximum(500)
        self.max_comments_spin.setValue(self.filters.get("maxComments", 50))
        self.max_comments_spin.setStyleSheet(INPUT_STYLE + "font-size: 13px; padding: 5px;")
        self.max_comments_spin.setFixedWidth(80)
        
        # Connect the controls
        self.max_comments_slider.valueChanged.connect(self.max_comments_spin.setValue)
        self.max_comments_spin.valueChanged.connect(self.max_comments_slider.setValue)
        self.max_comments_spin.valueChanged.connect(self.check_warning)
        
        limit_control_layout.addWidget(self.max_comments_slider, 4)
        limit_control_layout.addWidget(self.max_comments_spin, 1)
        limit_layout.addLayout(limit_control_layout)
        
        # Create a custom widget to hold tick marks and labels in the correct position
        class TickLabelWidget(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setMinimumHeight(25)
                
            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                
                # Get the width of the widget (should match slider width)
                width = self.width()
                
                # Draw tick labels at specific positions
                # The slider range is 10 to 500, with ticks at 10, 50, 100, 150, 200, ..., 500
                # We need to calculate the relative position on the widget width
                min_val = 10
                max_val = 500
                range_val = max_val - min_val
                
                tick_values = [10, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
                
                painter.setPen(QColor(COLORS['text_secondary']))
                font = painter.font()
                font.setPointSize(9)
                painter.setFont(font)
                
                for val in tick_values:
                    # Calculate x position
                    x_pos = ((val - min_val) / range_val) * (width - 20) + 10  # 10px offset on each side
                    
                    # Draw tick label
                    painter.drawText(int(x_pos - 10), 10, 20, 15, Qt.AlignCenter, str(val))
        
        # Add the custom tick label widget
        tick_label_widget = TickLabelWidget()
        limit_layout.addWidget(tick_label_widget)
        
        # Warning label
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet(f"color: {COLORS['warning']}; font-style: italic; font-size: 12px;")
        self.warning_label.setWordWrap(True)
        limit_layout.addWidget(self.warning_label)
        
        # Initial warning check
        self.check_warning(self.max_comments_spin.value())
        
        # Add all sections to main layout
        main_layout.addWidget(scope_group)
        main_layout.addWidget(limit_group)
        main_layout.addStretch(1)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.setStyleSheet(BUTTON_STYLE + "font-size: 13px;")
        self.reset_button.setMinimumHeight(40)
        self.reset_button.clicked.connect(self.reset_to_defaults)
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.setStyleSheet(BUTTON_STYLE + "font-size: 13px;")
        self.save_button.setMinimumHeight(40)
        self.save_button.clicked.connect(self.save_settings)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
    
    def check_warning(self, value):
        """Show a warning if the number of comments is high"""
        if value > 100:
            self.warning_label.setText("Warning: Scraping a large number of comments may take a long time.")
        else:
            self.warning_label.setText("")
    
    def reset_to_defaults(self):
        """Reset all filters to default values"""
        default_filters = {
            "includeReplies": True,
            "maxComments": 50,
            "minWordCount": 3,
            "excludeLinks": True,
            "excludeEmojisOnly": True
        }
        
        # Update UI
        self.include_replies.setChecked(default_filters["includeReplies"])
        self.max_comments_slider.setValue(default_filters["maxComments"])
        self.max_comments_spin.setValue(default_filters["maxComments"])
        self.min_word_spin.setValue(default_filters["minWordCount"])
        self.exclude_links.setChecked(default_filters["excludeLinks"])
        self.exclude_emojis.setChecked(default_filters["excludeEmojisOnly"])
        
        # Clear any warnings
        self.check_warning(default_filters["maxComments"])
    
    def save_settings(self):
        """Save the current settings and close the dialog"""
        # Get values from UI components
        self.filters["includeReplies"] = self.include_replies.isChecked()
        self.filters["maxComments"] = self.max_comments_spin.value()
        self.filters["resultsLimit"] = self.max_comments_spin.value()  # Keep this for scraper compatibility
        self.filters["minWordCount"] = self.min_word_spin.value()
        self.filters["excludeLinks"] = self.exclude_links.isChecked()
        self.filters["excludeEmojisOnly"] = self.exclude_emojis.isChecked()
        
        # Set default Apify-compatible settings (hidden from user)
        self.filters["viewOption"] = "RANKED_UNFILTERED"
        self.filters["timelineOption"] = "CHRONOLOGICAL"
        self.filters["filterPostsByLanguage"] = False
        
        # If it's a large number, show a confirmation
        if self.filters["maxComments"] > 100:
            confirm = QMessageBox.question(
                self,
                "Confirm Settings",
                f"You've set the maximum comments to {self.filters['maxComments']}. This may take a long time to scrape.\n\nDo you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return  # Don't close if the user cancels
        
        # Emit the signal with the updated filters
        self.filtersUpdated.emit(self.filters)
        
        # Close the dialog
        self.accept()
