#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Calendar CalDAV to MQTT - Simplified iCal Parser
Fetches iCal feed via CalDAV with authentication and publishes to MQTT
"""

import sys
import time
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
import re
import os
import requests
from requests.auth import HTTPBasicAuth

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

UPDATE_INTERVAL = 300  # 5 minutes

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)

def load_auth():
    """Load CalDAV URL and authentication"""
    url_file = os.path.expanduser("~/.gcal_ical_url.txt")
    auth_file = os.path.expanduser("~/.gcal_ical_auth.txt")

    if not os.path.exists(url_file) or not os.path.exists(auth_file):
        return None, None

    with open(url_file) as f:
        url = f.read().strip()
    with open(auth_file) as f:
        auth = f.read().strip()

    if ":" in auth:
        username, password = auth.split(":", 1)
        return url, (username, password)

    return None, None

def fetch_ical():
    """Fetch iCal feed with authentication"""
    url, auth = load_auth()
    if not url or not auth:
        log("ERROR: No authentication configured")
        return None

    try:
        response = requests.get(url, auth=HTTPBasicAuth(*auth), timeout=30)
        if response.status_code == 200:
            return response.text
        else:
            log(f"Error fetching calendar: HTTP {response.status_code}")
            return None
    except Exception as e:
        log(f"Error fetching calendar: {e}")
        return None

def parse_datetime(dt_str):
    """Parse iCal datetime string"""
    try:
        # Remove timezone info for simplicity
        dt_str = dt_str.split(';')[0].replace('TZID=', '').split(':')[-1]

        if 'T' in dt_str:
            # DateTime
            if 'Z' in dt_str:
                return datetime.strptime(dt_str, "%Y%m%dT%H%M%SZ")
            else:
                return datetime.strptime(dt_str, "%Y%m%dT%H%M%S")
        else:
            # Date only
            return datetime.strptime(dt_str, "%Y%m%d")
    except:
        return None

def parse_ical_events(ical_data):
    """Parse events from iCal data"""
    events = []

    # Split into individual events
    vevent_pattern = r'BEGIN:VEVENT(.*?)END:VEVENT'
    vevents = re.findall(vevent_pattern, ical_data, re.DOTALL)

    for vevent in vevents:
        try:
            event = {}

            # Extract fields
            summary_match = re.search(r'SUMMARY:(.*?)$', vevent, re.MULTILINE)
            if summary_match:
                event['summary'] = summary_match.group(1).strip()

            dtstart_match = re.search(r'DTSTART[;:]([^\r\n]+)', vevent)
            if dtstart_match:
                event['dtstart'] = parse_datetime(dtstart_match.group(1))

            dtend_match = re.search(r'DTEND[;:]([^\r\n]+)', vevent)
            if dtend_match:
                event['dtend'] = parse_datetime(dtend_match.group(1))

            location_match = re.search(r'LOCATION:(.*?)$', vevent, re.MULTILINE)
            if location_match:
                event['location'] = location_match.group(1).strip()

            description_match = re.search(r'DESCRIPTION:(.*?)$', vevent, re.MULTILINE)
            if description_match:
                event['description'] = description_match.group(1).strip()

            if event.get('dtstart'):
                events.append(event)

        except Exception as e:
            continue

    # Sort by start time
    events.sort(key=lambda x: x.get('dtstart', datetime.max))
    return events

def format_datetime(dt):
    if isinstance(dt, datetime):
        return dt.strftime("%d.%m.%Y %H:%M")
    return str(dt)

def get_time_until(start_dt):
    if not isinstance(start_dt, datetime):
        return ""

    now = datetime.now()
    delta = start_dt - now

    if delta.total_seconds() < 0:
        return "Prebieha"
    elif delta.total_seconds() < 3600:
        return f"{int(delta.total_seconds() / 60)} min"
    elif delta.total_seconds() < 86400:
        return f"{int(delta.total_seconds() / 3600)} hod"
    else:
        return f"{delta.days} dni"

def publish_events(client, all_events):
    """Publish events to MQTT"""
    now = datetime.now()

    # Get upcoming events
    upcoming = [e for e in all_events if e.get('dtstart') and e['dtstart'] > now]

    # Publish next event
    if upcoming:
        event = upcoming[0]
        client.publish(MQTT_TOPIC_NEXT_EVENT, event.get('summary', ''), retain=True)
        client.publish(MQTT_TOPIC_NEXT_START, format_datetime(event.get('dtstart')), retain=True)
        client.publish(MQTT_TOPIC_NEXT_END, format_datetime(event.get('dtend')), retain=True)
        client.publish(MQTT_TOPIC_NEXT_LOCATION, event.get('location', ''), retain=True)
        client.publish(MQTT_TOPIC_NEXT_DESCRIPTION, event.get('description', '')[:500], retain=True)
        client.publish(MQTT_TOPIC_NEXT_TIME_UNTIL, get_time_until(event.get('dtstart')), retain=True)
        log(f"Published next event: {event.get('summary')}")
    else:
        client.publish(MQTT_TOPIC_NEXT_EVENT, "", retain=True)
        log("No upcoming events")

    # Get today's events
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59)
    today_events = [e for e in all_events if e.get('dtstart') and today_start <= e['dtstart'] <= today_end]

    client.publish(MQTT_TOPIC_TODAY_COUNT, str(len(today_events)), retain=True)

    today_list = []
    for event in today_events:
        today_list.append(f"{format_datetime(event.get('dtstart'))} - {event.get('summary', '')}")

    client.publish(MQTT_TOPIC_TODAY_LIST, '\n'.join(today_list) if today_list else "Žiadne udalosti dnes", retain=True)
    log(f"Published {len(today_events)} events for today")

def main():
    log("Starting Google Calendar CalDAV MQTT Connector (iCal parser)")

    # Connect to MQTT
    client = mqtt.Client()
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        log(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        log(f"Failed to connect to MQTT broker: {e}")
        sys.exit(1)

    client.loop_start()
    client.publish(MQTT_TOPIC_STATUS, "running", retain=True)

    # Main loop
    while True:
        try:
            # Fetch and parse calendar
            ical_data = fetch_ical()
            if ical_data:
                events = parse_ical_events(ical_data)
                log(f"Parsed {len(events)} events from calendar")
                publish_events(client, events)
                client.publish(MQTT_TOPIC_STATUS, "running", retain=True)
            else:
                log("Failed to fetch calendar data")
                client.publish(MQTT_TOPIC_STATUS, "error: fetch failed", retain=True)

        except Exception as e:
            log(f"Error in main loop: {e}")
            client.publish(MQTT_TOPIC_STATUS, f"error: {str(e)}", retain=True)

        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
