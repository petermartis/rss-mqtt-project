# Manual Installation Guide

Complete step-by-step guide for manually installing the RSS to MQTT Publisher.

## Prerequisites

### 1. Install Mosquitto MQTT Broker

```bash
sudo apt-get update
sudo apt-get install mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

Verify installation:
```bash
sudo systemctl status mosquitto
```

### 2. Install Python Dependencies

```bash
sudo apt-get install python3-paho-mqtt python3-feedparser
```

## Installation Steps

### 1. Copy Publisher Script

```bash
cp rss_mqtt_publisher.py ~/rss_mqtt_publisher.py
chmod +x ~/rss_mqtt_publisher.py
```

### 2. Configure RSS Feeds

```bash
mkdir -p ~/.newsboat
cp feeds.txt ~/.newsboat/urls
```

To customize feeds, edit `~/.newsboat/urls`:
```bash
nano ~/.newsboat/urls
```

Format: `URL "Category" "Name"`

### 3. Install Management Commands

```bash
sudo cp bin/rss_* /usr/local/bin/
sudo chmod +x /usr/local/bin/rss_*
```

### 4. Install Systemd Service

```bash
sudo cp rss-mqtt.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rss-mqtt.service
sudo systemctl start rss-mqtt.service
```

### 5. Verify Installation

Check service status:
```bash
sudo systemctl status rss-mqtt
```

Check logs:
```bash
sudo journalctl -u rss-mqtt -f
```

Test MQTT messages:
```bash
mosquitto_sub -h localhost -t "news/#" -v
```

## Optional: Bash Integration

Add RSS welcome message and aliases to your `.bashrc`:

```bash
cat bashrc_snippet.sh >> ~/.bashrc
source ~/.bashrc
```

## Uninstallation

To completely remove the RSS publisher:

```bash
# Stop and disable service
sudo systemctl stop rss-mqtt
sudo systemctl disable rss-mqtt

# Remove files
sudo rm /etc/systemd/system/rss-mqtt.service
sudo rm /usr/local/bin/rss_*
rm ~/rss_mqtt_publisher.py
rm -rf ~/.newsboat

# Reload systemd
sudo systemctl daemon-reload
```

## Troubleshooting

### Service won't start

Check Python path in service file:
```bash
which python3
```

Edit service file if needed:
```bash
sudo nano /etc/systemd/system/rss-mqtt.service
```

### MQTT connection fails

Verify Mosquitto is running:
```bash
sudo systemctl status mosquitto
netstat -an | grep 1883
```

### No articles being published

Check RSS feeds are valid:
```bash
rss_channels
```

Manually test a feed:
```bash
curl -s "https://techcrunch.com/feed/" | head -50
```

### Permission issues

Ensure script is owned by the correct user:
```bash
ls -la ~/rss_mqtt_publisher.py
sudo systemctl cat rss-mqtt | grep User
```

## Configuration

### Change Update Frequency

Edit `rss_mqtt_publisher.py`:
- Line ~210: Change `60` to adjust new article check interval
- Line ~215: Change `6` to adjust feed rotation interval

### Add Authentication to MQTT

Edit `rss_mqtt_publisher.py` and add before `client.connect()`:
```python
client.username_pw_set("username", "password")
```

### Change MQTT Topics

Edit the topic constants at the top of `rss_mqtt_publisher.py`:
```python
MQTT_TOPIC_HEADLINE = "news/headline"
# Change to your preferred topics
```
