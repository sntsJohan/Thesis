from apify_client import ApifyClient
import csv

api = "apify_api_9vMtU9uC3KuUmdh9xrxDb4htCvQyXz09REvx"

def scrape_comments(fb_url, save_path, include_replies=True):
    client = ApifyClient(api)
    run_input = {
        "startUrls": [{"url": fb_url}],
        "resultsLimit": 1000,
        "includeNestedComments": include_replies,
        "viewOption": "RANKED_UNFILTERED",
    }
    run = client.actor("us5srxAYnsrkgUv2v").call(run_input=run_input)

    comments = list(client.dataset(run["defaultDatasetId"]).iterate_items())

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

