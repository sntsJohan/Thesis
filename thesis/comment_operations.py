from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QApplication
from PyQt5.QtCore import Qt
import pandas as pd
from utils import display_message
import reportlab
import matplotlib.pyplot as plt
import io
import datetime
import os
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import re
import numpy as np
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from model import classify_comment
from styles import COLORS

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

    # Guidance text based on classification
    guidance_text = ""
    concern_areas = []
    
    if prediction == "Potentially Harmful":
        guidance_text = "This comment may contain harmful content. Review recommended."
        concern_areas = ["Potential Harassment", "Possible Hate Speech", "Concerning Language"]
    elif prediction == "Requires Review":
        guidance_text = "This comment has elements that may need review. Use discretion."
        concern_areas = ["Ambiguous Intent", "Context Dependent"]
    elif prediction == "Likely Appropriate":
        guidance_text = "This comment appears appropriate based on analysis."
        concern_areas = []

    # Set text contents
    window.details_text_edit.clear()
    window.details_text_edit.append(f"<b>Comment:</b>\n{comment}\n")
    window.details_text_edit.append(f"<b>Commenter:</b> {commenter}\n")
    
    # Color-coded assessment based on prediction level
    assessment_color = COLORS['text']  # Default color
    if prediction == "Potentially Harmful":
        assessment_color = COLORS['potentially_harmful']
    elif prediction == "Requires Review":
        assessment_color = COLORS['requires_attention']
    elif prediction == "Likely Appropriate":
        assessment_color = COLORS['likely_appropriate']
        
    window.details_text_edit.append(f'<b>Assessment:</b> <span style="color:{assessment_color}; font-weight:bold;">{prediction}</span>\n')
    window.details_text_edit.append(f"<b>Confidence:</b> {confidence}\n")
    window.details_text_edit.append(f"<b>Status:</b> {'In List' if comment in window.selected_comments else 'Not in List'}\n")
    window.details_text_edit.append(f"<b>Guidance:</b> {guidance_text}\n")
    
    if concern_areas:
        window.details_text_edit.append("<b>Areas of Concern:</b>")
        cursor = window.details_text_edit.textCursor()
        for area in concern_areas:
            cursor.insertHtml(f'<span style="background-color: ["secondary"]; border-radius: 4px; padding: 2px 4px; margin: 2px; display: inline-block;">{area}</span> ')
        window.details_text_edit.setTextCursor(cursor)
    
    # Additional guidance disclaimer
    window.details_text_edit.append("\n<i>Note: This is an AI-assisted assessment meant to guide human review, not to provide definitive judgments.</i>")

