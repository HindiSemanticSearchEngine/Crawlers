import requests
from lxml import html
import time
from pymongo import MongoClient
from datetime import datetime
if __name__=="__main__":
    con =MongoClient()
    db=con.semantic_database
    news = db.news

for i in xrange(1, 316):
    page = requests.get("http://www.jansatta.com/page/"+str(i)+"/?s=news")
    tree = html.fromstring(page.content)
    article_urls = tree.xpath('//div[@class="newslistbx"]/h3/a/@href')
    for k in article_urls:
        page = requests.get(k)
        tree = html.fromstring(page.content)
        title = tree.xpath('//meta[@itemprop="headline"]/@content')
        image = tree.xpath('//meta [@name="twitter:image"]/@content')
        page_desc=tree.xpath('//meta[@itemprop="description"]/@content')
        page_url = k
        last_modified = tree.xpath('//meta [@itemprop="dateModified"]/@content')
        last_modified = last_modified[0]
        last_modified = last_modified.split('+')
        last_modified = last_modified[0]
        last_modified = datetime.strptime(last_modified, "%Y-%m-%dT%H:%M:%S")                   
        keyword = tree.xpath('//meta [@name="keywords"]/@content ')
        print(title)
        news.insert({"url":page_url, "title":title,"image":image,"keyword":keyword,"date and time":last_modified,"description":page_desc})
        
    



'''
for i in xrange(315) :
    page = requests.get("http://www.jansatta.com/latest-news/page/"+str(i)+"/?s=news")
    tree = html.fromstring(page.content)
    article_urls = tree.xpath('//div[@class="newslistbx"]/h3/a/@href')
    for j in article_urls:
    	urls.append(j)
'''