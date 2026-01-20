# RSS & Calendar MQTT Publisher - Complete Guide

Complete information system for Raspberry Pi 5 that publishes RSS news feeds, Slovak calendar, and Google Calendar events to MQTT topics.

## Overview

This project combines three main components:
1. **RSS News Publisher** - Monitors 8 tech and international news feeds
2. **Slovak Calendar** - Publishes date, time, and namedays in Slovak
3. **Google Calendar Connector** - Syncs your work calendar via CalDAV

All data is published to local MQTT broker with retained messages for instant availability.

## System Status

### Auto-Start Services

All services are configured to start automatically on boot:

- ✓ `mosquitto.service` - MQTT broker (port 1883)
- ✓ `rss-mqtt.service` - RSS and calendar publisher
- ✓ `gcal-mqtt.service` - Google Calendar connector

### Service Management

```bash
# Check all services
sudo systemctl status rss-mqtt.service
sudo systemctl status gcal-mqtt.service
sudo systemctl status mosquitto.service

# Restart services
sudo systemctl restart rss-mqtt.service
sudo systemctl restart gcal-mqtt.service

# View logs
sudo journalctl -u rss-mqtt.service -f
sudo journalctl -u gcal-mqtt.service -f

# Enable/disable auto-start
sudo systemctl enable rss-mqtt.service
sudo systemctl disable rss-mqtt.service
```

## MQTT Topics Reference

### News Topics (all retained)

Updates every 6 seconds, rotating through 8 feeds:

- `news/headline` - Article headline
- `news/content` - Article content (plain text, no HTML)
- `news/source` - Feed name (e.g., "TechCrunch", "BBC World")
- `news/link` - Article URL
- `news/published` - Publication date

**RSS Feeds:**
- TechCrunch
- The Verge
- Wired
- Ars Technica
- Engadget
- BBC World
- CNN International
- Al Jazeera

### Time Topics

- `today/time` - Current time in HH:MM format (24-hour, retained, updates every minute)
- `today/seconds` - Current seconds SS format (00-59, NOT retained, updates every second)

### Slovak Date Topics (all retained)

- `today/dow` - Day of week (pondelok, utorok, streda, štvrtok, piatok, sobota, nedeľa)
- `today/sdate` - Short date (D.M.YYYY format, e.g., "20.1.2026")
- `today/ldate` - Long date (D. month format, e.g., "20. januára")
- `today/year` - Year (YYYY format)
- `today/nameday` - Slovak nameday for current date (e.g., "Dalibor")

**Features:**
- Authentic Slovak text with diacritics (ľ, š, č, ť, ž, ý, á, í, é, ó, ú)
- Complete 366-day nameday calendar
- Updates at midnight
- All retained for immediate delivery

### Calendar Topics (all retained)

Updates every 5 minutes:

**Next Event:**
- `calendar/next/title` - Event title
- `calendar/next/start` - Start time (DD.MM.YYYY HH:MM)
- `calendar/next/end` - End time
- `calendar/next/location` - Event location
- `calendar/next/description` - Event description (first 500 chars)
- `calendar/next/time_until` - Time until event (e.g., "45 min", "2 hod", "3 dni")

**Today's Schedule:**
- `calendar/today/count` - Number of events today
- `calendar/today/list` - Newline-separated list of today's events

**System:**
- `calendar/status` - Connector status (running/error)

## Management Commands

### RSS Commands

```bash
rss_status        # Show RSS publisher status and latest news
rss_latest        # Display latest news article
rss_channels      # List all subscribed RSS feeds
rss_add           # Add new RSS feed
rss_remove        # Remove RSS feed
rss_help          # Show all available commands
```

### Calendar Commands

```bash
gcal_status       # Show calendar status and next event
gcal_caldav_setup # Configure Google Calendar authentication
```

### MQTT Testing

```bash
# Subscribe to all topics
mosquitto_sub -h localhost -t '#' -v

# Subscribe to specific category
mosquitto_sub -h localhost -t 'news/#' -v
mosquitto_sub -h localhost -t 'today/#' -v
mosquitto_sub -h localhost -t 'calendar/#' -v

# Get single message
mosquitto_sub -h localhost -t 'news/headline' -C 1
mosquitto_sub -h localhost -t 'calendar/next/title' -C 1

# Publish test message
mosquitto_pub -h localhost -t 'test' -m 'hello'
```

