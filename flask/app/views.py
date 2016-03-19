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
    form = SearchForm()
    return render_template('index.html',form=form)


@app.route('/search',methods=['GET','POST'])
def search():
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    search_query = """SELECT * FROM albums WHERE (tsv @@ to_tsquery(%s))
                      ORDER BY ts_rank(tsv,to_tsquery(%s))"""

    search_results = {};
    form = SearchForm()
    if form.validate_on_submit():
        print form.name.data
        try:
            ts_str = ' & '.join(form.name.data.split())
            cur.execute(search_query,(ts_str,ts_str))
            search_results = cur.fetchall()
        except:
            album = {}
            print('Error Searching Album')

    return render_template('search.html',search_results = search_results,form=form)

@app.route('/rec/<album_id>',methods=['GET'])
def rec(album_id):

    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """SELECT name,artist,url,id,fan_size,COUNT(*) FROM albums
     JOIN relationship ON albums.id = relationship.album_id
     WHERE relationship.fan_id IN (SELECT fan_id FROM relationship
     WHERE album_id = %s)
     GROUP BY name,artist,url,id,fan_size
     ORDER BY COUNT(*) DESC"""

    album_recs = {}

    try:
        cur.execute(query,(album_id,))
        album_recs = cur.fetchall()
    except:
        print('Error fetching rec')
    
    form = SearchForm()

    if album_recs == []:
        return (render_template('error.html',form=form))
    if (len(album_recs) > 10) :
        return render_template('rec.html',album = album_recs[1],album_recs=album_recs[2:10],form=form)
    else:
        return render_template('rec.html',album = album_recs[1],album_recs=album_recs[2:],form=form)
