"""
Example DAG: Basic ETL Pipeline
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'example_dag_basic',
    default_args=default_args,
    description='A simple ETL DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example', 'etl'],
)

def extract_data():
    print("Extracting data from source...")
    return {'records': 100, 'timestamp': datetime.now().isoformat()}

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

def transform_data(**context):
    print("Transforming data...")
    return {'status': 'transformed'}

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

load_task = BashOperator(
    task_id='load_data',
    bash_command='echo "Loading data..." && echo "Load complete!"',
    dag=dag,
)

validate_task = BashOperator(
    task_id='validate_results',
    bash_command='echo "Validating..." && echo "Validation passed!"',
    dag=dag,
)

extract_task >> transform_task >> load_task >> validate_task
