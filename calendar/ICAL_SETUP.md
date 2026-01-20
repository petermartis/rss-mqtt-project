# Google Calendar iCal MQTT Connector Setup

This is an alternative to the Google Calendar API that works when the API is disabled by your organization.

## Overview

Instead of using the Google Calendar API, this connector uses your calendar's private iCal feed URL. This works even when the Calendar API is disabled by your Google Workspace administrator.

## Setup Steps

### 1. Get Your Calendar's iCal URL

**On Desktop:**
1. Go to [Google Calendar](https://calendar.google.com)
2. Click the **Settings** gear icon (top right)
3. Click **Settings**
4. In the left sidebar, find your calendar under "Settings for my calendars"
5. Click on your calendar name
6. Scroll down to "**Integrate calendar**"
7. Find "**Secret address in iCal format**"
8. Click the **iCal** button to copy the URL
   - The URL looks like: `https://calendar.google.com/calendar/ical/YOUR_EMAIL/private-XXXXXXXX/basic.ics`

**Important:** This is a **private URL** - anyone with this URL can see your calendar events!

### 2. Save iCal URL on Raspberry Pi

SSH to your Raspberry Pi and save the URL:

```bash
ssh admin@192.168.3.11

# Save your iCal URL
echo "https://calendar.google.com/calendar/ical/YOUR_EMAIL/private-XXXXXXXX/basic.ics" > ~/.gcal_ical_url.txt

# Make sure only you can read it
chmod 600 ~/.gcal_ical_url.txt
```

### 3. Install the iCal Connector

```bash
# Copy the iCal connector script
cp ~/rss-mqtt-project/calendar/ical_mqtt_connector.py ~/gcal_mqtt_connector.py
chmod +x ~/gcal_mqtt_connector.py

# The systemd service is already installed, just restart it
sudo systemctl restart gcal-mqtt.service
sudo systemctl enable gcal-mqtt.service
```

### 4. Verify

```bash
gcal_status
```

You should see your upcoming calendar events!

## MQTT Topics

Same topics as the API version:
- `calendar/next/*` - Next event details
- `calendar/today/*` - Today's events
- `calendar/status` - Connector status

## Differences from API Version

### Advantages ✓
- **No API setup required** - Works immediately
- **No OAuth authentication** - Just need the iCal URL
- **Works with API disabled** - Bypasses API restrictions
- **Simpler setup** - One URL, no Google Cloud Console

### Limitations ✗
- **No attendee information** - iCal feeds don't include attendees
- **Private URL** - Must be kept secret
- **Slightly slower** - Downloads entire calendar each time
- **Limited to one calendar** - Can't easily access multiple calendars

## Security Notes

⚠️ **Important:** Your iCal URL is private and should be kept secret!

- Anyone with this URL can view all your calendar events
- The URL is stored in `~/.gcal_ical_url.txt` with restricted permissions (600)
- The URL never leaves your Raspberry Pi
- No data is sent to external servers

## Troubleshooting

### No Events Showing

1. Check the iCal URL is correct:
   ```bash
   cat ~/.gcal_ical_url.txt
   ```

2. Test fetching the calendar:
   ```bash
   curl -s "$(cat ~/.gcal_ical_url.txt)" | head -20
   ```
   You should see iCal data starting with `BEGIN:VCALENDAR`

3. Check service logs:
   ```bash
   sudo journalctl -u gcal-mqtt.service -n 50
   ```

### "Error fetching iCal feed"

- Verify you have internet connection
- Check the URL hasn't changed (Google sometimes regenerates these URLs)
- Make sure the URL includes the `/basic.ics` at the end

## Switching Back to API Version

If your organization later enables the Calendar API, you can switch back:

1. Follow the original API setup in `GCAL_SETUP.md`
2. Run `gcal_authenticate`
3. Replace the connector:
   ```bash
   cp ~/rss-mqtt-project/calendar/gcal_mqtt_connector.py ~/
   sudo systemctl restart gcal-mqtt.service
   ```

## Commands

Same commands work with both versions:
- `gcal_status` - Show calendar status
- `sudo systemctl restart gcal-mqtt.service` - Restart connector
- `sudo journalctl -u gcal-mqtt.service -f` - View logs
