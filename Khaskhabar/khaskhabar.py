from bs4 import BeautifulSoup
import requests

for i in range(1,1000):
    r=requests.get("http://www.khaskhabar.com/tags/news/"+str(i))
    soup = BeautifulSoup(r.content,"html.parser")
    for j in soup.find_all("div",class_="grid_16 alpha"):
        for k in j.find_all("p"):
            print(k.text)
    for title in soup.find_all("li"):
        for title1 in title.find_all("a"):
            print(title1.get("href"))
    for img in soup.find_all("li"):
        for img1 in title.find_all("a"):
            for img2 in img1.find_all("img"):
                print(img2.get("src"))
    
