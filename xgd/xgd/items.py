# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class XgdItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    create_at = scrapy.Field()
    url = scrapy.Field()
    short_url = scrapy.Field()
    title = scrapy.Field()
    meta_description = scrapy.Field()
    lang = scrapy.Field()
    content_type = scrapy.Field()
    is_used = scrapy.Field()
    failed = scrapy.Field()
