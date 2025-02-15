from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QTextEdit, QWidget, 
                           QFileDialog, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QSplitter, QFrame, QGridLayout, QComboBox, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QTextCursor  # Import QColor for color coding and QTextCursor for text formatting
from scraper import scrape_comments
from model import classify_comment
import pandas as pd
from utils import display_message
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE, TABLE_STYLE

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_comments = []  # Store selected comments
        self.setWindowTitle("Cyber Boolean")
        self.setGeometry(100, 100, 1200, 700)  # Made window wider
        self.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
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

        # URL Input
        url_layout = QHBoxLayout()
        self.url_label = QLabel("URL (Facebook Post):")
        self.url_label.setFont(FONTS['body'])
        self.url_input = QLineEdit()
        self.url_input.setStyleSheet(INPUT_STYLE)
        self.scrape_button = QPushButton("Scrape Comments")
        self.scrape_button.setFont(FONTS['button'])
        self.scrape_button.setStyleSheet(BUTTON_STYLE)
        self.scrape_button.clicked.connect(self.scrape_comments)
        url_layout.addWidget(self.url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.scrape_button)
        input_layout.addLayout(url_layout)

        # File Input
        file_layout = QHBoxLayout()
        self.file_label = QLabel("CSV File:")
        self.file_label.setFont(FONTS['body'])
        self.file_input = QLineEdit()
        self.file_input.setStyleSheet(INPUT_STYLE)
        self.browse_button = QPushButton("Browse")
        self.browse_button.setFont(FONTS['button'])
        self.browse_button.setStyleSheet(BUTTON_STYLE)
        self.browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(self.browse_button)
        input_layout.addLayout(file_layout)

        # Text Input
        self.text_label = QLabel("Enter Comment:")
        self.text_label.setFont(FONTS['body'])
        self.text_input = QLineEdit()
        self.text_input.setStyleSheet(INPUT_STYLE)
        input_layout.addWidget(self.text_label)
        input_layout.addWidget(self.text_input)

        # Classify Button
        self.classify_button = QPushButton("Classify Comment")
        self.classify_button.setFont(FONTS['button'])
        self.classify_button.setStyleSheet(BUTTON_STYLE)
        self.classify_button.clicked.connect(self.classify_comments)
        input_layout.addWidget(self.classify_button)

        # Add input container to main layout
        self.layout.addWidget(input_container)

        # Create a horizontal splitter for table and details
        splitter = QSplitter(Qt.Horizontal)  # Horizontal splitter

        # Table Container
        table_container = QWidget()
        table_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Set size policy
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
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Comment column stretches
        header.setSectionResizeMode(1, QHeaderView.Fixed)    # Prediction column fixed
        header.setSectionResizeMode(2, QHeaderView.Fixed)    # Confidence column fixed

        # Set fixed widths for the non-stretching columns
        self.output_table.setColumnWidth(1, 120)  # Prediction column
        self.output_table.setColumnWidth(2, 100)  # Confidence column

        self.output_table.setWordWrap(True)
        self.output_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.output_table.setSelectionMode(QTableWidget.SingleSelection)
        self.output_table.itemSelectionChanged.connect(self.update_details_panel)
        table_layout.addWidget(self.output_table)
        splitter.addWidget(table_container)

        # Details Panel
        details_container = QWidget()
        details_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Set size policy
        details_layout = QVBoxLayout(details_container)
        details_layout.setContentsMargins(10, 0, 0, 0)  # Add left margin

        # Create a container for title + details
        details_section = QWidget()
        details_section_layout = QVBoxLayout(details_section)
        details_section_layout.setSpacing(5)  # Reduce spacing between title & details
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
        self.details_text_edit.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px;")  # Increase font size
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
        buttons_layout.setSpacing(10)  # Increase spacing between buttons

        for i, btn in enumerate([self.flag_button, self.add_remove_button, self.export_selected_button, self.export_all_button]):
            btn.setStyleSheet(BUTTON_STYLE)
            btn.setFont(FONTS['button'])
            buttons_layout.addWidget(btn, i // 2, i % 2)  # Arrange buttons in a 2x2 grid
            btn.hide()  # Hide all buttons initially

        # Connect buttons
        self.flag_button.clicked.connect(self.flag_comment)
        self.add_remove_button.clicked.connect(self.toggle_list_status)
        self.export_selected_button.clicked.connect(self.export_selected)
        self.export_all_button.clicked.connect(self.export_all)

        # Add buttons widget to details layout
        details_layout.addWidget(buttons_widget)
        splitter.addWidget(details_container)

        # Set initial sizes for the splitter to make them equal
        splitter.setSizes([self.width() // 2, self.width() // 2])  # Equal sizes
        splitter.setStretchFactor(0, 1)  # Both sides stretch equally
        splitter.setStretchFactor(1, 1)

        # Add splitter to main layout
        self.layout.addWidget(splitter)

        # Set layout stretch factors
        self.layout.setStretch(0, 0)  # Input container doesn't stretch
        self.layout.setStretch(1, 1)  # Splitter takes remaining space

    def scrape_comments(self):
        url = self.url_input.text()
        if not url:
            display_message(self, "Error", "Please enter a URL.")
            return

        try:
            comments = scrape_comments(url)  # Call the placeholder function
            self.populate_table(comments)
        except Exception as e:
            display_message(self, "Error", f"Error scraping comments: {e}")

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.file_input.setText(file_path)

    def classify_comments(self):
        # Prioritize URL input, then CSV file, then text input
        if self.url_input.text():
            self.scrape_comments()  # Reuse scrape_comments to populate table
        elif self.file_input.text():
            file_path = self.file_input.text()
            try:
                df = pd.read_csv(file_path)
                comments = df.iloc[:, 0].tolist()  # Assuming first column contains comments
                self.populate_table(comments)
            except Exception as e:
                display_message(self, "Error", f"Error reading CSV file: {e}")
        elif self.text_input.text():
            comment = self.text_input.text()
            self.populate_table([comment])
        else:
            display_message(self, "Error", "Please enter a URL, select a CSV file, or enter a comment.")

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
                prediction_item.setBackground(QColor(COLORS['bullying']))
            else:
                prediction_item.setBackground(QColor(COLORS['normal']))

            confidence_item = QTableWidgetItem(f"{confidence:.2%}")
            confidence_item.setTextAlignment(Qt.AlignCenter)

            self.output_table.setItem(row_position, 0, comment_item)
            self.output_table.setItem(row_position, 1, prediction_item)
            self.output_table.setItem(row_position, 2, confidence_item)

            # Adjust row height to content
            self.output_table.resizeRowToContents(row_position)

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
        commenter = "Placeholder Commenter"  # Placeholder for commenter

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

        # Set text contents
        self.details_text_edit.clear()
        self.details_text_edit.append(f"<b>Comment:</b>\n{comment}\n")
        self.details_text_edit.append(f"<b>Commenter:</b> {commenter}\n")
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
        if comment in self.selected_comments:
            self.selected_comments.remove(comment)
            display_message(self, "Success", "Comment removed from list")
        else:
            self.selected_comments.append(comment)
            display_message(self, "Success", "Comment added to list")
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
