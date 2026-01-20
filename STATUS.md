# System Status

**Last Updated:** 2026-01-20

## ✅ System Ready

All services are configured, running, and set to auto-start on reboot.

### Service Status

| Service | Status | Auto-Start | Purpose |
|---------|--------|------------|---------|
| rss-mqtt.service | ● Running | Enabled | RSS feeds + Slovak calendar |
| gcal-mqtt.service | ● Running | Enabled | Google Calendar via CalDAV |
| mosquitto.service | ● Running | Enabled | MQTT broker (port 1883) |

### MQTT Topics Published

**News Topics** (8 feeds, rotating every 6 seconds):
- `news/headline`, `news/content`, `news/source`, `news/link`, `news/published`

**Slovak Calendar** (with diacritics):
- `today/time` (HH:MM), `today/seconds` (SS), `today/dow`, `today/sdate`, `today/ldate`, `today/year`, `today/nameday`

**Google Calendar**:
- `calendar/next/*` (title, start, end, location, description, time_until)
- `calendar/today/*` (count, list)

### Quick Commands

```bash
rss_status      # RSS publisher status
gcal_status     # Calendar connector status
rss_channels    # List RSS feeds
rss_help        # Show all commands
```

### Documentation

- **Complete Guide:** [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)
- **GitHub:** https://github.com/petermartis/rss-mqtt-project

### Test Reboot

```bash
sudo reboot
```

All services will start automatically within 30 seconds of boot.
