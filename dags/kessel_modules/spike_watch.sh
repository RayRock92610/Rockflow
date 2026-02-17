#!/bin/bash
# spike_watch.sh - ⛈❂ Pure Glyph Spike Check

source ~/glyph_aliases.sh

spike_watch() {
  echo "SEQUENCE: SPIKE WATCH"
  ⛈ ❂
  if [ -f ~/spike_watchdog.sh ]; then
    echo "⚠️ SPIKE DOG ARMED | BROKEN_SEAL recovery"
    BROKEN_SEAL
  else
    echo "✅ NO SPIKE DOG | zero-drift"
    ✦
  fi
  set_state "SPIKE_WATCH"
}

spike_watch
