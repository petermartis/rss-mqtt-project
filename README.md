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
- ⏰ Real-time clock updates every minute (today/time topic)

## MQTT Topics

All messages are published as plain text with retain flag:

- `news/headline` - Article headline
- `news/content` - Article content (max 500 chars)
- `news/source` - Feed name and category
- `news/link` - Article URL  
- `news/publish` - Publication date/time
- `today/time` - Current time (HH:MM format, updates every minute)

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
