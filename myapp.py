#!/usr/bin/env python
from flask import Flask, render_template, g
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

class Song(object):
    def __init__(self, title, artist, category, length):
        self.title = title
        self.artist = artist
        self.category = category
        self.length = length

def connect_db():
    return mdb.connect(host="localhost", port=3306, user="testuser",
                    passwd="test123", db="media_db")


@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()



@app.route('/')
@app.route('/home/')
def home():
    return render_template("home.html")

def get_movies():
    batman = Movie("Batman", "action", "movie")
    future = Movie("Back to the Future", "comedy", "movie")
    movies = [batman, future]

    return movies

def get_music():
    music = []

    return music

@app.route('/videos/')
def videos():
    movies = get_movies()
    return render_template("videos.html", movies=movies)

@app.route('/music/')
def music():
    return render_template("music.html")


if __name__ == '__main__':
    app.run()

