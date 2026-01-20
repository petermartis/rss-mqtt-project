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
MQTT_TOPIC_SECONDS = "today/seconds"
MQTT_TOPIC_DOW = "today/dow"
MQTT_TOPIC_SDATE = "today/sdate"
MQTT_TOPIC_LDATE = "today/ldate"
MQTT_TOPIC_YEAR = "today/year"
MQTT_TOPIC_NAMEDAY = "today/nameday"

# Slovak day names (without diacritics)
SLOVAK_DAYS = ["pondelok", "utorok", "streda", "stvrtok", "piatok", "sobota", "nedela"]

# Slovak month names in genitive case (without diacritics)
SLOVAK_MONTHS_GENITIVE = [
    "januara", "februara", "marca", "aprila", "maja", "juna",
    "jula", "augusta", "septembra", "oktobra", "novembra", "decembra"
]

# Slovak name days dictionary
NAMEDAYS = {
    "01-01": "Novy rok", "01-02": "Alexandra", "01-03": "Daniela", "01-04": "Drahoslav",
    "01-05": "Andrea", "01-06": "Antonia", "01-07": "Bohuslava", "01-08": "Severin",
    "01-09": "Alexej", "01-10": "Dasa", "01-11": "Malvina", "01-12": "Ernest",
    "01-13": "Rastislav", "01-14": "Radovan", "01-15": "Dobroslav", "01-16": "Kristina",
    "01-17": "Natasa", "01-18": "Bohdana", "01-19": "Drahomira", "01-20": "Dalibor",
    "01-21": "Vincent", "01-22": "Zora", "01-23": "Milos", "01-24": "Timotej",
    "01-25": "Gejza", "01-26": "Tamara", "01-27": "Bohus", "01-28": "Alfonz",
    "01-29": "Gaspar", "01-30": "Ema", "01-31": "Emil",
    "02-01": "Tatiana", "02-02": "Erik", "02-03": "Blazej", "02-04": "Veronika",
    "02-05": "Agata", "02-06": "Dorota", "02-07": "Vanda", "02-08": "Zoja",
    "02-09": "Zdenko", "02-10": "Gabriela", "02-11": "Dezider", "02-12": "Perla",
    "02-13": "Arpad", "02-14": "Valentin", "02-15": "Pravoslav", "02-16": "Ida Liana",
    "02-17": "Miloslava", "02-18": "Jaromir", "02-19": "Vlasta", "02-20": "Livia",
    "02-21": "Eleonora", "02-22": "Etela", "02-23": "Roman", "02-24": "Matej",
    "02-25": "Frederik", "02-26": "Viktor", "02-27": "Alexander", "02-28": "Zlatica",
    "02-29": "Radomir",
    "03-01": "Albin", "03-02": "Anezka", "03-03": "Bohumil", "03-04": "Kazimir",
    "03-05": "Fridrich", "03-06": "Radoslav", "03-07": "Tomas", "03-08": "Alan",
    "03-09": "Frantiska", "03-10": "Branislav", "03-11": "Angela", "03-12": "Gregor",
    "03-13": "Vlastimil", "03-14": "Matilda", "03-15": "Svetlana", "03-16": "Boleslav",
    "03-17": "Lubica", "03-18": "Eduard", "03-19": "Jozef", "03-20": "Vitazoslav",
    "03-21": "Blahoslav", "03-22": "Benadik", "03-23": "Adrian", "03-24": "Gabriel",
    "03-25": "Marian", "03-26": "Emanuel", "03-27": "Alena", "03-28": "Sona",
    "03-29": "Miroslav", "03-30": "Vieroslava", "03-31": "Benjamin",
    "04-01": "Hugo", "04-02": "Zita", "04-03": "Richard", "04-04": "Izidor",
    "04-05": "Miroslava", "04-06": "Irena", "04-07": "Zoltan", "04-08": "Albert",
    "04-09": "Milena", "04-10": "Igor", "04-11": "Julius", "04-12": "Estera",
    "04-13": "Ales", "04-14": "Justina", "04-15": "Fedor", "04-16": "Dana",
    "04-17": "Rudolf", "04-18": "Valer", "04-19": "Jela", "04-20": "Marcel",
    "04-21": "Ervin", "04-22": "Slavomir", "04-23": "Vojtech", "04-24": "Juraj",
    "04-25": "Marek", "04-26": "Jaroslava", "04-27": "Jaroslav", "04-28": "Jarmila",
    "04-29": "Lea", "04-30": "Anastazia",
    "05-01": "Sviatok prace", "05-02": "Zigmund", "05-03": "Galina", "05-04": "Florian",
    "05-05": "Lesana", "05-06": "Hermina", "05-07": "Monika", "05-08": "Ingrida",
    "05-09": "Roland", "05-10": "Viktoria", "05-11": "Blazena", "05-12": "Pankrac",
    "05-13": "Servac", "05-14": "Bonifac", "05-15": "Zofia", "05-16": "Svetozar",
    "05-17": "Gizela", "05-18": "Viola", "05-19": "Gertruda", "05-20": "Bernard",
    "05-21": "Zina", "05-22": "Julia", "05-23": "Zelmira", "05-24": "Ela",
    "05-25": "Urban", "05-26": "Dusan", "05-27": "Iveta", "05-28": "Viliam",
    "05-29": "Vilma", "05-30": "Ferdinand", "05-31": "Petronela",
    "06-01": "Zaneta", "06-02": "Xenia", "06-03": "Karolina", "06-04": "Lenka",
    "06-05": "Laura", "06-06": "Norbert", "06-07": "Robert", "06-08": "Medard",
    "06-09": "Stanislava", "06-10": "Margareta", "06-11": "Dobroslava", "06-12": "Zlatko",
    "06-13": "Anton", "06-14": "Vasil", "06-15": "Vit", "06-16": "Blanka",
    "06-17": "Adolf", "06-18": "Vratislav", "06-19": "Alfred", "06-20": "Valeria",
    "06-21": "Alojz", "06-22": "Paulina", "06-23": "Sidonia", "06-24": "Jan",
    "06-25": "Tadeas", "06-26": "Adriana", "06-27": "Ladislav", "06-28": "Beata",
    "06-29": "Peter", "06-30": "Melania",
    "07-01": "Diana", "07-02": "Berta", "07-03": "Miloslav", "07-04": "Prokop",
    "07-05": "Cyril", "07-06": "Patrik", "07-07": "Oliver", "07-08": "Ivan",
    "07-09": "Lujza", "07-10": "Amalia", "07-11": "Milota", "07-12": "Nina",
    "07-13": "Margita", "07-14": "Kamil", "07-15": "Henrich", "07-16": "Drahomir",
    "07-17": "Bohuslav", "07-18": "Kamila", "07-19": "Dusana", "07-20": "Ilja",
    "07-21": "Daniel", "07-22": "Magdalena", "07-23": "Olga", "07-24": "Vladimir",
    "07-25": "Jakub", "07-26": "Anna Hana", "07-27": "Bozena", "07-28": "Kristof",
    "07-29": "Marta", "07-30": "Libusa", "07-31": "Ignac",
    "08-01": "Bozidara", "08-02": "Gustav", "08-03": "Jergus", "08-04": "Dominik",
    "08-05": "Hortenzia", "08-06": "Jozefina", "08-07": "Stefania", "08-08": "Oskar",
    "08-09": "Lubomira", "08-10": "Vavrinec", "08-11": "Zuzana", "08-12": "Darina",
    "08-13": "Lubomir", "08-14": "Mojmir", "08-15": "Marcela", "08-16": "Leonard",
    "08-17": "Milica", "08-18": "Elena Helena", "08-19": "Lydia", "08-20": "Anabela",
    "08-21": "Jana", "08-22": "Tichomir", "08-23": "Filip", "08-24": "Bartolomej",
    "08-25": "Ludovit", "08-26": "Samuel", "08-27": "Silvia", "08-28": "Augustin",
    "08-29": "Nikola", "08-30": "Ruzena", "08-31": "Nora",
    "09-01": "Drahoslava", "09-02": "Linda", "09-03": "Belo", "09-04": "Rozalia",
    "09-05": "Regina", "09-06": "Alica", "09-07": "Marianna", "09-08": "Miriama",
    "09-09": "Martina", "09-10": "Oleg", "09-11": "Bystrik", "09-12": "Maria",
    "09-13": "Ctibor", "09-14": "Ludomil", "09-15": "Jolana", "09-16": "Ludomila",
    "09-17": "Olympia", "09-18": "Eugenia", "09-19": "Konstantin", "09-20": "Luboslav",
    "09-21": "Matus", "09-22": "Moric", "09-23": "Zdenka", "09-24": "Lubos",
    "09-25": "Vladislav", "09-26": "Edita", "09-27": "Cyprian", "09-28": "Vaclav",
    "09-29": "Michal", "09-30": "Jarolim",
    "10-01": "Arnold", "10-02": "Levoslav", "10-03": "Stela", "10-04": "Frantisek",
    "10-05": "Viera", "10-06": "Natalia", "10-07": "Eliska", "10-08": "Brigita",
    "10-09": "Dionyz", "10-10": "Slavomira", "10-11": "Valentina", "10-12": "Maximilian",
    "10-13": "Koloman", "10-14": "Boris", "10-15": "Terezia", "10-16": "Vladimira",
    "10-17": "Hedviga", "10-18": "Lukas", "10-19": "Kristian", "10-20": "Vendelin",
    "10-21": "Ursula", "10-22": "Sergej", "10-23": "Alojza", "10-24": "Kvetoslava",
    "10-25": "Aurel", "10-26": "Demeter", "10-27": "Sabina", "10-28": "Dobromila",
    "10-29": "Klara", "10-30": "Simona", "10-31": "Aurelia",
    "11-01": "Denis Denisa", "11-02": "Pamiatka zosnulych", "11-03": "Hubert", "11-04": "Karol",
    "11-05": "Imrich", "11-06": "Renata", "11-07": "Rene", "11-08": "Bohumir",
    "11-09": "Teodor", "11-10": "Tibor", "11-11": "Maros Martin", "11-12": "Svatopluk",
    "11-13": "Stanislav", "11-14": "Irma", "11-15": "Leopold", "11-16": "Agnesa",
    "11-17": "Klaudia", "11-18": "Eugen", "11-19": "Alzbeta", "11-20": "Felix",
    "11-21": "Elvira", "11-22": "Cecilia", "11-23": "Klement", "11-24": "Emilia",
    "11-25": "Katarina", "11-26": "Kornel", "11-27": "Milan", "11-28": "Henrieta",
    "11-29": "Vratko", "11-30": "Ondrej",
    "12-01": "Edmund", "12-02": "Bibiana", "12-03": "Oldrich", "12-04": "Barbora",
    "12-05": "Oto", "12-06": "Mikulas", "12-07": "Ambroz", "12-08": "Marina",
    "12-09": "Izabela", "12-10": "Raduz", "12-11": "Hilda", "12-12": "Otilia",
    "12-13": "Lucia", "12-14": "Branislava", "12-15": "Ivica", "12-16": "Albina",
    "12-17": "Kornelia", "12-18": "Slava", "12-19": "Judita", "12-20": "Dagmara",
    "12-21": "Bohdan", "12-22": "Adela", "12-23": "Nadezda", "12-24": "Adam",
    "12-25": "1.sviatok vianocny", "12-26": "Stefan", "12-27": "Filomena", "12-28": "Ivana",
    "12-29": "Milada", "12-30": "David", "12-31": "Silvester"
}

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
last_time_second = -1
last_date = None
last_year = None

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

