# Google Calendar CalDAV Connector

## Why CalDAV Instead of Calendar API?

Third-party calendar apps (Fantastical, Week Calendar, One Calendar, etc.) access Google Calendar using **CalDAV protocol** with OAuth2, NOT the Calendar API. This often works even when the Calendar API is disabled by your organization.

## How It Works

CalDAV is an older protocol that Google still supports for calendar access. It uses your Google App Password (a special password for apps) instead of API keys.

## Setup Steps

### 1. Create Google App Password

1. Go to: **https://myaccount.google.com/apppasswords**
2. Sign in with **peter.martis@seon.io**
3. You may need to enable 2-Step Verification first if not already enabled
4. Click **"Select app"** → Choose **"Mail"** or **"Other (Custom name)"**
5. If "Other", name it: **"Calendar MQTT"**
6. Click **"Generate"**
7. **Copy the 16-character password** (looks like: `xxxx xxxx xxxx xxxx`)
   - Remove spaces when entering it

**Important:** Keep this password secret - it grants access to your calendar!

### 2. Run Setup on Raspberry Pi

```bash
ssh admin@192.168.3.11

# Run the CalDAV setup
gcal_caldav_setup
```

You'll be asked for:
- Your email: `peter.martis@seon.io`
- App Password: `(the 16-character password you just created)`

### 3. Replace the Connector

The CalDAV connector is already in place. Just restart the service:

```bash
sudo systemctl restart gcal-mqtt.service
sudo systemctl enable gcal-mqtt.service
```

### 4. Verify

```bash
gcal_status
```

You should see your calendar events!

## MQTT Topics

Same topics as before:
- `calendar/next/*` - Next upcoming event details
- `calendar/today/*` - Today's events
- `calendar/status` - Connector status

## Advantages of CalDAV

✓ **Bypasses Calendar API restriction** - Uses different protocol
✓ **Same as third-party apps** - If Fantastical works, this should too
✓ **Simple authentication** - Just email + app password
✓ **No OAuth dance** - No browser authentication needed
✓ **Works with G Suite** - Designed for enterprise accounts

## Limitations

⚗ **Depends on CalDAV being enabled** - Some admins disable this too
⚗ **Requires 2-Step Verification** - To create app passwords
⚗ **No attendee details** - CalDAV has limited data compared to API

## Troubleshooting

### "Authentication Failed"

1. **Check 2-Step Verification is enabled:**
   - Go to https://myaccount.google.com/security
   - Enable "2-Step Verification" if not already enabled

2. **Create a new App Password:**
   - Old password might have expired
   - Go to https://myaccount.google.com/apppasswords
   - Generate new password

3. **Re-run setup:**
   ```bash
   gcal_caldav_setup
   ```

### "No calendars found"

- Your organization might have disabled CalDAV too
- Check with IT if CalDAV access is allowed
- Try accessing calendar from Fantastical or similar app - if that doesn't work, CalDAV is blocked

### Still Not Working?

If CalDAV is also blocked, your only options are:

1. **Make calendar public** and use iCal feed (not recommended for work)
2. **Use separate personal calendar** for display purposes
3. **Ask IT** to enable either Calendar API or CalDAV access

## Security Notes

⚠️ **App Password Security:**
- Treat it like a regular password - keep it secret
- Only stored locally on Raspberry Pi in `~/.gcal_caldav_auth.json` (file mode 600)
- Revoke anytime at https://myaccount.google.com/apppasswords
- No data leaves your local network

## Comparison: API vs CalDAV vs iCal

| Feature | Calendar API | CalDAV | iCal Feed |
|---------|--------------|--------|-----------|
| Requires API enabled | ✓ | ✗ | ✗ |
| OAuth browser auth | ✓ | ✗ | ✗ |
| App password needed | ✗ | ✓ | ✗ |
| Attendee information | ✓ | ✗ | ✗ |
| Works when blocked | ✗ | Maybe | Only if public |
| Used by 3rd party apps | Sometimes | ✓ | ✓ |

## Commands

```bash
gcal_caldav_setup          # Set up CalDAV credentials
gcal_status                # Check calendar status
sudo systemctl restart gcal-mqtt.service  # Restart connector
sudo journalctl -u gcal-mqtt.service -f   # View logs
```
