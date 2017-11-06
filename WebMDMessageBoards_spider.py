#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy

#TODO: topics dict, utf encoding (still) It/'s
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
        topics = dict()
        topic = response.css('div.browse-forums a.internal-link::text').extract()
        for href in response.css('div.browse-forums a.internal-link::attr(href)').extract():
            yield scrapy.Request(href, callback=self.parse_topic)

        

    def parse_topic(self, response):
        for href in response.css('li.content-item div.thread-detail a.internal-link::attr(href)').extract():
            yield scrapy.Request(href, callback=self.parse_thread)

    # Method for parsing a product page
    def parse_thread(self, response):
        
        # extracting thread-body returns a list of each sentence, so concat them into
        # a single string/paragraph
        # also, extra spaces at beginning/end of paragraphs that I'm not sure how to get rid of
        # without sacrificing a space in between sentences
        body = ""
        for text in response.css('ul.webmd-mb-thrd div.thread-body::text').extract():
            body += text.strip() + " "

        # TODO: nest responses?
        responses = []
        for r in response.css('ul.webmd-mb-rsp div.thread-detail'):
            rspBody = ""
            for text in r.css('div.thread-body::text').extract():
                rspBody += text.strip() + " "
            responses.append(rspBody.decode('utf-8'))

        yield {
            # to keep or not to keep username
            'Title': response.css('div.thread-detail a.internal-link::text').extract_first(),
            'Body': body,
            'Tags': response.css('li.tag-item a.tag::text').extract(),
            'Responses': responses
        }
