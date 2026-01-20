# Google Calendar MQTT Connector Setup

This guide explains how to set up Google Calendar integration with MQTT for Google Workspace (G Suite) accounts.

## Overview

The Google Calendar connector monitors your Google Workspace calendar and publishes upcoming events to MQTT topics in real-time. It updates every 5 minutes and publishes information about your next event and today's schedule.

## Prerequisites

- Google Workspace (G Suite) account
- Access to Google Cloud Console
- Python 3 with Google API libraries (already installed)

## Setup Steps

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project name/ID

### 2. Enable Google Calendar API

1. In Google Cloud Console, go to **APIs & Services > Library**
2. Search for "Google Calendar API"
3. Click on it and click **Enable**

### 3. Create OAuth 2.0 Credentials

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: **Internal** (for Google Workspace)
   - App name: `Calendar MQTT Connector`
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: No need to add (we use readonly calendar scope)
   - Click **Save and Continue**

4. Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: `Calendar MQTT Connector`
   - Click **Create**

5. Download the credentials:
   - Click the download icon (⬇) next to your client ID
   - This downloads a JSON file named like `client_secret_xxx.json`

### 4. Install Credentials on Raspberry Pi

Transfer the downloaded JSON file to your Raspberry Pi:

```bash
# On your computer, use scp or copy the content
scp client_secret_xxx.json admin@192.168.3.11:~/gcal_credentials.json

# Or manually copy the content to ~/gcal_credentials.json
```

Make sure the file is saved as `/home/admin/gcal_credentials.json`

### 5. Authenticate

Run the authentication script:

```bash
gcal_authenticate
```

This will:
- Open a browser window for Google OAuth
- Ask you to sign in to your Google Workspace account
- Request permission to read your calendar
- Save the authentication token

**Note:** The authentication happens locally on the Raspberry Pi. If you're connecting via SSH, you may need to:
- Use SSH with X11 forwarding: `ssh -X admin@192.168.3.11`
- Or run the authentication on the Pi directly with a monitor/keyboard

### 6. Start the Service

```bash
sudo systemctl start gcal-mqtt.service
sudo systemctl enable gcal-mqtt.service
```

### 7. Verify Operation

```bash
gcal_status
```

You should see:
- Service: Running
- Authentication: Configured
- Your next calendar event details

## MQTT Topics

All topics are retained and update every 5 minutes:

### Next Upcoming Event
- `calendar/next/title` - Event title/summary
- `calendar/next/start` - Start time (DD.MM.YYYY HH:MM)
- `calendar/next/end` - End time (DD.MM.YYYY HH:MM)
- `calendar/next/location` - Event location
- `calendar/next/description` - Event description (first 500 chars)
- `calendar/next/attendees` - Comma-separated list of attendee emails
- `calendar/next/time_until` - Human-readable time until event (e.g., "45 min", "2 hod", "3 dni")

### Today's Schedule
- `calendar/today/count` - Number of events today
- `calendar/today/list` - Newline-separated list of today's events

### System
- `calendar/status` - Connector status (running/error/authentication_required)

## Commands

- `gcal_status` - Show calendar connector status and next event
- `gcal_authenticate` - Run OAuth authentication (one-time setup)
- `sudo systemctl restart gcal-mqtt.service` - Restart the connector
- `sudo systemctl stop gcal-mqtt.service` - Stop the connector
- `sudo journalctl -u gcal-mqtt.service -f` - View live logs

## Testing MQTT Topics

```bash
# Subscribe to all calendar topics
mosquitto_sub -h localhost -t 'calendar/#' -v

# Subscribe to next event only
mosquitto_sub -h localhost -t 'calendar/next/#' -v

# Check today's events
mosquitto_sub -h localhost -t 'calendar/today/list' -C 1
```

## Troubleshooting

### Authentication Required Error

If you see "authentication_required" status:
```bash
gcal_authenticate
```

### Token Expired

The OAuth token should auto-refresh. If it fails:
```bash
rm ~/.gcal_token.pickle
gcal_authenticate
```

### No Events Showing

- Check that you have events in your Google Calendar
- Verify the service is running: `systemctl status gcal-mqtt.service`
- Check logs: `sudo journalctl -u gcal-mqtt.service -n 50`

### API Quota Exceeded

Google Calendar API has quota limits. The connector updates every 5 minutes to stay well within free tier limits (10,000 requests/day).

## Security Notes

- The OAuth token is stored securely in `~/.gcal_token.pickle`
- Only readonly calendar access is requested
- No calendar data is sent outside your local network
- All MQTT communication is local to your Raspberry Pi

## Integration with RSS Publisher

The calendar connector works alongside the RSS-MQTT publisher. Both services run independently and publish to different MQTT topics:

- RSS: `news/*` and `today/*` topics
- Calendar: `calendar/*` topics

You can subscribe to both using MQTT wildcards:
```bash
mosquitto_sub -h localhost -t '#' -v  # All topics
```
