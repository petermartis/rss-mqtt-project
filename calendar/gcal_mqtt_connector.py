#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Calendar to MQTT Connector for Google Workspace (G Suite)
Publishes upcoming calendar events to MQTT topics
"""

import sys
import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path
import pickle

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_NEXT_EVENT = "calendar/next/title"
MQTT_TOPIC_NEXT_START = "calendar/next/start"
MQTT_TOPIC_NEXT_END = "calendar/next/end"
MQTT_TOPIC_NEXT_LOCATION = "calendar/next/location"
MQTT_TOPIC_NEXT_DESCRIPTION = "calendar/next/description"
MQTT_TOPIC_NEXT_ATTENDEES = "calendar/next/attendees"
MQTT_TOPIC_NEXT_TIME_UNTIL = "calendar/next/time_until"
MQTT_TOPIC_TODAY_COUNT = "calendar/today/count"
MQTT_TOPIC_TODAY_LIST = "calendar/today/list"
MQTT_TOPIC_STATUS = "calendar/status"

# Google Calendar Configuration
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_FILE = '/home/admin/.gcal_token.pickle'
CREDENTIALS_FILE = '/home/admin/gcal_credentials.json'

# Update interval (seconds)
UPDATE_INTERVAL = 300  # 5 minutes

def log(message):
    """Print log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)

def get_calendar_service():
    """Get authenticated Google Calendar service"""
    creds = None

    # Load token if it exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, need to authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                log("Refreshed OAuth2 token")
            except Exception as e:
                log(f"Error refreshing token: {e}")
                return None
        else:
            log("ERROR: No valid credentials. Run gcal_authenticate first.")
            return None

        # Save the credentials for next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        log(f"Error building calendar service: {e}")
        return None

def format_datetime(dt_str):
    """Format datetime string to readable format"""
    try:
        # Parse ISO format datetime
        if 'T' in dt_str:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime("%d.%m.%Y %H:%M")
        else:
            # All-day event
            dt = datetime.strptime(dt_str, "%Y-%m-%d")
            return dt.strftime("%d.%m.%Y")
    except Exception as e:
        log(f"Error formatting datetime {dt_str}: {e}")
        return dt_str

def get_time_until(start_str):
    """Calculate time until event starts"""
    try:
        now = datetime.now()

        if 'T' in start_str:
            start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            # Remove timezone info for comparison
            if start.tzinfo:
                start = start.replace(tzinfo=None)
        else:
            # All-day event
            start = datetime.strptime(start_str, "%Y-%m-%d")

        delta = start - now

        if delta.total_seconds() < 0:
            return "Started"
        elif delta.total_seconds() < 3600:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes} min"
        elif delta.total_seconds() < 86400:
            hours = int(delta.total_seconds() / 3600)
            return f"{hours} hod"
        else:
            days = delta.days
            return f"{days} dni"
    except Exception as e:
        log(f"Error calculating time until: {e}")
        return ""

def clean_text(text):
    """Remove HTML tags and normalize text"""
    if not text:
        return ""
    # Basic HTML tag removal
    import re
    text = re.sub('<[^<]+?>', '', text)
    # Normalize whitespace
    text = ' '.join(text.split())
    return text.strip()

def get_upcoming_events(service, max_results=10):
    """Get upcoming calendar events"""
    try:
        now = datetime.utcnow().isoformat() + 'Z'

        # Get events from primary calendar
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        return events
    except HttpError as error:
        log(f"Google Calendar API error: {error}")
        return []
    except Exception as e:
        log(f"Error fetching events: {e}")
        return []

def get_today_events(service):
    """Get events for today"""
    try:
        # Start and end of today
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        time_min = start_of_day.isoformat() + 'Z'
        time_max = end_of_day.isoformat() + 'Z'

        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        return events
    except Exception as e:
        log(f"Error fetching today's events: {e}")
        return []

