from flask import Flask, request, redirect, render_template, url_for, session
import sqlite3
import os
import time


app = Flask(__name__)
DB_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(DB_ROOT, 'static', 'data.db')
app.secret_key = os.urandom(24)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']

        valid = validate(session['username'], session['password'])
        if not valid:
            error = 'Sorry, the username or password entered is incorrect. Try again.'
        else:
            return redirect(url_for('wall'))
    return render_template('login.html', error=error)


def validate(username, password):
    con = sqlite3.connect(DATABASE)
    valid = False
    with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM Users")
                rows = cur.fetchall()
                for row in rows:
                    db_username = row[0]
                    db_password = row[1]
                    if db_username == username and db_password == password:
                        valid = True
    return valid


@app.route('/wall', methods=['POST', 'GET'])
def wall():
    comments = get_comments()
    print comments
    if request.method == 'POST':
        make_post()
        return redirect(url_for('wall'))
    return render_template('wall.html', comments=comments)


def make_post():
    comment = request.form['comment']
    if comment:
        con = sqlite3.connect(DATABASE)
        with con:
            cur = con.cursor()
            cur.execute("INSERT INTO comments(username, comment,date) VALUES (?,?,?)",(session['username'], comment, time.strftime('%Y-%m-%d %H:%M:%S')))
            con.commit()


def get_comments():
    con = sqlite3.connect(DATABASE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM comments WHERE username=(?)", (session['username'],))
        rows = cur.fetchall()
    return rows



@app.route('/testuser')
def us():
    con = sqlite3.connect(DATABASE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        for row in rows:
            print row
    return 'it worked'

if __name__ == '__main__':
    app.run(debug=True)
