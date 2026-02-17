#!/bin/bash

BIN_FILE="$HOME/rayrock/manifesto.bin"
MODULE1="$HOME/kessel_modules/active/kessel_config_updater.sh"
MODULE2="$HOME/kessel_modules/active/kessel_backup_alert.sh"
TRIGGER1="$HOME/kessel_modules/active/kessel_special_action.sh"
TRIGGER2="$HOME/kessel_modules/active/kessel_scheduled_check.sh"
TRIGGER3="$HOME/kessel_modules/active/kessel_external_event.sh"
LOG_FILE="$HOME/kessel_modules/kessel_flow.log"

if [[ ! -f "$BIN_FILE" ]]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Binary missing, integrator cannot start" >> "$LOG_FILE"
    exit 1
fi

echo "⏳ Watching $BIN_FILE for changes..."
inotifywait -m -e close_write "$BIN_FILE" | while read -r path action file; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Binary updated, running modules & triggers..." >> "$LOG_FILE"
    bash "$MODULE1"
    bash "$MODULE2"

    # Check for special pattern in binary lines
    while IFS= read -r line; do
        if echo "$line" | grep -q "11110000"; then
            bash "$TRIGGER1"
        fi
    done < "$BIN_FILE"

    # Run other triggers
    bash "$TRIGGER2"
    bash "$TRIGGER3"
done
