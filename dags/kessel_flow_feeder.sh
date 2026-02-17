#!/bin/bash

BIN_FILE="$HOME/rayrock/manifesto.bin"
pulse_colors=(160 162 164 166 196 202 208 214 220 226 190 154 118 82 46)

# Check if binary exists
if [[ ! -f "$BIN_FILE" ]]; then
    echo "⚠️ Binary file not found at $BIN_FILE"
    exit 1
fi

# Read the pre-crunched binary and feed it as a "living" Kessel Flow stream
while IFS= read -r line; do
    clear
    for ((i=0;i<5;i++)); do
        color=${pulse_colors[$(( RANDOM % ${#pulse_colors[@]} ))]}
        display_line=$(echo "$line" | tr '01' ' █')
        printf "\e[38;5;${color}m%s\e[0m\n" "$display_line"
        sleep 0.2
    done
done < "$BIN_FILE"
