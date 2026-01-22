# Calendar Script Deployment

## Production Location

The calendar service runs from: `/home/admin/gcal_mqtt_connector.py`

This is managed by systemd service: `gcal-mqtt.service`

## Deploying Updates

When updating the calendar script:

```bash
# 1. Pull latest changes
cd ~/rss-mqtt-project
git pull

# 2. Copy updated script to production location
cp ~/rss-mqtt-project/calendar/gcal_caldav_simple.py ~/gcal_mqtt_connector.py

# 3. Restart the service
sudo systemctl restart gcal-mqtt

# 4. Verify it's working
gcal_status
```

## Service Management

```bash
# Check status
sudo systemctl status gcal-mqtt

# View logs
sudo journalctl -u gcal-mqtt -f

# Check MQTT topics
mosquitto_sub -h localhost -t "calendar/#" -v
```

## Timezone Handling

The script properly handles timezone conversions:
- Extracts TZID from iCal format (e.g., `TZID=Europe/Prague`)
- Converts all times to local timezone using Python's `zoneinfo` module
- Displays events in local time (CET/CEST)