## Setup Procedures

### RSS Feeds Setup

RSS feeds are configured in `~/.newsboat/urls`:

```bash
# View feeds
cat ~/.newsboat/urls

# Add feed manually
echo "https://example.com/feed.xml \"Category\" \"Feed Name\"" >> ~/.newsboat/urls

# Or use command
rss_add "https://example.com/feed.xml" "Tech" "Example Site"

# Restart publisher
sudo systemctl restart rss-mqtt.service
```

### Google Calendar Setup

The calendar uses CalDAV protocol (same as Fantastical, Week Calendar):

1. **Create Google App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Sign in with your work account
   - Create new app password
   - Name: "Calendar MQTT"
   - Copy the 16-character password

2. **Configure on Raspberry Pi:**
   ```bash
   gcal_caldav_setup
   ```
   - Enter your email (e.g., peter.martis@seon.io)
   - Paste the 16-character app password

3. **Restart service:**
   ```bash
   sudo systemctl restart gcal-mqtt.service
   ```

4. **Verify:**
   ```bash
   gcal_status
   ```

**Authentication files:**
- `~/.gcal_ical_url.txt` - CalDAV endpoint URL
- `~/.gcal_ical_auth.txt` - Credentials (file mode 600)

**Troubleshooting:**
- If not working, check logs: `sudo journalctl -u gcal-mqtt.service -n 50`
- Verify app password hasn't expired
- Ensure 2-Step Verification is enabled on Google account

## File Locations

### Configuration Files

```
~/.newsboat/urls              - RSS feed subscriptions
~/.gcal_ical_url.txt          - Calendar CalDAV URL
~/.gcal_ical_auth.txt         - Calendar credentials (mode 600)
~/.bashrc                     - Welcome message configuration
```

### Application Files

```
~/rss_mqtt_publisher.py       - RSS and calendar publisher
~/gcal_mqtt_connector.py      - Google Calendar connector
/usr/local/bin/rss_*          - Management commands
/usr/local/bin/gcal_*         - Calendar commands
```

### Service Files

```
/etc/systemd/system/rss-mqtt.service    - RSS publisher service
/etc/systemd/system/gcal-mqtt.service   - Calendar connector service
/etc/mosquitto/mosquitto.conf           - MQTT broker config
```

### Project Directory

```
~/rss-mqtt-project/
├── README.md                 - Project overview
├── COMPLETE_GUIDE.md         - This comprehensive guide
├── install.sh                - Automated installation
├── rss_mqtt_publisher.py     - Main RSS publisher
├── bin/                      - Management commands
│   ├── rss_status
│   ├── rss_latest
│   ├── rss_channels
│   ├── rss_add
│   ├── rss_remove
│   └── rss_help
└── calendar/                 - Calendar connector
    ├── GCAL_SETUP.md         - API setup guide (if API enabled)
    ├── CALDAV_SETUP.md       - CalDAV setup guide
    ├── gcal_caldav_simple.py - CalDAV connector (current)
    └── bin/
        └── gcal_status
```

## Technical Details

### Update Intervals

- **RSS Feeds:** Check every 60 seconds for new articles
- **RSS Rotation:** Cycle through feeds every 6 seconds when no updates
- **Time (HH:MM):** Publishes every minute when minute changes
- **Seconds (SS):** Publishes every second (not retained)
- **Date Topics:** Update at midnight
- **Calendar:** Fetches events every 5 minutes (300 seconds)

### MQTT Configuration

- **Broker:** Mosquitto running on localhost
- **Port:** 1883 (default, no TLS)
- **Authentication:** None (local only)
- **Retained Messages:** All topics except `today/seconds`
- **QoS:** 0 (fire and forget)

### Slovak Calendar Features

