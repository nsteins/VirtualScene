# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class FanItem(Item):
    username = Field()
    url = Field()
    name = Field()
    fan_id = Field()
    collection = Field()
    pass

class AlbumItem(Item):
    artist = Field()
    name = Field()
    album_id = Field()
    url = Field()
    fans = Field()
