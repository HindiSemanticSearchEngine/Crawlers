# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ndtv.items import ndtvItem
from datetime import datetime

class ndtvcrawler(CrawlSpider):
    name = 'ndtv_crawler'
    allowed_domains = ['khabar.ndtv.com']
    start_urls = ['https://khabar.ndtv.com/topic/news/news']

    rules = [
        Rule(LinkExtractor(allow='',restrict_xpaths=('//p[@class="header fbld"]/a')),callback='parse_item', follow=True),
        Rule(LinkExtractor(allow='',restrict_xpaths=('//div[@class="new_pagination"]/a[last()]')), follow=True),
    ]

    def parse_item(self, response):
        item = ndtvItem()

        item['url'] = Selector(response).xpath('//meta[@property="og:url"]/@content').extract()
        item['title'] = Selector(response).xpath('//meta[@property="og:title"]/@content').extract()
        item['des'] = Selector(response).xpath('//meta[@name="description"]/@content').extract()
        item['key'] = Selector(response).xpath('//meta[@name="keywords"]/@content').extract()
        item['imageUrl'] = Selector(response).xpath('//meta[@property="og:image"]/@content').extract()
        date_info=Selector(response).xpath('//meta[@name="publish-date"]/@content').extract()
        date_info = date_info[0].encode('utf-8')
        date_info = date_info.split('+')
        date_info = date_info[0].strip()
        item['date_published']=datetime.strptime(date_info,'%a, %d %b %Y %H:%M:%S')

        yield item