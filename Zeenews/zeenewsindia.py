//ZEENEWS SCRAPPING
//-----------------
import requests
from bs4 import BeautifulSoup
import urllib.request



for i in range(1,1000):
    r=requests.get("http://zeenews.india.com/hindi/india?page=" + str(i))
    soup = BeautifulSoup(r.content,"html.parser")
    for j in soup.find_all("h3",class_="lead-health-ab clear"):
        for k in j.find_all("a"):
            print(k.text)        
    for title in soup.find_all("h3",class_="lead-health-ab clear"):
        for url in title.find_all("a"):
            print(url.get('href'))
    for img in soup.find_all('div',class_="lead-health-nw"):
        for img1 in img.find_all('img'):
            print(img1.get('src'))
