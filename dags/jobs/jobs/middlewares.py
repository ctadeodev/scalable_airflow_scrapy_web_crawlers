
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from fake_useragent import UserAgent as FakeUserAgent


class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        super().__init__(user_agent)
        self.ua = FakeUserAgent()

    def process_request(self, request, spider):
        request.headers['User-Agent'] = self.ua.random
