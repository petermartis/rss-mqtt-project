#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Calendar CalDAV Setup
Configure App Password for CalDAV access
"""

import json
import os
import getpass

CREDENTIALS_FILE = os.path.expanduser("~/.gcal_caldav_auth.json")

def main():
    print("=" * 70)
    print("Google Calendar CalDAV Setup")
    print("=" * 70)
    print()
    print("This uses CalDAV protocol (same as third-party calendar apps)")
    print("like Fantastical, Week Calendar, etc.")
    print()
    print("You need a Google App Password (not your regular password)")
    print()
    print("Steps to create an App Password:")
    print("1. Go to: https://myaccount.google.com/apppasswords")
    print("2. Sign in with your Google account (peter.martis@seon.io)")
    print("3. Select 'Mail' and 'Other (Custom name)'")
    print("4. Name it: 'Calendar MQTT'")
    print("5. Click 'Generate'")
    print("6. Copy the 16-character password")
    print()
    print("=" * 70)
    print()

    # Get email
    email = input("Enter your Google email (peter.martis@seon.io): ").strip()
    if not email:
        print("Error: Email is required")
        return

    # Get app password
    print()
    print("Enter the App Password (16 characters, no spaces):")
    password = getpass.getpass("App Password: ").strip().replace(" ", "")

    if len(password) != 16:
        print()
        print("Warning: App Password should be 16 characters")
        print("Make sure you copied it correctly")
        print()
        confirm = input("Continue anyway? (y/n): ")
        if confirm.lower() != 'y':
            return

    # Save credentials
    credentials = {
        'email': email,
        'password': password
    }

    try:
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f)

        os.chmod(CREDENTIALS_FILE, 0o600)

        print()
        print("=" * 70)
        print("✓ Credentials saved successfully!")
        print(f"✓ File: {CREDENTIALS_FILE}")
        print()
        print("Next steps:")
        print("1. Start the calendar service:")
        print("   sudo systemctl restart gcal-mqtt.service")
        print()
        print("2. Check status:")
        print("   gcal_status")
        print()
        print("=" * 70)

    except Exception as e:
        print(f"Error saving credentials: {e}")

if __name__ == "__main__":
    main()
