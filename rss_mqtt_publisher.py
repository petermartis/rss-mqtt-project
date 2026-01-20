#!/usr/bin/env python3
import feedparser
import paho.mqtt.client as mqtt
import time
import hashlib
import unicodedata
import sys
from datetime import datetime

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_HEADLINE = "news/headline"
MQTT_TOPIC_CONTENT = "news/content"
MQTT_TOPIC_SOURCE = "news/source"
MQTT_TOPIC_LINK = "news/link"
MQTT_TOPIC_PUBLISH = "news/publish"
MQTT_TOPIC_TIME = "today/time"

# RSS Feeds
RSS_FEEDS = [
    {"url": "https://techcrunch.com/feed/", "name": "TechCrunch", "category": "Tech"},
    {"url": "https://www.theverge.com/rss/index.xml", "name": "The Verge", "category": "Tech"},
    {"url": "https://www.wired.com/feed/rss", "name": "Wired", "category": "Tech"},
    {"url": "https://arstechnica.com/feed/", "name": "Ars Technica", "category": "Tech"},
    {"url": "https://www.engadget.com/rss.xml", "name": "Engadget", "category": "Tech"},
    {"url": "https://feeds.bbci.co.uk/news/world/rss.xml", "name": "BBC World", "category": "News"},
    {"url": "http://rss.cnn.com/rss/edition.rss", "name": "CNN International", "category": "News"},
    {"url": "https://www.aljazeera.com/xml/rss/all.xml", "name": "Al Jazeera", "category": "News"}
]

# Store seen articles using hash
seen_articles = set()
feed_entries_cache = {}
current_feed_index = 0
last_time_minute = -1

