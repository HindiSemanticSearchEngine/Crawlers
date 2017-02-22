import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient

i = 1
a = []

if __name__ == "__main__":
    con = MongoClient()
    db = con.hindi-news_database
    news = db.news

while True:
    url = "http://www.patrika.com/tags/news&page="+str(i)+"/" # Link of any hindi website here
    re = requests.get(url)
    soup1 = BeautifulSoup(re.content,"lxml")
    page = soup1.find_all("a",{"class" : "paging"})
    if page == []:
        print "All Available pages have been scraped"
        break
    else:
        a = []
        ref_link = soup1.find_all("a",{"class" : "patrikaLink"})
        for item in ref_link:
            l = item.get('href')
            a.append(l)

        for li in a:
            r = requests.get(li)
            soup = BeautifulSoup(r.content,"lxml")
            title = soup.find_all("meta",{"property" : "og:title"})
            img_data = soup.find_all("meta",{"property" : "og:image"})
            news_url = soup.find_all("meta",{"property" : "og:url"})
            summary = soup.find_all("meta",{"property" : "og:description"})
            key = soup.find_all("meta",{"name" : "keywords"})
            datetime = soup.find_all("time",{"itemprop" : "datePublished"})
            for item,item1,item2,item3,item4,item5 in zip(title,img_data,news_url,summary,key,datetime):
                title_ref = item.get('content')
                img_ref = item1.get('content')
                url_ref = item2.get('content')
                keyword = item4.get('content')
                summary_ref = item3.get('content')
                date_time = item5.get('datetime')
                news.insert({"News_Title":title_ref,"News_URL":url_ref,"News_Date":date_time,"News_Image":img_ref,"News_Summary":summary_ref,"News_Keywords":keyword})
                print "Operation Successful"
            print("\n")
            i = i + 1
                
            
            
        
