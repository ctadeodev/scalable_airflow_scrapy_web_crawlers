# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    source_id = scrapy.Field()
    match_id = scrapy.Field()
    job_url = scrapy.Field()
    job_title = scrapy.Field()
    work_type = scrapy.Field()
    employer = scrapy.Field()
    salary = scrapy.Field()
    hours_per_week = scrapy.Field()
    location = scrapy.Field()
    job_description = scrapy.Field()
    date_posted = scrapy.Field()
    created_at = scrapy.Field()

    def __repr__(self):
        """only print out job_title after exiting the Pipeline"""
        return repr({"job_title": self['job_title']})
