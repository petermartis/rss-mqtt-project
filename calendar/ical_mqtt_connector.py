#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Calendar iCal to MQTT Connector
Uses public/private iCal feed URLs (no API required)
"""

import sys
import time
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
import urllib.request
import re

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

# Calendar Configuration
ICAL_URL_FILE = '/home/admin/.gcal_ical_url.txt'

# Update interval (seconds)
UPDATE_INTERVAL = 300  # 5 minutes

def log(message):
    """Print log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)

def parse_ical_datetime(dt_str):
    """Parse iCal datetime format"""
    # Remove TZID if present
    dt_str = re.sub(r'TZID=[^:]+:', '', dt_str)

    try:
        # Try datetime format
        if 'T' in dt_str:
            dt_str = dt_str.rstrip('Z')
            return datetime.strptime(dt_str, "%Y%m%dT%H%M%S")
        else:
            # Date only (all-day event)
            return datetime.strptime(dt_str, "%Y%m%d")
    except Exception as e:
        log(f"Error parsing datetime {dt_str}: {e}")
        return None

def parse_ical_content(ical_data):
    """Parse iCal/ICS content and extract events"""
    events = []
    current_event = {}
    in_event = False

    for line in ical_data.split('\n'):
        line = line.strip()

        if line == 'BEGIN:VEVENT':
            in_event = True
            current_event = {}
        elif line == 'END:VEVENT':
            if current_event:
                events.append(current_event)
            in_event = False
            current_event = {}
        elif in_event:
            if ':' in line:
                # Handle multi-line values
                if line.startswith(' '):
                    # Continuation of previous line
                    continue

                key_val = line.split(':', 1)
                if len(key_val) == 2:
                    key = key_val[0].split(';')[0]  # Remove parameters
                    value = key_val[1]

                    # Unescape special characters
                    value = value.replace('\\n', '\n').replace('\\,', ',')

                    if key == 'SUMMARY':
                        current_event['title'] = value
                    elif key == 'DTSTART':
                        current_event['start'] = parse_ical_datetime(value)
                    elif key == 'DTEND':
                        current_event['end'] = parse_ical_datetime(value)
                    elif key == 'LOCATION':
                        current_event['location'] = value
                    elif key == 'DESCRIPTION':
                        current_event['description'] = value

    return events

def fetch_ical_feed(url):
    """Fetch iCal feed from URL"""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        log(f"Error fetching iCal feed: {e}")
        return None

def get_upcoming_events(ical_data):
    """Get upcoming events from iCal data"""
    events = parse_ical_content(ical_data)

    # Filter future events
    now = datetime.now()
    future_events = [e for e in events if e.get('start') and e['start'] > now]

    # Sort by start time
    future_events.sort(key=lambda x: x['start'])

    return future_events[:10]

def get_today_events(ical_data):
    """Get today's events from iCal data"""
    events = parse_ical_content(ical_data)

    # Get today's date range
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Filter today's events
    today_events = []
    for e in events:
        if e.get('start'):
            if start_of_day <= e['start'] <= end_of_day:
                today_events.append(e)

    # Sort by start time
    today_events.sort(key=lambda x: x['start'])

    return today_events

def format_datetime(dt):
    """Format datetime to readable format"""
    try:
        if dt.hour == 0 and dt.minute == 0:
            # All-day event
            return dt.strftime("%d.%m.%Y")
        else:
            return dt.strftime("%d.%m.%Y %H:%M")
    except Exception as e:
        log(f"Error formatting datetime: {e}")
        return str(dt)

def get_time_until(start):
    """Calculate time until event starts"""
    try:
        now = datetime.now()
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

    # Extract event details
    title = event.get('title', 'No title')
    start = event.get('start')
    end = event.get('end')
    location = event.get('location', '')
    description = event.get('description', '')

    # Format times
    start_formatted = format_datetime(start) if start else ""
    end_formatted = format_datetime(end) if end else ""
    time_until = get_time_until(start) if start else ""

    # Publish to MQTT
    client.publish(MQTT_TOPIC_NEXT_EVENT, title, retain=True)
    client.publish(MQTT_TOPIC_NEXT_START, start_formatted, retain=True)
    client.publish(MQTT_TOPIC_NEXT_END, end_formatted, retain=True)
    client.publish(MQTT_TOPIC_NEXT_LOCATION, location, retain=True)
    client.publish(MQTT_TOPIC_NEXT_DESCRIPTION, description[:500], retain=True)
    client.publish(MQTT_TOPIC_NEXT_TIME_UNTIL, time_until, retain=True)

    log(f"Published next event: {title} at {start_formatted}")

def publish_today_events(client, events):
    """Publish today's event count and list"""
    count = len(events)
    client.publish(MQTT_TOPIC_TODAY_COUNT, str(count), retain=True)

    # Create event list
    event_list = []
    for event in events:
        title = event.get('title', 'No title')
        start = event.get('start')
        start_formatted = format_datetime(start) if start else ""
        event_list.append(f"{start_formatted} - {title}")

    today_list = '\n'.join(event_list) if event_list else "No events today"
    client.publish(MQTT_TOPIC_TODAY_LIST, today_list, retain=True)

    log(f"Published {count} events for today")

def main():
    """Main loop"""
    log("Starting Google Calendar iCal MQTT Connector")

    # Check for iCal URL
    try:
        with open(ICAL_URL_FILE, 'r') as f:
            ical_url = f.read().strip()
    except FileNotFoundError:
        log(f"ERROR: iCal URL file not found: {ICAL_URL_FILE}")
        log("Please save your calendar's secret iCal URL to this file")
        sys.exit(1)

    if not ical_url:
        log("ERROR: iCal URL is empty")
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
    client.publish(MQTT_TOPIC_STATUS, "running", retain=True)

    # Main loop
    while True:
        try:
            # Fetch iCal feed
            ical_data = fetch_ical_feed(ical_url)

            if ical_data:
                # Get upcoming events
                events = get_upcoming_events(ical_data)

                if events:
                    publish_next_event(client, events[0])
                else:
                    publish_next_event(client, None)

                # Get today's events
                today_events = get_today_events(ical_data)
                publish_today_events(client, today_events)

                client.publish(MQTT_TOPIC_STATUS, "running", retain=True)
            else:
                log("Failed to fetch iCal data")
                client.publish(MQTT_TOPIC_STATUS, "error: fetch failed", retain=True)

        except Exception as e:
            log(f"Error in main loop: {e}")
            client.publish(MQTT_TOPIC_STATUS, f"error: {str(e)}", retain=True)

        # Wait before next update
        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
