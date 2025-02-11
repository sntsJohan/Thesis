from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem
from PyQt5.QtCore import Qt
import pandas as pd
from utils import display_message

def update_details_panel(window):
    selected_items = window.output_table.selectedItems()
    if not selected_items:
        window.comment_label.setText("")
        window.info_label.setText("")
        for btn in [window.flag_button, window.add_button, 
                    window.remove_button, window.export_selected_button]:
            btn.hide()
        return
    row = selected_items[0].row()
    comment = window.output_table.item(row, 0).text()
    prediction = window.output_table.item(row, 1).text()
    confidence = window.output_table.item(row, 2).text()
    for btn in [window.flag_button, window.add_button, 
                window.remove_button, window.export_selected_button]:
        btn.show()
    window.add_button.setVisible(comment not in window.selected_comments)
    window.remove_button.setVisible(comment in window.selected_comments)
    rules_broken = ("• Harassment\n• Hate Speech\n• Threatening Language" 
                    if prediction == "Cyberbullying" else "None")
    window.comment_label.setText(f"Comment:\n{comment}")
    window.info_label.setText(
        f"Classification: {prediction}\n"
        f"Confidence: {confidence}\n"
        f"Status: {'In List' if comment in window.selected_comments else 'Not in List'}\n"
        f"Rules Broken: {rules_broken}"
    )

def flag_comment(window):
    selected_items = window.output_table.selectedItems()
    if not selected_items:
        display_message(window, "Error", "Please select a comment to flag")
        return
    display_message(window, "Success", "Comment has been flagged")

def add_to_list(window):
    selected_items = window.output_table.selectedItems()
    if not selected_items:
        display_message(window, "Error", "Please select a comment to add")
        return
    comment = window.output_table.item(selected_items[0].row(), 0).text()
    if comment not in window.selected_comments:
        window.selected_comments.append(comment)
        update_details_panel(window)
        display_message(window, "Success", "Comment added to list")

def remove_from_list(window):
    selected_items = window.output_table.selectedItems()
    if not selected_items:
        display_message(window, "Error", "Please select a comment to remove")
        return
    comment = window.output_table.item(selected_items[0].row(), 0).text()
    if comment in window.selected_comments:
        window.selected_comments.remove(comment)
        update_details_panel(window)
        display_message(window, "Success", "Comment removed from list")

def export_selected(window):
    if not window.selected_comments:
        display_message(window, "Error", "No comments selected for export")
        return
    file_path, _ = QFileDialog.getSaveFileName(window, "Export Selected Comments", "", "CSV Files (*.csv)")
    if file_path:
        try:
            df = pd.DataFrame(window.selected_comments, columns=['Comment'])
            df.to_csv(file_path, index=False)
            display_message(window, "Success", "Selected comments exported successfully")
        except Exception as e:
            display_message(window, "Error", f"Error exporting comments: {e}")

def export_all(window):
    if window.output_table.rowCount() == 0:
        display_message(window, "Error", "No comments to export")
        return
    file_path, _ = QFileDialog.getSaveFileName(window, "Export All Comments", "", "CSV Files (*.csv)")
    if file_path:
        try:
            comments = []
            predictions = []
            confidences = []
            for row in range(window.output_table.rowCount()):
                comments.append(window.output_table.item(row, 0).text())
                predictions.append(window.output_table.item(row, 1).text())
                confidences.append(window.output_table.item(row, 2).text())
            df = pd.DataFrame({
                'Comment': comments,
                'Prediction': predictions,
                'Confidence': confidences
            })
            df.to_csv(file_path, index=False)
            display_message(window, "Success", "All comments exported successfully")
        except Exception as e:
            display_message(window, "Error", f"Error exporting comments: {e}")

def sort_table(window, index):
    if index == 0:
        window.output_table.sortItems(0, Qt.AscendingOrder)
    elif index == 1:
        window.output_table.sortItems(0, Qt.DescendingOrder)
    elif index == 2:
        window.output_table.sortItems(1, Qt.AscendingOrder)
    elif index == 3:
        window.output_table.sortItems(2, Qt.DescendingOrder)
    elif index == 4:
        window.output_table.sortItems(2, Qt.AscendingOrder)
