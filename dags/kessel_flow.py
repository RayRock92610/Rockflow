from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'RayRock',
    'start_date': datetime(2026, 2, 1),
    'retries': 1,
}

with DAG('kessel_flow_monitor', default_args=default_args, schedule_interval='*/5 * * * *', catchup=False) as dag:
    # Check 2TB Falcon Dock
    check_falcon = BashOperator(
        task_id='check_falcon_dock',
        bash_command='df -h | grep -E "1.8T|1.9T|2.0T" || (echo "chewie" > /sdcard/Download/.audio_signal && exit 1)'
    )
    # R2 Chirp for new cargo
    scavenge_files = BashOperator(
        task_id='scavenge_cargo',
        bash_command='ls /sdcard/Download/smuggling_compartment/* && echo "r2" > /sdcard/Download/.audio_signal || echo "Quiet in the bay"'
    )
    check_falcon >> scavenge_files
