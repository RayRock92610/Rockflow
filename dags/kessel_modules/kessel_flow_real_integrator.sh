#!/bin/bash

BIN_FILE="$HOME/rayrock/manifesto.bin"
REAL_CONFIG="$HOME/kessel_modules/active/project_real_config.sh"
REAL_BUILD="$HOME/kessel_modules/active/project_build_trigger.sh"
LOG_FILE="$HOME/kessel_modules/kessel_flow.log"

inotifywait -m -e close_write "$BIN_FILE" | while read -r path action file; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Binary updated, running real project modules..." >> "$LOG_FILE"
    bash "$REAL_CONFIG"
    bash "$REAL_BUILD"
done
