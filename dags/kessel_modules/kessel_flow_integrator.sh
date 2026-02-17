#!/bin/bash

BIN_FILE="$HOME/rayrock/manifesto.bin"
ACTIVE_MODULE="$HOME/kessel_modules/active/kessel_config_updater.sh"
LOG_FILE="$HOME/kessel_modules/kessel_flow.log"

# Ensure required files exist
if [[ ! -f "$BIN_FILE" ]] || [[ ! -f "$ACTIVE_MODULE" ]]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Missing binary or active module" >> "$LOG_FILE"
    exit 1
fi

# Use inotify to watch for binary updates and trigger the active module
echo "⏳ Watching $BIN_FILE for changes..."
inotifywait -m -e close_write "$BIN_FILE" | while read -r path action file; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Binary updated, triggering active module..." >> "$LOG_FILE"
    bash "$ACTIVE_MODULE"
done
