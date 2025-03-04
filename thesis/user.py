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

# Reuse the LoadingOverlay from the main GUI
from loading_overlay import LoadingOverlay

class UserMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyber Boolean - User")
        self.showFullScreen()
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")
        
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.init_main_ui()
        
        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self)
    
    
    def show_main_ui(self):
        self.central_widget.setCurrentIndex(1)
    
    def init_main_ui(self):
        main_widget = QWidget()
        self.central_widget.addWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Cyberbullying Detection Tool")
        title.setFont(FONTS['header'])
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)
        
        # Input Container
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(10)
        input_layout.setContentsMargins(0, 0, 0, 0)

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
        
        # Results section - Add tab widget
        results_container = QWidget()
        results_layout = QVBoxLayout(results_container)
        
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
        results_layout.addWidget(self.initial_message)
        
        results_layout.addWidget(self.tab_widget)
        self.tab_widget.hide()  # Hide tab widget initially

        # Initialize tab counters
        self.csv_tab_count = 1
        self.url_tab_count = 1
        
        # Dictionary to store tab references
        self.tabs = {}
        
        self.layout.addWidget(results_container)
        
        # Set stretch factors
        self.layout.setStretch(0, 0)  # Title
        self.layout.setStretch(1, 0)  # Input
        self.layout.setStretch(2, 1)  # Results
        
        # Store comment metadata
        self.comment_metadata = {}
    
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

        # Switch to the new tab
        tab_index = self.tab_widget.indexOf(self.tabs[tab_name])
        self.tab_widget.setCurrentIndex(tab_index)
    
    def update_details_panel(self):
        # This is a simplified version that doesn't show detailed information
        # but keeps the function to avoid errors when selecting table rows
        pass

    def export_results(self):
        if self.output_table.rowCount() == 0:
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

                for row in range(self.output_table.rowCount()):
                    comments.append(self.output_table.item(row, 0).text())
                    predictions.append(self.output_table.item(row, 1).text())
                    confidences.append(self.output_table.item(row, 2).text())

                df = pd.DataFrame({
                    'Comment': comments,
                    'Prediction': predictions,
                    'Confidence': confidences
                })
                df.to_csv(file_path, index=False)
                display_message(self, "Success", "Results exported successfully")
            except Exception as e:
                display_message(self, "Error", f"Error exporting results: {e}")
 