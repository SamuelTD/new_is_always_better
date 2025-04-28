FROM apache/airflow:3.0.0-python3.12

USER airflow
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY allocine_scrapping /opt/airflow/allocine_scrapping


ENV AIRFLOW_HOME=/opt/airflow

