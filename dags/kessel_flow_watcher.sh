#!/bin/bash

BIN_FILE="$HOME/rayrock/manifesto.bin"

echo "⏳ Watching $BIN_FILE for changes..."

inotifywait -m -e close_write "$BIN_FILE" | while read -r path action file; do
    echo "📡 Detected binary update! Processing..."
    ~/kessel_modules/kessel_flow_module.sh
done
