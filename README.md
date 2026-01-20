# RSS to MQTT Publisher

Automated RSS feed aggregator that publishes news articles to MQTT topics in real-time. Perfect for Raspberry Pi and IoT projects.

**Repository:** https://github.com/petermartis/rss-mqtt-project

## Features

- 📰 Monitors 8 RSS feeds (5 Tech + 3 International News)
- 🔄 Rotates through feeds every 6 seconds
- 🆕 Checks for new articles every 60 seconds
- 📡 Publishes to retained MQTT topics (plain text)
- 🚀 Auto-starts on boot via systemd
- 🧹 Clean ASCII text (no HTML, no diacritics)
- 📝 Easy feed management commands
- ⏰ Real-time clock with seconds precision
- 📅 Slovak date and nameday calendar
- 🌍 Automatic timezone handling

## MQTT Topics

All messages are published as plain text.

### News Topics (Retained)
- `news/headline` - Article headline
- `news/content` - Article content (max 500 chars)
- `news/source` - Feed name (e.g., "TechCrunch", "BBC World")
- `news/link` - Article URL
- `news/published` - Publication date/time

### Time Topics
- `today/time` - Current time (HH:MM format, updates every minute) - **Retained**
- `today/seconds` - Current seconds (SS format, updates every second) - **Not retained**

### Date Topics (Retained)
- `today/dow` - Slovak day of week (e.g., "pondelok", "utorok", "streda")
- `today/sdate` - Short date (D.M.YYYY format, e.g., "20.1.2026")
- `today/ldate` - Long date (D. month format, e.g., "20. januara")
- `today/year` - Current year (YYYY format, e.g., "2026")
- `today/nameday` - Slovak name day (e.g., "Dalibor", "Novy rok")

## Requirements

- Raspberry Pi (tested on Pi 5) or any Linux system
- Python 3.11+
- Mosquitto MQTT Broker
- Internet connection

## Quick Installation

```bash
# Clone the repository
git clone https://github.com/petermartis/rss-mqtt-project.git
cd rss-mqtt-project

# Run installation script
chmod +x install.sh
sudo ./install.sh

# Service will start automatically
```

## Manual Installation

See [INSTALL.md](INSTALL.md) for detailed manual installation instructions.

## Usage

### Management Commands

```bash
rss_status      # Show service status
rss_latest      # Display latest news
rss_channels    # List subscribed feeds
rss_add URL     # Add new RSS feed
rss_remove URL  # Remove RSS feed
rss_help        # Show help
```

### Service Control

```bash
sudo systemctl start rss-mqtt
sudo systemctl stop rss-mqtt
sudo systemctl restart rss-mqtt
sudo systemctl status rss-mqtt
```

### Subscribe to News

```bash
# Subscribe to all news topics
mosquitto_sub -h localhost -t "news/#" -v

# Subscribe to headlines only
mosquitto_sub -h localhost -t "news/headline" -v

# Subscribe to all time topics
mosquitto_sub -h localhost -t "today/#" -v

# Subscribe to time updates (HH:MM every minute)
mosquitto_sub -h localhost -t "today/time" -v

# Subscribe to seconds (updates every second)
mosquitto_sub -h localhost -t "today/seconds" -v
```

## Default RSS Feeds

### Tech News (5)
- TechCrunch
- The Verge
- Wired
- Ars Technica
- Engadget

### International News (3)
- BBC World
- CNN International
- Al Jazeera

## Configuration

Edit `feeds.txt` to customize RSS feeds, then:

```bash
cp feeds.txt ~/.newsboat/urls
sudo systemctl restart rss-mqtt
```

## Slovak Calendar Features

The publisher includes full Slovak calendar support:

- **Day names**: pondelok, utorok, streda, stvrtok, piatok, sobota, nedela
- **Month names**: januara, februara, marca... (genitive case, no diacritics)
- **Name days**: 366 Slovak name days (including leap year)
- **Special days**: "Novy rok", "Sviatok prace", "1.sviatok vianocny", etc.
- **All text**: No diacritics (ASCII compatible)

## File Structure

```
rss-mqtt-project/
├── README.md                  # This file
├── INSTALL.md                 # Detailed installation guide
├── install.sh                 # Automated installation script
├── rss_mqtt_publisher.py      # Main publisher application
├── rss-mqtt.service           # Systemd service file
├── feeds.txt                  # RSS feed list
├── bin/                       # Management commands
│   ├── rss_status
│   ├── rss_latest
│   ├── rss_channels
│   ├── rss_add
│   ├── rss_remove
│   └── rss_help
└── bashrc_snippet.sh          # Optional bash integration
```

## Troubleshooting

### Service not running
```bash
sudo systemctl status rss-mqtt
sudo journalctl -u rss-mqtt -f
```

### No MQTT messages
```bash
# Check if Mosquitto is running
sudo systemctl status mosquitto

# Check if feeds are configured
rss_channels
```

### Add new feed not working
```bash
# After adding feeds, restart the service
sudo systemctl restart rss-mqtt
```

## Backup & Restore

### Create Backup
All project files are version controlled in this GitHub repository. To backup current configuration:

```bash
cd ~/rss-mqtt-project
cp ~/.newsboat/urls feeds.txt
cp ~/rss_mqtt_publisher.py .
git add .
git commit -m "Backup: $(date +%Y-%m-%d)"
git push
```

### Restore on New Raspberry Pi
If your SD card fails or you upgrade your Raspberry Pi, restore everything with:

```bash
# Clone the repository
git clone https://github.com/petermartis/rss-mqtt-project.git
cd rss-mqtt-project

# Run installation script (installs everything automatically)
chmod +x install.sh
sudo ./install.sh

# Service starts automatically - ready in under 2 minutes!
```

## License

MIT License - See LICENSE file

## Author

Created for Raspberry Pi home automation projects

## Contributing

Pull requests welcome! Please ensure:
- Code follows existing style
- Test on Raspberry Pi before submitting
- Update documentation as needed

## Google Calendar Integration

The project includes a Google Calendar connector that publishes upcoming events to MQTT topics. This works with Google Workspace (G Suite) accounts.

### Features

- **Next Event**: Publishes details about your next upcoming calendar event
- **Today's Schedule**: Shows count and list of today's events
- **Auto-refresh**: Updates every 5 minutes
- **Retained Messages**: All calendar data is retained for immediate delivery
- **OAuth2 Authentication**: Secure readonly access to your calendar

### MQTT Topics

**Next Event** (all retained):
- `calendar/next/title` - Event title
- `calendar/next/start` - Start time (DD.MM.YYYY HH:MM)
- `calendar/next/end` - End time
- `calendar/next/location` - Event location
- `calendar/next/description` - Event description
- `calendar/next/attendees` - List of attendees
- `calendar/next/time_until` - Time until event (e.g., "45 min", "2 hod")

**Today** (all retained):
- `calendar/today/count` - Number of events today
- `calendar/today/list` - List of today's events

**Status**:
- `calendar/status` - Connector status

### Setup

See [calendar/GCAL_SETUP.md](calendar/GCAL_SETUP.md) for complete setup instructions.

Quick setup:
1. Create Google Cloud project and enable Calendar API
2. Create OAuth 2.0 credentials (Desktop app)
3. Download credentials to `~/gcal_credentials.json`
4. Run `gcal_authenticate` to authenticate
5. Run `sudo systemctl start gcal-mqtt.service`

### Commands

- `gcal_status` - Show calendar status and next event
- `gcal_authenticate` - Set up Google OAuth authentication
