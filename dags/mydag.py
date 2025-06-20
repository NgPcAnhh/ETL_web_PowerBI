from datetime import datetime, timedelta
import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import crawl as extract
import transform as transform

# Add dags directory to Python path
sys.path.insert(0, '/opt/airflow/dags')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 19),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'my_etl_dag',
    default_args=default_args,
    schedule=timedelta(days=14), 
    catchup=False,
    tags=['etl', 'golang', 'python', 'financial']
)

def run_transform(**context):
    transform.main()

# Test environment
test_env_task = BashOperator(
    task_id='test_environment',
    bash_command='''
    echo "=== Environment Check ==="
    echo "PATH: $PATH"
    echo "GOROOT: $GOROOT"
    echo "GOPATH: $GOPATH"
    echo "Python path:"
    python -c "import sys; print('\\n'.join(sys.path))"
    
    echo "=== Go Check ==="
    which go || echo "Go not found"
    go version || echo "Go version failed"
    
    echo "=== Python Modules Check ==="
    python -c "import pandas; print(f'Pandas: {pandas.__version__}')"
    python -c "import sys; sys.path.append('/opt/airflow/dags'); import transform; print('Transform module imported successfully')"
    ''',
    dag=dag,
)

# Extract task using Go
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract.main,
    dag=dag,
)

# Transform task
transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=run_transform,
    dag=dag,
)

# Validation task
validate_task = BashOperator(
    task_id='validate_output',
    bash_command='''
    echo "=== Validating Transform Output ==="
    
    echo "Files in data_processed:"
    find /opt/airflow/csv/data_processed -name "*.csv" | head -10
    
    echo "Files in load/csv:"
    find /opt/airflow/load/csv -name "*.csv" | head -10
    
    echo "Sample content from processed files:"
    for file in /opt/airflow/load/csv/*.csv; do
        if [ -f "$file" ]; then
            echo "--- $file ---"
            head -3 "$file"
            echo "Total lines: $(wc -l < "$file")"
            echo
        fi
    done
    
    echo "Validation completed!"
    ''',
    dag=dag,
)

# Task dependencies
test_env_task >> extract_task >> transform_task >> validate_task