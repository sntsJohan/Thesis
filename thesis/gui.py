from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QTextEdit, QWidget, 
                           QFileDialog, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QSplitter, QGridLayout, QComboBox, QSizePolicy, QStackedWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QTextCursor  
from scraper import scrape_comments
from model import classify_comment
import pandas as pd
from utils import display_message
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE, TABLE_STYLE
import tempfile
import time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_comments = [] 
        self.setWindowTitle("Cyber Boolean")
        self.setGeometry(100, 100, 1200, 700)  
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")

        self.central_widget = QStackedWidget()  
        self.setCentralWidget(self.central_widget)

        self.init_welcome_screen()
        self.init_main_ui()

    def init_welcome_screen(self):
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setSpacing(20)
        welcome_layout.setContentsMargins(20, 20, 20, 20)

        welcome_label = QLabel("Welcome to Cyber Boolean")
        welcome_label.setFont(FONTS['header'])
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(welcome_label)

        get_started_button = QPushButton("Get Started")
        get_started_button.setFont(FONTS['button'])
        get_started_button.setStyleSheet(BUTTON_STYLE)
        get_started_button.setFixedWidth(150)  
        get_started_button.clicked.connect(self.show_main_ui)
        welcome_layout.addWidget(get_started_button, alignment=Qt.AlignCenter) 

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
        

        # Header layout with table title and sort dropdown
        sort_layout = QHBoxLayout()
        table_title = QLabel("Comments")
        table_title.setFont(FONTS['header'])
        sort_layout.addWidget(table_title)
        sort_layout.addStretch()
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Sort by Comments (A-Z)",
            "Sort by Comments (Z-A)",
            "Sort by Prediction (A-Z)",
            "Sort by Confidence (High to Low)",
            "Sort by Confidence (Low to High)"
        ])
        self.sort_combo.currentIndexChanged.connect(self.sort_table)
        sort_layout.addWidget(self.sort_combo)
        table_layout.addLayout(sort_layout)

        # Output Table
        self.output_table = QTableWidget()
        self.output_table.setSortingEnabled(True)
        self.output_table.setStyleSheet(TABLE_STYLE)
        self.output_table.setColumnCount(3)
        self.output_table.setHorizontalHeaderLabels(["Comment", "Prediction", "Confidence"])

        # Adjust column sizes to fill entire width
        header = self.output_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch) 
        header.setSectionResizeMode(1, QHeaderView.Fixed)    
        header.setSectionResizeMode(2, QHeaderView.Fixed)   

        self.output_table.setColumnWidth(1, 150)  # Increased width for Prediction column
        self.output_table.setColumnWidth(2, 100)  # Confidence column

        self.output_table.setWordWrap(True)
        self.output_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.output_table.setSelectionMode(QTableWidget.SingleSelection)
        self.output_table.itemSelectionChanged.connect(self.update_details_panel)
        table_layout.addWidget(self.output_table)
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
        self.flag_button = QPushButton("🚩 Flag Comment")
        self.add_remove_button = QPushButton("➕ Add to List")
        self.export_selected_button = QPushButton("💾 Export List")
        self.export_all_button = QPushButton("📤 Export All Results")

        # Add buttons to a grid layout
        buttons_widget = QWidget()
        buttons_layout = QGridLayout(buttons_widget)
        buttons_layout.setSpacing(10) 

        for i, btn in enumerate([self.flag_button, self.add_remove_button, self.export_selected_button, self.export_all_button]):
            btn.setStyleSheet(BUTTON_STYLE)
            btn.setFont(FONTS['button'])
            buttons_layout.addWidget(btn, i // 2, i % 2)  
            btn.hide()  

        # Connect buttons
        self.flag_button.clicked.connect(self.flag_comment)
        self.add_remove_button.clicked.connect(self.toggle_list_status)
        self.export_selected_button.clicked.connect(self.export_selected)
        self.export_all_button.clicked.connect(self.export_all)

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

    def scrape_comments(self):
        url = self.url_input.text()
        if not url:
            display_message(self, "Error", "Please enter a URL.")
            return

        try:
            from scraper import scrape_comments
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
                temp_path = temp_file.name
            scrape_comments(url, temp_path)
            df = pd.read_csv(temp_path)
            
            # Store additional comment metadata as instance variables
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

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.file_input.setText(file_path)

    def process_csv(self):
        if not self.file_input.text():
            display_message(self, "Error", "Please select a CSV file first")
            return
        try:
            df = pd.read_csv(self.file_input.text())
            comments = df.iloc[:, 0].tolist()
            self.populate_table(comments)
        except Exception as e:
            display_message(self, "Error", f"Error reading CSV file: {e}")

    def analyze_single(self):
        if not self.text_input.text():
            display_message(self, "Error", "Please enter a comment to analyze")
            return
        
        # Create metadata for the direct input comment
        comment = self.text_input.text()
        self.comment_metadata = {
            comment: {
                'profile_name': 'Direct Input',
                'profile_picture': '',
                'date': time.strftime('%Y-%m-%d %H:%M:%S'),  # Current time
                'likes_count': 'N/A',
                'profile_id': 'N/A'
            }
        }
        
        self.populate_table([comment])

    def populate_table(self, comments):
        # Only clear rows if not classifying a single comment
        if len(comments) > 1:
            self.output_table.setRowCount(0)

        for comment in comments:
            prediction, confidence = classify_comment(comment)
            row_position = self.output_table.rowCount()
            self.output_table.insertRow(row_position)

            # Create and set items with word wrap
            comment_item = QTableWidgetItem(comment)
            comment_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            prediction_item = QTableWidgetItem(prediction)
            prediction_item.setTextAlignment(Qt.AlignCenter)
            # Apply color coding based on prediction
            if prediction == "Cyberbullying":
                prediction_item.setForeground(QColor(COLORS['bullying']))
            else:
                prediction_item.setForeground(QColor(COLORS['normal']))

            confidence_item = QTableWidgetItem(f"{confidence:.2%}")
            confidence_item.setTextAlignment(Qt.AlignCenter)

            self.output_table.setItem(row_position, 0, comment_item)
            self.output_table.setItem(row_position, 1, prediction_item)
            self.output_table.setItem(row_position, 2, confidence_item)

            # Adjust row height to content
            self.output_table.resizeRowToContents(row_position)

            # Change row color if comment is in the list
            if comment in self.selected_comments:
                for col in range(self.output_table.columnCount()):
                    self.output_table.item(row_position, col).setBackground(QColor(COLORS['highlight']))

    def update_details_panel(self):
        selected_items = self.output_table.selectedItems()
        if not selected_items:
            self.details_text_edit.clear()
            # Hide operation buttons
            for btn in [self.flag_button, self.add_remove_button, self.export_selected_button, self.export_all_button]:
                btn.hide()
            return

        row = selected_items[0].row()
        comment = self.output_table.item(row, 0).text()
        prediction = self.output_table.item(row, 1).text()
        confidence = self.output_table.item(row, 2).text()
        
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
        for btn in [self.flag_button, self.add_remove_button, self.export_selected_button, self.export_all_button]:
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

    def flag_comment(self):
        selected_items = self.output_table.selectedItems()
        if not selected_items:
            display_message(self, "Error", "Please select a comment to flag")
            return
        # Implement flagging logic here
        display_message(self, "Success", "Comment has been flagged")

    def toggle_list_status(self):
        selected_items = self.output_table.selectedItems()
        if not selected_items:
            display_message(self, "Error", "Please select a comment to add or remove")
            return

        comment = self.output_table.item(selected_items[0].row(), 0).text()
        row = selected_items[0].row()
        if comment in self.selected_comments:
            self.selected_comments.remove(comment)
            display_message(self, "Success", "Comment removed from list")
            # Reset row color
            for col in range(self.output_table.columnCount()):
                self.output_table.item(row, col).setBackground(QColor(COLORS['normal']))
        else:
            self.selected_comments.append(comment)
            display_message(self, "Success", "Comment added to list")
            # Highlight row color
            for col in range(self.output_table.columnCount()):
                self.output_table.item(row, col).setBackground(QColor(COLORS['highlight']))
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
        if self.output_table.rowCount() == 0:
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
                display_message(self, "Success", "All comments exported successfully")
            except Exception as e:
                display_message(self, "Error", f"Error exporting comments: {e}")

    def sort_table(self):
        index = self.sort_combo.currentIndex()
        if index == 0:
            self.output_table.sortItems(0, Qt.AscendingOrder)
        elif index == 1:
            self.output_table.sortItems(0, Qt.DescendingOrder)
        elif index == 2:
            self.output_table.sortItems(1, Qt.AscendingOrder)
        elif index == 3:
            self.output_table.sortItems(2, Qt.DescendingOrder)
        elif index == 4:
            self.output_table.sortItems(2, Qt.AscendingOrder)
