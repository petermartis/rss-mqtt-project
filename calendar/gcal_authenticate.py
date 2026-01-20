#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Calendar Authentication Helper
One-time authentication setup for Google Workspace Calendar access
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Scopes for Google Calendar readonly access
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

TOKEN_FILE = '/home/admin/.gcal_token.pickle'
CREDENTIALS_FILE = '/home/admin/gcal_credentials.json'

def main():
    """Authenticate and save credentials"""
    print("Google Calendar Authentication Setup")
    print("=" * 50)
    print()

    # Check if credentials file exists
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"ERROR: Credentials file not found: {CREDENTIALS_FILE}")
        print()
        print("To set up Google Calendar access:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Google Calendar API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download the JSON file")
        print(f"6. Save it as: {CREDENTIALS_FILE}")
        print()
        return

    # Run OAuth flow
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES)

        print("Opening browser for authentication...")
        print("If browser doesn't open, copy the URL and open manually.")
        print()

        # Run local server for OAuth callback
        creds = flow.run_local_server(port=8080)

        # Save credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

        print()
        print("✓ Authentication successful!")
        print(f"✓ Token saved to: {TOKEN_FILE}")
        print()
        print("You can now start the calendar connector with:")
        print("  sudo systemctl start gcal-mqtt.service")
        print()

    except Exception as e:
        print(f"ERROR: Authentication failed: {e}")
        print()
        print("Make sure:")
        print("1. The credentials file is valid")
        print("2. You have network access")
        print("3. Port 8080 is available")
        print()

if __name__ == "__main__":
    main()
