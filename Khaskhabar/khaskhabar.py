from bs4 import BeautifulSoup
import requests
import time

for i in range(1,2000):
    r=requests.get("http://www.khaskhabar.com/tags/news/"+str(i))
    soup = BeautifulSoup(r.content,"html.parser")
    for j in soup.find_all("div",class_="grid_16 alpha"):
        for k in j.find_all("ul"):
            for l in k.find_all('li'):
                for g in l.find_all('a'):
                    url=(g.get('href'))
                    r=requests.get(url)
                    soup=BeautifulSoup(r.content,"html.parser")
                    for title in soup.find_all("meta",attrs={'property':"og:title"}):
                        print(title.get("content"))
                    for key in soup.find_all('meta',attrs={"name":"keywords"}):
                        print(key.get("content"))
                    for link in soup.find_all("link",attrs={'rel':"canonical"}):
                        print(link.get('href'))
                    for img in soup.find_all("meta",attrs={'property':"og:image"}):
                        print(img.get('content'))
                    for date in soup.find_all('meta',attrs={'property':"article:published_time"}):
                        print(date.get('content'))
                    print('\n')
    time.sleep(5)
