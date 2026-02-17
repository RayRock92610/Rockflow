#!/bin/bash

BIN_FILE="$HOME/rayrock/manifesto.bin"
LOG_FILE="$HOME/kessel_modules/kessel_flow.log"

# Ensure binary exists
if [[ ! -f "$BIN_FILE" ]]; then
    echo "⚠️ Binary file not found at $BIN_FILE"
    exit 1
fi

# Clear previous log
> "$LOG_FILE"

# Read binary line by line
while IFS= read -r line; do
    # ANALYTICS: count 1s and 0s
    ones=$(echo "$line" | grep -o "1" | wc -l)
    zeros=$(echo "$line" | grep -o "0" | wc -l)

    # LOG: store info
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Ones: $ones | Zeros: $zeros | Line length: ${#line}" >> "$LOG_FILE"

    # TRIGGER: example event (can expand)
    if (( ones > zeros )); then
        echo "🔥 High one-density line detected, triggering Rayrock alert!"
    fi

    # Optional delay to simulate live processing
    sleep 0.1
done < "$BIN_FILE"

echo "✅ Binary processed and logged to $LOG_FILE"
