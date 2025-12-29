import requests
import json
import re
import os
import time

YOUTUBE_POSTS_URL = "https://www.youtube.com/@ClashOfClans/posts"
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def extract_posts(data, max_posts=50):
    posts = []

    def walk(obj):
        if isinstance(obj, dict):
            if "backstagePostRenderer" in obj:
                r = obj["backstagePostRenderer"]
                post_id = r.get("postId")

                # ---- TEXT ----
                text_runs = r.get("contentText", {}).get("runs", [])
                text = "".join(run.get("text", "") for run in text_runs).strip()

                # ---- IMAGES / GIFS ----
                images = []

                attachment = r.get("backstageAttachment", {})
                if "imageRenderer" in attachment:
                    thumbnails = attachment["imageRenderer"]["image"]["thumbnails"]
                    images.append(thumbnails[-1]["url"])

                if "multiImageRenderer" in attachment:
                    for img in attachment["multiImageRenderer"]["images"]:
                        thumbnails = img["image"]["thumbnails"]
                        images.append(thumbnails[-1]["url"])

                posts.append({
                    "id": post_id,
                    "text": text,
                    "images": images
                })

            for v in obj.values():
                walk(v)

        elif isinstance(obj, list):
            for i in obj:
                walk(i)

    walk(data)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for p in posts:
        if p["id"] and p["id"] not in seen:
            seen.add(p["id"])
            unique.append(p)

    return unique[:max_posts]


def fetch_community_posts():
    html = requests.get(YOUTUBE_POSTS_URL, headers=HEADERS).text
    match = re.search(r"ytInitialData\s*=\s*(\{.*?\});", html, re.DOTALL)

    if not match:
        print("❌ ytInitialData not found")
        return []

    data = json.loads(match.group(1))
    print("✅ ytInitialData parsed")

    posts = extract_posts(data, max_posts=50)
    posts.reverse()
    print(f"✅ Found {len(posts)} community posts")

    return posts

def send_text(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHANNEL_ID,
            "text": text,
            "disable_web_page_preview": False
        }
    )

def send_photo(photo_url, caption):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        json={
            "chat_id": CHANNEL_ID,
            "photo": photo_url,
            "caption": caption[:1024]  # Telegram limit
        }
    )

def main():
    html = requests.get(YOUTUBE_POSTS_URL, headers=HEADERS).text
    match = re.search(r"ytInitialData\s*=\s*(\{.*?\});", html, re.DOTALL)
    if not match:
        print("ytInitialData not found")
        return

    data = json.loads(match.group(1))
    posts = extract_posts(data, max_posts=50)

    if not posts:
        print("No posts found")
        return

    last_id = ""
    if os.path.exists("last_post_id.txt"):
        last_id = open("last_post_id.txt").read().strip()

    new_posts = []
    for post in posts:
        if post["id"] == last_id:
            break
        new_posts.append(post)

    # Send oldest → newest
    for post in reversed(new_posts):
        header = "📢 *Clash of Clans – Community Post*\n\n"
        text = header + (post["text"] or "")

        if post["images"]:
            send_photo(post["images"][0], text)
        else:
            send_text(text)

    if new_posts:
        with open("last_post_id.txt", "w") as f:
            f.write(new_posts[0]["id"])

if __name__ == "__main__":
    main()
