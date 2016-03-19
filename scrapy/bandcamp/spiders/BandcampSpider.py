import scrapy
import re
import json
import pdb
import urlparse
import os
import psycopg2

from bandcamp.items import FanItem,AlbumItem
from ..settings import DATABASE

class BCSpider(scrapy.Spider):
    name = 'bandcamp'
    with open(os.path.join(os.path.dirname(__file__),'albums.txt')) as f:
        start_urls = [x.strip(' \t\n') for x in f.readlines()]
   
    def __init__(self):
        self.con = psycopg2.connect(**DATABASE)
        self.cur = self.con.cursor()

    def parse(self,response):
        request = scrapy.Request(response.url,callback=self.parse_album)
        request.meta['dep']=0
        yield(request)

    def parse_album(self, response):
        album = AlbumItem()

        album_re = re.compile(r'EmbedData = {(.*?)};',re.DOTALL)
        id_re = re.compile(r'value: (\d*)')
        for text in response.xpath('//script'):
            albumdata = text.re(album_re)
            if albumdata:
                albumstr = albumdata[0].replace('"','')
                album_list = dict(item.strip().split(': ',1) for item in re.split(', ?\n',albumstr))
        album['album_id'] = id_re.search(album_list['tralbum_param']).group(1)
        album['url'] = album_list['linkback'].replace(' + ','')
        album['name'] = album_list['album_title']
        album['artist'] = album_list['artist']

        r = response.xpath('//div[@id="collectors-data"]/@data-blob').extract()[0]
        js = json.loads(r)
        album['fans'] = list(fan['fan_id'] for fan in js['thumbs'])
        
        if js['more_thumbs_available']:
            api_url = urlparse.urlparse(album['url']).hostname
            api_url = 'https://'+api_url+'/api/tralbumcollectors/1/thumbs'
            api_body = '{"tralbum_type":"a","tralbum_id":'+album['album_id']+',"offset":80,"count":700}'
            more_thumbs_request = scrapy.Request(url=api_url,method='POST',body=api_body
                                    ,callback=self.parse_thumbs)
            more_thumbs_request.meta['album']=album
            yield(more_thumbs_request)
        yield(album)
        
        for fan in js['thumbs']:
            try:
                self.cur.execute("SELECT * FROM fans WHERE id=%s",(fan['fan_id'],))
                if self.cur.fetchone() is None:
                    url = 'http://bandcamp.com/'+fan['username']
                    request = scrapy.Request(url, callback=self.parse_fan)
                    request.meta['dep'] = response.meta['dep'] +1
                    yield(request)
            except Exception as e:
                print('Error parsing fans: ' + e)

    def parse_thumbs(self, response):
        album = response.meta['album']
        jsonresponse = json.loads(response.body_as_unicode())
        new_fans = list(fan['fan_id'] for fan in jsonresponse['results'])
        album['fans'] += new_fans

        if jsonresponse['more_available']:
            api_url = urlparse.urlparse(album['url']).hostname
            api_url = 'https://'+api_url+'/api/tralbumcollectors/1/thumbs'
            api_body = '{"tralbum_type":"a","tralbum_id":' + album['album_id']+',"offset":80,"count":700}'

            more_thumbs_request = scrapy.Request(url=api_url,method='POST'
                    ,body=api_body,callback=self.parse_thumbs)
            more_thumbs_request.meta['album']=album
            yield(more_thumbs_request)

        yield(album)

        for fan in jsonresponse['results']:
            try:
                self.cur.execute("SELECT * FROM fans WHERE id=%s",(fan['fan_id'],))
                if self.cur.fetchone() is None:
                    url = 'http://bandcamp.com/'+fan['username'] 
                    request = scrapy.Request(url, callback=self.parse_fan) 
                    request.meta['dep'] = response.meta['dep']+1
                    yield(request)
            except Exception as e:
                print ("Error parsing fans: " + e)
 



    def parse_fan(self, response):
        fan = FanItem()

        coll_re = re.compile(r'item_details: {(.*)},.*?redownload_urls',re.DOTALL)
        fan_re = re.compile(r'var FanData = {(.*?)};',re.DOTALL)
        
        for text in response.xpath('//script'):
            collection_data = text.re(coll_re)
            if collection_data:
                coll_json = json.loads('{'+collection_data[0]+'}')
            fan_data = text.re(fan_re)
            if fan_data:
                fan_str = fan_data[0].replace('"','')
                fan_list = dict(item.strip().split(': ') 
                    for item in fan_str.split(',\n'))
        fan['username'] = fan_list['username']
        fan['name'] = fan_list['name']
        fan['url'] = fan_list['trackpipe_url']
        fan['fan_id'] = fan_list['fan_id']
        fan['collection'] = list(int(key) for key in coll_json.keys())

        for album in coll_json.values():
            try:
                self.cur.execute("SELECT * FROM albums WHERE id=%s",(album['tralbum_id'],))
                if self.cur.fetchone() is None:
                    request = scrapy.Request(album['item_url'],callback=self.parse_album)
                    request.meta['dep'] = response.meta['dep']
                    yield(request)
            except Exception as e:
                print ('Error: ' + e)

        yield(fan)
