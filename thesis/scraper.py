from apify_client import ApifyClient
import csv
import time

api = "apify_api_9vMtU9uC3KuUmdh9xrxDb4htCvQyXz09REvx"

def scrape_comments(fb_url, save_path):
    client = ApifyClient(api)
    run_input = {
        "startUrls": [{"url": fb_url}],
        "resultsLimit": 1000,
        "includeNestedComments": True,  # Changed to True to get replies
        "viewOption": "RANKED_UNFILTERED",
    }
    run = client.actor("us5srxAYnsrkgUv2v").call(run_input=run_input)

    with open(save_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Text', 'Profile Name', 'Profile Picture', 'Date', 'Likes Count', 'Profile ID', 'Is Reply', 'Reply To'])
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            is_reply = bool(item.get("replyTo", False))
            reply_to = item.get("replyToName", "") if is_reply else ""
            
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

