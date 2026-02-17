#!/bin/bash

BIN_FILE="$HOME/rayrock/manifesto.bin"
ACTIVE_MODULE1="$HOME/kessel_modules/active/kessel_config_updater.sh"
ACTIVE_MODULE2="$HOME/kessel_modules/active/kessel_backup_alert.sh"
LOG_FILE="$HOME/kessel_modules/kessel_flow.log"

if [[ ! -f "$BIN_FILE" ]] || [[ ! -f "$ACTIVE_MODULE1" ]] || [[ ! -f "$ACTIVE_MODULE2" ]]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Missing binary or active modules" >> "$LOG_FILE"
    exit 1
fi

echo "⏳ Watching $BIN_FILE for changes..."
inotifywait -m -e close_write "$BIN_FILE" | while read -r path action file; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Binary updated, triggering active modules..." >> "$LOG_FILE"
    bash "$ACTIVE_MODULE1"
    bash "$ACTIVE_MODULE2"
done
