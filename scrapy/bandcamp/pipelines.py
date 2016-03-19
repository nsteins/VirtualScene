#-*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from items import AlbumItem,FanItem
from settings import DATABASE

import psycopg2

class BandcampPipeline(object):

    def __init__(self):
        try:
            self.con = psycopg2.connect(**DATABASE)
            self.cur = self.con.cursor()

            cur = self.cur
            con = self.con

            cur.execute(("CREATE TABLE IF NOT EXISTS albums(id BIGINT PRIMARY KEY,artist TEXT,name TEXT,url TEXT,"
                         "fan_size INT)"))
            cur.execute(("CREATE TABLE IF NOT EXISTS fans(id BIGINT PRIMARY KEY,username TEXT,name TEXT,url TEXT,"
                         "coll_size INT)"))
            cur.execute("CREATE TABLE IF NOT EXISTS relationship(album_id BIGINT, fan_id BIGINT, PRIMARY KEY(album_id,fan_id))")
            
            self.ins_album = ('INSERT INTO albums (id,artist,name,url,fan_size)'
                'VALUES (%(id)s,%(artist)s,%(name)s,%(url)s,%(fan_size)s) ON CONFLICT (id)'
                'DO UPDATE SET (artist,name,url,fan_size)=(%(artist)s,%(name)s,%(url)s,%(fan_size)s)')
            self.ins_fan = ('INSERT INTO fans (id,username,name,url,coll_size)'
                'VALUES (%(id)s,%(username)s,%(name)s,%(url)s,%(coll_size)s) ON CONFLICT (id)'
                'DO UPDATE SET (username,name,url,coll_size)=(%(username)s,%(name)s,%(url)s,%(coll_size)s)')
            self.ins_rel = ('INSERT INTO relationship(album_id,fan_id)'
                'VALUES (%s,%s) ON CONFLICT DO NOTHING')

            con.commit()

        except psycopg2.Error as e:
            if con:
                con.rollback()
            print 'Error %s' % e
            raise


    def process_item(self, item, spider):
        
        if type(item) is AlbumItem:
            try:
                alb ={'id':item['album_id'],'artist':item['artist'],'name':item['name']
                    ,'url':item['url'],'fan_size':len(item['fans'])}
                self.cur.execute(self.ins_album,alb)
                relation = list((item['album_id'],fan_id) for fan_id in item['fans'])
                self.cur.executemany(self.ins_rel,relation)
                self.con.commit()
            except:
                self.con.rollback()
                raise

        if type(item) is FanItem:
            try:
                fan = {'id':item['fan_id'],'username':item['username'],'name':item['name']
                    ,'url':item['url'],'coll_size':len(item['collection'])}
                self.cur.execute(self.ins_fan,fan)
                self.con.commit()
            except:
                self.con.rollback()
                raise

        return item
