from apify_client import ApifyClient
import csv
from api_db import get_api_key

def scrape_comments(fb_url, save_path, filters=None):
    # Get API key from database
    api = get_api_key('apify')
    if not api:
        raise ValueError("API key not found in database. Please set an API key first.")
    
    client = ApifyClient(api)
    
    # Set default filters if none provided
    if filters is None:
        filters = {
            "includeReplies": True,
            "resultsLimit": 50,
            "viewOption": "RANKED_UNFILTERED",
            "timelineOption": "CHRONOLOGICAL",
            "filterPostsByLanguage": False,
            "filterCommentsLanguage": "en",
            "maxComments": 50
        }
    
    # Get max comments limit (used both for API call and local truncation)
    max_comments = filters.get("maxComments", 50)
    
    # Configure actor input based on filters - request slightly more than needed
    # to ensure we get at least the requested amount after filtering
    run_input = {
        "startUrls": [{"url": fb_url}],
        "resultsLimit": max(max_comments + 10, int(max_comments * 1.2)),  # Request 20% more or at least 10 more
        "includeNestedComments": filters.get("includeReplies", True),
        "viewOption": filters.get("viewOption", "RANKED_UNFILTERED"),
    }
    
    # Add timeline option if available
    if "timelineOption" in filters:
        run_input["timelineOption"] = filters["timelineOption"]
        
    # Add language filtering if enabled
    if filters.get("filterPostsByLanguage", False):
        run_input["filterPostsByLanguage"] = True
        run_input["language"] = filters.get("filterCommentsLanguage", "en")
    
    # Run the actor
    run = client.actor("us5srxAYnsrkgUv2v").call(run_input=run_input)

    # Get the results
    comments = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    # Apply strict limit to enforce maxComments
    comments = comments[:max_comments]

    # Write to CSV
    with open(save_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Text', 'Profile Name', 'Profile Picture', 'Date', 'Likes Count', 
                        'Profile ID', 'Is Reply', 'Reply To'])
        
        for item in comments:
            is_reply = item.get("threadingDepth", 0) == 1
            reply_to = ""
            
            if is_reply and "parentComment" in item:
                parent = item["parentComment"]["author"]
                reply_to = f"{parent.get('name', '')} ({parent.get('id', '')})"
            
            writer.writerow([
                item.get("text", "No text"),
                item.get("profileName", "No profileName"),
                item.get("profilePicture", ""),
                item.get("date", ""),
                item.get("likesCount", 0),
                item.get("profileId", ""),
                is_reply,
                reply_to
            ])
    
    return save_path

