from telegram.ext.dispatcher import run_async
import requests
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import random
import sys
import lxml.html as lh
import html2markdown
import re
from threading import Thread
import time
from multiprocessing import Queue
from functools import reduce  # python 3
headers_Get = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'lang': 'en-us'
}


class FreeProxy:

    def __init__(self, country_id=[], timeout=0.5, rand=False, anonym=False):
        self.country_id = country_id
        self.timeout = timeout
        self.random = rand
        self.anonym = anonym
        #self.proxy_list = self.get_proxy_list()

    def get_proxy_list(self):
        try:
            page = requests.get('https://www.sslproxies.org')
            doc = lh.fromstring(page.content)
            tr_elements = doc.xpath('//*[@id="proxylisttable"]//tr')
            if not self.country_id:
                proxies = [f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}' for i in
                           range(1, 101)
                           if((tr_elements[i][4].text_content()) == 'anonymous' if self.anonym else True)]  # check the 5th column for `anonymous` if needed
            else:
                proxies = [f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}' for i in
                           range(1, 101)
                           if tr_elements[i][2].text_content() in self.country_id
                           and ((tr_elements[i][4].text_content()) == 'anonymous' if self.anonym else True)]  # check the 5th column for `anonymous` if needed
            return proxies
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

    def get(self, url):
        return requests.get(url, headers=headers_Get)
        proxy_list = self.proxy_list
        if self.random:
            random.shuffle(proxy_list)
            proxy_list = proxy_list
        working_proxy = None
        while True:
            for i in range(len(proxy_list)):
                proxies = {
                    'http': "http://" + proxy_list[i],
                }
                try:
                    return requests.get(url, proxies=proxies, timeout=self.timeout, headers=headers_Get)
                    working_proxy = proxies
                except requests.exceptions.RequestException:
                    continue
            break
        if not working_proxy:
            if self.country_id is not None:
                self.country_id = None
                return self.get(url)
            else:
                return 'There are no working proxies at this time.'


frp = FreeProxy(rand=False, timeout=1.9)


def getGooglePage(query):
    output = BeautifulSoup(frp.get(
        "http://www.google.com/search?q="+query.replace(" ", "+")).text, 'html.parser')
    for script in output(["script", "style"]):
        script.decompose()    # rip it out
    return output


def getSearchResult(soup: BeautifulSoup, queue):
    website_list = []
    for attrs in soup.find_all("div", {"class": "g"}):
        try:
            domain = attrs.find('a')['href']
            title = attrs.find('h3').text
            desc = attrs.findAll('span')[-1].text
            website = {"@type": "website", 'title': title.replace(
                ",", " "), 'link': domain, 'description': desc.replace(",", " ")}
            website_list.append(website)
        except Exception as e:
            print(e)
    return queue.put(website_list)


def getQuickAnswerbox(soup: BeautifulSoup, queue):
    try:

        return queue.put([{"@type": "quickie", "result": soup.find("div",{"class":"xpdopen"}).find("div",{"role": "heading"}).text}])
    except:
        return queue.put([])


def googleGraph(soup: BeautifulSoup, queue):
    mydiv = None
    try:
        mydiv: BeautifulSoup = soup.findAll(
            "div", {"class": "kp-wholepage"})[0]
    except:
        return queue.put([])
    images = None
    try:
        images = [ *[i['data-lpage']
                      for i in mydiv.findAll("div", {"data-attrid": "image"})], *[i['data-lpage']
                  for i in mydiv.findAll("g-img", {"data-attrid": "image"})]]
    except:
        pass
    attrs: BeautifulSoup =mydiv.findAll(
        "div", {"data-attrid": re.compile(".*\:\/.*")})
    definations = []
    title = None
    try:
        title = mydiv.findAll("h2", {"data-attrid": "title"})[0].text
    except:
        return queue.put([])
    subtitle = None
    try:
        subtitle = mydiv.findAll("div", {"data-attrid": "subtitle"})[0].text
    except:
        pass
    specificdefine = None
    try:
        specificdefine = mydiv.findAll(
            "div", {"data-attrid": "description"})[0].findAll("span")[0].text
    except:
        pass
    for i in attrs:
        prpname = []
        for ik in i.findAll("a"):
            try:
                prpname.append(
                {'text': ik.get_text(" "), 'href': "http://www.google.com"+ik['href'] if ik['href'][0] == "/" else ik['href']})
            except:
                pass
            ik.extract()
        othersl = prpname[1:][::-1]
        if(len(othersl) == 0):
            continue
        others = [*othersl][0:4]
        vl = {'name': prpname[0], "answer": i.get_text(" ").replace(
            "፡", "").strip(), "otherLinks": others}
        definations.append(vl)
    return queue.put([{
        "@type": "kgraph",
        "title": title,
        "subtitle": subtitle,
        "images": images,
        "definations": definations,
        "specificdefine": specificdefine
    }])


def sorter(e):
    if(e['@type'] == "kgraph"):
        return 0
    elif(e['@type'] == "quickie"):
        return 3
    else:
        return 5


def Compose(Query):
    page = getGooglePage(Query)
    tasks = (getSearchResult, getQuickAnswerbox, googleGraph)
    q = Queue(999)
    threads = []

    for task in tasks:
        t = Thread(target=task, args=(page, q))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    # return  [q.get() for _ in range(len(tasks))]
    flattenedList = [j for sub in [q.get() for _ in range(len(tasks))]
                     for j in sub]
    flattenedList.sort(key=sorter)
    return flattenedList


def GenerateKgMessage(kg):
    genstr = """{imageloc}<b>{title}</b>
<i>{subtitle}</i>
<code>{description}</code>
{properties}
""".format(imageloc="".join(["""<a href='{img}'>&#8203;</a>""".format(img=image) for image in kg['images'][0:1]]), title=kg['title'], subtitle=kg['subtitle'] or "", description=kg['specificdefine'], properties="".join(["""
- <b><a href='{link}'>{question}</a></b>: {answer} {suplements}""".format(link=question['name']['href'], question=question['name']['text'], answer=question['answer'], suplements=" | ".join(["<a href='{link}'>{text}</a>".format(link=sup['href'], text=sup['text']) for sup in question['otherLinks']])) for question in kg['definations']])).replace(": : ", ": ").replace(" , ", "").replace(",", "").replace(": Profiles", " |")
    return genstr