def publish_next_event(client, event):
    """Publish next upcoming event to MQTT"""
    if not event:
        # No upcoming events
        client.publish(MQTT_TOPIC_NEXT_EVENT, "", retain=True)
        client.publish(MQTT_TOPIC_NEXT_START, "", retain=True)
        client.publish(MQTT_TOPIC_NEXT_END, "", retain=True)
        client.publish(MQTT_TOPIC_NEXT_LOCATION, "", retain=True)
        client.publish(MQTT_TOPIC_NEXT_DESCRIPTION, "", retain=True)
        client.publish(MQTT_TOPIC_NEXT_ATTENDEES, "", retain=True)
        client.publish(MQTT_TOPIC_NEXT_TIME_UNTIL, "", retain=True)
        log("No upcoming events")
        return

    # Extract event details
    title = event.get('summary', 'No title')
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))
    location = event.get('location', '')
    description = clean_text(event.get('description', ''))

    # Get attendees
    attendees = event.get('attendees', [])
    attendee_list = ', '.join([a.get('email', '') for a in attendees])

    # Format times
    start_formatted = format_datetime(start)
    end_formatted = format_datetime(end)
    time_until = get_time_until(start)

    # Publish to MQTT
    client.publish(MQTT_TOPIC_NEXT_EVENT, title, retain=True)
    client.publish(MQTT_TOPIC_NEXT_START, start_formatted, retain=True)
    client.publish(MQTT_TOPIC_NEXT_END, end_formatted, retain=True)
    client.publish(MQTT_TOPIC_NEXT_LOCATION, location, retain=True)
    client.publish(MQTT_TOPIC_NEXT_DESCRIPTION, description[:500], retain=True)  # Limit length
    client.publish(MQTT_TOPIC_NEXT_ATTENDEES, attendee_list, retain=True)
    client.publish(MQTT_TOPIC_NEXT_TIME_UNTIL, time_until, retain=True)

    log(f"Published next event: {title} at {start_formatted}")

def publish_today_events(client, events):
    """Publish today's event count and list"""
    count = len(events)
    client.publish(MQTT_TOPIC_TODAY_COUNT, str(count), retain=True)

    # Create a simple list of today's events
    event_list = []
    for event in events:
        title = event.get('summary', 'No title')
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_formatted = format_datetime(start)
        event_list.append(f"{start_formatted} - {title}")

    # Join with newlines
    today_list = '\n'.join(event_list) if event_list else "No events today"
    client.publish(MQTT_TOPIC_TODAY_LIST, today_list, retain=True)

    log(f"Published {count} events for today")

def main():
    """Main loop"""
    log("Starting Google Calendar MQTT Connector")

    # Check for credentials file
    if not os.path.exists(CREDENTIALS_FILE):
        log(f"ERROR: Credentials file not found: {CREDENTIALS_FILE}")
        log("Please download credentials from Google Cloud Console and save as gcal_credentials.json")
        sys.exit(1)

    # Connect to MQTT
    client = mqtt.Client()

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        log(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        log(f"Failed to connect to MQTT broker: {e}")
        sys.exit(1)

    client.loop_start()

    # Publish status
    client.publish(MQTT_TOPIC_STATUS, "initializing", retain=True)

    # Get calendar service
    service = get_calendar_service()

    if not service:
        client.publish(MQTT_TOPIC_STATUS, "authentication_required", retain=True)
        log("ERROR: Authentication required. Run gcal_authenticate first.")
        sys.exit(1)

    client.publish(MQTT_TOPIC_STATUS, "running", retain=True)
    log("Calendar service authenticated successfully")

    # Main loop
    while True:
        try:
            # Get upcoming events
            events = get_upcoming_events(service, max_results=10)

            if events:
                # Publish next event
                publish_next_event(client, events[0])
            else:
                publish_next_event(client, None)

            # Get today's events
            today_events = get_today_events(service)
            publish_today_events(client, today_events)

            client.publish(MQTT_TOPIC_STATUS, "running", retain=True)

        except Exception as e:
            log(f"Error in main loop: {e}")
            client.publish(MQTT_TOPIC_STATUS, f"error: {str(e)}", retain=True)

        # Wait before next update
        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
