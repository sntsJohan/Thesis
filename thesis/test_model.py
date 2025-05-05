#!/usr/bin/env python
from model import classify_comment

def test_model():
    """Test the guidance-oriented content assessment model with sample comments"""
    
    test_comments = [
        "I really enjoyed your presentation today, great work!",
        "You are so stupid, nobody likes you",
        "Looking forward to seeing you at the meeting tomorrow",
        "Just kill yourself already, you're worthless",
        "The weather is nice today, isn't it?",
        "You're not as bad as some of the others I guess",
        "I don't really like this, but whatever",
        "Maybe consider doing something else with your life?",
        "This is kind of boring honestly",
        "I can't believe you think that's okay"
    ]
    
    print("\nTesting guidance-oriented content assessment model...")
    print("-" * 70)
    print(f"{'COMMENT':<40} | {'ASSESSMENT':<20} | {'CONFIDENCE'}")
    print("-" * 70)
    
    for comment in test_comments:
        assessment, confidence = classify_comment(comment)
        print(f"{comment[:37] + '...' if len(comment) > 37 else comment:<40} | {assessment:<20} | {confidence:.1f}%")
    
    print("-" * 70)
    print("Assessment levels explanation:")
    print("• Potentially Harmful: Content with strong indicators of harm. Should be prioritized for review.")
    print("• Requires Review: Content with ambiguous intent that should be reviewed")
    print("• Likely Appropriate: Content that appears non-harmful based on the model.")
    print("\nNote: This is a guidance tool to assist human review, not to make definitive judgments.")

if __name__ == "__main__":
    test_model() 