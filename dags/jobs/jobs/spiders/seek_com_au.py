import re

import scrapy
from scrapy.http import Request

from jobs.items import JobItem


class SeekComAuSpider(scrapy.Spider):
    name = "seek_com_au"
    base_url = 'https://www.seek.com.au/'

    def start_requests(self):
        self.query = re.sub(r'\s+', '-', self.query)
        yield Request(
            f'https://www.seek.com.au/{self.query}',
            meta={'page': 1},
            callback=self.handle_search_results
        )

    def handle_search_results(self, response):
        if 'No matching search results' in response.text:
            return
        
        job_links = response.xpath('//article[@data-card-type="JobCard"]//a[contains(@href, "/job/")]/@href').extract()
        for job_link in job_links:
            yield response.follow(job_link, callback=self.handle_job_page)
        page = response.meta['page'] + 1
        yield Request(
            f'{response.url}?page={page}',
            meta={'page': page},
            callback=self.handle_search_results
        )

    def handle_job_page(self, response):
        yield JobItem(
            match_id=self.get_match_id(response.url),
            job_url=response.url,
            job_title=response.xpath('//h1[@data-automation="job-detail-title"]/text()').get(),
            work_type=response.xpath('//span[@data-automation="job-detail-work-type"]/text()').get(),
            employer=response.xpath('//span[@data-automation="advertiser-name"]//text()').get(),
            salary=response.xpath('//span[@data-automation="job-detail-salary"]/text()').get(),
            location=response.xpath('//span[@data-automation="job-detail-location"]/text()').get(),
            job_description='\n'.join(response.xpath('//div[@data-automation="jobAdDetails"]//text()').extract()),
        )

    def get_match_id(self, job_url):
        return re.search(r'job/(\d+)\?type', job_url).group(1)
