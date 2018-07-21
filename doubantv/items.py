# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubantvItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field() #电视名
    link = scrapy.Field() #电视网址
    rate = scrapy.Field() #电视剧评分

class DoubantvcommentItem(scrapy.Item):
    author = scrapy.Field() #评论人
    publish_time = scrapy.Field() #评论时间
    comment = scrapy.Field() #评论
    votes = scrapy.Field() #赞的人数
    #rating = scrapy.Field() #打分

