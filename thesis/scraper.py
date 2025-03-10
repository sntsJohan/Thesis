from apify_client import ApifyClient
import csv
import time
import base64

api = "apify_api_9vMtU9uC3KuUmdh9xrxDb4htCvQyXz09REvx"

def decode_fb_id(encoded_id):
    """Decode Facebook's base64 encoded ID and return the parts"""
    try:
        decoded = base64.b64decode(encoded_id).decode('utf-8')
        parts = decoded.split('_')
        return parts if len(parts) > 1 else [decoded, None]
    except:
        return [None, None]

def detect_replies(comments):
    """Analyze comments to detect which ones are replies based on ID structure"""
    # Extract all comment IDs first
    all_ids = set()
    for comment in comments:
        comment_id = comment.get('id', '')
        if comment_id:
            _, comment_num = decode_fb_id(comment_id)
            if comment_num:
                all_ids.add(comment_num)
    
    # Check each comment to see if it's a reply
    for comment in comments:
        comment_id = comment.get('id', '')
        if comment_id:
            parent_id, comment_num = decode_fb_id(comment_id)
            # If the parent ID exists in our set of comment IDs, it's a reply
            comment['is_reply'] = bool(parent_id in all_ids)
            comment['reply_to_id'] = parent_id if comment['is_reply'] else ''
    
    return comments

def scrape_comments(fb_url, save_path, include_replies=True):
    client = ApifyClient(api)
    run_input = {
        "startUrls": [{"url": fb_url}],
        "resultsLimit": 1000,
        "includeNestedComments": include_replies,  # Use the parameter here
        "viewOption": "RANKED_UNFILTERED",
    }
    run = client.actor("us5srxAYnsrkgUv2v").call(run_input=run_input)

    # Collect all comments first to analyze reply structure
    comments = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    comments = detect_replies(comments)

    with open(save_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Text', 'Profile Name', 'Profile Picture', 'Date', 'Likes Count', 
                        'Profile ID', 'Is Reply', 'Reply To'])
        
        for item in comments:
            writer.writerow([
                item.get("text", "No text"),
                item.get("profileName", "No profileName"),
                item.get("profilePicture", ""),
                item.get("date", ""),
                item.get("likesCount", 0),
                item.get("profileId", ""),
                item.get("is_reply", False),
                item.get("reply_to_id", "")
            ])
    
    return save_path

