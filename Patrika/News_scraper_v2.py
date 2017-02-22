import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

i = 1

if __name__ == "__main__":
    con = MongoClient()
    db = con.patrika_database
    news = db.news

while True:
    url = "http://www.patrika.com/tags/news&page="+str(i)+"/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content,"lxml")
    page = soup.find_all("a",{"class":"paging"})
    if page == []:
        print "All Availaible Pages have been scraped"
        break

    else:
        title = soup.find_all("a",{"class" : "patrikaLink"})
        img_data = soup.find_all("img",{"width" : "313px"})
        summary = soup.find_all("span",{"class" : "tagsynopsis"})
        date = soup.find_all("span",{"class" : "tagdate"})


        for item,item2,item3,item4 in zip(title,img_data,summary,date):
            imgUrl = item2.get('src')
            res = requests.get(imgUrl)
            res.raise_for_status()
            news.insert({"News_Date" : item4.text,"News_Title" : item.text,"News_Summary" : item3.text,"url" : url,"Image_URL" : imgUrl})
            print "Operation Successful"

        i = i + 1
         
