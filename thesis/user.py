from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QTextEdit, QWidget, 
                           QFileDialog, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QSplitter, QGridLayout, QComboBox, 
                           QSizePolicy, QStackedWidget, QFrame, QTabWidget, QMessageBox)
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
from comment_operations import generate_report, generate_report_user

# Reuse the LoadingOverlay from the main GUI
from loading_overlay import LoadingOverlay

class UserMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyber Boolean - Simple View")
        self.showFullScreen()
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")
        
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.init_main_ui()
        
        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self)

        # Store reference to main window
        self.main_window = None

    def set_main_window(self, main_window):
        self.main_window = main_window

    def sign_out(self):
        """Sign out and return to main GUI"""
        from gui import MainWindow  # Import here to avoid circular import
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()
    
    def show_main_ui(self):
        self.central_widget.setCurrentIndex(1)
    
    def init_main_ui(self):
        main_widget = QWidget()
        self.central_widget.addWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)
        self.layout.setSpacing(10)  # Reduced spacing
        self.layout.setContentsMargins(10, 10, 10, 10)  # Reduced margins

        # Top header section with sign out button and title in one row
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add sign out button
        self.sign_out_button = QPushButton("Sign Out")
        self.sign_out_button.setFont(FONTS['button'])
        self.sign_out_button.setStyleSheet(BUTTON_STYLE)
        self.sign_out_button.setFixedWidth(100)  # Smaller width
        self.sign_out_button.clicked.connect(self.sign_out)
        
        # Title
        title = QLabel("Cyberbullying Detection Tool")
        title.setFont(FONTS['header'])
        title.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(self.sign_out_button)
        header_layout.addWidget(title, 1)  # Title takes remaining space
        header_layout.addSpacing(100)  # Balance the layout
        
        self.layout.addWidget(header_widget)
        
        # Collapsible input section
        input_container = QWidget()
        input_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)  # Limit vertical size
        input_layout = QHBoxLayout(input_container)  # Changed to horizontal for space efficiency
        input_layout.setSpacing(10)
        input_layout.setContentsMargins(0, 0, 0, 0)

        # Facebook Post Section - Made more compact
        fb_section = QWidget()
        fb_section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['secondary']};
                border-radius: 4px;
            }}
        """)
        fb_layout = QVBoxLayout(fb_section)
        fb_layout.setSpacing(5)  # Reduced spacing
        fb_layout.setContentsMargins(8, 8, 8, 8)  # Reduced padding
        
        fb_title = QLabel("Facebook Post")
        fb_title.setFont(FONTS['button'])  # Smaller font
        fb_title.setAlignment(Qt.AlignCenter)
        self.url_input = QLineEdit()
        self.url_input.setStyleSheet(INPUT_STYLE)
        self.url_input.setPlaceholderText("Enter Facebook Post URL")
        self.scrape_button = QPushButton("Scrape Comments")
        self.scrape_button.setFont(FONTS['button'])
        self.scrape_button.setStyleSheet(BUTTON_STYLE)
        self.scrape_button.clicked.connect(self.scrape_comments)
        
        fb_layout.addWidget(fb_title)
        fb_layout.addWidget(self.url_input)
        fb_layout.addWidget(self.scrape_button)
        input_layout.addWidget(fb_section)

        # CSV File Section - Made more compact
        csv_section = QWidget()
        csv_section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['secondary']};
                border-radius: 4px;
            }}
        """)
        csv_layout = QVBoxLayout(csv_section)
        csv_layout.setSpacing(5)  # Reduced spacing
        csv_layout.setContentsMargins(8, 8, 8, 8)  # Reduced padding
        
        csv_title = QLabel("CSV File")
        csv_title.setFont(FONTS['button'])  # Smaller font
        csv_title.setAlignment(Qt.AlignCenter)
        
        file_browse_layout = QHBoxLayout()
        self.file_input = QLineEdit()
        self.file_input.setStyleSheet(INPUT_STYLE)
        self.file_input.setPlaceholderText("Select CSV file")
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.setFont(FONTS['button'])
        self.browse_button.setStyleSheet(BUTTON_STYLE)
        self.browse_button.setFixedWidth(80)  # Smaller button
        self.browse_button.clicked.connect(self.browse_file)
        
        file_browse_layout.addWidget(self.file_input)
        file_browse_layout.addWidget(self.browse_button)
        
        self.process_csv_button = QPushButton("Process CSV")
        self.process_csv_button.setFont(FONTS['button'])
        self.process_csv_button.setStyleSheet(BUTTON_STYLE)
        self.process_csv_button.clicked.connect(self.process_csv)
        
        csv_layout.addWidget(csv_title)
        csv_layout.addLayout(file_browse_layout)
        csv_layout.addWidget(self.process_csv_button)
        input_layout.addWidget(csv_section)

        # Direct Input Section - Made more compact
        direct_section = QWidget()
        direct_section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['secondary']};
                border-radius: 4px;
            }}
        """)
        direct_layout = QVBoxLayout(direct_section)
        direct_layout.setSpacing(5)  # Reduced spacing
        direct_layout.setContentsMargins(8, 8, 8, 8)  # Reduced padding
        
        direct_title = QLabel("Direct Input")
        direct_title.setFont(FONTS['button'])  # Smaller font
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
        input_layout.addWidget(direct_section)

        # Add input container to main layout with fixed height
        self.layout.addWidget(input_container)
        
        # Make a line separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"background-color: {COLORS['border']};")
        self.layout.addWidget(separator)
        
     # Results section with tab widget - Modified to match input containers
        results_container = QWidget()
        results_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['secondary']};
                border-radius: 4px;
            }}
        """)
        results_layout = QVBoxLayout(results_container)
        results_layout.setContentsMargins(8, 8, 8, 8)  # Match input section padding
        
        # Table controls in a compact horizontal layout with better alignment
        table_controls = QWidget()
        table_controls.setStyleSheet("border: none;")  # Remove border for inner widget
        controls_layout = QHBoxLayout(table_controls)
        controls_layout.setContentsMargins(0, 0, 0, 5)  # Minimal margins
        
        # Create a container for the title with proper alignment
        title_container = QWidget()
        title_container.setStyleSheet("border: none;")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        table_title = QLabel("Results")
        table_title.setFont(FONTS['header'])
        table_title.setAlignment(Qt.AlignLeft)
        title_layout.addWidget(table_title)
        title_layout.addStretch()
        
        # Add the title container to the main controls layout
        controls_layout.addWidget(title_container, 1)  # Give title container stretch priority
        
        # Initial message widget with styled container
        message_container = QWidget()
        message_container.setStyleSheet("border: none;")  # Remove border for inner widget
        message_layout = QVBoxLayout(message_container)
        message_layout.setContentsMargins(5, 10, 5, 10)  # Better padding for message
        
        self.initial_message = QLabel("No analysis performed yet.\nResults will appear here.")
        self.initial_message.setAlignment(Qt.AlignCenter)
        self.initial_message.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px;")
        message_layout.addWidget(self.initial_message)
        
        # Tab widget styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: transparent;
            }}
            QTabBar::tab {{
                background: {COLORS['surface']};
                color: {COLORS['text']};
                padding: 6px 10px;
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
        
        # Add initial message to tab widget area
        results_layout.addWidget(message_container)
        results_layout.addWidget(self.tab_widget)
        self.tab_widget.hide()  # Hide tab widget initially

        # Initialize tab counters
        self.csv_tab_count = 1
        self.url_tab_count = 1
        
        # Dictionary to store tab references
        self.tabs = {}
        
        # Add results container to main layout with stretch factor
        self.layout.addWidget(results_container, 1)  # Give it maximum stretch
            
        # Set stretch factors
        self.layout.setStretch(0, 0)  # Header
        self.layout.setStretch(1, 0)  # Input - minimal height
        self.layout.setStretch(2, 0)  # Separator - minimal height
        self.layout.setStretch(3, 1)  # Results - takes all remaining space
    
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
        header_layout = QHBoxLayout()
        table_title = QLabel("Comments")
        table_title.setFont(FONTS['header'])
        header_layout.addWidget(table_title)
        
        # Add search bar
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search comments...")
        search_bar.setStyleSheet(INPUT_STYLE)
        search_bar.setMaximumWidth(300)
        search_layout.addWidget(search_bar)
        
        header_layout.addWidget(search_container)
        header_layout.addStretch()
        
        sort_combo = QComboBox()
        sort_combo.addItems([
            "Sort by Comments (A-Z)",
            "Sort by Comments (Z-A)",
            "Sort by Prediction (A-Z)",
            "Sort by Confidence (High to Low)",
            "Sort by Confidence (Low to High)"
        ])
        header_layout.addWidget(sort_combo)
        tab_layout.addLayout(header_layout)

        # Create table
        table = QTableWidget()
        table.setSortingEnabled(True)
        # Update the table style to include alternating row colors
        table.setStyleSheet(f"""
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
        """)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Comment", "Prediction", "Confidence"])
        table.setAlternatingRowColors(True)  # Keep only one instance of this

        # Adjust column sizes
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        table.setColumnWidth(1, 150)
        table.setColumnWidth(2, 100)

        # Enable better table behavior
        table.setWordWrap(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Store sort combo and connect it
        table.sort_combo = sort_combo
        sort_combo.currentIndexChanged.connect(lambda: self.sort_table(table))
        
        tab_layout.addWidget(table)
        
        # Connect search functionality
        def filter_table():
            search_text = search_bar.text().lower()
            for row in range(table.rowCount()):
                comment = table.item(row, 0).text().lower()
                table.setRowHidden(row, search_text not in comment)
        
        search_bar.textChanged.connect(filter_table)
        
        # Store search bar reference
        table.search_bar = search_bar
        
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

    def populate_table(self, comments):
        """Create new tab and populate it based on input type"""
        # Store the input source before clearing
        file_path = self.file_input.text()
        url = self.url_input.text()

        # Clear inputs after checking
        self.file_input.clear()
        self.url_input.clear()
        self.text_input.clear()  # Also clear the text input field

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

        # Resize rows after all data is added for better performance
        table.resizeRowsToContents()
        
        # Switch to the new tab
        tab_index = self.tab_widget.indexOf(self.tabs[tab_name])
        self.tab_widget.setCurrentIndex(tab_index)
        
        # Ensure we're focusing on the table part of the window
        # by scrolling to top
        table.scrollToTop()
    
    def update_details_panel(self):
        # This is a simplified version that doesn't show detailed information
        # but keeps the function to avoid errors when selecting table rows
        pass

    def export_results(self):
        current_table = self.get_current_table()
        if not current_table or current_table.rowCount() == 0:
            display_message(self, "Error", "No comments to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                comments = []
                predictions = []
                confidences = []

                for row in range(current_table.rowCount()):
                    comments.append(current_table.item(row, 0).text())
                    predictions.append(current_table.item(row, 1).text())
                    confidences.append(current_table.item(row, 2).text())

                df = pd.DataFrame({
                    'Comment': comments,
                    'Prediction': predictions,
                    'Confidence': confidences
                })
                df.to_csv(file_path, index=False)
                display_message(self, "Success", "Results exported successfully")
            except Exception as e:
                display_message(self, "Error", f"Error exporting results: {e}")