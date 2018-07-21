# -*- coding: utf-8 -*-
import random
import re
import scrapy
import time
from scrapy import Request
import json

from doubantv.items import DoubantvItem, DoubantvcommentItem

user_agent_list = [\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"\
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",\
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",\
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",\
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",\
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",\
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",\
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",\
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]
ua = random.choice(user_agent_list)#随机抽取User-Agent
headers = {
          'Accept-Encoding':'gzip, deflate, sdch, br',
          'Accept-Language':'zh-CN,zh;q=0.8',
          'Connection':'keep-alive',
          'Referer':'https://movie.douban.com/j/search_subjects?',
          'User-Agent':ua
          }

class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/j/search_subjects?type=tv&tag=%E5%9B%BD%E4%BA%A7%E5%89%A7&sort=recommend&page_limit=20&page_start=0']
    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse,headers=headers)

    def parse(self, response):
        contents = json.loads(response.text)

        item = DoubantvItem()
        for content in contents['subjects']:
            item['id'] =content['id']
            item['title'] =content['title']
            item['rate'] = content['rate']
            item['link'] =content['url']
            yield item
            link_list=[]
            link_list.append(item['link'])
            for link in link_list:
                base_url = link + 'comments?start={}&limit=20&sort=time&status=P'
                #base_url =item['link']+'comments?start={}&limit=20&sort=time&status=P'
                for i in range(11):
                    url = base_url.format(str(i * 20))
                    yield Request(url=url, callback=self.comment_parse,dont_filter=True,headers=headers)

    def comment_parse(self,response):
        contents = response.xpath('//div[@class="comment"]')
        for content in contents:

            item = DoubantvcommentItem()
            item['comment'] = content.xpath('p/span[@class="short"]/text()').extract_first()
            item['author'] = content.xpath('h3/span[@class="comment-info"]/a/text()').extract_first()
            item['comment_time'] = content.xpath('h3/span[2]/span[3]/text()').extract_first()
            temp_rating =content.xpath('h3//span[starts-with(@class,"allstar")]').re('<span class="allstar(.*?) rating".*?</span>',re.S)[0]
            item['rating'] = int(temp_rating) / 10
            item['votes'] = content.xpath('h3//span[@class="votes"]/text()').extract_first()

            yield item







