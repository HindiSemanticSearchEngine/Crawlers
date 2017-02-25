import requests
from lxml import html
import hashlib
from datetime import datetime
from pymongo import MongoClient
from re import findall
import os.path

header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'}
client = MongoClient()
dataBase = client.Jagran
collection = dataBase.news
collection.create_index('hash', background=True)
currentPageLinks = []


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


def get_links_from_page(link, write_to_file):
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

    links = tree.xpath('//ul[@class="listing"]/li/h3/a/@href')
    if len(links) == 0:
        write_url_to_file('http://www.jagran.com/search/news-page2')
        return False

    global currentPageLinks
    del currentPageLinks[:]
    for i in xrange(0, len(links)):
        currentPageLinks.append('http://www.jagran.com' + links[i])
    if write_to_file:
        write_url_to_file(link)
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
        last_modified = datetime.strptime(last_modified, "%Y-%m-%dT%H:%M:%S")

        summary = tree.xpath('//div[@class="article-summery"]/text()')
        summary = summary[0].encode('utf-8')
        meta_description = tree.xpath('//meta[@property="og:description"]/@content')
        meta_description = meta_description[0].encode('utf-8')

        all_descriptions = tree.xpath('//div[@class="article-content"]/p/text()')
        description = ''
        for i in xrange(0, len(all_descriptions)):
            description += all_descriptions[i]
        description = description.encode('utf-8')
        page_hash = hashlib.md5(meta_title + meta_description).hexdigest()

        data_set = {
            'title': title,
            'hash': page_hash,
            'description': description,
            'summary': summary,
            'last_modified': last_modified,
            'url': url,
            'keywords': keywords
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
    result = get_links_from_page('http://www.jagran.com/search/news-page', False)
    for j in xrange(0, len(currentPageLinks)):
        get_info_from_page(currentPageLinks[j])

    if os.path.isfile('JagranLastUrl.txt'):
        print "File exists"
    else:
        print "File does not exist. Creating file..."
        fx = open('JagranLastUrl.txt', 'w')
        fx.write('http://www.jagran.com/search/news-page2')
        fx.close()

    start_file = open('JagranLastUrl.txt')
    link_url = start_file.read()
    start_file.close()
    link_url = link_url.strip()
    link_url = link_url.split('-')
    link_url = link_url[1]

    counter = int(findall('\d+', link_url)[0])
    while True:
        result = get_links_from_page('http://www.jagran.com/search/news-page' + str(counter), True)
        if not result:
            break
        for j in xrange(0, len(currentPageLinks)):
            get_info_from_page(currentPageLinks[j])
        counter += 1

    print "Wowser. All done!!!"
    write_logs_to_file("", True, "Wowser. All Done!!!")
