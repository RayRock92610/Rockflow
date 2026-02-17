#!/bin/bash

BIN_FILE="$HOME/rayrock/manifesto.bin"
MULTI_MODULE="$HOME/kessel_modules/multi_project/kessel_multi_project.sh"
LOG_FILE="$HOME/kessel_modules/kessel_flow.log"

if [[ ! -f "$BIN_FILE" ]] || [[ ! -f "$MULTI_MODULE" ]]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Missing binary or orchestration module" >> "$LOG_FILE"
    exit 1
fi

echo "⏳ Watching $BIN_FILE for changes to orchestrate projects..."
inotifywait -m -e close_write "$BIN_FILE" | while read -r path action file; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Binary updated, orchestrating all projects..." >> "$LOG_FILE"
    bash "$MULTI_MODULE"
done
