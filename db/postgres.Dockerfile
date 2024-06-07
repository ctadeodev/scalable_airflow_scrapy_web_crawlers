FROM postgres:13
COPY init-database.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init-database.sh
RUN /docker-entrypoint-initdb.d/init-database.sh