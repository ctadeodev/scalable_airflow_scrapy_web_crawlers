CREATE SCHEMA IF NOT EXISTS jobs;

CREATE TABLE IF NOT EXISTS jobs.sources (
    source_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url VARCHAR(100) NOT NULL
);

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
);

CREATE TABLE IF NOT EXISTS jobs.crawlers (
    id SERIAL PRIMARY KEY,
    source_id INT REFERENCES jobs.sources(source_id),
    name VARCHAR(200) NOT NULL unique,
    crawler_name VARCHAR(200) NOT NULL,
    args VARCHAR(200) NOT NULL,
    frequency VARCHAR(20) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    priority INT DEFAULT 4,
    pool VARCHAR(100) NOT NULL
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'jobs'
        AND tablename = 'jobs'
        AND indexname = 'idx_jobs_source_id'
    ) THEN
        CREATE INDEX idx_jobs_source_id ON jobs.jobs (source_id);
    END IF;
    IF NOT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'jobs'
        AND tablename = 'jobs'
        AND indexname = 'idx_jobs_match_id'
    ) THEN
        CREATE INDEX idx_jobs_match_id ON jobs.jobs (match_id);
    END IF;
END $$;