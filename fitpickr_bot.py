import requests
import feedparser
import time
import schedule
import json
import os
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================
BOT_TOKEN = "8717064816:AAE3pMETlkT4X3Ps8oSmJWlBo28QE7JgMz0"
CHANNEL = "@fitpickrdeals"
AFFILIATE_TAG = "rashmiyadav02-20"
POSTED_FILE = "posted_deals.json"

# Fitness keywords to filter deals
FITNESS_KEYWORDS = [
    "protein", "whey", "supplement", "vitamin",
    "yoga mat", "resistance band", "dumbbell", "kettlebell",
    "massage gun", "foam roller", "fitness tracker",
    "smartwatch", "running shoes", "gym", "workout",
    "treadmill", "exercise bike", "jump rope",
    "creatine", "pre-workout", "bcaa", "collagen",
    "sleep tracker", "smart ring", "weight scale"
]

# ============================================
# LOAD / SAVE POSTED DEALS
# ============================================
def load_posted():
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r") as f:
            return json.load(f)
    return []

def save_posted(posted):
    with open(POSTED_FILE, "w") as f:
        json.dump(posted, f)

# ============================================
# ADD AFFILIATE TAG TO AMAZON LINK
# ============================================
def add_affiliate(url):
    if "amazon.com" in url:
        if "?" in url:
            return f"{url}&tag={AFFILIATE_TAG}"
        else:
            return f"{url}?tag={AFFILIATE_TAG}"
    return url

# ============================================
# FETCH DEALS FROM SLICKDEALS RSS
# ============================================
def fetch_deals():
    feeds = [
        "https://slickdeals.net/newsearch.php?mode=frontpage&searcharea=deals&q=fitness&rss=1",
        "https://slickdeals.net/newsearch.php?mode=frontpage&searcharea=deals&q=protein&rss=1",
        "https://slickdeals.net/newsearch.php?mode=frontpage&searcharea=deals&q=gym+equipment&rss=1",
    ]
    
    deals = []
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                deals.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.get("summary", "")[:200]
                })
        except Exception as e:
            print(f"Feed error: {e}")
    
    return deals

# ============================================
# CHECK IF DEAL IS FITNESS RELATED
# ============================================
def is_fitness_deal(deal):
    text = (deal["title"] + " " + deal["summary"]).lower()
    return any(kw in text for kw in FITNESS_KEYWORDS)

# ============================================
# FORMAT MESSAGE
# ============================================
def format_message(deal):
    title = deal["title"]
    link = deal["link"]
    
    # Add affiliate tag if Amazon link
    if "amazon.com" in link:
        link = add_affiliate(link)
    
    message = f"""🔥 *Hot Fitness Deal!*

💪 *{title}*

🛒 {link}

🏋️ _FitPickr Deals — Honest Fitness & Health Picks_
🌐 fitpickr.lifenbyte.com

#fitness #deals #amazon #health #workout"""
    
    return message

# ============================================
# SEND TO TELEGRAM
# ============================================
def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    response = requests.post(url, json=payload)
    return response.json()

# ============================================
# MAIN JOB
# ============================================
def post_deals():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking for new deals...")
    
    posted = load_posted()
    deals = fetch_deals()
    new_count = 0
    
    for deal in deals:
        if deal["title"] in posted:
            continue
        
        if not is_fitness_deal(deal):
            continue
        
        message = format_message(deal)
        result = send_message(message)
        
        if result.get("ok"):
            posted.append(deal["title"])
            save_posted(posted)
            new_count += 1
            print(f"✅ Posted: {deal['title'][:50]}...")
            time.sleep(5)  # Wait between posts
        else:
            print(f"❌ Failed: {result}")
    
    if new_count == 0:
        print("No new fitness deals found.")
    else:
        print(f"✅ Posted {new_count} new deals!")

# ============================================
# SCHEDULE & RUN
# ============================================
if __name__ == "__main__":
    print("🏋️ FitPickr Deals Bot Starting...")
    print(f"📢 Channel: {CHANNEL}")
    print(f"🏷️ Affiliate: {AFFILIATE_TAG}")
    print("=" * 40)
    
    # Run immediately on start
    post_deals()
    
    # Then every 3 hours
    schedule.every(3).hours.do(post_deals)
    
    print("\n⏰ Scheduled to run every 3 hours...")
    print("Press Ctrl+C to stop.\n")
    
    while True:
        schedule.run_pending()
        time.sleep(60)
