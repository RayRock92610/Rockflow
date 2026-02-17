#!/bin/bash

BIN_FILE="$HOME/rayrock/manifesto.bin"
pulse_colors=(160 162 164 166 196 202 208 214 220 226 190 154 118 82 46)
NUM_LAYERS=5   # number of layers to display
SLEEP_TIME=0.15

# Check binary exists
if [[ ! -f "$BIN_FILE" ]]; then
    echo "⚠️ Binary file not found at $BIN_FILE"
    exit 1
fi

# Load binary into an array
mapfile -t BIN_LINES < "$BIN_FILE"

# Infinite multi-layer pulse
while true; do
    clear
    for ((layer=0; layer<NUM_LAYERS; layer++)); do
        color=${pulse_colors[$(( RANDOM % ${#pulse_colors[@]} ))]}
        # Pick a random line from the binary for this layer
        line="${BIN_LINES[$(( RANDOM % ${#BIN_LINES[@]} ))]}"
        display_line=$(echo "$line" | tr '01' ' █')
        printf "\e[38;5;${color}m%s\e[0m\n" "$display_line"
    done
    sleep $SLEEP_TIME
done
