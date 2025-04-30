# ----------------------------------------------
# Étape 1 : Base propre sur Debian stable
# ----------------------------------------------
FROM python:3.10-slim-bullseye

# Évite les prompts interactifs d'apt
ENV DEBIAN_FRONTEND=noninteractive

# ----------------------------------------------
# Étape 2 : Install des dépendances système
# ----------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    libpq-dev \
    libssl-dev \
                    git \
    curl \
    gnupg2 \
    unixodbc-dev \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# Ajouter Microsoft SQL Server ODBC Driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ----------------------------------------------
# Étape 3 : Installation des librairies Python
# ----------------------------------------------

# Airflow + scrapy + pyodbc
RUN pip install --no-cache-dir apache-airflow==2.9.1 \
    'apache-airflow-providers-postgres' \
    pyodbc \
    scrapy

# Optionnel : installer des requirements supplémentaires si besoin
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# ----------------------------------------------
# Étape 4 : Variables d'environnement pour Airflow
# ----------------------------------------------
ENV AIRFLOW_HOME=/opt/airflow
WORKDIR /opt/airflow

# ----------------------------------------------
# Étape 5 : Dossiers nécessaires
# ----------------------------------------------
RUN mkdir -p /opt/airflow/dags /opt/airflow/logs /opt/airflow/plugins

# ----------------------------------------------
# Étape 6 : Entrypoint
# (Tu peux surcharger depuis docker-compose)
# ----------------------------------------------
ENTRYPOINT ["airflow"]

CMD ["webserver"]
