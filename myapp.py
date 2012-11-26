#!/usr/bin/env python
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify, json
from itertools import groupby
import MySQLdb as mdb
import MySQLdb.cursors

DEBUG=True
SECRET_KEY = 'development key'

app = Flask(__name__)
app.config.from_object(__name__)

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

def get_band(band_id):
    query = """SELECT band_id as id, name, year_started AS begin,
               year_ended AS end, website
               FROM band WHERE band_id = %s"""

    cursor = g.db.cursor()
    cursor.execute(query, band_id)
    band = cursor.fetchone()

    return band

def get_bands():
    band_query = """SELECT b.band_id, b.name, b.year_started, b.year_ended,
                    b.website
                    FROM band b
                    GROUP BY b.name
                    ORDER BY b.name"""

    #grab all bands
    cursor = g.db.cursor()
    cursor.execute(band_query)

    row_bands = cursor.fetchall()

    bands = []
    for band in row_bands:
        aBand = dict(id=band['band_id'], name=band['name'],
        begin=band['year_started'], end=band['year_ended'],
        website=band['website'],
        members=[], albums=[], labels=[], genres=[])

        # If 0, then band is currently active
        if aBand['end'] == 0:
            aBand['end'] = "Present"

        # Grab band members for band
        aBand['members'] = get_members(aBand['id'])
        aBand['albums'] = get_band_albums(aBand['id'])

        for album in aBand['albums']:
            # Add genres and labels to band, if not already added
            genre = album['genre']
            label = album['label']
            if genre not in aBand['genres']:
                aBand['genres'].append(genre)
            if label not in aBand['labels']:
                aBand['labels'].append(label)

        # Add band to list of bandj
        bands.append(aBand)

    return bands

def get_members(band_id):
    member_query = """SELECT CONCAT(f_name, ' ', l_name) as name, a.artist_id
                      FROM artist a
                      INNER JOIN band_member bm ON bm.member = a.artist_id
                      WHERE bm.band = %s"""

    cursor = g.db.cursor()
    cursor.execute(member_query, band_id)
    row_members = cursor.fetchall()

    members = []
    for member in row_members:
        a_name = member['name']
        a_id = member['artist_id']
        aMember = dict(id=a_id, name=a_name)
        members.append(aMember)

    return members

def get_band_albums(band_id):
    album_query = """SELECT a.album_id, a.name, a.record_label, a.genre,
                     a.release_date
                     FROM band_album ba
                     LEFT JOIN album a ON a.album_id=ba.album
                     WHERE ba.band = %s
                     ORDER BY release_date"""

    # Grab albums for the band
    cursor = g.db.cursor()
    cursor.execute(album_query, band_id)
    row_albums = cursor.fetchall()

    albums = []
    for album in row_albums:
        anAlbum = dict(id=album['album_id'], name=album['name'],
            label=album['record_label'], genre=album['genre'],
            release=album['release_date'])

        anAlbum['songs'] = get_album_songs(anAlbum['id'])

        albums.append(anAlbum)

    return albums

@app.route("/band/albums")
def band_albums():
    album_query = """SELECT a.album_id, a.name
                     FROM band_album ba
                     LEFT JOIN album a ON a.album_id=ba.album
                     WHERE ba.band = %s
                     ORDER BY a.name"""

    band = request.args.get('band_id', 0, type=int)
    if band:
        cursor = g.db.cursor()
        cursor.execute(album_query, band)
        row_albums = cursor.fetchall()

        albums = []
        for album in row_albums:
            albums.append(dict(id=album['album_id'], name=album['name']))

        return jsonify(albums=albums)

def get_artist(artist_id):
    query = """SELECT CONCAT(a.f_name, ' ', a.l_name) as name, artist_id as id
                FROM artist a
                WHERE a.artist_id = %s"""

    cursor = g.db.cursor()
    cursor.execute(query, artist_id)
    artist = cursor.fetch()

    return artist

