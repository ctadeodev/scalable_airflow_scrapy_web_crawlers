from datetime import timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago
from airflow.hooks.postgres_hook import PostgresHook


def fetch_crawler_jobs():
    """
    Fetches crawler jobs from the jobs.crawlers table.
    """
    pg_hook = PostgresHook(postgres_conn_id='ingest_db_conn_id')
    connection = pg_hook.get_conn()
    cursor = connection.cursor()
    cursor.execute(
        """SELECT name, crawler_name, args, frequency, pool, priority
           FROM jobs.crawlers
           WHERE enabled=TRUE
        """
    )
    records = cursor.fetchall()
    cursor.close()
    connection.close()
    return records

def create_dag(name, crawler_name, args, frequency, pool, priority):
    """
    Creates a DAG with dynamically generated Bash tasks based on the job record.
    """
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
        'start_date': days_ago(1),  # Set the start date appropriately
    }

    dag = DAG(
        name,
        default_args=default_args,
        description='A DAG with dynamically generated Bash tasks',
        schedule_interval=f'@{frequency}',  # Schedule to run daily,
        catchup=False
    )

    start = DummyOperator(task_id='start', dag=dag)
    end = DummyOperator(task_id='end', dag=dag)

    crawl_task = BashOperator(
        task_id=f'job_{name}',
        bash_command=f"scrapy crawl {crawler_name} {args}",
        cwd='/opt/airflow/dags/jobs',
        pool=pool,
        priority_weight=priority,
        dag=dag,
    )

    start >> crawl_task >> end

    return dag

# Fetch job records from the database
crawler_jobs = fetch_crawler_jobs()

# Create a DAG for each job record
for (name, crawler_name, args, frequency, pool, priority) in crawler_jobs:
    globals()[name] = create_dag(name, crawler_name, args, frequency, pool, priority)
