#!/data/data/com.termux/files/usr/bin/bash

# ------------------- CONFIG -------------------
KF_HOME="$HOME/storage/shared/kesselflow"
BACKUP_SCRIPT="$KF_HOME/backup_kesselflow.sh"
VENV="$KF_HOME/venv"
DAG_AUDIT_INTERVAL=3600   # 1 hour
LOG_FILE="$KF_HOME/self_heal.log"
AIRFLOW_BIN="$VENV/bin/airflow"

# ----------------- FUNCTIONS ------------------

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Self-heal Kesselflow environment
heal_environment() {
    log "⚡ Checking Kesselflow environment..."
    mkdir -p "$KF_HOME/dags" "$KF_HOME/policies" "$KF_HOME/logs" "$KF_HOME/backups"

    if [ ! -d "$VENV" ]; then
        log "⚠️  Virtualenv missing, rebuilding..."
        python3 -m venv "$VENV"
    fi

    if [ ! -x "$AIRFLOW_BIN" ]; then
        log "⚠️  Airflow missing, installing..."
        source "$VENV/bin/activate"
        pip install --upgrade pip
        pip install apache-airflow==2.8.3
    fi
}

# Start Airflow scheduler + webserver
start_airflow() {
    log "🚀 Starting Airflow scheduler + webserver..."
    source "$VENV/bin/activate"
    nohup "$AIRFLOW_BIN" scheduler &> "$KF_HOME/logs/scheduler.log" &
    nohup "$AIRFLOW_BIN" webserver &> "$KF_HOME/logs/webserver.log" &
}

# Hourly DAG audit (self-healing)
dag_audit() {
    while true; do
        log "🔹 Auditing DAGs..."
        for dag_file in "$KF_HOME/dags"/*.py; do
            python3 -m py_compile "$dag_file" 2>>"$KF_HOME/logs/dag_errors.log"
        done
        log "✅ DAG audit complete."
        sleep "$DAG_AUDIT_INTERVAL"
    done
}

# Autonomous backup trigger
run_backup() {
    bash "$BACKUP_SCRIPT" "$1"
}

# ------------------ MAIN LOOP ------------------

log "🏁 Kesselflow autonomous launch starting..."
heal_environment
start_airflow

# Run DAG audit in background
dag_audit &

# Run backup for last 1 day by default
run_backup 1 &

log "🎯 Kesselflow fully autonomous, self-healing deployed!"
