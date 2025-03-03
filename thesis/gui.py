from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QTextEdit, QWidget, 
                           QFileDialog, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QSplitter, QGridLayout, QComboBox, QSizePolicy, QStackedWidget, QFrame, QTabWidget, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QTextCursor  
from scraper import scrape_comments
from model import classify_comment
import pandas as pd
from utils import display_message
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE, TABLE_STYLE
import tempfile
import time
from PyQt5.QtWidgets import QApplication
from comment_operations import generate_report

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_comments = [] 
        self.setWindowTitle("Cyber Boolean")
        self.showFullScreen()  # Makes the window fullscreen
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")

        self.central_widget = QStackedWidget()  
        self.setCentralWidget(self.central_widget)

        self.init_welcome_screen()
        self.init_main_ui()

        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self)

    def init_welcome_screen(self):
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setSpacing(0)  # We'll control spacing manually for better hierarchy
        welcome_layout.setContentsMargins(40, 0, 40, 0)  # Remove top/bottom margins

        # Add stretch to push content down from top
        welcome_layout.addStretch(1)

        # Header container for visual grouping
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setSpacing(15)  # Consistent spacing between header elements
        header_layout.setContentsMargins(0, 0, 0, 0)

        # App title - largest and most prominent
        title_label = QLabel("Cyber Boolean")
        title_label.setFont(FONTS['header'])
        title_label.setStyleSheet(f"""
            font-size: 42px; 
            color: {COLORS['primary']};
            letter-spacing: 1px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)

        # Subtitle - secondary emphasis
        subtitle_label = QLabel("Cyberbullying Detection System")
        subtitle_label.setFont(FONTS['header'])
        subtitle_label.setStyleSheet(f"""
            font-size: 18px; 
            color: {COLORS['text']};
            letter-spacing: 0.5px;
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)

        welcome_layout.addWidget(header_container)
        welcome_layout.addSpacing(40)  # Significant space between header and description

        # Description - tertiary emphasis
        description = QLabel(
            "Detect and analyze cyberbullying in online comments"
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet(f"""
            font-size: 15px; 
            color: {COLORS['secondary']};
            letter-spacing: 0.2px;
        """)
        welcome_layout.addWidget(description)
        
        welcome_layout.addSpacing(50)  # Large space before call to action

        # Get started button - clear call to action
        get_started_button = QPushButton("Get Started")
        get_started_button.setFont(FONTS['button'])
        get_started_button.setStyleSheet(f"""
            {BUTTON_STYLE}
            padding: 12px 30px;
            font-size: 16px;
            border-radius: 6px;
        """)
        get_started_button.setFixedWidth(200)
        get_started_button.clicked.connect(self.show_main_ui)
        welcome_layout.addWidget(get_started_button, alignment=Qt.AlignCenter)

        # Add stretch to push content up from bottom
        welcome_layout.addStretch(1)
        
        # Version info - smallest emphasis
        version_label = QLabel("Version 1.0")
        version_label.setAlignment(Qt.AlignRight)
        version_label.setStyleSheet(f"""
            color: {COLORS['secondary']}; 
            font-size: 12px;
            opacity: 0.8;
        """)
        welcome_layout.addWidget(version_label)

        self.central_widget.addWidget(welcome_widget)

    def show_main_ui(self):
        self.central_widget.setCurrentIndex(1)

    def init_main_ui(self):
        main_widget = QWidget()
        self.central_widget.addWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.init_ui()

    def init_ui(self):
        # Input Container
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(10)
        input_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = QLabel("Cyberbullying Detection System")
        title.setFont(FONTS['header'])
        title.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(title)

        # Create horizontal layout for input sections
        input_sections = QHBoxLayout()
        input_sections.setSpacing(20)  # Space between sections

        # Facebook Post Section
        fb_section = QWidget()
        fb_section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['secondary']};
                border-radius: 4px;
                padding: 10px;
            }}
        """)
        fb_layout = QVBoxLayout(fb_section)
        fb_layout.setSpacing(10)
        
        fb_title = QLabel("Facebook Post")
        fb_title.setFont(FONTS['header'])
        fb_title.setAlignment(Qt.AlignCenter)
        self.url_input = QLineEdit()
        self.url_input.setStyleSheet(INPUT_STYLE)
        self.url_input.setPlaceholderText("Enter Facebook Post URL")
        self.scrape_button = QPushButton("Scrape and Classify Comments")
        self.scrape_button.setFont(FONTS['button'])
        self.scrape_button.setStyleSheet(BUTTON_STYLE)
        self.scrape_button.clicked.connect(self.scrape_comments)
        
        fb_layout.addWidget(fb_title)
        fb_layout.addWidget(self.url_input)
        fb_layout.addWidget(self.scrape_button)
        input_sections.addWidget(fb_section)

        # CSV File Section
        csv_section = QWidget()
        csv_section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['secondary']};
                border-radius: 4px;
                padding: 10px;
            }}
        """)
        csv_layout = QVBoxLayout(csv_section)
        csv_layout.setSpacing(10)
        
        csv_title = QLabel("CSV File")
        csv_title.setFont(FONTS['header'])
        csv_title.setAlignment(Qt.AlignCenter)
        self.file_input = QLineEdit()
        self.file_input.setStyleSheet(INPUT_STYLE)
        self.file_input.setPlaceholderText("Select CSV file")
        browse_layout = QHBoxLayout()
        self.browse_button = QPushButton("Browse")
        self.browse_button.setFont(FONTS['button'])
        self.browse_button.setStyleSheet(BUTTON_STYLE)
        self.browse_button.clicked.connect(self.browse_file)
        self.process_csv_button = QPushButton("Process CSV")
        self.process_csv_button.setFont(FONTS['button'])
        self.process_csv_button.setStyleSheet(BUTTON_STYLE)
        self.process_csv_button.clicked.connect(self.process_csv)
        browse_layout.addWidget(self.browse_button)
        browse_layout.addWidget(self.process_csv_button)
        
        csv_layout.addWidget(csv_title)
        csv_layout.addWidget(self.file_input)
        csv_layout.addLayout(browse_layout)
        input_sections.addWidget(csv_section)

        # Direct Input Section
        direct_section = QWidget()
        direct_section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['secondary']};
                border-radius: 4px;
                padding: 10px;
            }}
        """)
        direct_layout = QVBoxLayout(direct_section)
        direct_layout.setSpacing(10)
        
        direct_title = QLabel("Direct Input")
        direct_title.setFont(FONTS['header'])
        direct_title.setAlignment(Qt.AlignCenter)
        self.text_input = QLineEdit()
        self.text_input.setStyleSheet(INPUT_STYLE)
        self.text_input.setPlaceholderText("Enter comment to analyze")
        self.analyze_button = QPushButton("Analyze Comment")
        self.analyze_button.setFont(FONTS['button'])
        self.analyze_button.setStyleSheet(BUTTON_STYLE)
        self.analyze_button.clicked.connect(self.analyze_single)
        
        direct_layout.addWidget(direct_title)
        direct_layout.addWidget(self.text_input)
        direct_layout.addWidget(self.analyze_button)
        input_sections.addWidget(direct_section)

        # Add input sections to main layout
        input_layout.addLayout(input_sections)
        self.layout.addWidget(input_container)

        # Create a horizontal splitter for table and details
        splitter = QSplitter(Qt.Horizontal) 

        # Table Container
        table_container = QWidget()
        table_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['secondary']};
                background: {COLORS['surface']};
            }}
            QTabBar::tab {{
                background: {COLORS['surface']};
                color: {COLORS['text']};
                padding: 8px 12px;
                border: 1px solid {COLORS['secondary']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['primary']};
                color: {COLORS['text']};
            }}
        """)

        # Initial message widget
        self.initial_message = QLabel("No analysis performed yet.\nResults will appear here.")
        self.initial_message.setAlignment(Qt.AlignCenter)
        self.initial_message.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px;")
        table_layout.addWidget(self.initial_message)
        
        table_layout.addWidget(self.tab_widget)
        self.tab_widget.hide()  # Hide tab widget initially

        # Initialize tab counters
        self.csv_tab_count = 1
        self.url_tab_count = 1
        
        # Dictionary to store tab references
        self.tabs = {}

        splitter.addWidget(table_container)

        # Details Panel
        details_container = QWidget()
        details_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  
        details_layout = QVBoxLayout(details_container)
        details_layout.setContentsMargins(10, 0, 0, 0) 

        # Create a container for title + details
        details_section = QWidget()
        details_section_layout = QVBoxLayout(details_section)
        details_section_layout.setSpacing(5) 
        details_section_layout.setContentsMargins(10, 10, 10, 10)

        # Add title inside the same section
        details_title = QLabel("Comment Details")
        details_title.setFont(FONTS['header'])
        details_section_layout.addWidget(details_title)

        # Details content (kept inside same layout)
        details_widget = QWidget()
        details_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['secondary']};
                border-radius: 4px;
            }}
        """)
        details_widget_layout = QVBoxLayout(details_widget)
        details_widget_layout.setSpacing(10)

        # Add text edit for details
        self.details_text_edit = QTextEdit()
        self.details_text_edit.setReadOnly(True)
        self.details_text_edit.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px;") 
        details_widget_layout.addWidget(self.details_text_edit)

        # Add details_widget inside details_section
        details_section_layout.addWidget(details_widget)

        # Add the combined section to the details panel
        details_layout.addWidget(details_section)

        # Operations Buttons inside details
        self.show_summary_button = QPushButton("📊 Show Summary")
        self.add_remove_button = QPushButton("➕ Add to List")
        self.export_selected_button = QPushButton("💾 Export List")
        self.export_all_button = QPushButton("📤 Export All Results")
        self.generate_report_button = QPushButton("📝 Generate Report")

        # Add buttons to a grid layout
        buttons_widget = QWidget()
        buttons_layout = QGridLayout(buttons_widget)
        buttons_layout.setSpacing(10) 

        buttons = [
            self.show_summary_button, 
            self.add_remove_button, 
            self.export_selected_button, 
            self.export_all_button,
            self.generate_report_button
        ]
        
        for i, btn in enumerate(buttons):
            btn.setStyleSheet(BUTTON_STYLE)
            btn.setFont(FONTS['button'])
            buttons_layout.addWidget(btn, i // 2, i % 2)
            btn.hide()

        # Connect buttons
        self.show_summary_button.clicked.connect(self.show_summary)
        self.add_remove_button.clicked.connect(self.toggle_list_status)
        self.export_selected_button.clicked.connect(self.export_selected)
        self.export_all_button.clicked.connect(self.export_all)
        self.generate_report_button.clicked.connect(lambda: generate_report(self))

        # Add buttons widget to details layout
        details_layout.addWidget(buttons_widget)
        splitter.addWidget(details_container)

        # Set initial sizes for the splitter to make them equal
        splitter.setSizes([self.width() // 2, self.width() // 2]) 
        splitter.setStretchFactor(0, 1) 
        splitter.setStretchFactor(1, 1)

        # Add splitter to main layout
        self.layout.addWidget(splitter)

        # Set layout stretch factors
        self.layout.setStretch(0, 0)  
        self.layout.setStretch(1, 1) 

    def show_loading(self, show=True):
        if show:
            self.loading_overlay.show()
        else:
            self.loading_overlay.hide()

    def scrape_comments(self):
        url = self.url_input.text()
        if not url:
            display_message(self, "Error", "Please enter a URL.")
            return

        try:
            self.show_loading(True)  # Show loading overlay
            QApplication.processEvents()  # Ensure the UI updates
            
            from scraper import scrape_comments
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
                temp_path = temp_file.name
            scrape_comments(url, temp_path)
            df = pd.read_csv(temp_path)
            
            # Store additional comment metadata
            self.comment_metadata = {}
            for _, row in df.iterrows():
                self.comment_metadata[row['Text']] = {
                    'profile_name': row['Profile Name'],
                    'profile_picture': row['Profile Picture'],
                    'date': row['Date'],
                    'likes_count': row['Likes Count'],
                    'profile_id': row['Profile ID']
                }
            
            comments = df['Text'].tolist()
            self.populate_table(comments)
        except Exception as e:
            display_message(self, "Error", f"Error scraping comments: {e}")
        finally:
            self.show_loading(False)  # Hide loading overlay

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.file_input.setText(file_path)

    def process_csv(self):
        if not self.file_input.text():
            display_message(self, "Error", "Please select a CSV file first")
            return
        try:
            self.show_loading(True)  # Show loading overlay
            QApplication.processEvents()  # Ensure the UI updates
            
            df = pd.read_csv(self.file_input.text())
            comments = df.iloc[:, 0].tolist()
            
            # Create metadata for CSV comments
            self.comment_metadata = {}
            for comment in comments:
                self.comment_metadata[comment] = {
                    'profile_name': 'CSV Input',
                    'profile_picture': '',
                    'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'likes_count': 'N/A',
                    'profile_id': 'N/A'
                }
            
            self.populate_table(comments)
        except Exception as e:
            display_message(self, "Error", f"Error reading CSV file: {e}")
        finally:
            self.show_loading(False)  # Hide loading overlay

    def analyze_single(self):
        if not self.text_input.text():
            display_message(self, "Error", "Please enter a comment to analyze")
            return
        
        try:
            self.show_loading(True)  # Show loading overlay
            QApplication.processEvents()  # Ensure the UI updates
            
            # Create metadata for the direct input comment
            comment = self.text_input.text()
            self.comment_metadata = {
                comment: {
                    'profile_name': 'Direct Input',
                    'profile_picture': '',
                    'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'likes_count': 'N/A',
                    'profile_id': 'N/A'
                }
            }
            
            self.populate_table([comment])
        finally:
            self.show_loading(False)  # Hide loading overlay

    def create_empty_tab(self, tab_type):
        """Create a new empty tab with table"""
        if tab_type == "Direct Inputs" and "Direct Inputs" in self.tabs:
            # Return existing Direct Inputs table
            return self.tabs["Direct Inputs"].findChild(QTableWidget)

        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        
        # Header layout with table title and sort dropdown
        sort_layout = QHBoxLayout()
        table_title = QLabel("Comments")
        table_title.setFont(FONTS['header'])
        sort_layout.addWidget(table_title)
        sort_layout.addStretch()
        
        sort_combo = QComboBox()
        sort_combo.addItems([
            "Sort by Comments (A-Z)",
            "Sort by Comments (Z-A)",
            "Sort by Prediction (A-Z)",
            "Sort by Confidence (High to Low)",
            "Sort by Confidence (Low to High)"
        ])
        sort_layout.addWidget(sort_combo)
        tab_layout.addLayout(sort_layout)

        # Create table
        table = QTableWidget()
        table.setSortingEnabled(True)
        table.setStyleSheet(TABLE_STYLE)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Comment", "Prediction", "Confidence"])

        # Adjust column sizes
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        table.setColumnWidth(1, 150)
        table.setColumnWidth(2, 100)

        table.setWordWrap(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.itemSelectionChanged.connect(self.update_details_panel)
        
        # Store sort combo and connect it
        table.sort_combo = sort_combo
        sort_combo.currentIndexChanged.connect(lambda: self.sort_table(table))
        
        tab_layout.addWidget(table)
        
        # Add tab to widget and store reference
        self.tab_widget.addTab(tab, tab_type)
        self.tabs[tab_type] = tab
        
        # Show tab widget and hide initial message when first tab is created
        if self.tab_widget.isHidden():
            self.initial_message.hide()
            self.tab_widget.show()
            
        return table

    def get_current_table(self):
        """Get the table widget from the current tab"""
        current_tab = self.tab_widget.currentWidget()
        return current_tab.findChild(QTableWidget)

    def populate_table(self, comments):
        """Create new tab and populate it based on input type"""
        # Store the input source before clearing
        file_path = self.file_input.text()
        url = self.url_input.text()

        # Clear inputs after checking
        self.file_input.clear()
        self.url_input.clear()

        if len(comments) == 1:  # Direct input
            tab_name = "Direct Inputs"
        elif file_path:  # CSV input
            # Get filename without path and extension
            file_name = file_path.split('/')[-1].split('\\')[-1]  # Handle both Unix and Windows paths
            file_name = file_name.rsplit('.', 1)[0]  # Remove extension
            
            # Truncate if longer than 20 characters
            if len(file_name) > 20:
                file_name = file_name[:17] + "..."
            
            # Check if tab with this name already exists
            if file_name in self.tabs:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Question)
                msg.setWindowTitle("Duplicate File Name")
                msg.setText(f"A tab with name '{file_name}' already exists.")
                msg.setInformativeText("Do you want to replace the existing tab or create a new one?")
                replace_button = msg.addButton("Replace", QMessageBox.YesRole)
                new_tab_button = msg.addButton("Create New", QMessageBox.NoRole)
                msg.addButton("Cancel", QMessageBox.RejectRole)
                
                msg.exec_()
                
                if msg.clickedButton() == replace_button:
                    # Remove existing tab
                    old_tab_index = self.tab_widget.indexOf(self.tabs[file_name])
                    self.tab_widget.removeTab(old_tab_index)
                    del self.tabs[file_name]
                    tab_name = file_name
                elif msg.clickedButton() == new_tab_button:
                    # Find next available number
                    counter = 2
                    while f"{file_name} ({counter})" in self.tabs:
                        counter += 1
                    tab_name = f"{file_name} ({counter})"
                else:
                    # User clicked Cancel
                    return
            else:
                tab_name = file_name
                
        elif url:  # Facebook post
            tab_name = f"Facebook Post {self.url_tab_count}"
            self.url_tab_count += 1
        else:  # Fallback case
            tab_name = f"Analysis {self.csv_tab_count + self.url_tab_count}"

        # Create new tab and get its table
        table = self.create_empty_tab(tab_name)
        
        for comment in comments:
            prediction, confidence = classify_comment(comment)
            row_position = table.rowCount()
            table.insertRow(row_position)

            comment_item = QTableWidgetItem(comment)
            comment_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            prediction_item = QTableWidgetItem(prediction)
            prediction_item.setTextAlignment(Qt.AlignCenter)
            if prediction == "Cyberbullying":
                prediction_item.setForeground(QColor(COLORS['bullying']))
            else:
                prediction_item.setForeground(QColor(COLORS['normal']))

            confidence_item = QTableWidgetItem(f"{confidence:.2%}")
            confidence_item.setTextAlignment(Qt.AlignCenter)

            table.setItem(row_position, 0, comment_item)
            table.setItem(row_position, 1, prediction_item)
            table.setItem(row_position, 2, confidence_item)

            table.resizeRowToContents(row_position)

            if comment in self.selected_comments:
                for col in range(table.columnCount()):
                    table.item(row_position, col).setBackground(QColor(COLORS['highlight']))

        # Switch to the new tab
        tab_index = self.tab_widget.indexOf(self.tabs[tab_name])
        self.tab_widget.setCurrentIndex(tab_index)

    def sort_table(self, table):
        """Sort the specified table based on its combo box selection"""
        sort_combo = table.sort_combo
        index = sort_combo.currentIndex()
        if index == 0:
            table.sortItems(0, Qt.AscendingOrder)
        elif index == 1:
            table.sortItems(0, Qt.DescendingOrder)
        elif index == 2:
            table.sortItems(1, Qt.AscendingOrder)
        elif index == 3:
            table.sortItems(2, Qt.DescendingOrder)
        elif index == 4:
            table.sortItems(2, Qt.AscendingOrder)

    def update_details_panel(self):
        selected_items = self.get_current_table().selectedItems()
        if not selected_items:
            self.details_text_edit.clear()
            # Hide operation buttons
            for btn in [self.show_summary_button, self.add_remove_button, self.export_selected_button, self.export_all_button, self.generate_report_button]:
                btn.hide()
            return

        row = selected_items[0].row()
        comment = self.get_current_table().item(row, 0).text()
        prediction = self.get_current_table().item(row, 1).text()
        confidence = self.get_current_table().item(row, 2).text()
        
        # Get metadata for the comment if available
        metadata = self.comment_metadata.get(comment, {
            'profile_name': 'N/A',
            'profile_picture': '',
            'date': 'N/A',
            'likes_count': 'N/A',
            'profile_id': 'N/A'
        })
        
        commenter = metadata.get('profile_name', 'N/A')
        date = metadata.get('date', 'N/A')
        likes = metadata.get('likes_count', 'N/A')

        # Show all operation buttons
        for btn in [self.show_summary_button, self.add_remove_button, 
                   self.export_selected_button, self.export_all_button,
                   self.generate_report_button]:
            btn.show()

        # Update add/remove button text based on list status
        if comment in self.selected_comments:
            self.add_remove_button.setText("➖ Remove from List")
        else:
            self.add_remove_button.setText("➕ Add to List")

        # Rules text
        rules_broken = ["Harassment", "Hate Speech", "Threatening Language"] if prediction == "Cyberbullying" else []

        # Set text contents with additional metadata
        self.details_text_edit.clear()
        self.details_text_edit.append(f"<b>Comment:</b>\n{comment}\n")
        self.details_text_edit.append(f"<b>Commenter:</b> {commenter}\n")
        self.details_text_edit.append(f"<b>Date:</b> {date}\n")
        self.details_text_edit.append(f"<b>Likes:</b> {likes}\n")
        self.details_text_edit.append(f"<b>Classification:</b> {prediction}\n")
        self.details_text_edit.append(f"<b>Confidence:</b> {confidence}\n")
        self.details_text_edit.append(f"<b>Status:</b> {'In List' if comment in self.selected_comments else 'Not in List'}\n")
        self.details_text_edit.append("<b>Rules Broken:</b>")

        cursor = self.details_text_edit.textCursor()
        for rule in rules_broken:
            cursor.insertHtml(f'<span style="background-color: {COLORS["secondary"]}; border-radius: 4px; padding: 2px 4px; margin: 2px; display: inline-block;">{rule}</span> ')
        self.details_text_edit.setTextCursor(cursor)

    def show_summary(self):
        total_comments = self.get_current_table().rowCount()
        if total_comments == 0:
            display_message(self, "Error", "No comments to summarize")
            return

        cyberbullying_count = 0
        normal_count = 0
        high_confidence_count = 0  # Comments with confidence > 90%

        for row in range(total_comments):
            prediction = self.get_current_table().item(row, 1).text()
            confidence = float(self.get_current_table().item(row, 2).text().strip('%')) / 100

            if prediction == "Cyberbullying":
                cyberbullying_count += 1
            else:
                normal_count += 1

            if confidence > 0.9:
                high_confidence_count += 1

        summary_text = (
            f"Analysis Summary:\n\n"
            f"Total Comments Analyzed: {total_comments}\n"
            f"Cyberbullying Comments: {cyberbullying_count} ({(cyberbullying_count/total_comments)*100:.1f}%)\n"
            f"Normal Comments: {normal_count} ({(normal_count/total_comments)*100:.1f}%)\n"
            f"High Confidence Predictions: {high_confidence_count} ({(high_confidence_count/total_comments)*100:.1f}%)\n"
            f"Comments in Selection List: {len(self.selected_comments)}"
        )

        display_message(self, "Results Summary", summary_text)

    def toggle_list_status(self):
        selected_items = self.get_current_table().selectedItems()
        if not selected_items:
            display_message(self, "Error", "Please select a comment to add or remove")
            return

        comment = self.get_current_table().item(selected_items[0].row(), 0).text()
        row = selected_items[0].row()
        if comment in self.selected_comments:
            self.selected_comments.remove(comment)
            display_message(self, "Success", "Comment removed from list")
            # Reset row color
            for col in range(self.get_current_table().columnCount()):
                self.get_current_table().item(row, col).setBackground(QColor(COLORS['normal']))
        else:
            self.selected_comments.append(comment)
            display_message(self, "Success", "Comment added to list")
            # Highlight row color
            for col in range(self.get_current_table().columnCount()):
                self.get_current_table().item(row, col).setBackground(QColor(COLORS['highlight']))
        self.update_details_panel()

    def export_selected(self):
        if not self.selected_comments:
            display_message(self, "Error", "No comments selected for export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Selected Comments", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                df = pd.DataFrame(self.selected_comments, columns=['Comment'])
                df.to_csv(file_path, index=False)
                display_message(self, "Success", "Selected comments exported successfully")
            except Exception as e:
                display_message(self, "Error", f"Error exporting comments: {e}")

    def export_all(self):
        if self.get_current_table().rowCount() == 0:
            display_message(self, "Error", "No comments to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export All Comments", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                comments = []
                predictions = []
                confidences = []

                for row in range(self.get_current_table().rowCount()):
                    comments.append(self.get_current_table().item(row, 0).text())
                    predictions.append(self.get_current_table().item(row, 1).text())
                    confidences.append(self.get_current_table().item(row, 2).text())

                df = pd.DataFrame({
                    'Comment': comments,
                    'Prediction': predictions,
                    'Confidence': confidences
                })
                df.to_csv(file_path, index=False)
                display_message(self, "Success", "All comments exported successfully")
            except Exception as e:
                display_message(self, "Error", f"Error exporting comments: {e}")

