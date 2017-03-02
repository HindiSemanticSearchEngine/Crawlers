import requests
from lxml import html
import hashlib
from datetime import datetime
from dateutil.parser import parse
from pymongo import MongoClient
from re import findall
import os.path

header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'}
client = MongoClient()
dataBase = client.Jagran
collection = dataBase.news
collection.create_index('hash', background=True)
current_page_links = []

valid_xpath = ''
result_link = ''
current_end_url = ''
page_extension = '-page'

start_urls = []
start_urls.append("http://www.jagran.com/search/news")
start_urls.append("http://www.jagran.com/news/sports-news-hindi")
start_urls.append("http://www.jagran.com/news/national-news-hindi")
start_urls.append("http://www.jagran.com/news/world-news-hindi")


def write_url_to_file(link):
    print "Writing Url To File..."
    fx = open('JagranLastUrl.txt', mode='w')
    fx.write(link)
    fx.close()


def write_logs_to_file(url, success, reason):
    fx = open("JagranLogs.txt", 'a')
    if success:
        fx.write('Got and Parsed All Links!!!' + "\n")
    else:
        fx.write("Url: " + url + "\n")
        fx.write("Reason: " + reason + "\n")

    fx.write("Current Time: " + str(datetime.now().time()) + "\n")
    if success:
        fx.write("\n")
    fx.close()


def get_links_from_page(link, write_to_file, index):
    print "Getting Page List: " + link
    # noinspection PyUnusedLocal
    tree = ''
    try:
        page = requests.get(link, headers=header)
        tree = html.fromstring(page.content)
    except Exception as e:
        print "Error Occurred: " + str(e)
        write_logs_to_file(link, False, str(e))
        return True

    links = tree.xpath(valid_xpath)
    if len(links) == 0:
        return False

    global current_page_links
    del current_page_links[:]
    for i in xrange(0, len(links)):
        current_page_links.append('http://www.jagran.com' + links[i])
    if write_to_file:
        write_url_to_file(link + " " + index)
    return True


def get_info_from_page(link):
    print "Getting page: " + link
    # noinspection PyUnusedLocal
    tree = ''
    try:
        page = requests.get(link, headers=header)
        tree = html.fromstring(page.content)
    except Exception as e:
        print "Error Occurred: " + str(e)
        write_logs_to_file(link, False, str(e))
        return

    try:
        title = tree.xpath('//section[@class="title"]/h1/text()')
        title = title[0].encode('utf-8')
        meta_title = tree.xpath('//meta[@property="og:title"]/@content')
        meta_title = meta_title[0].encode('utf-8')

        keywords = tree.xpath('//meta[@name="keywords"]/@content')
        keywords = keywords[0].split(',')
        for i in xrange(0, len(keywords)):
            keywords[i] = keywords[i].strip()
            keywords[i] = keywords[i].encode('utf-8')

        url = link

        last_modified = tree.xpath('//meta[@http-equiv="Last-Modified"]/@content')
        last_modified = last_modified[0].encode('utf-8')
        last_modified = last_modified.split('+')
        last_modified = last_modified[0]
        last_modified = parse(last_modified)

        summary = tree.xpath('//div[@class="article-summery"]/text()')
        summary = summary[0].encode('utf-8')

        meta_description = tree.xpath('//meta[@property="og:description"]/@content')
        meta_description = meta_description[0].encode('utf-8')

        image = tree.xpath('//div[@id="jagran_image_id"]/img/@src')
        image = image[0]

        all_descriptions = tree.xpath('//div[@class="article-content"]/p/text()')
        description = ''
        for i in xrange(0, len(all_descriptions)):
            description += all_descriptions[i]
        description = description.encode('utf-8')
        page_hash = hashlib.md5(meta_title + meta_description).hexdigest()

        data_set = {
            'title': title,
            'meta_title': meta_title,
            'hash': page_hash,
            'description': description,
            'meta_description': meta_description,
            'summary': summary,
            'last_modified': last_modified,
            'url': url,
            'keywords': keywords,
            'image': image
        }
        add_to_database(data_set)
    except Exception as e:
        print "Error Occurred: " + str(e)
        write_logs_to_file(link, False, str(e))


def add_to_database(data_set):
    print "Adding " + data_set['title'] + " to database..."
    data_hash = data_set['hash']
    data = collection.find_one({'hash': data_hash})

    if data is not None:
        print "Page Already Added!!!"
        print ""
        return

    collection.insert_one(data_set)
    print "Data Added!!!"
    print ""


if __name__ == '__main__':
    j = 0
    if os.path.isfile("JagranLastUrl.txt"):
        print "File Exists"
        start_file = open("JagranLastUrl.txt")
        file_contents = start_file.read()
        start_file.close()
        j = int(findall("\d+", file_contents)[1])
    else:
        print "File does not exist. Creating file..."
        fx = open('JagranLastUrl.txt', 'w')
        fx.write(start_urls[j] + page_extension + "2 0")
        fx.close()

    for i in xrange(j, len(start_urls)):
        if i == 0:
            result_link = start_urls[i]
            valid_xpath = "//ul[@class=\"listing\"]/li/h3/a[@href]/@href"
            current_end_url = start_urls[i] + page_extension + "2"
        else:
            result_link = start_urls[i] + ".html"
            valid_xpath = "//ul[@class=\"listing\"]/li/h2/a[@href]/@href"
            current_end_url = start_urls[i] + page_extension + "2.html"

        result = get_links_from_page(result_link, False, str(i))
        if result:
            for k in xrange(0, len(current_page_links)):
                get_info_from_page(current_page_links[k])

        start_file = open("JagranLastUrl.txt")
        file_contents = start_file.read()
        counter = 2
        counter = int(findall("\d+", file_contents)[0])

        while True:
            if i == 0:
                result_link = start_urls[i] + page_extension + str(counter)
            else:
                result_link = start_urls[i] + page_extension + str(counter) + ".html"

            result = get_links_from_page(result_link, True, str(i))
            if not result:
                break
            for k in xrange(0, len(current_page_links)):
                get_info_from_page(current_page_links[k])
            counter += 1

        print "======================="
        print "== Set of URLs done. =="
        print "======================="
        write_logs_to_file("", True, "")

        if i == 3:
            current_end_url = start_urls[0] + page_extension + "2 0"
        else:
            current_end_url = start_urls[i + 1] + page_extension + "2.html" + str(i + 1)
        write_url_to_file(current_end_url)

    print "Wowser. All done!!!"
    write_logs_to_file("", True, "")

