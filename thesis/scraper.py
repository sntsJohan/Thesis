from apify_client import ApifyClient
import csv
import time

def scrape_comments(fb_url, save_path):
    client = ApifyClient("apify_api_KOPcEZ8wzyIM4n9c7MEkub7mz0HbHn1iV3Df")
    run_input = {
        "startUrls": [{"url": fb_url}],
        "resultsLimit": 1000,
        "includeNestedComments": False,
        "viewOption": "RANKED_UNFILTERED",
    }
    run = client.actor("us5srxAYnsrkgUv2v").call(run_input=run_input)

    with open(save_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Text', 'Profile Name', 'Profile Picture', 'Date', 'Likes Count', 'Profile ID'])
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            writer.writerow([
                item.get("text", "No text"),
                item.get("profileName", "No profileName"),
                item.get("profilePicture", ""),
                item.get("date", ""),
                item.get("likesCount", 0),
                item.get("profileId", "")
            ])
    return save_path

