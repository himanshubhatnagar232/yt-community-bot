# YouTube Community → Telegram Alerts

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![GitHub Actions](https://img.shields.io/github/actions/workflow/status/himanshubhatnagar232/yt-community-bot/run.yml?label=GitHub%20Actions)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-GitHub%20Actions-lightgrey)

## TL;DR

A lightweight, serverless tool that **monitors YouTube Community / Posts tabs and delivers updates to Telegram**.

Built to avoid YouTube doomscrolling while still staying informed about important updates (events, rewards, announcements).

* 🚫 No YouTube app needed
* 🧠 No Shorts, no distractions
* ⚙️ Runs automatically via GitHub Actions
* 🔁 Easily reusable for **any YouTube channel**

---

## Project motivation

Many creators and games (including Clash of Clans) publish **important updates exclusively through YouTube Community posts** rather than videos.

Checking these updates manually usually means:

* opening YouTube
* getting pulled into Shorts or recommendations
* forgetting to check regularly

This project provides a **clean, distraction-free alternative**:

* YouTube Community posts are monitored automatically
* Updates are delivered directly to **Telegram**, where notifications stay focused
* The system runs entirely in the background

The result is a simple, reliable way to stay informed without engaging with the YouTube feed.

---

## What this project does

* Monitors a YouTube channel’s **Posts / Community tab**
* Detects newly published community posts
* Sends them to a Telegram channel
* Prevents duplicate notifications
* Preserves chronological order (old → new)
* Runs on a scheduled basis using GitHub Actions

The implementation is **generic by design**:

* Works with any YouTube channel
* Requires only a URL change to switch targets
* Can be extended with keyword filtering, regex rules, or additional destinations

---

## High-level architecture

```
YouTube Posts tab
        ↓
GitHub Actions (scheduled cron)
        ↓
Python scraper (ytInitialData)
        ↓
Last-seen post tracking
        ↓
Telegram Bot API
        ↓
Telegram Channel
```

Key design notes:

* YouTube does not expose an official API for community posts
* Post data is embedded in page-level JSON (`ytInitialData`)
* This project safely extracts and processes that data without authentication

---

## Technology stack

* Python 3
* GitHub Actions (cron-based execution)
* Telegram Bot API
* Read-only YouTube web scraping

No servers, databases, or paid infrastructure are required.

---

## Repository structure

```
.
├── main.py                  # Core scraping and notification logic
├── requirements.txt         # Python dependencies
├── last_post_id.txt         # Cursor to prevent duplicate notifications
└── .github/workflows/
    └── run.yml              # GitHub Actions workflow definition
```

---

## Setup guide

### 1. Create a Telegram bot

1. Open Telegram and start **@BotFather**
2. Run:

   ```
   /newbot
   ```
3. Choose a name and username
4. Copy the generated **BOT_TOKEN**

---

### 2. Create a Telegram channel

1. Create a **Telegram Channel** (not a group)
2. Add your bot as an **Administrator**
3. Grant permission to post messages

#### Obtain the channel ID

* Post a message in the channel
* Forward it to **@userinfobot**
* Note the numeric ID (e.g. `-100XXXXXXXXXX`)

---

### 3. Configure the YouTube channel

In `main.py`, update the target URL:

```python
YOUTUBE_POSTS_URL = "https://www.youtube.com/@ClashOfClans/posts"
```

To monitor a different channel, simply replace this URL.

---

### 4. Configure GitHub Actions secrets

In the GitHub repository:

```
Settings → Secrets and variables → Actions
```

Add the following **Repository Secrets**:

* `BOT_TOKEN` — Telegram bot token
* `CHANNEL_ID` — Telegram channel ID

Optional (for future extensions):

* `ENABLE_FILTER` — feature flag for keyword filtering

---

### 5. Enable GitHub Actions write permissions

This is required so the workflow can update `last_post_id.txt`.

```
Settings → Actions → General
```

Enable:

* ✅ Read and write permissions
* ✅ Allow GitHub Actions to push commits

---

### 6. Run the workflow

* Open the **Actions** tab
* Select the workflow
* Run it manually once for validation

After this:

* The workflow will execute automatically on schedule
* New community posts will appear in Telegram

---

## Duplicate prevention and ordering

* The ID of the most recent processed post is stored in `last_post_id.txt`
* Each run compares visible posts against this value
* Only newer posts are sent
* The file is committed back to the repository by GitHub Actions

This ensures:

* No historical spam
* No repeated notifications
* Safe restarts and redeployments

---

## Extending the project

### Keyword or regex filtering

Posts can be filtered before sending:

```python
import re

KEYWORDS = [r"free", r"reward", r"claim"]

if any(re.search(k, post_text, re.IGNORECASE) for k in KEYWORDS):
    send_to_telegram(post)
```

This enables:

* Freebie-only alerts
* Event-only alerts
* Custom notification logic

---

### Supporting additional YouTube channels

The scraper logic is channel-agnostic.

Only this value needs to change:

```python
YOUTUBE_POSTS_URL = "https://www.youtube.com/@SomeOtherChannel/posts"
```

---

### WhatsApp delivery (future work)

Possible extensions include:

* Manual forwarding from Telegram to a WhatsApp Channel
* Automated forwarding via WhatsApp Cloud API

Telegram is intentionally used as the primary destination because it is automation-friendly and ToS-safe.

---

## Known limitations

* YouTube embeds only ~8–12 recent posts per page
* Older posts require continuation-token pagination (not implemented by design)
* Image handling varies based on YouTube renderer types

These trade-offs keep the system stable, lightweight, and low-maintenance.

---

## Summary

This project provides:

* A distraction-free way to consume YouTube Community updates
* A reusable monitoring tool for any channel
* A fully serverless, free automation pipeline

If you want the information without the feed, this tool is built for that purpose.

---

## License

This project is open-source and intended for personal and educational use. Modify and extend it freely.
