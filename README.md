# VirtualScene

This project is an album recommendation system for items available on bandcamp.com. The web app is currently running at http://virtualscene.net  If you enter the name of an album from bandcamp, it will display a carousel containing the most popular albums amongst users who own the initial album. You can listen to the albums using the embedded bandcamp player or click through to the appropriate album site and purchase the album through bandcamp. 

The project files consist of two separate parts: 
    a scrapy app that crawls bandcamp.com for album and user data and stores it in a postgres database 
    a flask app that provides a web interface for accessing album info and recommended albums from the postgres database
    

If you wanted to run this site yourself there are several steps you would need to take beyond just 'pip install -r requirements.txt' (which you should obviously do)

  - install and configure postgresql-9.5
  
  - put your postgresql login info into both flask/app/settings.py AND scrapy/bandcamp/settings.py
  
  - run the scrapy spider to populate the database with the info from bandcamp.com (you have to do this slowly so that you don't upset their servers, it will take a long time)
  
  - edit flask/config.py to input your SECRET KEY
  
  - download BxSlider from http://bxslider.com/ and put it in flask/app/static

## Enabling Text Search Using Postgresql
After the database is populated using the scrapy spider, it is necessary to edit the database in order to enable text search of the album and artist names

First, we are going to enable the postgres extension unaccent in order to allow for english keyboard searches of non-standard english names

```postgresql
CREATE EXTENSION unaccent;
```

Next, we create a new column for our table that contains the tsvector for the album name and the artist name. Since the project is focused on albums, we use the `setweight()` function to rank matches to the album name higher than matches to the artist name.

```
ALTER TABLE albums ADD COLUMN tsv tsvector;
UPDATE albums SET tsv = (setweight(to_tsvector('English',unaccent(name)),'A') ||
setweight(to_tsvector('English',unaccent(artist)),'B'));
```

Finally, we use ``gin()`` to create an index to speed up our searches

```
CREATE INDEX tsv_idx ON albums USING gin(tsv);
```

We can now search for album names and order the results by relevance using ts_rank

```
SELECT artist,name FROM albums WHERE tsv @@ to_tsquery('CANCER & MONEY')
ORDER BY ts_rank(tsv,to_tsquery('CANCER & MONEY'));
```

## Deploying on Apache
deployment was tested on a standard Ubuntu AWS EC2 machine

First, install apache and the wsgi mod
```
$ sudo apt-get install apache2
$ sudo apt-get install libapache2-mod-wsgi
$ sudo a2enmod wsgi
```

edit the flask/VirtualScene_example.wsgi file to contain the path to the projects virtualenv and then save it as flask/VirtualScene.wsgi

copy flask/000-default.conf to /etc/apache2/sites-enabled/000-default.conf

link the flask project directory to apache's www folder with

```
$ sudo ln -sT VirtualScene/flask /var/www/html/VirtualScene
```

and finally restart apache with 

```
$ sudo apache2ctl restart
```

and the whole thing should be up and running!
