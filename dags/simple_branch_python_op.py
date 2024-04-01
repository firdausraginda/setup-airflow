# Import DAG object
from airflow.models import DAG
# Import the BranchPythonOperator
from airflow.operators.python_operator import BranchPythonOperator
# Import the DummyOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime

# Define the default_args dictionary
default_args = {
  'owner': 'airflow',
  'start_date': datetime(year=2021, month=1, day=1),
  'retries': 2,
}

def check_date(**kwargs):
    if int(kwargs['ds_nodash']) % 2 == 0:
        return 'even_day_task'
    else:
        return 'odd_day_task'

with DAG(
    # Define DAG id
    'branch_python_operator',
    default_args=default_args,
    description='check the execution date',
    tags=['explore-airflow', 'python-operator'],
    # To enabled/disabled backfilling, set the catchup property
    catchup=False,
    schedule_interval='@daily'
) as dag:
    branch_task = BranchPythonOperator(
        task_id='branch_task',
        provide_context=True,
        python_callable=check_date,
        dag=dag
    )

    even_day_task = DummyOperator(
        task_id='even_day_task', 
        dag=dag
    )

    odd_day_task = DummyOperator(
        task_id='odd_day_task', 
        dag=dag
    )

    # Define task depedencies
    branch_task >> even_day_task
    branch_task >> odd_day_task