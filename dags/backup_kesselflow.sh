#!/data/data/com.termux/files/usr/bin/bash

# ------------------- CONFIG -------------------
KF_HOME="$HOME/storage/shared/kesselflow"
BACKUP_DIR="$KF_HOME/backups"
EXTERNAL_DRIVE_PATHS=(
    "/storage/XXXX-XXXX"        # typical OTG mount path
    "/mnt/media_rw/XXXX-XXXX"   # alternative mount path
)
DAYS=${1:-1}  # default to 1 day if not specified
DATE_NOW=$(date +%Y%m%d_%H%M)
LOG_FILE="$KF_HOME/self_heal.log"
KF_DIRS=("$KF_HOME/dags" "$KF_HOME/policies" "$KF_HOME/venv" "$KF_HOME/logs")

mkdir -p "$BACKUP_DIR"

# ----------------- FUNCTIONS ------------------

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Self-healing for missing Kesselflow dirs
heal_kesselflow() {
    for d in "${KF_DIRS[@]}"; do
        if [ ! -d "$d" ]; then
            log "⚠️  Missing directory $d, recreating..."
            mkdir -p "$d"
        fi
    done
}

# Compress last N days of files
compress_backup() {
    log "🔹 Compressing last $DAYS day(s) of Kesselflow files..."
    # find files modified in last N days
    FILES=$(find "$KF_HOME" -type f -mtime -"${DAYS}")
    if [ -z "$FILES" ]; then
        log "⚠️  No files found for last $DAYS day(s), skipping backup."
        return 1
    fi
    ARCHIVE="$BACKUP_DIR/kesselflow_backup_$DATE_NOW.tar.gz"
    tar -czf "$ARCHIVE" $FILES
    log "✅ Backup created: $ARCHIVE"
    echo "$ARCHIVE"
}

# Sync backup to external drives if available
sync_to_external() {
    local SRC=$1
    for d in "${EXTERNAL_DRIVE_PATHS[@]}"; do
        if [ -d "$d" ] && [ -w "$d" ]; then
            log "🔹 Syncing backup to external drive $d..."
            cp "$SRC" "$d/"
            log "✅ Backup synced to $d"
        fi
    done
}

# ------------------ MAIN ----------------------

log "🚀 Starting Kesselflow autonomous backup..."
heal_kesselflow

BACKUP_FILE=$(compress_backup)
if [ $? -eq 0 ]; then
    sync_to_external "$BACKUP_FILE"
else
    log "⚠️  Backup skipped due to no files."
fi

log "🏁 Kesselflow backup complete!"
