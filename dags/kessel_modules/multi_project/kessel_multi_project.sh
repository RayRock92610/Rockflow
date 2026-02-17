#!/bin/bash

BIN_FILE="$HOME/rayrock/manifesto.bin"
LOG_FILE="$HOME/kessel_modules/kessel_flow.log"

# Project definitions
declare -A PROJECTS
PROJECTS["A"]="$HOME/projects/project_a"
PROJECTS["B"]="$HOME/projects/project_b"
PROJECTS["C"]="$HOME/projects/project_c"

# Read binary and trigger actions per project
while IFS= read -r line; do
    ones=$(echo "$line" | grep -o "1" | wc -l)
    zeros=$(echo "$line" | grep -o "0" | wc -l)

    for P in "${!PROJECTS[@]}"; do
        PROJ_DIR="${PROJECTS[$P]}"
        CONFIG="$PROJ_DIR/config/app.cfg"

        mkdir -p "$(dirname "$CONFIG")"

        # Conditional: if 1-density > 0-density, run Project A, else Project B, else Project C
        if (( ones > zeros )); then
            echo "mode=production" > "$CONFIG"
            [[ -x "$PROJ_DIR/build.sh" ]] && bash "$PROJ_DIR/build.sh"
            [[ -x "$PROJ_DIR/deploy.sh" ]] && bash "$PROJ_DIR/deploy.sh"
            echo "$(date '+%Y-%m-%d %H:%M:%S') | Project $P updated to production, build & deploy triggered" >> "$LOG_FILE"
        else
            echo "mode=development" > "$CONFIG"
            [[ -x "$PROJ_DIR/build.sh" ]] && bash "$PROJ_DIR/build.sh"
            echo "$(date '+%Y-%m-%d %H:%M:%S') | Project $P updated to development, build triggered" >> "$LOG_FILE"
        fi
    done
done < "$BIN_FILE"
