# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

#
# class DoubantvPipeline(object):
#     def process_item(self, item, spider):
#         return item


from datetime import datetime
from hashlib import md5
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi
from doubantv.items import *
import logging
import sys
import ujson
from kafka import KafkaProducer

class KafkaPipeline(object):
    '''
    Pushes a serialized item to appropriate Kafka topics.
    '''

    def __init__(self, producer, topic):
        self.producer = producer
        self.topic = topic
        logging.debug("Setup kafka pipeline")

    @classmethod
    def from_settings(cls, settings):
        try:
            producer = KafkaProducer(bootstrap_servers=settings['bootstrap_servers'],
                                     sasl_mechanism="PLAIN",
                                     security_protocol='SASL_SSL',
                                     api_version=(0, 10),
                                     retries=5,
                                     sasl_plain_username=settings['sasl_plain_username'],
                                     sasl_plain_password=settings['sasl_plain_password'])

        except Exception as e:
            logging.error("Unable to connect to Kafka in Pipeline"\
                ", raising exit flag.")
            # this is critical so we choose to exit.
            # exiting because this is a different thread from the crawlers
            # and we want to ensure we can connect to Kafka when we boot
            sys.exit(1)
        topic = settings['KAFKA_TOPIC']
        #use_base64 = settings['KAFKA_BASE_64_ENCODE']

        return cls(producer, topic)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def _get_time(self):
        '''
        Returns an ISO formatted string of the current time
        '''
        return datetime.utcnow().isoformat()

    def process_item(self, item, spider):
        try:
            logging.debug("Processing item in KafkaPipeline")
            datum = dict(item)
            datum["timestamp"] = self._get_time()
            try:
                message = ujson.dumps(datum, sort_keys=True)
            except Exception as e:
                logging.error(e.message)
                message = 'json failed to parse'
            self.producer.send(self.topic, message, key=str(datum['id']))
        except Exception as e:
            logging.error(e.message)
        return item

    def close_spider(self, spider):
        logging.info("Closing Kafka Pipeline")
        self.producer.flush()
        self.producer.close(timeout=10)
