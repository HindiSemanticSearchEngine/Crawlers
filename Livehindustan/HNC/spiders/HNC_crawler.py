# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from HNC.items import HncItem

class HncCrawlerSpider(CrawlSpider):
    name = 'HNC_crawler'
    allowed_domains = ['livehindustan.com']
    start_urls = [
    'http://www.livehindustan.com/national/news-1',
    'http://www.livehindustan.com/international/news-1',
    'http://www.livehindustan.com/sports/news-1',
    'http://www.livehindustan.com/business/news-1',
    'http://www.livehindustan.com/cricket/news-1',
    'http://www.livehindustan.com/entertainment/news-1',
    'http://www.livehindustan.com/gadgets/news-1',
    'http://www.livehindustan.com/lifestyle/news-1'
    ]

    rules = [
        Rule(LinkExtractor(allow='',restrict_xpaths=('//div[@class="main_news_img"]/a')),callback='parse_item', follow=True),
        Rule(LinkExtractor(allow='',restrict_xpaths=('//div[@class="paging"]/a')), follow=True),
    ]

    def parse_item(self, response):
        item = HncItem()

        item['url'] = Selector(response).xpath('//meta[@property="og:url"]/@content').extract()
        item['title'] = Selector(response).xpath('//meta[@name="twitter:title"]/@content').extract()
        item['summary'] = Selector(response).xpath('//meta[@name="description"]/@content').extract()
        item['description'] = Selector(response).xpath('//meta[@name="twitter:description"]/@content').extract()
        item['keywords'] = Selector(response).xpath('//meta[@name="keywords"]/@content').extract()
        item['date_time'] = Selector(response).xpath('//meta[@name="article:published_time"]/@content').extract()
        item['image_url'] = Selector(response).xpath('//meta[@property="og:image"]/@content').extract()


        yield item
