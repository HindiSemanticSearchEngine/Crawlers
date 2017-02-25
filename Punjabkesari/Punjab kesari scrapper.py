

import requests
from bs4 import BeautifulSoup
import urllib.request



for i in range(1,2000):
    r=requests.get("http://www.punjabkesari.in/latest.aspx?pageno=" + str(i))
    soup = BeautifulSoup(r.content,"html.parser")
    for j in soup.find_all("h2"):
        for k in j.find_all("a"):
            url=(k.get('href'))
            r=requests.get(url)
            soup=BeautifulSoup(r.content,"html.parser")
            for l in soup.find_all('div',class_="story-part"):
                for g in l.find_all("h2"):
                    print(g.text)
            for keywords in soup.find_all("head"):
                for key in keywords.find_all("meta"):
                                          print(key.get("content"))
                for link in keywords.find_all("link"):
                    print(link.get('href'))
