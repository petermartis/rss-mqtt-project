    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════════════╗"
    echo "║         RSS & Calendar MQTT Publisher - Raspberry Pi 5                   ║"
    echo "╚═══════════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # RSS Service Status
    if systemctl is-active --quiet rss-mqtt.service; then
        echo -e "  RSS Publisher:      \033[0;32m●\033[0m Running  (8 feeds + Slovak calendar)"
    else
        echo -e "  RSS Publisher:      \033[0;31m●\033[0m Stopped"
    fi
    
    # Calendar Service Status
    if systemctl is-active --quiet gcal-mqtt.service; then
        echo -e "  Calendar Connector: \033[0;32m●\033[0m Running  (Google Calendar via CalDAV)"
    else
        echo -e "  Calendar Connector: \033[0;31m●\033[0m Stopped"
    fi
    
    # MQTT Broker Status
    if systemctl is-active --quiet mosquitto.service; then
        echo -e "  MQTT Broker:        \033[0;32m●\033[0m Running  (localhost:1883)"
    else
        echo -e "  MQTT Broker:        \033[0;31m●\033[0m Stopped"
    fi
    
    echo ""
    echo "  MQTT Topics:"
    echo "    • news/*        - RSS headlines, content, source (8 feeds)"
    echo "    • today/*       - Slovak date, time, namedays"
    echo "    • calendar/*    - Next event, today's schedule"
    echo ""
    echo "  Quick Commands:"
    echo "    rss_status      - RSS publisher status and latest news"
    echo "    rss_channels    - List RSS feeds"
    echo "    gcal_status     - Calendar status and next event"
    echo "    rss_help        - Show all available commands"
    echo ""
    echo "  Monitor MQTT:"
    echo "    mosquitto_sub -h localhost -t '#' -v"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi
