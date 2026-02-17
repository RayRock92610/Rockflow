#!/bin/bash

LOG_FILE="$HOME/kessel_modules/kessel_flow.log"
PROJECT="$1"
STATUS="$2"

# Example: dynamic notification placeholder
echo "$(date '+%Y-%m-%d %H:%M:%S') | NOTIFICATION: Project $PROJECT status changed → $STATUS" >> "$LOG_FILE"

# Optional: real notifications
# curl -X POST -H 'Content-type: application/json' --data '{"text":"Project '$PROJECT' status: '$STATUS'"}' https://hooks.slack.com/services/...
