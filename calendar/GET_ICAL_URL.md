# How to Get Your Google Calendar iCal URL

The public URL doesn't work because your calendar needs to use the **private/secret** iCal URL.

## Step-by-Step Instructions

### Method 1: Via Google Calendar Settings (Desktop)

1. **Open Google Calendar**
   - Go to https://calendar.google.com
   - Make sure you're logged in as peter.martis@seon.io

2. **Open Settings**
   - Click the ⚙️ gear icon (top right)
   - Select **Settings**

3. **Select Your Calendar**
   - In the left sidebar, look for "Settings for my calendars"
   - Click on **peter.martis@seon.io** (your main calendar)

4. **Find the iCal URL**
   - Scroll down to the section **"Integrate calendar"**
   - You'll see several options:
     - Public URL to this calendar (if calendar is public)
     - **Secret address in iCal format** ← This is what you need!

5. **Copy the Secret iCal URL**
   - Find the line "Secret address in iCal format"
   - Click the 📋 copy icon next to the URL
   - The URL will look like:
     ```
     https://calendar.google.com/calendar/ical/peter.martis%40seon.io/private-XXXXXXXXXX/basic.ics
     ```
   - Note the `/private-XXXXXXXXXX/` part - this is your secret key

### Method 2: Via Calendar Settings (Alternative Path)

1. Go to https://calendar.google.com/calendar/u/0/r/settings
2. Click on your calendar name in the left sidebar
3. Scroll to "Integrate calendar"
4. Copy the "Secret address in iCal format"

## Once You Have the URL

SSH to your Raspberry Pi and save it:

```bash
ssh admin@192.168.3.11

# Save the URL (replace with your actual URL)
echo "https://calendar.google.com/calendar/ical/peter.martis%40seon.io/private-XXXXXXXXXX/basic.ics" > ~/.gcal_ical_url.txt

# Protect the file
chmod 600 ~/.gcal_ical_url.txt

# Start the calendar service
sudo systemctl start gcal-mqtt.service
sudo systemctl enable gcal-mqtt.service

# Check status
gcal_status
```

## Important Notes

⚠️ **Keep this URL private!**
- Anyone with this URL can see all your calendar events
- Never share it publicly or commit it to git
- It's stored securely on your Raspberry Pi only

✓ **This works even though the Calendar API is disabled**
- Uses iCal feed instead of API
- No OAuth needed
- No Google Cloud Console setup required

## Troubleshooting

If the URL still doesn't work:

1. **Check if you copied the full URL**
   ```bash
   cat ~/.gcal_ical_url.txt
   ```
   Should show a complete URL starting with `https://` and ending with `.ics`

2. **Test the URL**
   ```bash
   curl -s "$(cat ~/.gcal_ical_url.txt)" | head -20
   ```
   Should show iCal data starting with `BEGIN:VCALENDAR`

3. **Check service logs**
   ```bash
   sudo journalctl -u gcal-mqtt.service -n 50
   ```

## Screenshot Guide

I can't show screenshots here, but when you're in Google Calendar settings, you're looking for:

```
Integrate calendar
├─ Calendar ID: peter.martis@seon.io
├─ Public URL to this calendar: [if enabled]
└─ Secret address in iCal format:
   ├─ iCal: [https://calendar.google.com/calendar/ical/...] ← Copy this!
   └─ HTML: [https://calendar.google.com/calendar/embed/...]
```
