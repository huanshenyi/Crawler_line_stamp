import requests
from lxml import etree
import threading
from queue import Queue
import csv


class Procuder(threading.Thread):

    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }

    def __init__(self, page_queue, joke_queue, *args, **kwargs):
        super(Procuder, self).__init__(*args, **kwargs)
        self.base_domain = 'http://www.budejie.com'
        self.page_queue = page_queue
        self.joke_queue = joke_queue

    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url = self.page_queue.get()
            response = requests.get(url, headers=self.headers)
            text = response.text
            html = etree.HTML(text)
            descs = html.xpath("//div[@class='j-r-list-c-desc']")
            for desc in descs:
                jocker = desc.xpath(".//text()")
                link = self.base_domain+desc.xpath(".//a/@href")[0]
                jock = "\n".join(jocker).strip()
                self.joke_queue.put((jock, link))
            print('='*30+'%sページ目ダウンロード終わり'%url.split('/')[-1]+'='*30)

class Consumer(threading.Thread):

    def __init__(self, joke_queue, writer, gLock, *args, **kwargs):
        super(Consumer, self).__init__(*args, **kwargs)
        self.joke_queue = joke_queue
        self.writer = writer
        self.Lock = gLock

    def run(self):
        while True:
            try:
                joke_info = self.joke_queue.get(timeout=40)
                joke, link = joke_info
                self.Lock.acquire()
                self.writer.writerow((joke, link))
                self.Lock.release()
                print('一個保存された')
            except:
                print('break')
                break

def main():
    page_queue = Queue(10)
    joke_queue = Queue(500)
    gLock = threading.Lock()
    fp = open('bsbdj.csv', 'a', newline='', encoding='utf-8')
    writer = csv.writer(fp)
    writer.writerow(('content', 'link'))

    for x in range(1, 11):
        url = 'http://www.budejie.com/%d' % x
        page_queue.put(url)

    for x in range(5):
        t = Procuder(page_queue, joke_queue)
        t.start()

    for x in range(5):
        t = Consumer(joke_queue, writer, gLock)
        t.start()

if __name__ == '__main__':

    main()