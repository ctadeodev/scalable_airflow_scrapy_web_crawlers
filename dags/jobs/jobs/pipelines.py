import re
import logging

import psycopg2
from scrapy.exceptions import DropItem


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class JobsPipeline:

    def __init__(self):
        connection_params = {
            'host': 'postgres',
            'port': 5432,
            'user': 'airflow',
            'password': 'airflow',
            'database': 'ingest_db'
        }
        self.connection = psycopg2.connect(**connection_params)
        self.cursor = self.connection.cursor()

        ## Create tables if none exists
        self.create_tables()

    def process_item(self, item, spider):
        item['source_id'] = self.get_source_id(spider)
        item['match_id'] = self.get_match_id(item)
        data = self.clean_data(item)
        try:
            self.cursor.execute("""
                INSERT INTO jobs.jobs (
                    match_id, source_id, job_url, job_title, work_type, employer, salary,
                    hours_per_week, location, job_description, date_posted
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (match_id) DO UPDATE SET
                    source_id = EXCLUDED.source_id,
                    job_url = EXCLUDED.job_url,
                    job_title = EXCLUDED.job_title,
                    work_type = EXCLUDED.work_type,
                    employer = EXCLUDED.employer,
                    salary = EXCLUDED.salary,
                    hours_per_week = EXCLUDED.hours_per_week,
                    location = EXCLUDED.location,
                    job_description = EXCLUDED.job_description,
                    date_posted = EXCLUDED.date_posted,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                data.get('match_id'),
                data.get('source_id'),
                data.get('job_url'),
                data.get('job_title'),
                data.get('work_type'),
                data.get('employer'),
                data.get('salary'),
                data.get('hours_per_week'),
                data.get('location'),
                data.get('job_description'),
                data.get('date_posted')
            ))
            self.connection.commit()
        except psycopg2.Error as e:
            # Handle any errors during the insertion process
            spider.logger.error(f"Error inserting item: {e}")
            self.connection.rollback()
            raise DropItem(f"Error inserting item: {e}")
        return item

    def get_source_id(self, spider):
        query = "SELECT source_id FROM jobs.sources WHERE name = %s;"
        self.cursor.execute(query, (spider.name, ))
        try:
            return self.cursor.fetchone()[0]
        except TypeError:
            try:
                spider.logger.info(f"Adding new source: {spider.name}")
                query = "INSERT INTO jobs.sources (name, url) VALUES (%s, %s)"
                self.cursor.execute(query, (spider.name, spider.base_url))
                self.connection.commit()
            except psycopg2.Error as e:
                # Handle any errors during the insertion process
                spider.logger.error(f"Failed to insert source: {spider.name} ({e})")
                self.connection.rollback()
                raise DropItem(f"Failed to insert source: {spider.name} ({e})")
            return self.get_source_id(spider)

    def get_match_id(self, item):
        return re.search(r'-(\d+)$', item['job_url']).group(1)

    def clean_data(self, item):
        def try_int(value):
            try:
                return int(float((value or '').replace(',', '')))
            except ValueError:
                return None
        data = dict(item)
        data['hours_per_week'] = try_int(data['hours_per_week'])
        return data

    def close_spider(self, spider):
        ## Close cursor & connection to database
        self.cursor.close()
        self.connection.close()

    def create_tables(self):
        create_sources_table  = """
            CREATE TABLE IF NOT EXISTS jobs.sources (
                source_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                url VARCHAR(100) NOT NULL
            )
            """
        create_jobs_table = """
            CREATE TABLE IF NOT EXISTS jobs.jobs (
                job_id SERIAL PRIMARY KEY,
                match_id VARCHAR(32) NOT NULL UNIQUE,
                source_id INT REFERENCES jobs.sources(source_id),
                job_url VARCHAR(200) NOT NULL,
                job_title VARCHAR(200) NOT NULL,
                work_type VARCHAR(50),
                employer VARCHAR(100) NOT NULL,
                salary VARCHAR(100),
                hours_per_week INT,
                location VARCHAR(100),
                job_description TEXT,
                date_posted TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        self.connection.commit()
        try:
            self.cursor.execute(create_sources_table)
            self.cursor.execute(create_jobs_table)
            self.connection.commit()
        except psycopg2.Error as e:
            # Handle any errors during the insertion process
            logging.error(f"Error creating tables: {e}")
            self.connection.rollback()
            raise DropItem(f"Error creating tables: {e}")
