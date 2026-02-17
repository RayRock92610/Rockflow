#!/bin/bash

CONFIG_FILE="$HOME/kessel_modules/active/project_config.cfg"
BACKUP_DIR="$HOME/kessel_modules/active/backups"
LOG_FILE="$HOME/kessel_modules/kessel_flow.log"

mkdir -p "$BACKUP_DIR"

# Backup config if it exists
if [[ -f "$CONFIG_FILE" ]]; then
    TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    cp "$CONFIG_FILE" "$BACKUP_DIR/project_config_$TIMESTAMP.cfg"
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Backup created: project_config_$TIMESTAMP.cfg" >> "$LOG_FILE"

    # Example trigger: log alert if feature_x is enabled
    if grep -q "feature_x=enabled" "$CONFIG_FILE"; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') | ALERT: feature_x enabled!" >> "$LOG_FILE"
    fi
fi
