#!/bin/bash

BIN_FILE="$HOME/rayrock/manifesto.bin"
PROJECT_CONFIG="$HOME/my_real_project/config/app.cfg"
LOG_FILE="$HOME/kessel_modules/kessel_flow.log"

mkdir -p "$(dirname "$PROJECT_CONFIG")"

while IFS= read -r line; do
    ones=$(echo "$line" | grep -o "1" | wc -l)
    zeros=$(echo "$line" | grep -o "0" | wc -l)

    # Real update logic: enable production mode if 1-density > 0-density
    if (( ones > zeros )); then
        echo "mode=production" > "$PROJECT_CONFIG"
    else
        echo "mode=development" > "$PROJECT_CONFIG"
    fi

    echo "$(date '+%Y-%m-%d %H:%M:%S') | Real project config updated: $(cat $PROJECT_CONFIG)" >> "$LOG_FILE"
done < "$BIN_FILE"
