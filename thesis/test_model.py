#!/usr/bin/env python
from model import classify_comment

def test_model():
    """Test the cyberbullying detection model with sample comments"""
    
    test_comments = [
        "I really enjoyed your presentation today, great work!",
        "You are so stupid, nobody likes you",
        "Looking forward to seeing you at the meeting tomorrow",
        "Just kill yourself already, you're worthless",
        "The weather is nice today, isn't it?"
    ]
    
    print("\nTesting cyberbullying detection model...")
    print("-" * 60)
    
    for comment in test_comments:
        result, confidence = classify_comment(comment)
        print(f"\nComment: \"{comment}\"")
        print(f"Classification: {result}")
        print(f"Confidence score: {confidence:.4f}")
    
    print("-" * 60)
    print("Model testing complete.")

if __name__ == "__main__":
    test_model() 