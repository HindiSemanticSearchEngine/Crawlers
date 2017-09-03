
import requests
from bs4 import BeautifulSoup
import urllib.request
import time



for i in range(1,5200):
    r=requests.get("http://www.punjabkesari.in/latest.aspx?pageno=" + str(i))
    soup = BeautifulSoup(r.content,"html.parser")
    for j in soup.find_all("h2"):
        for k in j.find_all("a"):
            url=(k.get('href'))
            r=requests.get(url)
            soup=BeautifulSoup(r.content,"html.parser")
            for title in soup.find_all('meta',attrs={'name':"description"}):
                print(title.get('content'))
            for key in soup.find_all('meta',attrs={"name":"keywords"}):
                                          print(key.get("content"))
            for link in soup.find_all("link",attrs={'rel':"amphtml"}):
                    print(link.get('href'))
            for img in soup.find_all("span",class_="phot"):
                for img1 in img.find_all("img"):
                    print(img1.get('src'))
            for date in soup.find_all('meta',attrs={'property':"article:published_time"}):
                print(date.get('content'))
            print('\n')
    time.sleep(5)
