import requests
from lxml import html
import time

# List to store all article-urls from each page
urls = [] 

for i in xrange(315) :
    page = requests.get("http://www.jansatta.com/latest-news/page/"+str(i)+"/?s=news")
    time.delay(5)
    tree = html.fromstring(page.content)
    article_urls = tree.xpath('//div[@class="newslistbx"]/h3/a/@href')
    for j in article_urls:
        # Each article url is appended in a global list urls[]
    	urls.append(j)

#Now request is being send to each article page and required data is scraped        
for k in urls:
    page = requests.get(k)
    tree = html.fromstring(page.content)
    title = tree.xpath('//meta[@itemprop="headline"]/@content')
    image = tree.xpath('//meta [@name="twitter:image"]/@content')
    page_url = k
    date_time = tree.xpath('//meta [@itemprop="dateModified"]/@content')
    keyword = tree.xpath('//meta [@name="keywords"]/@content ')
    
    # Data will be inserted in mongodb
    # collection.insert({"url":page_url, "title":title})
    print(title)
    time.delay(5)