def get_artists():
    query = """SELECT CONCAT(a.f_name, ' ',a.l_name) as name, a.artist_id AS id
               FROM artist a ORDER BY name"""

    cursor = g.db.cursor()
    cursor.execute(query)
    artists = cursor.fetchall()

    return artists

def get_album_songs(album_id):
    album_song = """SELECT s.song_id, s.name, s.length, alb.track_num
                    FROM album_song alb
                    LEFT JOIN song s ON s.song_id=alb.song
                    WHERE alb.album=%s
                    ORDER BY alb.track_num"""

    cursor = g.db.cursor()
    cursor.execute(album_song, album_id)
    row_songs = cursor.fetchall()

    songs = []
    for song in row_songs:
        aSong = dict(id=song['song_id'], name=song['name'],
            length=song['length'], track_num=song['track_num'])

        songs.append(aSong)

    return songs

def get_album(album_id):
    album_query = """SELECT a.album_id, a.name, a.record_label, a.genre,
                     a.release_date, b.name as band, b.band_id
                     FROM band_album ba
                     LEFT JOIN album a ON a.album_id=ba.album
                     LEFT JOIN band b on b.band_id=ba.band
                     WHERE ba.album = %s"""

    # Grab albums for the band
    cursor = g.db.cursor()
    cursor.execute(album_query, album_id)
    album_result = cursor.fetchone()

    album = dict(id=album_result['album_id'], name=album_result['name'],
        label=album_result['record_label'], genre=album_result['genre'],
        release=album_result['release_date'], band=album_result['band'],
        band_id=album_result['band_id'])

    album['songs'] = get_album_songs(album_id)

    return album

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
    # Gather template data
    bands = get_bands()
    artists = get_artists()

    return render_template("music.html", bands=bands, artists=artists)

@app.route('/create/band', methods=['POST','GET'])
def create_band():
    name = request.form['band_name']
    started = request.form['year_started']
    ended = request.form['year_ended']
    website = request.form['band_website']

    query = """INSERT INTO band(name, year_started, year_ended, website)
               VALUES (%s, %s, %s, %s)"""

    try:
        cur = g.db.cursor()
        cur.execute(query, (name, started, ended, website))
        g.db.commit()
    except mdb.Error, e:
        print "An error has occurred. %s" % e
        message = 'Error attempting to add band "%s"' % name
        msg_type = 'error'
    else:
        message = 'Successfully added band "%s"' % name
        msg_type = 'success'

    flash(message, msg_type)
    return redirect(url_for('music'))

@app.route('/create/album', methods=['POST', 'GET'])
def create_album():
    # Check if any values are empty.
    errors = False
    for key, value in request.form.iteritems():
        if value == '':
            errors = True
            if key == "band":
                err_message = 'Error, must select an existing band!'
            else:
                err_message = 'Error, %s cannot be empty.' % key
            flash(err_message, "error")

    #if title in get_band_albums():
    #    errors = True
    #    err_message = 'Error, album "%s" already exists for band "%s"'
    #    flash(err_message % (title, band), 'error')

    if not errors:
        # Still needs error checking for if album exists. However albums are on
        # their own table. Making checking harder. May want to adjust schema.
        album_query = """INSERT INTO album(name, release_date, record_label, genre)
                   VALUES (%s, %s, %s, %s)"""

        band_album_query = """INSERT INTO band_album(band, album)
                              SELECT %s, LAST_INSERT_ID()"""

        cur = g.db.cursor()
        band = request.form['band']
        band = get_band(band)
        title = request.form['title']
        genre = request.form['genre']
        label = request.form['label']
        release = request.form['release']

        try:
            cur.execute(album_query, (title, release, label, genre))
            cur.execute(band_album_query, band['id'])
            g.db.commit()
        except mdb.Error, e:
            print "An error has occurred. %s" % e
            message = 'Error attempting to add album "%s" to band "%s"' % \
            (title, band['name'])
            msg_type = 'error'
        else:
            message = 'Successfully added album "%s" for band "%s"' % \
            (title, band['name'])
            msg_type = 'success'

        flash(message, msg_type)

    return redirect(url_for('music'))

