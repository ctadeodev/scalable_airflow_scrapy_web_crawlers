FROM apache/airflow:2.9.1
# USER root
# RUN apt-get update \
#   && apt-get install -y --no-install-recommends libpq-dev python3-dev \
#   && apt-get autoremove -yqq --purge \
#   && apt-get clean \
#   && rm -rf /var/lib/apt/lists/*
# USER airflow
ADD requirements.txt .
RUN pip install apache-airflow==${AIRFLOW_VERSION} -r requirements.txt