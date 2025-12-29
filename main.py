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

def extract_backstage_posts(data):
    posts = []

    def walk(obj):
        if isinstance(obj, dict):
            if "backstagePostRenderer" in obj:
                renderer = obj["backstagePostRenderer"]
                post_id = renderer.get("postId")

                text_runs = renderer.get("contentText", {}).get("runs", [])
                text = "".join(r.get("text", "") for r in text_runs)

                if post_id and text:
                    posts.append((post_id, text))

            for v in obj.values():
                walk(v)

        elif isinstance(obj, list):
            for i in obj:
                walk(i)

    walk(data)
    return posts

def fetch_community_posts():
    html = requests.get(YOUTUBE_COMMUNITY_URL, headers=HEADERS).text
    match = re.search(r"ytInitialData\s*=\s*(\{.*?\});", html, re.DOTALL)

    if not match:
        print("❌ ytInitialData not found")
        return []

    data = json.loads(match.group(1))
    print("✅ ytInitialData parsed")

    posts = extract_backstage_posts(data)
    print(f"✅ Found {len(posts)} community posts")

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

    # test
    send_to_telegram(f'Hello there {time.time()}')
    # test

    last_id = open("last_post_id.txt").read().strip() if os.path.exists("last_post_id.txt") else None

    posts = fetch_community_posts()
    if not posts:
        return

    new_posts = []

    for post_id, text in posts:
        if post_id == last_id:
            break
        new_posts.append((post_id, text))

    # Send from oldest → newest
    for post_id, text in reversed(new_posts):
        send_to_telegram(text)

    if new_posts:
        with open("last_post_id.txt", "w") as f:
            f.write(new_posts[0][0])

if __name__ == "__main__":
    main()
