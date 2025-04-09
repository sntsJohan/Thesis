from model import classify_comment

def admin_classify_comment(text):
    """
    Admin interface for classifying a comment using the model.
    This is a wrapper around classify_comment that can be extended with
    admin-specific functionality like logging or enhanced reporting.
    
    Args:
        text (str): The comment text to classify
        
    Returns:
        tuple: (prediction_label, confidence_score)
    """
    # Call the main classification function from model.py
    prediction, confidence = classify_comment(text)
    
    # Could add admin-specific functionality here:
    # - Enhanced logging 
    # - Additional processing
    # - Store results in admin-specific database, etc.
    
    return prediction, confidence

def batch_classify_comments(comments_list):
    """
    Process a batch of comments for admin analysis
    
    Args:
        comments_list (list): List of comment strings to classify
        
    Returns:
        list: List of dictionaries with comment text, prediction and confidence
    """
    results = []
    
    for comment in comments_list:
        prediction, confidence = admin_classify_comment(comment)
        results.append({
            'comment_text': comment,
            'prediction': prediction,
            'confidence': confidence
        })
    
    return results 