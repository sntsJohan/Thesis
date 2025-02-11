from sample_data import SAMPLE_POST_COMMENTS
import random

def scrape_comments(url):
    """
    Simulate comment scraping using sample data.
    For development/testing purposes only.
    """
    # Simulate loading time
    import time
    time.sleep(1)
    
    # Return 3-8 random comments from sample data
    num_comments = random.randint(3, 8)
    return random.sample(SAMPLE_POST_COMMENTS, num_comments)