def publish_seconds(client):
    """Publish current seconds to MQTT (not retained)"""
    current_seconds = datetime.now().strftime("%S")
    client.publish(MQTT_TOPIC_SECONDS, current_seconds, retain=False)

def publish_date_info(client):
    """Publish all date-related information"""
    now = datetime.now()

    # Day of week (Slovak)
    dow_index = now.weekday()
    dow = SLOVAK_DAYS[dow_index]
    client.publish(MQTT_TOPIC_DOW, dow, retain=True)
    log(f"Published day of week: {dow}")

    # Short date (D.M.YYYY)
    sdate = f"{now.day}.{now.month}.{now.year}"
    client.publish(MQTT_TOPIC_SDATE, sdate, retain=True)
    log(f"Published short date: {sdate}")

    # Long date (D. month_name_genitive)
    day = now.day
    month_name = SLOVAK_MONTHS_GENITIVE[now.month - 1]
    ldate = f"{day}. {month_name}"
    client.publish(MQTT_TOPIC_LDATE, ldate, retain=True)
    log(f"Published long date: {ldate}")

    # Year
    year = now.strftime("%Y")
    client.publish(MQTT_TOPIC_YEAR, year, retain=True)
    log(f"Published year: {year}")

    # Name day
    date_key = now.strftime("%m-%d")
    nameday = NAMEDAYS.get(date_key, "")
    if nameday:
        client.publish(MQTT_TOPIC_NAMEDAY, nameday, retain=True)
        log(f"Published nameday: {nameday}")

