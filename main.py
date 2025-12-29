import requests
import json
import re
import os
import time

YOUTUBE_COMMUNITY_URL = "https://www.youtube.com/@ClashOfClans/community"
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_community_posts():
    html = requests.get(YOUTUBE_COMMUNITY_URL, headers=HEADERS).text
    match = re.search(r"var ytInitialData = (.*?);</script>", html)
    if not match:
        return []

    data = json.loads(match.group(1))

    posts = []
    tabs = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]

    for tab in tabs:
        if "tabRenderer" in tab and tab["tabRenderer"].get("title") == "Community":
            contents = tab["tabRenderer"]["content"]["sectionListRenderer"]["contents"]

            for item in contents:
                if "itemSectionRenderer" in item:
                    for post in item["itemSectionRenderer"]["contents"]:
                        renderer = post.get("backstagePostRenderer")
                        if renderer:
                            post_id = renderer["postId"]
                            text_runs = renderer.get("contentText", {}).get("runs", [])
                            text = "".join(r["text"] for r in text_runs)
                            posts.append((post_id, text))

    return posts

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": f"📢 New Clash of Clans Community Post\n\n{text}",
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload)

def main():
    last_id = open("last_post_id.txt").read().strip() if os.path.exists("last_post_id.txt") else None

    posts = fetch_community_posts()
    if not posts:
        return

    new_posts = []

    for post_id, text in posts:
        if post_id == last_id:
            break
        new_posts.append((post_id, text))

    # test
    send_to_telegram(f'Hello there {time.time()}')
    # test

    # Send from oldest → newest
    for post_id, text in reversed(new_posts):
        send_to_telegram(text)

    if new_posts:
        with open("last_post_id.txt", "w") as f:
            f.write(new_posts[0][0])

if __name__ == "__main__":
    main()
