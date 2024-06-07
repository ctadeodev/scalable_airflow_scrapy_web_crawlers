from urllib.parse import urlencode

import scrapy
from scrapy.http import Request
from scrapy.utils.response import open_in_browser

from jobs.items import JobItem


class OnlineJobsPhSpider(scrapy.Spider):
    name = 'online_jobs_ph'
    base_url = 'https://www.onlinejobs.ph'
    job_search_url = f'{base_url}/jobseekers/jobsearch?'

    def start_requests(self):
        query = {
            'jobkeyword': self.job,
            'fullTime': getattr(self, 'fulltime', 'on'),
            'partTime': getattr(self, 'parttime', 'on'),
            'Freelance': getattr(self, 'freelance', 'on'),
        }
        yield Request(
            self.job_search_url + urlencode(query),
            callback=self.handle_search_results
        )

    def handle_search_results(self, response):
        for div in response.xpath('//div[contains(@class, "latest-job-post")]'):
            yield response.follow(
                div.xpath('.//a/@href').get(),
                meta={
                    'Employer': div.xpath('.//p/text()').get().replace('•', '').strip(),
                    'Job Title': div.xpath('.//h4/text()').get()
                },
                callback=self.handle_job_page
            )
        next_page_link = response.xpath('//a[@rel="next"]/@href').get()
        if next_page_link:
            yield Request(
                next_page_link,
                callback=self.handle_search_results
            )

    def handle_job_page(self, response):
        def get_value(keyword):
            xpath_expr = f'//*[text()="{keyword}"]/following-sibling::*[1]/text()'
            return response.xpath(xpath_expr).get().strip()
        yield JobItem(
            job_url=response.url,
            job_title=response.meta['Job Title'],
            work_type=get_value('TYPE OF WORK'),
            employer=response.meta['Employer'],
            salary=get_value('SALARY'),
            hours_per_week=get_value('HOURS PER WEEK'),
            location='Philippines',
            job_description=''.join(response.xpath('//p[@id="job-description"]/text()').extract()),
            date_posted=get_value('DATE POSTED')
        )
