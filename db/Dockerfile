FROM postgres:13
COPY jobs.sql /usr/local/bin/jobs.sql
COPY custom-entrypoint.sh /usr/local/bin/custom-entrypoint.sh
ENV PGHOST localhost
ENV PGUSER airflow
ENV PGPASSWORD airflow
ENV POSTGRES_INGEST_DB ingest_db
RUN chmod +x /usr/local/bin/custom-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/custom-entrypoint.sh"]