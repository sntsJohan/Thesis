from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem
from PyQt5.QtCore import Qt
import pandas as pd
from utils import display_message
import reportlab
import matplotlib.pyplot as plt
import io
import datetime
import os

def update_details_panel(window):
    selected_items = window.output_table.selectedItems()
    if not selected_items:
        window.details_text_edit.clear()
        # Disable row operations when no row is selected
        row_buttons = [window.add_remove_button, window.export_selected_button]
        for btn in row_buttons:
            btn.setEnabled(False)
        return

    # Enable row operation buttons since a row is selected
    row_buttons = [window.add_remove_button, window.export_selected_button]
    for btn in row_buttons:
        btn.setEnabled(True)

    row = selected_items[0].row()
    comment = window.output_table.item(row, 0).text()
    prediction = window.output_table.item(row, 1).text()
    confidence = window.output_table.item(row, 2).text()
    commenter = "Placeholder Commenter"  # Placeholder for commenter

    # Update add/remove button text based on list status
    if comment in window.selected_comments:
        window.add_remove_button.setText("➖ Remove from List")
    else:
        window.add_remove_button.setText("➕ Add to List")

    # Rules text
    rules_broken = ["Harassment", "Hate Speech", "Threatening Language"] if prediction == "Cyberbullying" else []

    # Set text contents
    window.details_text_edit.clear()
    window.details_text_edit.append(f"<b>Comment:</b>\n{comment}\n")
    window.details_text_edit.append(f"<b>Commenter:</b> {commenter}\n")
    window.details_text_edit.append(f"<b>Classification:</b> {prediction}\n")
    window.details_text_edit.append(f"<b>Confidence:</b> {confidence}\n")
    window.details_text_edit.append(f"<b>Status:</b> {'In List' if comment in window.selected_comments else 'Not in List'}\n")
    window.details_text_edit.append("<b>Rules Broken:</b>")

    cursor = window.details_text_edit.textCursor()
    for rule in rules_broken:
        cursor.insertHtml(f'<span style="background-color: ["secondary"]; border-radius: 4px; padding: 2px 4px; margin: 2px; display: inline-block;">{rule}</span> ')
    window.details_text_edit.setTextCursor(cursor)

def show_summary(window):
    total_comments = window.output_table.rowCount()
    if total_comments == 0:
        display_message(window, "Error", "No comments to summarize")
        return

    cyberbullying_count = 0
    normal_count = 0
    high_confidence_count = 0  # Comments with confidence > 90%

    for row in range(total_comments):
        prediction = window.output_table.item(row, 1).text()
        confidence = float(window.output_table.item(row, 2).text().strip('%')) / 100

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
        f"Comments in Selection List: {len(window.selected_comments)}"
    )

    display_message(window, "Results Summary", summary_text)

def toggle_list_status(window):
    selected_items = window.output_table.selectedItems()
    if not selected_items:
        display_message(window, "Error", "Please select a comment to add or remove")
        return

    comment = window.output_table.item(selected_items[0].row(), 0).text()
    if comment in window.selected_comments:
        window.selected_comments.remove(comment)
        display_message(window, "Success", "Comment removed from list")
    else:
        window.selected_comments.append(comment)
        display_message(window, "Success", "Comment added to list")
    update_details_panel(window)

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