def check_and_publish_time(client):
    """Check if minute changed and publish time"""
    global last_time_minute

    current_minute = datetime.now().minute

    if current_minute != last_time_minute:
        last_time_minute = current_minute
        publish_time(client)
        return True

    return False

def check_and_publish_seconds(client):
    """Check if second changed and publish seconds"""
    global last_time_second

    current_second = datetime.now().second

    if current_second != last_time_second:
        last_time_second = current_second
        publish_seconds(client)
        return True

    return False

def check_and_publish_date(client):
    """Check if date changed and publish date information"""
    global last_date

    current_date = datetime.now().date()

    if current_date != last_date:
        last_date = current_date
        publish_date_info(client)
        return True

    return False

def check_and_publish_year(client):
    """Check if year changed and publish year"""
    global last_year

    current_year = datetime.now().year

    if current_year != last_year:
        last_year = current_year
        year = datetime.now().strftime("%Y")
        client.publish(MQTT_TOPIC_YEAR, year, retain=True)
        log(f"Published year: {year}")
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
    # Note: Just publish feed_name without (Tech) or (News) suffix
    client.publish(MQTT_TOPIC_HEADLINE, headline, retain=True)
    client.publish(MQTT_TOPIC_CONTENT, content, retain=True)
    client.publish(MQTT_TOPIC_SOURCE, feed_name, retain=True)
    client.publish(MQTT_TOPIC_LINK, link, retain=True)
    client.publish(MQTT_TOPIC_PUBLISH, published, retain=True)

    log(f"Published from {feed_name}: {headline[:60]}...")