@app.route('/create/artist', methods=['POST', 'GET'])
def create_artist():
    errors = False
    for key, value in request.form.iteritems():
        if value == '':
            errors = True
            err_message = 'Error, must enter %s name.' % key
            flash(err_message, "error")

    if not errors:
        artist_query = """INSERT INTO artist(f_name, l_name)
                          VALUES (%s, %s)"""

        cur = g.db.cursor()
        first = request.form['first']
        last = request.form['last']
        artist = (first, last)

        try:
            cur.execute(artist_query, artist)
            g.db.commit()
        except mdb.Error, e:
            print "An error has occurred. %s" % e
            message = 'Error attempting to add artist "%s %s"' % artist
            msg_type = 'error'
        else:
            message = 'Successfully added artist "%s %s"' % artist
            msg_type = 'success'

        flash(message, msg_type)

    return redirect(url_for('music'))

@app.route('/create/song', methods=['POST', 'GET'])
def create_song():
    errors = False
    for key, value in request.form.iteritems():
        if value == '':
            errors = True
            err_message = 'Error, "%s" cannot be empty!' % key
            flash(err_message, "error")

    if not errors:
        song_query = """INSERT INTO song(name, length)
                        VALUES (%s, %s)"""
        song_album_query = """INSERT INTO album_song(album, song, track_num)
                              SELECT %s, LAST_INSERT_ID(), %s"""

        cursor = g.db.cursor()
        song = request.form['song']
        album = request.form['album']
        album = get_album(album)
        length = request.form['length']
        number = request.form['track_num']

        try:
            cursor.execute(song_query, (song, length))
            cursor.execute(song_album_query, (album['id'], number))
            g.db.commit()
        except mdb.Error, e:
            print "An error has occurred. %s" % e
            message = 'Error attempting to add song "%s" to album "%s"' % \
            (song, album['name'])
            msg_type = 'error'
        else:
            message = 'Successfully added song "%s" to album "%s"' % \
            (song, album['name'])
            msg_type = 'success'

        flash(message, msg_type)

    return redirect(url_for('music'))

@app.route('/add/artist', methods=['POST', 'GET'])
def add_artist():
    err_message = "Error, %s required"
    error = False

    b_id = request.form['band']
    a_id = request.form['artist']
    if b_id == '':
        error = True
        flash(err_message % "Band", "error")
    if a_id == '':
        error = True
        flash(err_message % "Artist", "error")

    if not error:
        cur = g.db.cursor()

        band = get_band(b_id)
        artist = get_artist(a_id)

        query = """INSERT INTO band_member(band, member) VALUES (%s, %s)"""

        try:
            cur.execute(query, (band['id'], artist['id']))
            g.db.commit()
        except mdb.Error, e:
            print "An error has occurred. %s" % e
                #1062
            message = 'Error attempting to add artist "%s" to band "%s"' % \
                (artist['name'], band['name'])
            msg_type = 'error'
        else:
            message = 'Successfully added artist "%s" to band "%s"' % \
                (artist['name'], band['name'])
            msg_type = 'success'

    flash(message, msg_type)

    return redirect(url_for('music'))


@app.route('/artist/<int:a_id>')
def artist(a_id):
    return str(a_id)

@app.route('/band/<int:b_id>')
def band(b_id):
    band = get_band(b_id)
    albums = get_band_albums(b_id)
    return render_template("band.html", band=band, albums=albums)

@app.route('/album/<int:alb_id>')
def album(alb_id):
    album = get_album(alb_id)
    return render_template("album.html", album=album)

if __name__ == '__main__':
    app.run()

