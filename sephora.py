# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from sephora.items import SephoraItem
import re
import pandas as pd
import json
import math
import time

n_count_tot=0


class SephoraSpider(scrapy.Spider):
    name = 'sephora'
    allowed_domains = ['https://www.sephora.com']
    start_urls = ['http://https://www.sephora.com']

    def parse(self, response):
        # time.sleep(0.5)
        # this scrapes all of the brands
        # links = response.xpath('//a[@class="u-hoverRed u-db u-p1"]//@href').extract()
        # links = [x + "?products=all" for x in links]

        # brand_links = ["/fenty-beauty-rihanna", "/kiehls", "/lancome", "/estee-lauder", "/the-ordinary",
        # "/shiseido", "/sk-ii", "/clinique", "/benefit-cosmetics", "dr-jart", "/chanel", "/nars",
        # "/laneige", "/urban-decay", "/bobbi-brown"]

        brand_links = [""]
        brand_links=[x + "?products=all" for x in brand_links]

        # this scrapes only the brands inside brand_links
        links = ["https://www.sephora.com" + link for link in brand_links]

        for url in links:
            # time.sleep(0.5)
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        # time.sleep(0.5)
        dictionary = response.xpath('//script[@id="searchResult"]/text()').extract()
        dictionary = re.findall('"products":\[(.*?)\]', dictionary[0])[0]

        product_urls = re.findall('"product_url":"(.*?)",', dictionary)
        product_names = re.findall('"display_name":"(.*?)",', dictionary)
        product_ids = re.findall('"id":"(.*?)",', dictionary)
        ratings = re.findall('"rating":(.*?),', dictionary)
        brand_names = re.findall('"brand_name":"(.*?)",', dictionary)
        # list_prices = re.findall('"list_price":(.*?),', dictionary)

        links2 = ["https://www.sephora.com" + link for link in product_urls]

        if len(product_urls) != len(ratings) != len(brand_names):
            print('Number of products do not match with ratings')

        product_df = pd.DataFrame({'links2': links2, 'product_names': product_names, 'p_id': product_ids,
                                   'ratings': ratings, 'brand_names': brand_names})

        print(product_df.head())
        print(list(product_df.index))

        for n in list(product_df.index):
            product = product_df.loc[n, 'product_names']
            p_id = product_df.loc[n, 'p_id']
            p_star = product_df.loc[n, 'ratings']
            brand_name = product_df.loc[n, 'brand_names']

            print(product_df.loc[n, 'links2'])

            # if n>0:
            # time.sleep(20)

            yield Request(product_df.loc[n, 'links2'], callback=self.parse_detail,
                          meta={'product': product, 'p_id': p_id, 'p_star': p_star, 'brand_name': brand_name, })

    def parse_detail(self, response):
        # time.sleep(0.5)
        print('parse_detail')

        product = response.meta['product']
        p_id = response.meta['p_id']
        p_star = response.meta['p_star']
        brand_name = response.meta['brand_name']

        p_category = response.xpath('//a[@class="css-u2mtre"]/text()').extract_first()

        try:
            p_price = response.xpath('//div[@class="css-18suhml"]/text()').extract()
            p_price = p_price[0]
        except:
            p_price = None

        p_num_reviews = response.xpath('//span[@class="css-1dz7b4e"]/text()').extract()
        p_num_reviews = p_num_reviews[0]
        p_num_reviews = p_num_reviews.replace('s', '')
        p_num_reviews = p_num_reviews.replace(' review', '')
        p_num_reviews = int(p_num_reviews)

        print('Number of reviews: {}'.format(p_num_reviews))

        # create code here that creates a list of urls for calling the reviews
        # you will use p_num_reviews, use the "{}".format technique

        # max_n = math.ceil(p_num_reviews/30)
        # low_range = [x*30 for x in list(range(0,max_n))]
        # up_range = [x*30 for x in list(range(1,max_n+1))]

        links3 = ['https://api.bazaarvoice.com/data/reviews.json?Filter=ProductId%3A' +
                  p_id + '&Sort=Helpfulness%3Adesc&Limit=' +
                  '{}&Offset={}&Include=Products%2CComments&'.format(min(int(p_num_reviews), int(100)), 0) +
                  'Stats=Reviews&passkey=rwbw526r2e7spptqd2qzbkp7&apiversion=5.4']

        for url in links3:
            # time.sleep(0.5)
            yield Request(url, callback=self.parse_reviews,
                          meta={'product': product, 'p_id': p_id, 'p_star': p_star, 'brand_name': brand_name,
                                'p_category': p_category, 'p_num_reviews': p_num_reviews, 'p_price': p_price})

    def parse_reviews(self, response):
        # time.sleep(0.5)
        print('parse_reviews')

        product = response.meta['product']
        p_id = response.meta['p_id']
        p_star = response.meta['p_star']
        brand_name = response.meta['brand_name']
        p_price = response.meta['p_price']
        p_category = response.meta['p_category']
        p_num_reviews = response.meta['p_num_reviews']

        data = json.loads(response.text)
        # check keys
        # data.keys()
        reviews = data['Results']  # this is a list
        # each element inside reviews is a dictionary
        # tmp[0].keys() will give the keys of the dictionaries inside reviews

        # create code here which arranges the data from the json dictionary into a dataframe

        n_count = 0
        global n_count_tot

        for review in reviews:

            try:
                reviewer = review['UserNickname']
            except:
                reviewer = None
            try:
                r_star = review['Rating']
            except:
                r_star = None

            try:
                r_eyecolor = review['ContextDataValues']['eyeColor']['Value']
            except:
                r_eyecolor = None

            try:
                r_haircolor = review['ContextDataValues']['hairColor']['Value']
            except:
                r_haircolor = None

            try:
                r_skintone = review['ContextDataValues']['skinTone']['Value']
            except:
                r_skintone = None

            try:
                r_skintype = review['ContextDataValues']['skinType']['Value']
            except:
                r_skintype = None
            try:
                r_skinconcerns = review['ContextDataValues']['skinConcerns']['Value']
            except:
                r_skinconcerns = None

            try:
                r_review = review['ReviewText']
            except:
                r_review = None

            # need to create an error handler for empty data for reviews

            print('BRAND: {} PRODUCT: {}'.format(brand_name, product))
            print('ID: {} STARS: {}'.format(reviewer, r_star))
            print('=' * 50)

            item = SephoraItem()
            item['product'] = product
            item['p_id'] = p_id
            item['p_star'] = p_star
            item['brand_name'] = brand_name
            item['p_price'] = p_price
            item['p_category'] = p_category
            item['p_num_reviews'] = p_num_reviews

            # all of these needs to be taken from the reviews list/dictionary

            item['reviewer'] = reviewer
            item['r_star'] = r_star
            item['r_eyecolor'] = r_eyecolor
            item['r_haircolor'] = r_haircolor
            item['r_skintone'] = r_skintone
            item['r_skintype'] = r_skintype
            item['r_skinconcerns'] = r_skinconcerns
            item['r_review'] = r_review

            # time.sleep(0.025)
            n_count += 1
            n_count_tot += 1

            yield item

        print('=' * 50)
        print('TOTAL NUMBER OF REVIEWS: {}'.format(int(p_num_reviews)))
        print('NUMBER OF REVIEWS TO BE PULLED: {}'.format(len(reviews)))
        print('ACTUAL NUMBER PULLED {}'.format(n_count))
        print('TOTAL NUMBER PULLED {}'.format(n_count_tot))
        print('=' * 50)
