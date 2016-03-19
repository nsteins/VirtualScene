from flask import render_template
from app import app
from .forms import SearchForm

import psycopg2
import psycopg2.extras

from settings import DATABASE

def connectToDB():
    try:
        return psycopg2.connect(**DATABASE)
    except:
        print("Can't connect to database")



@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=['GET','POST'])

def index():
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("SELECT * FROM albums WHERE name=%s",('Whenever, If Ever',))
        album = cur.fetchone()
    except:
        album = {}
        print('Error Selecting Album')

    query = """SELECT name,artist,url,id,fan_size,COUNT(*) FROM albums
     JOIN relationship ON albums.id = relationship.album_id
     WHERE relationship.fan_id IN (SELECT fan_id FROM relationship
     WHERE album_id IN (SELECT id FROM albums WHERE name=%s))
     GROUP BY name,artist,url,id,fan_size
     ORDER BY COUNT(*) DESC"""

    try:
        cur.execute(query,('Whenever, If Ever',))
        album_recs = cur.fetchall()
    except:
        print('Error Fetching Recommendations')

    form = SearchForm()
    if form.validate_on_submit():
        print form.name.data
        try:
            cur.execute("SELECT * FROM albums WHERE name=%s",(form.name.data,))
            album = cur.fetchone()
        except:
            album = {}
            print('Error Selecting Album')
        try:
            cur.execute(query,(form.name.data,))
            album_recs = cur.fetchall()
        except:
            print('Error Fetching Recommendations')
 
    return render_template('index.html',album=album,album_recs=album_recs[1:10],
        form=form)
