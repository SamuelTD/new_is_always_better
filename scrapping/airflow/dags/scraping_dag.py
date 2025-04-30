from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'ludivine',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='weekly_scraping_allocine',
    default_args=default_args,
    schedule_interval='0 */1 * * *',  # ou '0 0 * * 1' pour chaque lundi
    catchup=False,
    tags=['scraping'],
) as dag:

    run_spider = BashOperator(
        task_id='run_my_scrapy_spider',
        #bash_command='cd /home/utilisateur/Documents/cinema/new_is_always_better/scrapping/allocine_scrapping/ && scrapy crawl allocine_spider_releases -o {spider}_{t_date}.csv'
        bash_command='cd /opt/airflow/allocine_scrapping/allocine_scrapping && python runner_releases.py'

    )

    run_spider
