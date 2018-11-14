# -*- coding: utf-8 -*-
import scrapy


class SephoraspySpider(scrapy.Spider):
    name = 'sephoraspy'
    allowed_domains = ['www.sephora.com/brands-list']
    start_urls = ['http://www.sephora.com/brands-list/']

    def parse(self, response):
        self.log("I just visited: " + response.url)
