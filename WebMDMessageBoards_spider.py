#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy

class BurpeeSpider(scrapy.Spider):
    name = "webmdMB"
    rate = 1.

    def __init__(self):
        self.download_delay = 1/self.rate

    def start_requests(self):
        start_urls = ["https://messageboards.webmd.com/health-conditions/"]
        for url in start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        for href in response.css('div.browse-forums a.internal-link::attr(href)').extract():
            yield scrapy.Request(href, callback=self.parse_topic)

    # parse all the threads in every page of the topic (10 threads per page)
    def parse_topic(self, response):
        for href in response.css('li.content-item div.thread-detail a.internal-link::attr(href)').extract():
            yield scrapy.Request(href, callback=self.parse_thread)

        next_page = response.css('div.pager a.next::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_topic)

    def parse_thread(self, response):
        
        body = ""
        for text in response.css('ul.webmd-mb-thrd div.thread-body::text').extract():
            body += text.encode('utf-8').decode('utf-8').strip() + " "

        # TODO: nest responses?
        responses = []
        for r in response.css('ul.webmd-mb-rsp div.thread-detail'):
            rspBody = ""
            for text in r.css('div.thread-body::text').extract():
                rspBody += text.encode('utf-8').decode('utf-8').strip() + " "
            responses.append(rspBody)

        yield {
            'Topic': response.css('h1.title a::text').extract_first(),
            'Title': response.css('div.thread-detail a.internal-link::text').extract_first(),
            'Body': body,
            'Tags': response.css('li.tag-item a.tag::text').extract(),
            'Responses': responses
        }