def fetch_feed(feed):
    """Fetch and parse RSS feed"""
    try:
        parsed = feedparser.parse(feed['url'])
        if parsed.entries:
            return parsed.entries
        return []
    except Exception as e:
        log(f"Error fetching {feed['name']}: {e}")
        return []

def check_for_new_articles(client):
    """Check all feeds for new articles"""
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

    return new_articles_found

def rotate_feeds(client):
    """Rotate through cached feed entries every 6 seconds"""
    global current_feed_index

    if not feed_entries_cache:
        return

    # Get current feed
    feed = RSS_FEEDS[current_feed_index]
    feed_name = feed['name']

    # Get entries from cache
    entries = feed_entries_cache.get(feed_name, [])

    if entries:
        publish_article(client, feed_name, feed['category'], entries[0])

    # Move to next feed
    current_feed_index = (current_feed_index + 1) % len(RSS_FEEDS)

def main():
    """Main application loop"""
    global last_date, last_year

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

    # Publish initial time and date information
    publish_time(client)
    last_date = datetime.now().date()
    last_year = datetime.now().year
    publish_date_info(client)

    # Initial fetch of all feeds
    log("Performing initial feed fetch...")
    check_for_new_articles(client)

    last_check_time = time.time()
    last_rotation_time = time.time()

    log("Starting main loop...")

    try:
        while True:
            current_time = time.time()

            # Check and publish seconds every iteration
            check_and_publish_seconds(client)

            # Check and publish time every second (publishes only when minute changes)
            check_and_publish_time(client)

            # Check and publish date (publishes only when date changes)
            check_and_publish_date(client)

            # Check and publish year (publishes only when year changes)
            check_and_publish_year(client)

            # Check for new articles every 60 seconds
            if current_time - last_check_time >= 60:
                check_for_new_articles(client)
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
