import requests
from bs4 import BeautifulSoup
import urllib.request
import time

for i in range(1,650):
    r=requests.get("http://www.livehindustan.com/sports/news-"+str(i))
    soup=BeautifulSoup(r.content,"html.parser")
    for j in soup.find_all('div',attrs={"class":"upper-first "}):
        for k in j.find_all('h4'):
            for urls in k.find_all('a'):
                print(urls.get('href'))
                print(urls.text)
        for img in j.find_all('a',attrs={"class":"listing-pht-blcks pull-left"}):
            for img1 in img.find_all('img'):
                print(img1.get('src'))
        for q in j.find_all('div',attrs={"class":"list-time-tags tags-list"}):
            for q1 in q.find_all('p'):
                print(q1.text)
            for q2 in q.find_all('span'):
                print(q2.text)
        print("\n\n");
    time.sleep(5)
