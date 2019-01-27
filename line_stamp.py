import requests
from lxml import etree
import re
from urllib import request
from random import randint
import os


Main_url = []

def search_urls(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    respomse = requests.get(url, headers=headers).json()
    for key in respomse['items']:
        Main_url.append("https://store.line.me/stickershop/product/{}/ja".format(key['id']))
    search_img(Main_url, headers)

def search_img(Main_url, headers):
    for page_url in Main_url:
        text = requests.get(page_url, headers=headers).text
        html = etree.HTML(text)
        title_base = html.xpath("//h3[@class='mdCMN08Ttl']/text()")[0]
        title = re.sub('[\【\】\(\(\＆\☘\/]','',title_base)
        lis = html.xpath("//ul[@class='mdCMN09Ul']/li/div[@class='mdCMN09LiInner']/span/@style")
        imags = list(map(lambda x: re.search(r'(https).+?(true)',x).group(),lis))
        os.mkdir(os.getcwd()+r"\\images\\"+title)
        for imag in imags:
            request.urlretrieve(imag, 'images/{}/'.format(title)+str(randint(0, 500))+'.png')

def main():
    keyword = input('ダウンロードしたいスタンプのキーワードを入れて:')
    url = 'https://store.line.me/api/search/sticker?query={}&offset=0&limit=36&type=ALL&includeFacets=true'.format(keyword)
    val=search_urls(url)

if __name__ =="__main__":
    main()