def log(message):
    """Log message with timestamp"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)

def remove_diacritics(text):
    """Remove diacritics/accents from text"""
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def clean_text(text):
    """Remove HTML tags, special characters, and clean text to plain ASCII"""
    if not text:
        return ""
    
    import re
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Replace common HTML entities
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
    text = text.replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#039;', "'")
    text = text.replace('&#8217;', "'").replace('&#8216;', "'")
    text = text.replace('&#8220;', '"').replace('&#8221;', '"')
    text = text.replace('&#8211;', '-').replace('&#8212;', '-')
    text = text.replace('&rsquo;', "'").replace('&lsquo;', "'")
    text = text.replace('&rdquo;', '"').replace('&ldquo;', '"')
    text = text.replace('&ndash;', '-').replace('&mdash;', '-')
    
    # Remove diacritics
    text = remove_diacritics(text)
    
    # Remove any remaining non-ASCII characters
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Clean up whitespace
    text = ' '.join(text.split())
    
    return text.strip()

def get_article_hash(entry):
    """Create unique hash for article"""
    title = entry.get('title', '')
    link = entry.get('link', '')
    return hashlib.md5(f"{title}{link}".encode()).hexdigest()

def on_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        log("Connected to MQTT Broker")
    else:
        log(f"Failed to connect, return code {rc}")

def publish_time(client):
    """Publish current time to MQTT"""
    current_time = datetime.now().strftime("%H:%M")
    client.publish(MQTT_TOPIC_TIME, current_time, retain=True)
    log(f"Published time: {current_time}")

def check_and_publish_time(client):
    """Check if minute changed and publish time"""
    global last_time_minute

    current_minute = datetime.now().minute

    if current_minute != last_time_minute:
        last_time_minute = current_minute
        publish_time(client)
        return True

    return False

def clear_old_topics(client):
    """Clear old retained messages from legacy topics"""
    log("Clearing old retained messages...")
    old_topics = [
        "news/techcrunch_com",
        "news/feeds_arstechnica_com",
        "news/dennikn_sk",
        "news/www_wired_com",
        "news/www_zdnet_com",
        "news/www_engadget_com",
        "news/feeds_bbci_co_uk",
        "news/www_theverge_com",
        "news/title",
        "news/body"
    ]
    
    for topic in old_topics:
        client.publish(topic, "", retain=True)
        log(f"  Cleared {topic}")

def publish_article(client, feed_name, category, entry):
    """Publish article to MQTT as plain text across multiple topics with retain flag"""
    # Clean and prepare data
    headline = clean_text(entry.get('title', 'No title'))
    content = clean_text(entry.get('description', entry.get('summary', 'No content available')))
    link = entry.get('link', '')
    published = entry.get('published', '')
    
    # Limit content length
    if len(content) > 500:
        content = content[:497] + "..."
    
    # Publish to separate topics as plain text with retain flag
    client.publish(MQTT_TOPIC_HEADLINE, headline, retain=True)
    client.publish(MQTT_TOPIC_CONTENT, content, retain=True)
    client.publish(MQTT_TOPIC_SOURCE, f"{feed_name} ({category})", retain=True)
    client.publish(MQTT_TOPIC_LINK, link, retain=True)
    client.publish(MQTT_TOPIC_PUBLISH, published, retain=True)
    
    log(f"Published from {feed_name}: {headline[:60]}...")

def fetch_feed(feed):
    """Fetch and parse RSS feed"""
    try:
        log(f"Fetching {feed['name']}...")
        parsed = feedparser.parse(feed['url'])
        if parsed.entries:
            log(f"  Found {len(parsed.entries)} entries in {feed['name']}")
            return parsed.entries
        else:
            log(f"  No entries found in {feed['name']}")
        return []
    except Exception as e:
        log(f"Error fetching {feed['name']}: {e}")
        return []

def check_for_new_articles(client):
    """Check all feeds for new articles"""
    log("Checking for new articles...")
    new_articles_found = False
    
    for feed in RSS_FEEDS:
        entries = fetch_feed(feed)
        
        # Store entries in cache for rotation
        feed_entries_cache[feed['name']] = entries
        
        # Check for new articles
        for entry in entries[:5]:  # Check top 5 entries only
            article_hash = get_article_hash(entry)
            
            if article_hash not in seen_articles:
                seen_articles.add(article_hash)
                publish_article(client, feed['name'], feed['category'], entry)
                new_articles_found = True
    
    if not new_articles_found:
        log("No new articles found")
    
    return new_articles_found

def rotate_feeds(client):
    """Rotate through cached feed entries every 6 seconds"""
    global current_feed_index
    
    if not feed_entries_cache:
        log("No cached entries available for rotation")
        return
    
    # Get current feed
    feed = RSS_FEEDS[current_feed_index]
    feed_name = feed['name']
    
    # Get entries from cache
    entries = feed_entries_cache.get(feed_name, [])
    
    if entries:
        # Publish the first entry
        log(f"Rotating: {feed_name}")
        publish_article(client, feed_name, feed['category'], entries[0])
    else:
        log(f"No entries in cache for {feed_name}")
    
    # Move to next feed
    current_feed_index = (current_feed_index + 1) % len(RSS_FEEDS)

def main():
    """Main application loop"""
    # Setup MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    
    log("Starting RSS to MQTT Publisher...")
    log(f"Connecting to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        time.sleep(2)  # Give time to connect
    except Exception as e:
        log(f"Error connecting to MQTT: {e}")
        return
    
    # Clear old retained messages
    clear_old_topics(client)
    time.sleep(1)

    # Publish initial time
    publish_time(client)

    # Initial fetch of all feeds
    log("Performing initial feed fetch...")
    check_for_new_articles(client)
    
    last_check_time = time.time()
    last_rotation_time = time.time()
    
    log("Starting main loop...")
    
    try:
        while True:
            current_time = time.time()

            # Check and publish time every second (publishes only when minute changes)
            check_and_publish_time(client)

            # Check for new articles every 60 seconds
            if current_time - last_check_time >= 60:
                new_found = check_for_new_articles(client)
                last_check_time = current_time

            # Rotate feeds every 6 seconds
            if current_time - last_rotation_time >= 6:
                rotate_feeds(client)
                last_rotation_time = current_time

            time.sleep(1)
    
    except KeyboardInterrupt:
        log("Shutting down...")
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        log(f"Error in main loop: {e}")
        client.loop_stop()
        client.disconnect()
        raise

if __name__ == "__main__":
    main()
