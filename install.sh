#!/bin/bash

# RSS to MQTT Publisher Installation Script
# For Raspberry Pi / Debian-based Linux systems

set -e

echo "=========================================="
echo "RSS to MQTT Publisher - Installation"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please run without sudo. The script will ask for sudo when needed."
    exit 1
fi

# Check for required commands
command -v mosquitto >/dev/null 2>&1 || { echo "ERROR: Mosquitto MQTT broker not found. Please install mosquitto first."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "ERROR: Python 3 not found. Please install python3 first."; exit 1; }

echo "✓ Prerequisites check passed"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
sudo apt-get update -qq
sudo apt-get install -y python3-paho-mqtt python3-feedparser
echo "✓ Python dependencies installed"
echo ""

# Copy publisher script
echo "Installing RSS publisher..."
cp rss_mqtt_publisher.py ~/rss_mqtt_publisher.py
chmod +x ~/rss_mqtt_publisher.py
echo "✓ Publisher installed to ~/rss_mqtt_publisher.py"
echo ""

# Install management commands
echo "Installing management commands..."
sudo cp bin/rss_* /usr/local/bin/
sudo chmod +x /usr/local/bin/rss_*
echo "✓ Commands installed to /usr/local/bin/"
echo ""

# Setup RSS feeds
echo "Setting up RSS feeds..."
mkdir -p ~/.newsboat
cp feeds.txt ~/.newsboat/urls
echo "✓ RSS feeds configured"
echo ""

# Install systemd service
echo "Installing systemd service..."
sudo cp rss-mqtt.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rss-mqtt.service
echo "✓ Service installed and enabled"
echo ""

# Start service
echo "Starting RSS to MQTT service..."
sudo systemctl start rss-mqtt.service
sleep 2

if systemctl is-active --quiet rss-mqtt; then
    echo "✓ Service started successfully"
else
    echo "✗ Service failed to start. Check: sudo journalctl -u rss-mqtt -n 50"
    exit 1
fi

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Available commands:"
echo "  rss_status      - Show service status"
echo "  rss_latest      - Display latest news"
echo "  rss_channels    - List RSS feeds"
echo "  rss_add <URL>   - Add RSS feed"
echo "  rss_remove <URL> - Remove RSS feed"
echo "  rss_help        - Show help"
echo ""
echo "MQTT Topics: news/headline, news/content, news/source, news/link, news/publish"
echo ""
echo "Test with: mosquitto_sub -h localhost -t 'news/#' -v"
echo ""
