CREATE SCHEMA jobs;

CREATE TABLE IF NOT EXISTS jobs.sources (
    source_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url VARCHAR(100) NOT NULL
)

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

CREATE TABLE IF NOT EXISTS jobs.crawlers (
    id SERIAL PRIMARY KEY,
    source_id INT REFERENCES jobs.sources(source_id),
    name VARCHAR(200) NOT NULL unique,
    crawler_name VARCHAR(200) NOT NULL,
    args VARCHAR(200) NOT NULL,
    frequency VARCHAR(20) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE
);

-- INSERT INTO jobs.crawlers (source_id, name, crawler_name, args, frequency) VALUES (1, 'online_jobs_ph_python_developer', 'online_jobs_ph', '-a "job=python developer"', 'daily');
-- INSERT INTO jobs.crawlers (source_id, name, crawler_name, args, frequency) VALUES (1, 'online_jobs_ph_data_engineer', 'online_jobs_ph', '-a "job=data engineer"', 'daily');
-- INSERT INTO jobs.crawlers (source_id, name, crawler_name, args, frequency) VALUES (1, 'online_jobs_ph_software_engineer', 'online_jobs_ph', '-a "job=software engineer"', 'daily');
-- INSERT INTO jobs.crawlers (source_id, name, crawler_name, args, frequency) VALUES (1, 'online_jobs_ph_software_developer', 'online_jobs_ph', '-a "job=software developer"', 'daily');
-- INSERT INTO jobs.crawlers (source_id, name, crawler_name, args, frequency) VALUES (1, 'online_jobs_ph_python_programmer', 'online_jobs_ph', '-a "job=python programmer"', 'daily');
-- INSERT INTO jobs.crawlers (source_id, name, crawler_name, args, frequency, enabled) VALUES (1, 'online_jobs_ph_va', 'online_jobs_ph', '-a "job=va"', 'daily', FALSE);

CREATE TABLE jobs.highwatermark (
    id SERIAL PRIMARY KEY,
    crawler_id INT REFERENCES jobs.crawlers(id),
    name VARCHAR(100) NOT NULL,
    value VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

CREATE INDEX idx_jobs_source_id ON jobs.jobs (source_id);
CREATE INDEX idx_jobs_match_id ON jobs.jobs (match_id);
CREATE INDEX idx_highwatermark_crawler_id ON jobs.highwatermark (crawler_id);