def generate_report_from_window(window):
    """Generate detailed report from the main window"""
    if window.get_current_table().rowCount() == 0:
        display_message(window, "Error", "No data available to generate report")
        return

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        import matplotlib.pyplot as plt
        import io
        import datetime
        import os

        # Collect data for charts and table
        data = []
        total_rows = window.get_current_table().rowCount()
        cyberbullying_count = 0
        normal_count = 0
        confidence_ranges = {'90-100%': 0, '80-89%': 0, '70-79%': 0, '<70%': 0}

        for row in range(total_rows):
            comment = window.get_current_table().item(row, 0).text()
            prediction = window.get_current_table().item(row, 1).text()
            confidence = window.get_current_table().item(row, 2).text()
            confidence_value = float(confidence.strip('%'))
            
            # Store data for table
            data.append([comment, prediction, confidence])
            
            if prediction == "Cyberbullying":
                cyberbullying_count += 1
            else:
                normal_count += 1
                
            # Categorize confidence
            if confidence_value >= 90:
                confidence_ranges['90-100%'] += 1
            elif confidence_value >= 80:
                confidence_ranges['80-89%'] += 1
            elif confidence_value >= 70:
                confidence_ranges['70-79%'] += 1
            else:
                confidence_ranges['<70%'] += 1

        # Create classification distribution pie chart
        plt.figure(figsize=(6, 4))
        plt.pie([cyberbullying_count, normal_count], 
                labels=['Cyberbullying', 'Normal'],
                autopct='%1.1f%%',
                colors=['#ff9999', '#66b3ff'])
        plt.title('Comment Classification Distribution')
        
        # Save pie chart to memory
        pie_chart_data = io.BytesIO()
        plt.savefig(pie_chart_data, format='png', bbox_inches='tight')
        pie_chart_data.seek(0)
        plt.close()

        # Create confidence distribution bar chart
        plt.figure(figsize=(6, 4))
        bars = plt.bar(confidence_ranges.keys(), confidence_ranges.values())
        plt.title('Confidence Level Distribution')
        plt.xlabel('Confidence Range')
        plt.ylabel('Number of Comments')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        # Save bar chart to memory
        bar_chart_data = io.BytesIO()
        plt.savefig(bar_chart_data, format='png', bbox_inches='tight')
        bar_chart_data.seek(0)
        plt.close()

        # Create the PDF document
        file_path, _ = QFileDialog.getSaveFileName(
            window, "Save Report", "", "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1a237e')
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#303f9f')
        )

        # Content elements
        elements = []

        # Create header table for logo and title
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            img = Image(logo_path)
            img.drawHeight = 0.8*inch
            img.drawWidth = 0.8*inch
            
            header_data = [[img, Paragraph("Cyberbullying Detection Report", title_style)]]
            header_table = Table(header_data, colWidths=[1*inch, 6*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            elements.append(header_table)
        else:
            elements.append(Paragraph("Cyberbullying Detection Report", title_style))

        elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%B %d, %Y %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Add charts section
        elements.append(Paragraph("Visual Analysis", subtitle_style))
        
        # Add pie chart
        elements.append(Image(pie_chart_data, width=4*inch, height=3*inch))
        elements.append(Spacer(1, 10))
        
        # Add bar chart
        elements.append(Image(bar_chart_data, width=4*inch, height=3*inch))
        elements.append(Spacer(1, 20))

        # Add summary section
        elements.append(Paragraph("Analysis Summary", subtitle_style))
        summary_data = [
            ["Total Comments Analyzed:", str(total_rows)],
            ["Cyberbullying Comments:", f"{cyberbullying_count} ({(cyberbullying_count/total_rows)*100:.1f}%)"],
            ["Normal Comments:", f"{normal_count} ({(normal_count/total_rows)*100:.1f}%)"],
            ["High Confidence Predictions: ", f"{cyberbullying_count} ({(cyberbullying_count/total_rows)*100:.1f}%)"],
            ["Comments in Selection List:", str(len(window.selected_comments))]
        ]
        
        summary_table = Table(summary_data, colWidths=[200, 300])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#303f9f')),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # Add detailed results section
        elements.append(Paragraph("Detailed Analysis Results", subtitle_style))
        
        # Prepare table data with headers
        table_data = [['Comment', 'Classification', 'Confidence']] + [
            [Paragraph(comment, styles['Normal']), prediction, confidence]  # Wrap comments in Paragraph
            for comment, prediction, confidence in data
        ]
        
        # Create the main results table with adjusted widths
        results_table = Table(table_data, colWidths=[400, 80, 80])  # Wider comment column
        results_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header row
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),      # Data rows
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eaf6')),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a237e')),   # Header text
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to top
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('WORDWRAP', (0, 0), (-1, -1), True),  # Enable word wrapping
        ]))
        elements.append(results_table)

        # Build the PDF
        doc.build(elements)
        
        display_message(window, "Success", "Report generated successfully")
        
    except Exception as e:
        display_message(window, "Error", f"Error generating report: {e}")