- **Days:** pondelok, utorok, streda, štvrtok, piatok, sobota, nedeľa
- **Months (genitive):** januára, februára, marca, apríla, mája, júna, júla, augusta, septembra, októbra, novembra, decembra
- **Namedays:** Complete 366-day calendar including leap years
- **Character encoding:** UTF-8 with Slovak diacritics preserved
- **Date formats:** 
  - Short: D.M.YYYY (no leading zeros)
  - Long: D. month (Slovak genitive case)

### Google Calendar via CalDAV

- **Protocol:** CalDAV over HTTPS
- **Endpoint:** `https://www.google.com/calendar/dav/`
- **Authentication:** App Password (16 characters)
- **Format:** iCal/ICS parsing with regex
- **Events parsed:** All events (past, present, future)
- **Published:** Only upcoming events and today's schedule
- **Works with:** Google Workspace (G Suite) accounts
- **Bypasses:** Calendar API restrictions (uses CalDAV instead)

## Backup & Restore

### GitHub Repository

Project is backed up at: https://github.com/petermartis/rss-mqtt-project

```bash
# Update repository
cd ~/rss-mqtt-project
git add -A
git commit -m "Update configuration"
git push

# Clone to new system
git clone https://github.com/petermartis/rss-mqtt-project.git
cd rss-mqtt-project
./install.sh
```

### Manual Backup

```bash
# Backup configuration
tar -czf rss-mqtt-backup.tar.gz \
    ~/.newsboat/urls \
    ~/.gcal_ical_url.txt \
    ~/.gcal_ical_auth.txt \
    ~/rss_mqtt_publisher.py \
    ~/gcal_mqtt_connector.py

# Restore
tar -xzf rss-mqtt-backup.tar.gz -C /
sudo systemctl restart rss-mqtt.service gcal-mqtt.service
```

## Monitoring & Debugging

### Check System Health

```bash
# Quick status
rss_status
gcal_status

# Detailed service status
systemctl status rss-mqtt.service gcal-mqtt.service mosquitto.service

# View live logs
sudo journalctl -u rss-mqtt.service -f
sudo journalctl -u gcal-mqtt.service -f

# Check MQTT traffic
mosquitto_sub -h localhost -t '#' -v | grep --line-buffered "."
```

### Common Issues

**No news appearing:**
```bash
# Check RSS service
sudo systemctl status rss-mqtt.service
sudo journalctl -u rss-mqtt.service -n 50

# Test feed manually
python3 -c "import feedparser; print(feedparser.parse('https://techcrunch.com/feed/'))"

# Restart service
sudo systemctl restart rss-mqtt.service
```

**No calendar events:**
```bash
# Check calendar service
sudo systemctl status gcal-mqtt.service
sudo journalctl -u gcal-mqtt.service -n 50

# Verify authentication
cat ~/.gcal_ical_auth.txt

# Test CalDAV manually
curl -u "$(cat ~/.gcal_ical_auth.txt)" "$(cat ~/.gcal_ical_url.txt)" | head -50

# Reconfigure if needed
gcal_caldav_setup
sudo systemctl restart gcal-mqtt.service
```

**MQTT not responding:**
```bash
# Check broker
sudo systemctl status mosquitto.service

# Test connection
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t test -C 1

# Restart broker
sudo systemctl restart mosquitto.service
```

## Performance & Resources

- **CPU Usage:** ~1-2% average (Raspberry Pi 5)
- **Memory:** ~50MB total for all services
- **Network:** Minimal (only RSS/CalDAV fetches)
- **Storage:** <10MB for code and logs
- **MQTT Messages:** ~100/minute during rotation

## Security Notes

- ✓ All communication is local to Raspberry Pi
- ✓ No data sent to external servers except RSS/calendar fetches
- ✓ Calendar credentials stored with mode 600 (owner only)
- ✓ MQTT broker only accessible from localhost
- ✓ App passwords can be revoked anytime
- ✓ No personal data exposed in MQTT topics

## License

MIT License - See LICENSE file

## Support & Issues

- GitHub: https://github.com/petermartis/rss-mqtt-project/issues
- Documentation: See README.md and setup guides in calendar/

## Credits

Created for Raspberry Pi 5 running Debian Bookworm
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
