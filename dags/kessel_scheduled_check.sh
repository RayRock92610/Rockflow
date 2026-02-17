#!/bin/bash

BIN_FILE="$HOME/rayrock/manifesto.bin"
LOG_FILE="$HOME/kessel_modules/kessel_flow.log"

if [[ -f "$BIN_FILE" ]]; then
    LINE_COUNT=$(wc -l < "$BIN_FILE")
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Scheduled check: $LINE_COUNT lines in binary" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Scheduled check: Binary not found" >> "$LOG_FILE"
fi
