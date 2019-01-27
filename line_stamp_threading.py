import requests
from lxml import etree
import re
from urllib import request
from random import randint
import os
from queue import Queue
import threading

Main_url = []


"""生産者クラス"""
class Procuder(threading.Thread):

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }

    def __init__(self, page_queue, img_queue, *args, **kwargs):
        super(Procuder, self).__init__(*args, **kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.page_queue.empty():
                  break
            url = self.page_queue.get()
            self.parse_page(url)

    def parse_page(self, url):
        respomse = requests.get(url, headers=self.headers).json()
        for key in respomse['items']:
            Main_url.append("https://store.line.me/stickershop/product/{}/ja".format(key['id']))
        self.search_img(Main_url, self.headers)

    def search_img(self, Main_url, headers):
        for page_url in Main_url:
            text = requests.get(page_url, headers=headers).text
            html = etree.HTML(text)
            title_base = html.xpath("//h3[@class='mdCMN08Ttl']/text()")[0]
            title = re.sub('[\【\】\(\(\＆\☘\/]', '', title_base)
            lis = html.xpath("//ul[@class='mdCMN09Ul']/li/div[@class='mdCMN09LiInner']/span/@style")
            imags = list(map(lambda x: re.search(r'(https).+?(true)', x).group(), lis))
            os.mkdir(os.getcwd() + r"\\images\\" + title)
            for imag in imags:

                #request.urlretrieve(imag, 'images/{}/'.format(title) + str(randint(0, 500)) + '.png')
                filename=str(randint(0, 500))+'.png'
                self.img_queue.put((imag, filename, title))


class Consumer(threading.Thread):
    def __init__(self, page_queue, img_queue, *args, **kwargs):
        super(Consumer, self).__init__(*args, **kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:

            img_url, filename,title = self.img_queue.get()
            request.urlretrieve(img_url,'images/'+title+'/'+filename)
            print(filename+'ダウンロード終わり')


def main():
    keyword = input('ダウンロードしたいスタンプのキーワードを入れて:')
    url = 'https://store.line.me/api/search/sticker?query={}&offset=0&limit=36&type=ALL&includeFacets=true'.format(keyword)
    page_queue = Queue(100)
    img_queue = Queue(1000)

    page_queue.put(url)

    for x in range(5):
        t1 = Procuder(page_queue, img_queue)
        t1.start()
    for x in range(5):
        t2 = Consumer(page_queue, img_queue)
        t2.start()
if __name__ =="__main__":
    main()


