#!/usr/bin/env python
from flask import Flask, render_template, g, url_for, request
import MySQLdb as mdb

app = Flask(__name__)
app.debug = True

class Movie(object):
    def __init__(self, title, genre, category):
        self.title = title
        self.genre = genre
        self.category = category

class Artist(object):
    def __init__(self, f_name, l_name):
        self.f_name = f_name
        self.l_name = l_name
        self.full_name = f_name + " " + l_name

class Song(object):
    def __init__(self, title, artist, album, category, length):
        self.title = title
        self.artist = artist
        self.album = album
        self.category = category
        self.length = length

class Album(object):
    def __init__(self, title, num_songs, songs):
        self.title = title
        self.num_songs = num_songs
        self.songs = songs

def connect_db():
    return mdb.connect(host="localhost", port=3306, user="testuser",
                    passwd="test123", db="media_db")


@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()



@app.route('/home/')
@app.route('/')
def home():
    return render_template("home.html")

def get_movies():
    batman = Movie("Batman", "action", "movie")
    future = Movie("Back to the Future", "comedy", "movie")
    movies = [batman, future]

    return movies

def get_songs():
    aSong = Song("Dear Prudence","The Beatles","The Beatles","Rock",3.56*60)
    songs = [aSong]
    return songs

def get_artists():
    artists = ['Test1','Tester2','Some Unknown Artist']
    return artists

def get_movie_genres():
    genres = ["action", "adventure", "comedy", "crime", "horror"]
    return genres

@app.route('/videos/')
def videos():
    movies = get_movies()
    genres = get_movie_genres()
    return render_template("videos.html", movies=movies, genres=genres)

@app.route('/music/')
def music():
    artists = get_artists()
    songs = get_songs()
    return render_template("music.html", artists=artists, songs=songs)

@app.route('/add_video', methods=['POST','GET'])
def add_video():
    return "Not yet implemented"

@app.route('/add_music', methods=['POST','GET'])
def add_music():
    return "Not yet implemented"


if __name__ == '__main__':
    app.run()

