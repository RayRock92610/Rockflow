#!/data/data/com.termux/files/usr/bin/bash

termux-wake-lock
set -e

# --- Step 0: Shared storage directories ---
echo "[*] Creating shared Kesselflow directories..."
mkdir -p ~/storage/shared/kesselflow/{dags,logs,policies,scripts,venv}

# --- Step 1: Install minimal system packages ---
echo "[*] Installing required packages..."
pkg update -y
pkg install -y python git curl coreutils

# --- Step 2: Create virtual environment ---
VENV_PATH=~/storage/shared/kesselflow/venv
if [ -d "$VENV_PATH" ]; then
    echo "[*] Removing old venv..."
    rm -rf "$VENV_PATH"
fi

echo "[*] Creating Python venv..."
python3 -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"

# --- Step 3: Upgrade pip & install Airflow ---
echo "[*] Installing Python packages..."
pip install --upgrade pip setuptools wheel
pip install "apache-airflow==2.8.4" colorlog pydantic

# --- Step 4: Deploy self-healing Kesselflow script ---
WATCHDOG_SCRIPT=~/storage/shared/kesselflow/kesselflow_autorun.sh
echo "[*] Deploying immortal watchdog script..."
cat > "$WATCHDOG_SCRIPT" << 'WEOF'
#!/data/data/com.termux/files/usr/bin/bash

termux-wake-lock
export PATH=$HOME/.termux/bin:$PATH
export AIRFLOW_HOME=~/storage/shared/kesselflow
export AIRFLOW__CORE__DAGS_FOLDER=$AIRFLOW_HOME/dags
export AIRFLOW__CORE__LOGS_FOLDER=$AIRFLOW_HOME/logs
export AIRFLOW__CORE__PLUGINS_FOLDER=$AIRFLOW_HOME/policies

VENV_PATH=$AIRFLOW_HOME/venv
source $VENV_PATH/bin/activate || {
    echo "[!] Venv missing, rebuilding..."
    python3 -m venv $VENV_PATH
    source $VENV_PATH/bin/activate
    pip install --upgrade pip setuptools wheel
    pip install "apache-airflow==2.8.4" colorlog pydantic
}

while true; do
    if ! command -v airflow &>/dev/null; then
        echo "[!] Airflow missing, rebuilding venv..."
        rm -rf $VENV_PATH
        python3 -m venv $VENV_PATH
        source $VENV_PATH/bin/activate
        pip install --upgrade pip setuptools wheel
        pip install "apache-airflow==2.8.4" colorlog pydantic
    fi

    if ! pgrep -f "airflow scheduler" >/dev/null; then
        echo "[*] Restarting Airflow scheduler..."
        airflow scheduler &>/dev/null &
    fi

    if ! pgrep -f "airflow webserver" >/dev/null; then
        echo "[*] Restarting Airflow webserver..."
        airflow webserver --port 8080 &>/dev/null &
    fi

    sleep 60
done
WEOF

chmod +x "$WATCHDOG_SCRIPT"

# --- Step 5: Deploy Termux boot integration ---
echo "[*] Configuring Termux boot..."
pkg install -y termux-services termux-api
mkdir -p ~/.termux/boot/
cp "$WATCHDOG_SCRIPT" ~/.termux/boot/

# --- Step 6: Launch immediately ---
echo "[*] Launching Kesselflow now..."
bash "$WATCHDOG_SCRIPT" &

echo "✅ Kesselflow fully autonomous & self-healing deployed!"
