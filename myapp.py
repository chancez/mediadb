#!/usr/bin/env python
from flask import Flask, render_template, g, url_for, request
from itertools import groupby
import MySQLdb as mdb
import MySQLdb.cursors

app = Flask(__name__)
app.debug = True

def connect_db():
    return mdb.connect(host="localhost", port=3306, user="testuser",
                    passwd="test123", db="media_db",
                    cursorclass=mdb.cursors.DictCursor)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

def get_movies():
    movies = []
    return movies

def get_songs():
    songs = []
    return songs

def get_actors():
    actors = []
    return actors

def get_movie_genres():
    genres = ["action", "adventure", "comedy", "crime", "horror"]
    return genres


@app.route('/home/')
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/videos/')
def videos():
    movies = get_movies()
    genres = get_movie_genres()
    return render_template("videos.html", movies=movies, genres=genres)

@app.route('/movie/<int:movie_id>')
def get_movie(movie_id):
    movies = get_movies()
    movie = ''

    return render_template("movie.html", movie=movie)

@app.route('/music/')
def music():
    query = """SELECT b.band_id, b.name, b.year_started, b.year_ended, b.website,
               a.artist_id, CONCAT(a.f_name, ' ',a.l_name) as artist
               FROM band_member m
               LEFT JOIN artist a ON m.member = a.artist_id
               LEFT JOIN band b ON m.band = b.band_id
               GROUP BY b.name, artist
               ORDER BY b.band_id, a.artist_id"""

    cur = g.db.cursor()
    cur.execute(query)
    row_bands = cur.fetchall()

    bands = []
    for band, members in groupby(row_bands, lambda row: row['band_id']):
        first = True
        for member in members:
            # First iteration grabs band info
            if first == True:
                aBand = dict(name=member['name'], begin=member['year_started'],
                end=member['year_ended'], website=member['website'], members={})

                if aBand['end'] == 0:
                    aBand['end'] = "Present"
                first = False

            # Add each member to the band's member dict, with their ID as key
            artist = member['artist']
            artist_id = member['artist_id']
            aBand['members'][artist_id] = artist

        bands.append(aBand)

    return render_template("music.html", bands=bands)

@app.route('/artist/<int:a_id>')
def get_artist(a_id):
    return str(a_id)

@app.route('/add_video', methods=['POST','GET'])
def add_video():
    return "Not yet implemented"

@app.route('/add_music', methods=['POST','GET'])
def add_music():
    return "Not yet implemented"


if __name__ == '__main__':
    app.run()

