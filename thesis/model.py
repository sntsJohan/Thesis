from sample_data import SAMPLE_COMMENTS
import random

def classify_comment(comment):
    """
    Simulate comment classification using sample data.
    For development/testing purposes only.
    """
    # First try to find an exact match in sample data
    for sample in SAMPLE_COMMENTS:
        if comment.lower() == sample["comment"].lower():
            return sample["prediction"], sample["confidence"]
    
    # If no exact match, return random classification
    is_cyberbullying = random.random() < 0.3  # 30% chance of being classified as cyberbullying
    
    if is_cyberbullying:
        return "Cyberbullying", random.uniform(0.70, 0.99)
    else:
        return "Not Cyberbullying", random.uniform(0.75, 0.99)
