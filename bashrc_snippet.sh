# RSS to MQTT Publisher - Bash Integration
# Add this to your ~/.bashrc for RSS management features

# RSS to MQTT aliases
alias rss_stat='rss_status'
alias rss_news='rss_latest'
alias rss_list='rss_channels'

# RSS help function
rss_help_func() {
    rss_help
}

# RSS welcome message on SSH login
if [[ $- == *i* ]] && [[ -n "$SSH_CONNECTION" || -n "$SSH_CLIENT" ]]; then
    echo ""
    rss_help
    
    # Show current RSS service status
    if systemctl is-active --quiet rss-mqtt; then
        echo -e "\033[0;32m✓ RSS-to-MQTT Publisher is currently running\033[0m"
        FEEDS=$(grep -E "^https?://" ~/.newsboat/urls 2>/dev/null | wc -l)
        echo -e "\033[0;34m  Publishing from $FEEDS RSS feeds every 6 seconds\033[0m"
    else
        echo -e "\033[0;31m✗ RSS-to-MQTT Publisher is not running\033[0m"
        echo -e "\033[0;33m  Use 'sudo systemctl start rss-mqtt' to start\033[0m"
    fi
    echo ""
fi
