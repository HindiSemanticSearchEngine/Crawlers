import requests
from bs4 import BeautifulSoup
import urllib.request
import time



for i in range(1,2000):
    r=requests.get("http://zeenews.india.com/hindi/india?page=" + str(i))
    soup = BeautifulSoup(r.content,"html.parser")
    for j in soup.find_all("div",class_="lead-health-nw"):
        for k in j.find_all("h3"):
            for d in k.find_all('a'):
                f=d.get('href')
                url=('http://zeenews.india.com' + str(f))
                r=requests.get(url)
                soup=BeautifulSoup(r.content,"html.parser")
                for title in soup.find_all('meta',attrs={'name':"viewport"}):
                    for title1 in title.find_all('title'):
                        print(title1.text)
                for key in soup.find_all('meta',attrs={"name":"keywords"}):
                                          print(key.get("content"))
                for link in soup.find_all("link",attrs={'rel':"amphtml"}):
                    print(link.get('href'))
                for img in soup.find_all("div",class_="field-item even"):
                    for img1 in img.find_all("img"):
                        print(img1.get('src'))
                for date in soup.find_all('meta',attrs={'property':"article:published_time"}):
                    print(date.get('content'))
                print('\n')
    time.sleep(5)
