#!/bin/bash
#
# Install Google Calendar MQTT Connector
#

echo "Installing Google Calendar MQTT Connector..."
echo ""

# Check if running as admin user
if [ "$USER" != "admin" ]; then
    echo "Error: Please run as admin user"
    exit 1
fi

# Install Google API libraries
echo "Installing Google API libraries..."
sudo apt-get update
sudo apt-get install -y python3-google-auth python3-google-auth-oauthlib python3-google-auth-httplib2 python3-googleapi

# Copy main scripts
echo "Installing calendar connector scripts..."
cp gcal_mqtt_connector.py ~/
cp gcal_authenticate.py ~/
chmod +x ~/gcal_mqtt_connector.py
chmod +x ~/gcal_authenticate.py

# Install management commands
echo "Installing management commands..."
sudo cp bin/gcal_status /usr/local/bin/
sudo chmod +x /usr/local/bin/gcal_status
sudo ln -sf /home/admin/gcal_authenticate.py /usr/local/bin/gcal_authenticate

# Install systemd service
echo "Installing systemd service..."
sudo cp gcal-mqtt.service /etc/systemd/system/
sudo systemctl daemon-reload

echo ""
echo "✓ Google Calendar MQTT Connector installed successfully!"
echo ""
echo "Next steps:"
echo "1. Set up Google Cloud credentials (see GCAL_SETUP.md)"
echo "2. Download OAuth credentials from Google Cloud Console"
echo "3. Save credentials as ~/gcal_credentials.json"
echo "4. Run: gcal_authenticate"
echo "5. Run: sudo systemctl start gcal-mqtt.service"
echo "6. Run: sudo systemctl enable gcal-mqtt.service"
echo ""
echo "Commands:"
echo "  gcal_status        - Show calendar status and next event"
echo "  gcal_authenticate  - Set up Google OAuth authentication"
echo ""