def show_summary(window):
    total_comments = window.output_table.rowCount()
    if total_comments == 0:
        display_message(window, "Error", "No comments to summarize")
        return

    potentially_harmful_count = 0
    requires_review_count = 0
    likely_appropriate_count = 0
    high_confidence_count = 0  # Comments with confidence > 90%

    for row in range(total_comments):
        prediction = window.output_table.item(row, 1).text()
        confidence = float(window.output_table.item(row, 2).text().strip('%')) / 100

        if prediction == "Potentially Harmful":
            potentially_harmful_count += 1
        elif prediction == "Requires Review":
            requires_review_count += 1
        elif prediction == "Likely Appropriate":
            likely_appropriate_count += 1

        if confidence > 0.9:
            high_confidence_count += 1

    summary_text = (
        f"Analysis Summary:\n\n"
        f"Total Comments Analyzed: {total_comments}\n"
        f"<span style='color:{COLORS['potentially_harmful']}'>Potentially Harmful Comments: {potentially_harmful_count} ({(potentially_harmful_count/total_comments)*100:.1f}%)</span>\n"
        f"<span style='color:{COLORS['requires_attention']}'>Comments Needing Review: {requires_review_count} ({(requires_review_count/total_comments)*100:.1f}%)</span>\n"
        f"<span style='color:{COLORS['likely_appropriate']}'>Likely Appropriate Comments: {likely_appropriate_count} ({(likely_appropriate_count/total_comments)*100:.1f}%)</span>\n"
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

def generate_report(window):
    """
    Generate comprehensive analysis report with charts, word cloud, and interpretations.
    Works for both admin and user interfaces.
    """
    current_table = window.get_current_table()
    if not current_table or current_table.rowCount() == 0:
        display_message(window, "Error", "No data available to generate report")
        return

    # Show loading overlay during the entire report generation process
    window.loading_overlay.show("Generating report...")
    QApplication.processEvents()  # Force UI update to show loading overlay
    
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
        import matplotlib.pyplot as plt
        from wordcloud import WordCloud
        import io
        import datetime
        import os
        import re
        from stopwords import TAGALOG_STOP_WORDS

        # Collect data for charts and table
        data = []
        total_rows = current_table.rowCount()
        potentially_harmful_count = 0
        requires_review_count = 0
        likely_appropriate_count = 0
        confidence_ranges = {'90-100%': 0, '80-89%': 0, '70-79%': 0, '<70%': 0}
        all_comments = []

        for row in range(total_rows):
            comment_item = current_table.item(row, 0)
            prediction_item = current_table.item(row, 1)
            confidence_item = current_table.item(row, 2)
            
            if not comment_item or not prediction_item or not confidence_item:
                continue
                
            comment = comment_item.text()
            comment_text = comment_item.data(Qt.UserRole) or comment
            prediction = prediction_item.text()
            confidence = confidence_item.text()
            
            # Convert confidence from string to float
            try:
                confidence_value = float(confidence.strip('%'))
            except ValueError:
                confidence_value = 0.0
            
            # Store data for table
            data.append([comment_text, prediction, confidence])
            all_comments.append(comment_text)
            
            # Count by prediction type
            if prediction == "Potentially Harmful":
                potentially_harmful_count += 1
            elif prediction == "Requires Review":
                requires_review_count += 1
            elif prediction == "Likely Appropriate":
                likely_appropriate_count += 1
                
            # Categorize confidence
            if confidence_value >= 90:
                confidence_ranges['90-100%'] += 1
            elif confidence_value >= 80:
                confidence_ranges['80-89%'] += 1
            elif confidence_value >= 70:
                confidence_ranges['70-79%'] += 1
            else:
                confidence_ranges['<70%'] += 1
                
        # Perform advanced sentiment analysis using transformers
        def get_sentiment_analyzer():
            try:
                # First try loading a multilingual model to handle both English and Tagalog
                model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForSequenceClassification.from_pretrained(model_name)
                sentiment_analyzer = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
                return sentiment_analyzer
            except Exception as e:
                print(f"Error loading multilingual sentiment model: {e}")
                try:
                    # Fall back to default English model if multilingual not available
                    sentiment_analyzer = pipeline("sentiment-analysis")
                    return sentiment_analyzer
                except Exception as e:
                    print(f"Error loading sentiment model: {e}")
                    return None

        def analyze_sentiment(text, analyzer):
            if not analyzer:
                # Fallback to basic approach if models aren't available
                positive_words = ["good", "great", "excellent", "awesome", "nice", "love", "happy"]
                negative_words = ["bad", "worst", "terrible", "horrible", "hate", "dislike", "awful"]
                
                text = text.lower()
                words = text.split()
                
                positive_count = sum(1 for word in words if word in positive_words)
                negative_count = sum(1 for word in words if word in negative_words)
                
                if positive_count > negative_count:
                    return "Positive"
                elif negative_count > positive_count:
                    return "Negative"
                else:
                    return "Neutral"
            
            try:
                # Most models have character limits
                if len(text) > 512:
                    text = text[:512]
                
                result = analyzer(text)
                
                # Parse result based on model output format
                label = result[0]['label']
                
                # Map different model outputs to standardized format
                if 'POSITIVE' in label or '5' in label or '4' in label:
                    return "Positive"
                elif 'NEGATIVE' in label or '1' in label or '2' in label:
                    return "Negative"
                else:
                    return "Neutral"
            except Exception as e:
                print(f"Error in sentiment analysis: {e}")
                return "Neutral"

        print("Initializing sentiment analyzer...")
        sentiment_analyzer = get_sentiment_analyzer()
        
        print("Analyzing sentiment for all comments...")
        # Use it for all comments (but limit to 100 comments max for performance)
        sample_comments = all_comments[:100] if len(all_comments) > 100 else all_comments
        all_sentiments = [analyze_sentiment(comment, sentiment_analyzer) for comment in sample_comments]
        
        print("Analyzing sentiment for cyberbullying comments...")
        # Analyze cyberbullying comments
        sample_cb_comments = [comment for comment, prediction, _ in data[:100] if prediction == "Cyberbullying"]
        cb_sentiments = [analyze_sentiment(comment, sentiment_analyzer) for comment in sample_cb_comments]
        
        # Determine overall sentiment
        positive_count = all_sentiments.count("Positive")
        negative_count = all_sentiments.count("Negative")
        neutral_count = all_sentiments.count("Neutral")

        # Determine primary sentiment
        if positive_count > negative_count and positive_count > neutral_count:
            sentiment_result = "Positive"
        elif negative_count > positive_count and negative_count > neutral_count:
            sentiment_result = "Negative"
        else:
            sentiment_result = "Neutral"

        # Determine cyberbullying content sentiment if applicable
        if cb_sentiments:
            cb_positive_count = cb_sentiments.count("Positive")
            cb_negative_count = cb_sentiments.count("Negative")
            cb_neutral_count = cb_sentiments.count("Neutral")
            
            if cb_positive_count > cb_negative_count and cb_positive_count > cb_neutral_count:
                cb_sentiment_result = "Positive"
            elif cb_negative_count > cb_positive_count and cb_negative_count > cb_neutral_count:
                cb_sentiment_result = "Negative"
            else:
                cb_sentiment_result = "Neutral"
        else:
            cb_sentiment_result = "N/A"
            
        print(f"Overall sentiment: {sentiment_result}")
        print(f"Cyberbullying content sentiment: {cb_sentiment_result}")

        # Create classification distribution pie chart
        plt.figure(figsize=(6, 4))
        plt.pie([potentially_harmful_count, requires_review_count, likely_appropriate_count], 
                labels=['Potentially Harmful', 'Requires Review', 'Likely Appropriate'],
                autopct='%1.1f%%',
                colors=[COLORS['potentially_harmful'], COLORS['requires_attention'], COLORS['likely_appropriate']],
                textprops={'color': 'white'})
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
        
        # Create sentiment analysis chart
        plt.figure(figsize=(6, 4))
        sentiment_counts = [all_sentiments.count("Positive"), all_sentiments.count("Neutral"), all_sentiments.count("Negative")]
        sentiment_labels = ['Positive', 'Neutral', 'Negative']
        sentiment_colors = ['#66cc99', '#6699cc', '#cc6666']
        
        # Create bar chart for sentiment distribution
        plt.bar(sentiment_labels, sentiment_counts, color=sentiment_colors)
        plt.title('Sentiment Distribution')
        plt.ylabel('Number of Comments')
        
        # Add value labels on bars
        for i, count in enumerate(sentiment_counts):
            plt.text(i, count + 0.5, str(count), ha='center')
            
        # Save sentiment chart to memory
        sentiment_chart_data = io.BytesIO()
        plt.savefig(sentiment_chart_data, format='png', bbox_inches='tight')
        sentiment_chart_data.seek(0)
        plt.close()
        
        # Generate Word Cloud
        try:
            # Text preprocessing function
            def preprocess_text(text):
                text = text.lower()
                text = re.sub(r'http\S+|www\S+|https\S+', '', text)
                text = re.sub(r'[^\w\s]', '', text)
                text = ' '.join(text.split())
                return text

            # Create separate word clouds for normal and potentially harmful comments
            normal_comments = [comment for comment, prediction, _ in data if prediction == "Likely Appropriate"]
            requires_review_comments = [comment for comment, prediction, _ in data if prediction == "Requires Review"]
            potentially_harmful_comments = [comment for comment, prediction, _ in data if prediction == "Potentially Harmful"]
            
            processed_normal = [preprocess_text(comment) for comment in normal_comments] if normal_comments else [""]
            processed_rr = [preprocess_text(comment) for comment in requires_review_comments] if requires_review_comments else [""]
            processed_cb = [preprocess_text(comment) for comment in potentially_harmful_comments] if potentially_harmful_comments else [""]
            processed_all = [preprocess_text(comment) for comment in all_comments]
            
            # Calculate word frequencies first - before creating the wordcloud
            from collections import Counter
            
            # Get most common words across all comments
            all_words = ' '.join(processed_all).split()
            word_counts = Counter(all_words)
            for word in TAGALOG_STOP_WORDS:
                if word in word_counts:
                    del word_counts[word]
            
            # Get most common words in cyberbullying comments
            cb_words = ' '.join(processed_cb).split()
            cb_word_counts = Counter(cb_words)
            for word in TAGALOG_STOP_WORDS:
                if word in cb_word_counts:
                    del cb_word_counts[word]
            
            # Store most common words for later reference
            common_words = [word for word, _ in word_counts.most_common(5)] if word_counts else []
            common_cb_words = [word for word, _ in cb_word_counts.most_common(5)] if cb_word_counts else []
            
            print(f"Most common words: {common_words}")
            print(f"Most common words in cyberbullying: {common_cb_words}")
            
            # Generate combined word cloud
            wordcloud = WordCloud(
                width=800, 
                height=400,
                background_color='white',
                max_words=100,
                stopwords=TAGALOG_STOP_WORDS,
                collocations=False,
                colormap='plasma'
            ).generate(' '.join(processed_all))

            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Most Common Words in All Comments')
            
            # Save combined word cloud to memory
            wordcloud_data = io.BytesIO()
            plt.savefig(wordcloud_data, format='png', bbox_inches='tight', pad_inches=0.1)
            plt.close()
            wordcloud_data.seek(0)
            
            # Generate potentially harmful content word cloud if there are enough comments
            if len(processed_cb) > 5:
                cb_wordcloud = WordCloud(
                    width=800, 
                    height=400,
                    background_color='white',
                    max_words=50,
                    stopwords=TAGALOG_STOP_WORDS,
                    collocations=False,
                    colormap='plasma'
                ).generate(' '.join(processed_cb))

                plt.figure(figsize=(10, 5))
                plt.imshow(cb_wordcloud, interpolation='bilinear')
                plt.axis('off')
                plt.title('Common Words in Potentially Harmful Comments')
                
                # Save potentially harmful content word cloud to memory
                cb_wordcloud_data = io.BytesIO()
                plt.savefig(cb_wordcloud_data, format='png', bbox_inches='tight', pad_inches=0.1)
                plt.close()
                cb_wordcloud_data.seek(0)
            else:
                cb_wordcloud_data = None
            
        except Exception as wc_error:
            print(f"Error generating word cloud: {wc_error}")
            wordcloud_data = None
            cb_wordcloud_data = None

        # All report data has been prepared, now ask user where to save
        # Only at this point we'll interrupt the loading overlay for file selection
        # Note: We're keeping the overlay visible during file selection
        
        # Get file path for saving report
        file_path, _ = QFileDialog.getSaveFileName(
            window, "Save Report", "", "PDF Files (*.pdf)"
        )
        
        # If user cancelled, return without error
        if not file_path:
            return False
        
        # Update loading message for PDF creation phase
        window.loading_overlay.show("Creating PDF report...")
        QApplication.processEvents()  # Force UI update to show loading overlay

        # Create the PDF document
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
        
        interpretation_style = ParagraphStyle(
            'Interpretation',
            parent=styles['Normal'],
            fontSize=10,
            spaceBefore=5,
            spaceAfter=15,
            textColor=colors.HexColor('#37474f'),
            borderWidth=1,
            borderColor=colors.HexColor('#e0e0e0'),
            borderPadding=10,
            borderRadius=5,
            backColor=colors.HexColor('#f5f5f5')
        )

        recommendation_style = ParagraphStyle(
            'Recommendation',
            parent=styles['Normal'],
            fontSize=10,
            spaceBefore=5,
            spaceAfter=15,
            textColor=colors.HexColor('#37474f'),
            borderWidth=1,
            borderColor=colors.HexColor('#e0e0e0'),
            borderPadding=10,
            borderRadius=5,
            backColor=colors.HexColor('#f5f5f5')
        )

        small_style = ParagraphStyle(
            'SmallText',
            parent=styles['Normal'],
            fontSize=8,
            spaceBefore=5,
            spaceAfter=5,
            textColor=colors.HexColor('#37474f'),
            borderWidth=1,
            borderColor=colors.HexColor('#e0e0e0'),
            borderPadding=10,
            borderRadius=5,
            backColor=colors.HexColor('#f5f5f5')
        )

        # Content elements
        elements = []

        # Determine the base path relative to this script
        base_path = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_path, "assets", "applogo.png")

        # Create header with logo if available
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

        # Add timestamp
        elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%B %d, %Y %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Add executive summary
        elements.append(Paragraph("Executive Summary", subtitle_style))
        elements.append(Spacer(1, 5))
        
        # Generate executive summary text based on analysis results
        cb_percentage = (potentially_harmful_count/total_rows)*100 if total_rows > 0 else 0
        cyber_count = potentially_harmful_count
        
        # Use the pre-calculated common words from earlier
        if cb_percentage > 0:
            # Make sure common_cb_words is defined and not empty
            cb_terms = ', '.join(common_cb_words) if common_cb_words else 'N/A'
            
            summary_text = f"""
            This report analyzes {total_rows} comments for potential cyberbullying content. The analysis found that <b>{cb_percentage:.1f}%</b> of the 
            comments contain language consistent with cyberbullying. A total of <b>{cyber_count}</b> comments were identified as potentially problematic.
            <br/><br/>
            Key findings:<br/>
            &bull; Most common terms in problematic comments: {cb_terms}<br/>
            &bull; Primary sentiment in flagged comments: {sentiment_result if sentiment_result else 'Neutral'}<br/>
            <br/>
            Based on these findings, {'immediate attention is recommended' if cb_percentage >= 25 else 'continued monitoring is advised'}.
            Detailed analysis and specific recommendations are provided in the following sections.
            """
        else:
            summary_text = f"""
            This report analyzes {total_rows} comments for potential cyberbullying content. No cyberbullying content was detected in this analysis.
            <br/><br/>
            Key findings:<br/>
            &bull; All comments appear to contain appropriate language<br/>
            &bull; Primary sentiment in all comments: {sentiment_result if sentiment_result else 'Neutral'}<br/>
            <br/>
            Continued monitoring is advised as a precautionary measure, though no immediate action is required.
            """
            
        elements.append(Paragraph(summary_text, interpretation_style))
        elements.append(Spacer(1, 20))
        
        # Add analysis details
        elements.append(Paragraph("Analysis Details", subtitle_style))
        
        # Add summary section
        elements.append(Paragraph("Analysis Summary", subtitle_style))
        
        # Calculate statistics and percentages
        cb_percentage = (potentially_harmful_count/total_rows)*100 if total_rows > 0 else 0
        rr_percentage = (requires_review_count/total_rows)*100 if total_rows > 0 else 0
        la_percentage = (likely_appropriate_count/total_rows)*100 if total_rows > 0 else 0
        high_confidence = confidence_ranges['90-100%']
        high_confidence_percentage = (high_confidence/total_rows)*100 if total_rows > 0 else 0
        
        # Prepare summary data
        summary_data = [
            ["Total Comments Analyzed:", str(total_rows)],
            ["Potentially Harmful Comments:", f"{potentially_harmful_count} ({cb_percentage:.1f}%)"],
            ["Requires Review Comments:", f"{requires_review_count} ({rr_percentage:.1f}%)"],
            ["Likely Appropriate Comments:", f"{likely_appropriate_count} ({la_percentage:.1f}%)"],
            ["High Confidence Predictions (>90%):", f"{high_confidence} ({high_confidence_percentage:.1f}%)"]
        ]
        
        # Add selected comment count if applicable
        if hasattr(window, 'selected_comments'):
            summary_data.append(["Comments in Selection List:", str(len(window.selected_comments))])
        
        # Create summary table
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
        elements.append(Spacer(1, 10))
        
        # Add interpretation of summary results
        interpretation_text = ""
        if cb_percentage > 50:
            interpretation_text = f"The analysis shows that a majority ({cb_percentage:.1f}%) of the comments are classified as cyberbullying. This indicates significant presence of harmful content that may require moderation or intervention."
        elif cb_percentage > 30:
            interpretation_text = f"The analysis shows a considerable amount ({cb_percentage:.1f}%) of comments classified as cyberbullying, which suggests notable presence of potentially harmful content."
        elif cb_percentage > 10:
            interpretation_text = f"The analysis detected some cyberbullying content ({cb_percentage:.1f}%), but the majority of comments appear to be normal."
        else:
            interpretation_text = f"The analysis found minimal cyberbullying content ({cb_percentage:.1f}%). Most comments appear to be normal and non-harmful."
            
        # Add confidence interpretation
        if high_confidence_percentage > 80:
            interpretation_text += f" The model shows high confidence in its predictions, with {high_confidence_percentage:.1f}% of predictions having over 90% confidence."
        elif high_confidence_percentage > 50:
            interpretation_text += f" The model shows moderate confidence in its predictions, with {high_confidence_percentage:.1f}% of predictions having over 90% confidence."
        else:
            interpretation_text += f" The model shows relatively low confidence in many of its predictions, with only {high_confidence_percentage:.1f}% having over 90% confidence. Results may benefit from manual review."
        
        elements.append(Paragraph(interpretation_text, interpretation_style))
        elements.append(Spacer(1, 10))

        # Add charts section
        elements.append(PageBreak())
        elements.append(Paragraph("Visual Analysis", subtitle_style))
        
        # Add pie chart
        if pie_chart_data:
            elements.append(Paragraph("Classification Distribution", subtitle_style))
            elements.append(Spacer(1, 5))
            elements.append(Image(pie_chart_data, width=400, height=300))
            elements.append(Spacer(1, 10))
            
            # Add interpretation of pie chart
            pie_interpretation = ""
            if cb_percentage >= 50:
                pie_interpretation = f"The chart shows a concerning distribution with {cb_percentage:.1f}% of comments classified as cyberbullying. This high percentage indicates a significant moderation challenge that requires immediate attention."
            elif cb_percentage >= 25:
                pie_interpretation = f"The chart shows a moderate level of concerning content with {cb_percentage:.1f}% of comments classified as cyberbullying. This indicates the need for enhanced monitoring and targeted interventions."
            elif cb_percentage > 0:
                pie_interpretation = f"The chart shows a relatively small portion ({cb_percentage:.1f}%) of comments classified as cyberbullying. While not alarming, this still indicates the presence of some problematic content that should be monitored."
            else:
                pie_interpretation = "The chart shows no cyberbullying content was detected in the analyzed comments, indicating a healthy communication environment."
                
            elements.append(Paragraph(pie_interpretation, interpretation_style))
            elements.append(Spacer(1, 20))

        # Add confidence distribution bar chart
        elements.append(PageBreak())
        elements.append(Paragraph("Confidence Level Distribution", subtitle_style))
        elements.append(Spacer(1, 5))
        if bar_chart_data:
            elements.append(Image(bar_chart_data, width=400, height=300))
            elements.append(Spacer(1, 10))

            # Interpretation of confidence bar chart
            conf_interpretation = ""
            if high_confidence_percentage > 80:
                conf_interpretation = f"The high confidence levels ({high_confidence_percentage:.1f}% > 90%) suggest the model's predictions are generally reliable for this dataset."
            elif high_confidence_percentage > 50:
                conf_interpretation = f"The moderate confidence levels ({high_confidence_percentage:.1f}% > 90%) suggest the model is reasonably certain, but some predictions may benefit from manual review."
            else:
                conf_interpretation = f"The lower confidence levels ({high_confidence_percentage:.1f}% > 90%) indicate that while the model provides insights, manual review of uncertain predictions is recommended for higher accuracy."
                
            elements.append(Paragraph(conf_interpretation, interpretation_style))
            elements.append(Spacer(1, 20))

        # Add sentiment analysis chart
        if sentiment_chart_data:
            elements.append(PageBreak())
            elements.append(Paragraph("Sentiment Analysis", subtitle_style))
            elements.append(Spacer(1, 5))
            elements.append(Image(sentiment_chart_data, width=400, height=300))
            elements.append(Spacer(1, 10))
            
            # Add interpretation of sentiment chart
            if sentiment_result == "Negative" and cb_percentage > 25:
                sentiment_interpretation = "The sentiment analysis reveals a predominantly negative tone in the comments, which correlates with the high level of cyberbullying content detected. This suggests a potentially toxic communication environment that requires intervention."
            elif sentiment_result == "Negative":
                sentiment_interpretation = "Despite the relatively low level of cyberbullying content, the sentiment analysis shows a predominantly negative tone. This may indicate underlying tensions or dissatisfaction that could escalate if not addressed."
            elif sentiment_result == "Positive" and cb_percentage > 25:
                sentiment_interpretation = "Interestingly, despite the significant presence of cyberbullying content, the overall positive sentiment suggests the harmful behavior may be concentrated among a smaller subset of users or discussions."
            elif sentiment_result == "Positive":
                sentiment_interpretation = "The sentiment analysis shows a predominantly positive tone, consistent with the low levels of cyberbullying content detected. This suggests a generally healthy communication environment."
            else:
                sentiment_interpretation = "The sentiment analysis shows a mixed or neutral distribution of sentiment across the comments, suggesting varied emotional content that requires careful monitoring."
                
            elements.append(Paragraph(sentiment_interpretation, interpretation_style))
            elements.append(Spacer(1, 20))

        # Add word cloud
        if wordcloud_data:
            elements.append(PageBreak())
            elements.append(Paragraph("Word Frequency Analysis (All Comments)", subtitle_style))
            elements.append(Spacer(1, 5))
            elements.append(Image(wordcloud_data, width=400, height=300))
            elements.append(Spacer(1, 10))
            
            # Add interpretation of word cloud
            if common_words:
                word_terms = ', '.join(common_words[:3])
                word_cloud_interpretation = f"The word cloud highlights the most frequent terms across all comments. Terms such as {word_terms} appear frequently in the dataset, providing insight into common discussion topics."
            else:
                word_cloud_interpretation = "The word cloud shows the distribution of terms across all comments. No specific concerning patterns were identified in the frequently used words."
                
            elements.append(Paragraph(word_cloud_interpretation, interpretation_style))
            elements.append(Spacer(1, 20))
            
            # Add cyberbullying-specific word cloud if available
            if cb_wordcloud_data and potentially_harmful_count > 5:
                elements.append(PageBreak())
                elements.append(Paragraph("Cyberbullying Word Frequency Analysis", subtitle_style))
                elements.append(Spacer(1, 5))
                elements.append(Image(cb_wordcloud_data, width=400, height=300))
                elements.append(Spacer(1, 10))
                
                # Add interpretation of cyberbullying word cloud
                cb_interpretation = f"This word cloud specifically highlights the most common terms found in comments classified as cyberbullying. These terms may be useful indicators for developing more targeted content moderation filters and understanding the nature of problematic content in the dataset."
                
                # Add more specific interpretation based on cyberbullying percentage and common words
                if common_cb_words and len(common_cb_words) >= 3:
                    cb_terms = ', '.join(common_cb_words[:3])
                    cb_interpretation += f" The most frequent terms in cyberbullying comments were: {cb_terms}."
                
                if cb_percentage > 30:
                    cb_interpretation += f" The high frequency of these terms ({cb_percentage:.1f}% of all comments) suggests a persistent pattern of harmful language that should be addressed."
                elif cb_percentage > 10:
                    cb_interpretation += f" With {cb_percentage:.1f}% of comments containing these terms, there is a moderate level of concerning content that warrants attention."
                
                elements.append(Paragraph(cb_interpretation, interpretation_style))
                elements.append(Spacer(1, 20))

        # Add detailed results section
        elements.append(PageBreak())
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
        
        # Add recommendations section
        elements.append(PageBreak())
        elements.append(Paragraph("Recommendations", title_style))
        elements.append(Spacer(1, 10))
        
        # Determine recommendations based on percentage and sentiment
        sentiment_factor = ""
        if sentiment_result == "Negative" and cb_percentage > 15:
            sentiment_factor = "The predominantly negative sentiment coupled with cyberbullying content suggests an environment where negativity may be reinforcing harmful behavior."
        elif sentiment_result == "Negative":
            sentiment_factor = "The predominantly negative sentiment, despite lower levels of cyberbullying, indicates potential underlying tensions that could escalate."
        elif sentiment_result == "Positive" and cb_percentage > 15:
            sentiment_factor = "Despite the presence of cyberbullying content, the overall positive sentiment suggests the harmful behavior may be concentrated in specific user groups or discussions."
        
        if cb_percentage >= 50:
            recommendation_text = f"""
            <b>High cyberbullying content detected ({cb_percentage:.1f}%)</b><br/><br/>
            
            1. <b>Immediate Action Required:</b> The high percentage of cyberbullying content indicates a serious problem that requires prompt intervention.<br/><br/>
            
            2. <b>Content Moderation:</b> Implement stricter comment moderation measures, including:<br/>
               &bull; Pre-approval of comments before they appear publicly<br/>
               &bull; Automatic filtering of harmful language<br/>
               &bull; Temporary comment restrictions until the situation improves<br/><br/>
            
            3. <b>Community Guidelines:</b> Establish or reinforce clear community guidelines that explicitly prohibit harassment, hate speech, and cyberbullying.<br/><br/>
            
            4. <b>Educational Outreach:</b> Consider educational initiatives to raise awareness about the impact of cyberbullying and promote positive online interaction.<br/><br/>
            
            5. <b>Regular Monitoring:</b> Continue to monitor the comment section closely and conduct follow-up analyses to track improvement.<br/><br/>
            
            {sentiment_factor}
            """
        elif cb_percentage >= 25:
            recommendation_text = f"""
            <b>Moderate cyberbullying content detected ({cb_percentage:.1f}%)</b><br/><br/>
            
            1. <b>Enhanced Monitoring:</b> Increase the frequency of comment section review to identify and address problematic content quickly.<br/><br/>
            
            2. <b>Targeted Moderation:</b> Focus moderation efforts on:<br/>
               &bull; Comments containing the most frequent harmful terms identified in the word cloud<br/>
               &bull; Threads or discussions that may be escalating in negativity<br/><br/>
            
            3. <b>Community Engagement:</b> Actively engage with the community to promote positive interactions and discourage negative behavior.<br/><br/>
            
            4. <b>Clear Guidelines:</b> Ensure your community guidelines are visible and clearly communicate expectations for respectful communication.<br/><br/>
            
            5. <b>Follow-up Analysis:</b> Conduct a follow-up analysis within 2-4 weeks to monitor for improvement or deterioration.<br/><br/>
            """
        else:
            recommendation_text = f"""
            <b>Low cyberbullying content detected ({cb_percentage:.1f}%)</b><br/><br/>
            
            1. <b>Continued Monitoring:</b> While the current levels of problematic content are low, maintaining regular monitoring is recommended.<br/><br/>
            
            2. <b>Preventive Measures:</b> Consider implementing subtle preventive measures such as:<br/>
               &bull; Positive reinforcement for constructive comments<br/>
               &bull; Occasional reminders about community guidelines<br/><br/>
            
            3. <b>Community Building:</b> Focus on strengthening the positive aspects of your community to maintain the healthy environment.<br/><br/>
            
            4. <b>Periodic Assessment:</b> Schedule periodic assessments (every 1-2 months) to ensure the comment section maintains its positive nature.<br/><br/>
            
            5. <b>Educational Resources:</b> Make resources available for users to learn about digital citizenship and respectful online communication.<br/><br/>
            """

        elements.append(Paragraph(recommendation_text, recommendation_style))
        
        # Add contact information and final note
        elements.append(Spacer(1, 20))
        
        # Add technical notes section
        elements.append(Paragraph("Technical Notes", subtitle_style))
        technical_notes = f"""
        &bull; This report was generated using an mBERT and SVM-based cyberbullying detection system<br/>
        &bull; Classification confidence is based on the prediction model's probability score<br/>
        &bull; Word clouds exclude common stop words in both English and Tagalog<br/>
        &bull; Sentiment analysis utilizes a specialized model designed for social media content<br/>
        &bull; The system may not catch all instances of cyberbullying, particularly those using coded language or novel terms<br/>
        """
        elements.append(Paragraph(technical_notes, small_style))
        elements.append(Spacer(1, 10))
        
        elements.append(Paragraph("For additional support or questions about this report, please contact the system administrator.", interpretation_style))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"Report generated on {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}", small_style))

        # Build the PDF
        doc.build(elements)
        
        display_message(window, "Success", f"Report saved to {file_path}")
        return True
    except Exception as e:
        display_message(window, "Error", f"Error generating report: {e}")
        print(f"Error generating report: {e}")
        return False
    finally:
        # Always hide loading overlay when finished
        window.loading_overlay.hide()
        QApplication.processEvents()  # Force UI update to hide loading overlay

# Alias functions to maintain compatibility with existing code
generate_report_from_window = generate_report
generate_report_user = generate_report