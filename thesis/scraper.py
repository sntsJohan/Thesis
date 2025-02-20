from apify_client import ApifyClient
import csv
import time

def scrape_comments(fb_url, save_path):
    client = ApifyClient("apify_api_nOj5UhPGTgVo3VuHB3Udm0HVPZeMaM3Sl5sS")
    run_input = {
        "startUrls": [{"url": fb_url}],
        "resultsLimit": 1000,
        "includeNestedComments": False,
        "viewOption": "RANKED_UNFILTERED",
    }
    run = client.actor("KoJrdxJCTtpon81KY").call(run_input=run_input)

    with open(save_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Text', 'Profile Name'])
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            text = item.get("text", "No text")
            profile_name = item.get("profileName", "No profileName")
            writer.writerow([text, profile_name])
    return save_path

