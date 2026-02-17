#!/bin/bash

BIN_FILE="$HOME/rayrock/manifesto.bin"
LOG_FILE="$HOME/kessel_modules/kessel_flow.log"

# Ensure binary exists
if [[ ! -f "$BIN_FILE" ]]; then
    echo "⚠️ Binary file not found at $BIN_FILE" >> "$LOG_FILE"
    exit 1
fi

# Read binary silently
while IFS= read -r line; do
    ones=$(echo "$line" | grep -o "1" | wc -l)
    zeros=$(echo "$line" | grep -o "0" | wc -l)

    # Log analytics silently
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Ones: $ones | Zeros: $zeros | Line length: ${#line}" >> "$LOG_FILE"

    # Trigger event silently (example: could call another script or API)
    if (( ones > zeros )); then
        echo "$(date '+%Y-%m-%d %H:%M:%S') | High one-density detected" >> "$LOG_FILE"
    fi
done < "$BIN_FILE"