def generate_report_user(window):
    """Generate a simplified report for the user interface"""
    current_table = window.get_current_table()
    if current_table.rowCount() == 0:
        display_message(window, "Error", "No data available to generate report")
        return

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        import matplotlib.pyplot as plt
        import io
        import datetime
        import os

        # Collect data for charts and table
        data = []
        total_rows = current_table.rowCount()
        cyberbullying_count = 0
        normal_count = 0
        confidence_ranges = {'90-100%': 0, '80-89%': 0, '70-79%': 0, '<70%': 0}

        for row in range(total_rows):
            comment = current_table.item(row, 0).text()
            prediction = current_table.item(row, 1).text()
            confidence = current_table.item(row, 2).text()
            confidence_value = float(confidence.strip('%'))
            
            # Store data for table
            data.append([comment, prediction, confidence])
            
            if prediction == "Cyberbullying":
                cyberbullying_count += 1
            else:
                normal_count += 1
                
            # Categorize confidence
            if confidence_value >= 90:
                confidence_ranges['90-100%'] += 1
            elif confidence_value >= 80:
                confidence_ranges['80-89%'] += 1
            elif confidence_value >= 70:
                confidence_ranges['70-79%'] += 1
            else:
                confidence_ranges['<70%'] += 1

        # Create classification distribution pie chart
        plt.figure(figsize=(6, 4))
        plt.pie([cyberbullying_count, normal_count], 
                labels=['Cyberbullying', 'Normal'],
                autopct='%1.1f%%',
                colors=['#ff9999', '#66b3ff'])
        plt.title('Comment Classification Distribution')
        
        # Save pie chart to memory
        pie_chart_data = io.BytesIO()
        plt.savefig(pie_chart_data, format='png', bbox_inches='tight')
        pie_chart_data.seek(0)
        plt.close()

        # Create confidence distribution bar chart
        plt.figure(figsize=(6, 4))
        bars = plt.bar(confidence_ranges.keys(), confidence_ranges.values())
        plt.title('Confidence Level Distribution')
        plt.xlabel('Confidence Range')
        plt.ylabel('Number of Comments')
        plt.xticks(rotation=45)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        # Save bar chart to memory
        bar_chart_data = io.BytesIO()
        plt.savefig(bar_chart_data, format='png', bbox_inches='tight')
        bar_chart_data.seek(0)
        plt.close()

        # Create the PDF document
        file_path, _ = QFileDialog.getSaveFileName(
            window, "Save Report", "", "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1a237e')
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#303f9f')
        )

        # Content elements
        elements = []

        # Title
        elements.append(Paragraph("Cyberbullying Detection Report", title_style))
        elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%B %d, %Y %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Add charts section
        elements.append(Paragraph("Visual Analysis", subtitle_style))
        
        # Add pie chart
        elements.append(Image(pie_chart_data, width=4*inch, height=3*inch))
        elements.append(Spacer(1, 10))
        
        # Add bar chart
        elements.append(Image(bar_chart_data, width=4*inch, height=3*inch))
        elements.append(Spacer(1, 20))

        # Add summary section
        elements.append(Paragraph("Analysis Summary", subtitle_style))
        summary_data = [
            ["Total Comments Analyzed:", str(total_rows)],
            ["Cyberbullying Comments:", f"{cyberbullying_count} ({(cyberbullying_count/total_rows)*100:.1f}%)"],
            ["Normal Comments:", f"{normal_count} ({(normal_count/total_rows)*100:.1f}%)"],
            ["High Confidence Predictions (>90%):", f"{confidence_ranges['90-100%']} ({(confidence_ranges['90-100%']/total_rows)*100:.1f}%)"]
        ]
        
        summary_table = Table(summary_data, colWidths=[200, 300])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#303f9f')),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # Add detailed results section
        elements.append(Paragraph("Detailed Analysis Results", subtitle_style))
        
        # Prepare table data with headers
        table_data = [['Comment', 'Classification', 'Confidence']] + [
            [Paragraph(comment, styles['Normal']), prediction, confidence]
            for comment, prediction, confidence in data
        ]
        
        # Create the main results table with adjusted widths
        results_table = Table(table_data, colWidths=[400, 80, 80])
        results_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eaf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('WORDWRAP', (0, 0), (-1, -1), True),
        ]))
        elements.append(results_table)

        # Build the PDF
        doc.build(elements)
        
        display_message(window, "Success", "Report generated successfully")
        
    except Exception as e:
        display_message(window, "Error", f"Error generating report: {e}")
