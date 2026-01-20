#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Calendar CalDAV to MQTT Connector
Uses CalDAV protocol with OAuth2 (same as third-party calendar apps)
"""

import sys
import time
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
import caldav
from caldav.elements import dav
import requests
from requests.auth import HTTPBasicAuth
import json
import os

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
MQTT_TOPIC_NEXT_TIME_UNTIL = "calendar/next/time_until"
MQTT_TOPIC_TODAY_COUNT = "calendar/today/count"
MQTT_TOPIC_TODAY_LIST = "calendar/today/list"
MQTT_TOPIC_STATUS = "calendar/status"

# Google CalDAV Configuration
CALDAV_URL = "https://apidata.googleusercontent.com/caldav/v2/"
CREDENTIALS_FILE = os.path.expanduser("~/.gcal_caldav_auth.json")

# Update interval (seconds)
UPDATE_INTERVAL = 300  # 5 minutes

def log(message):
    """Print log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)

def load_credentials():
    """Load saved email and app password"""
    if not os.path.exists(CREDENTIALS_FILE):
        return None, None

    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            creds = json.load(f)
            return creds.get('email'), creds.get('password')
    except Exception as e:
        log(f"Error loading credentials: {e}")
        return None, None

def format_datetime(dt):
    """Format datetime to readable format"""
    try:
        if isinstance(dt, datetime):
            return dt.strftime("%d.%m.%Y %H:%M")
        else:
            # All-day event (date only)
            return dt.strftime("%d.%m.%Y")
    except Exception as e:
        log(f"Error formatting datetime: {e}")
        return str(dt)

def get_time_until(start_dt):
    """Calculate time until event starts"""
    try:
        now = datetime.now()

        # Handle all-day events
        if not isinstance(start_dt, datetime):
            start_dt = datetime.combine(start_dt, datetime.min.time())

        # Make timezone-naive for comparison
        if start_dt.tzinfo:
            start_dt = start_dt.replace(tzinfo=None)

        delta = start_dt - now

        if delta.total_seconds() < 0:
            return "Prebieha"
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
    """Clean and normalize text"""
    if not text:
        return ""
    # Normalize whitespace
    text = ' '.join(str(text).split())
    return text.strip()

def connect_caldav():
    """Connect to Google Calendar via CalDAV"""
    email, password = load_credentials()

    if not email or not password:
        log("ERROR: CalDAV credentials not found")
        log("Please run: gcal_caldav_setup")
        return None

    try:
        # Connect to CalDAV
        client = caldav.DAVClient(
            url=CALDAV_URL + email + "/events/",
            username=email,
            password=password
        )

        principal = client.principal()
        calendars = principal.calendars()

        if not calendars:
            log("ERROR: No calendars found")
            return None

        # Use primary calendar
        calendar = calendars[0]
        log(f"Connected to calendar: {email}")
        return calendar

    except Exception as e:
        log(f"CalDAV connection error: {e}")
        log("Note: You need an App Password from Google")
        log("Go to: https://myaccount.google.com/apppasswords")
        return None

def get_events(calendar, start_date, end_date):
    """Get events from calendar"""
    try:
        events = calendar.date_search(
            start=start_date,
            end=end_date,
            expand=True
        )

        event_list = []
        for event in events:
            try:
                vevent = event.vobject_instance.vevent

                # Extract event details
                event_data = {
                    'summary': getattr(vevent, 'summary', None),
                    'dtstart': getattr(vevent, 'dtstart', None),
                    'dtend': getattr(vevent, 'dtend', None),
                    'location': getattr(vevent, 'location', None),
                    'description': getattr(vevent, 'description', None),
                }

                # Get values
                if event_data['summary']:
                    event_data['summary'] = event_data['summary'].value
                if event_data['dtstart']:
                    event_data['dtstart'] = event_data['dtstart'].value
                if event_data['dtend']:
                    event_data['dtend'] = event_data['dtend'].value
                if event_data['location']:
                    event_data['location'] = event_data['location'].value
                if event_data['description']:
                    event_data['description'] = event_data['description'].value

                event_list.append(event_data)

            except Exception as e:
                log(f"Error parsing event: {e}")
                continue

        # Sort by start time
        event_list.sort(key=lambda x: x['dtstart'] if x['dtstart'] else datetime.max)

        return event_list

    except Exception as e:
        log(f"Error fetching events: {e}")
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
        client.publish(MQTT_TOPIC_NEXT_TIME_UNTIL, "", retain=True)
        log("No upcoming events")
        return

    # Publish event details
    title = clean_text(event.get('summary', 'Bez názvu'))
    start_formatted = format_datetime(event.get('dtstart'))
    end_formatted = format_datetime(event.get('dtend'))
    location = clean_text(event.get('location', ''))
    description = clean_text(event.get('description', ''))
    time_until = get_time_until(event.get('dtstart'))

    client.publish(MQTT_TOPIC_NEXT_EVENT, title, retain=True)
    client.publish(MQTT_TOPIC_NEXT_START, start_formatted, retain=True)
    client.publish(MQTT_TOPIC_NEXT_END, end_formatted, retain=True)
    client.publish(MQTT_TOPIC_NEXT_LOCATION, location, retain=True)
    client.publish(MQTT_TOPIC_NEXT_DESCRIPTION, description[:500], retain=True)
    client.publish(MQTT_TOPIC_NEXT_TIME_UNTIL, time_until, retain=True)

    log(f"Published next event: {title} at {start_formatted}")

def publish_today_events(mqtt_client, events):
    """Publish today's event count and list"""
    count = len(events)
    mqtt_client.publish(MQTT_TOPIC_TODAY_COUNT, str(count), retain=True)

    # Create list of today's events
    event_list = []
    for event in events:
        title = clean_text(event.get('summary', 'Bez názvu'))
        start_formatted = format_datetime(event.get('dtstart'))
        event_list.append(f"{start_formatted} - {title}")

    today_list = '\n'.join(event_list) if event_list else "Žiadne udalosti dnes"
    mqtt_client.publish(MQTT_TOPIC_TODAY_LIST, today_list, retain=True)

    log(f"Published {count} events for today")

def main():
    """Main loop"""
    log("Starting Google Calendar CalDAV MQTT Connector")

    # Connect to MQTT
    mqtt_client = mqtt.Client()

    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        log(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        log(f"Failed to connect to MQTT broker: {e}")
        sys.exit(1)

    mqtt_client.loop_start()
    mqtt_client.publish(MQTT_TOPIC_STATUS, "initializing", retain=True)

    # Connect to CalDAV
    calendar = connect_caldav()

    if not calendar:
        mqtt_client.publish(MQTT_TOPIC_STATUS, "authentication_required", retain=True)
        log("ERROR: Run gcal_caldav_setup to configure credentials")
        sys.exit(1)

    mqtt_client.publish(MQTT_TOPIC_STATUS, "running", retain=True)
    log("CalDAV connection established")

    # Main loop
    while True:
        try:
            # Get upcoming events (next 30 days)
            now = datetime.now()
            future = now + timedelta(days=30)

            events = get_events(calendar, now, future)

            if events:
                publish_next_event(mqtt_client, events[0])
            else:
                publish_next_event(mqtt_client, None)

            # Get today's events
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

            today_events = get_events(calendar, today_start, today_end)
            publish_today_events(mqtt_client, today_events)

            mqtt_client.publish(MQTT_TOPIC_STATUS, "running", retain=True)

        except Exception as e:
            log(f"Error in main loop: {e}")
            mqtt_client.publish(MQTT_TOPIC_STATUS, f"error: {str(e)}", retain=True)

        # Wait before next update
        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
