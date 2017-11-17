from flask import Flask, request, redirect, render_template, url_for, session, g
import sqlite3
import os
import time


app = Flask(__name__)
DB_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(DB_ROOT, 'static', 'db.db')
app.secret_key = os.urandom(24)

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = sqlite3.connect(DATABASE)
        g.db = db
    return db

@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('static/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        valid = validate(username, password)

        if not valid:
            error = 'Sorry, the username or password entered is incorrect. Try again.'
        else:
            session['username'] = username
            session['password'] = password
            return redirect(url_for('wall'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']

        if new_username in rows[0]:
            error = 'Sorry, that username has been taken. Please try another.'
        else:
            with db:
                cur.execute("INSERT INTO users(username, password) VALUES (?,?)", (new_username, new_password))
                db.commit
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


def validate(username, password):
    db = get_db()
    valid = False
    with db:
                cur = db.cursor()
                cur.execute("SELECT * FROM users WHERE username=(?)", (username,))
                row = cur.fetchall()
                if row:
                    session['user_id'] = row[0][0]
                    print session['user_id']
                    db_username = row[0][1]
                    db_password = row[0][2]
                    if db_username == username and db_password == password:
                        valid = True
    return valid


@app.route('/wall', methods=['POST', 'GET'])
def wall():
    comments = None
    id = session['user_id']
    print id
    if get_comments(id):
        comments = get_comments(id)
    if request.method == 'POST':
        make_post(id)
        return redirect(url_for('wall'))
    return render_template('wall.html', comments=comments)


def make_post(user_id):
    comment = request.form['comment']
    if comment:
        db = sqlite3.connect(DATABASE)
        with db:
            cur = db.cursor()
            cur.execute("INSERT INTO comments(user_id, comment) VALUES (?,?)", (user_id, comment))
            db.commit()


def get_comments(uid):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users INNER JOIN comments on (users.user_id=comments.user_id) WHERE comments.user_id=(?)", (uid, ))
    rows = cur.fetchall()
    print rows
    return rows


if __name__ == '__main__':
    app.run(debug=True)
