import scrapy
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scraper.items import ScraperItem

class AmarSpider(CrawlSpider):
	name="amarUjala"
	allowed_domains =["amarujala.com"]
	start_urls=["http://www.amarujala.com/search?search=news",]

	rules=[
		Rule(LinkExtractor(allow='',restrict_xpaths=('//section[@class="pd10 auw-lazy-load"]/h3/a')),callback='parse_item',follow=True),
	]

	def parse_item(self,response):
		item=ScraperItem()

		item['url']=Selector(response).xpath('//meta[@property="og:url"]/@content').extract()
		item['title']=Selector(response).xpath('//meta[@name="twitter:title"]/@content').extract()
		item['des']=Selector(response).xpath('//meta[@name="twitter:description"]/@content').extract()
		item['key']=Selector(response).xpath('//meta[@name="keywords"]/@content').extract()
		item['imageUrl']=Selector(response).xpath('//meta[@property="og:image"]/@content').extract()

		yield item
