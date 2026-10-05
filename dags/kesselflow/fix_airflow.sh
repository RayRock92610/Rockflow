#!/bin/bash
# Fix Airflow Missing Dependencies - UserLAnd Edition

echo "╔════════════════════════════════════════════════════╗"
echo "║   Airflow Dependency Fixer - KesselFlow           ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Activate venv
if [ -d ~/airflow_sandbox/venv ]; then
    echo "Activating virtual environment..."
    source ~/airflow_sandbox/venv/bin/activate
fi

install_if_missing() {
    python3 -c "import $1" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "Installing missing module: $1"
        pip install $2
    else
        echo "Module $1 already installed"
    fi
}

echo "[1/4] Installing core Python modules..."
install_if_missing packaging packaging
install_if_missing setuptools setuptools
install_if_missing wheel wheel

echo ""
echo "[2/4] Installing Airflow SSH dependencies..."
install_if_missing paramiko paramiko
install_if_missing pendulum pendulum
install_if_missing sqlalchemy sqlalchemy
install_if_missing alembic alembic
install_if_missing apache_airflow_providers_ssh apache-airflow-providers-ssh

echo ""
echo "[3/4] Verifying installations..."
python3 -c "import airflow; print(f'✓ Airflow: {airflow.__version__}')" 2>/dev/null || echo "⚠ Airflow check failed"
python3 -c "import packaging; print('✓ packaging: OK')" 2>/dev/null || echo "⚠ packaging check failed"
python3 -c "import paramiko; print('✓ paramiko: OK')" 2>/dev/null || echo "⚠ paramiko check failed"

echo ""
echo "[4/4] Reloading DAGs..."
airflow dags list >/dev/null 2>&1 && echo "✓ DAG listing works" || echo "⚠ DAG list failed - check DAG files"

echo ""
echo "═══════════════════════════════════════════════════"
echo "Test your DAG with:"
echo "  cd ~/airflow_sandbox/dags"
echo "  python3 snozzberry_ssh.py"
echo "═══════════════════════════════════════════════════"
