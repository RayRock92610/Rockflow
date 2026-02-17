#!/bin/bash

BIN_PROCESSOR="$HOME/kessel_modules/kessel_flow_bg.sh"

# Run silently in the background
nohup "$BIN_PROCESSOR" &>/dev/null &

echo "✅ Kessel Flow background processor started silently."
