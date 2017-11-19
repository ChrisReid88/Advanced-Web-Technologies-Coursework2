from flask import Flask, request, redirect, render_template, url_for, session, g
import sqlite3, os, time, bcrypt
from functools import wraps

app = Flask(__name__)
DB_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(DB_ROOT, 'static', 'db.db')
app.secret_key = os.urandom(24)
salt = bcrypt.gensalt()

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


def requires_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        status = session.get('logged_in', False)
        if not status:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        valid = check_auth(username, password)

        if not valid:
            error = 'Sorry, the username or password entered is incorrect. Try again.'
        else:
            session['username'] = username
            session['password'] = password
            session['logged_in'] = True
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
        new_password = bcrypt.hashpw(request.form['password'].encode('utf8'), salt)
        for row in rows:
            if new_username == row[1]:
                error = 'Sorry, that username has been taken. Please try another.'
            else:
                insert_new_user(new_username, new_password)
                return redirect(url_for('login'))
    return render_template('register.html', error=error)


def check_auth(username, password):
    db = get_db()
    valid = False
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE username=(?)", (username,))
        row = cur.fetchall()
        if row:
            session['user_id'] = row[0][0]
            db_username = row[0][1]
            db_password = row[0][2]
            if db_username == username and db_password == bcrypt.hashpw(password.encode('utf8'), db_password.encode('utf8')):

                valid = True

    return valid


@app.route('/', methods=['POST', 'GET'])
@requires_login
def wall():

    id = session['user_id']
    comments = None
    follower_comments = None
    avatar = None
    users = get_users(id)
    if get_profile_picture(id):
        avatar = get_profile_picture(id)
    if get_following_comments(id):
        follower_comments = get_following_comments(id)
        print follower_comments
    if get_own_comments(id):
        comments = get_own_comments(id)

    if request.method == 'POST':
        if request.form['submit'] == 'make-comment':
            make_post(id)
            return redirect(url_for('wall'))
        for user in users:
            if request.form['submit'] in user:
                follow(id, request.form['submit'])
                return redirect(url_for('wall'))

    return render_template('wall.html', comments=comments, follower_comments=follower_comments, users=users, avatar=avatar)


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET','POST'])
def profile():

    id = session['user_id']
    comments = None
    avatar = None

    if get_profile_picture(id):
        avatar = get_profile_picture(id)
    if get_own_comments(session['user_id']):
        comments = get_own_comments(session['user_id'])
    if request.method == 'POST':
        if request.form['submit'] == 'make-comment':
            make_post(id)
            return redirect(url_for('profile'))

    return render_template('account.html', comments=comments, avatar=avatar)


def make_post(user_id):
    comment = request.form['comment']
    if comment:
        db = get_db()
        with db:
            cur = db.cursor()
            cur.execute("INSERT INTO comments(user_id, comment) VALUES (?,?)", (user_id, comment))
            db.commit()


def follow(uid, fun):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT user_id FROM USERS WHERE username=(?)", (fun,))
    row = cur.fetchall()
    fid = row[0][0]

    with db:
        cur.execute("INSERT INTO followers(id_user, id_following) VALUES (?,?)", (uid, fid))
        db.commit()


def get_own_comments(uid):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM users INNER JOIN comments on (users.user_id=comments.user_id) WHERE comments.user_id=(?)",
        (uid,))
    rows = cur.fetchall()
    return rows


def get_following_comments(uid):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id_following FROM followers WHERE id_user=(?)", (uid,))
    rows = cur.fetchall()
    list = [r[0] for r in rows]
    placeholder = '?'
    placeholders = ', '.join(placeholder for id in list)
    query = "SELECT * FROM users INNER JOIN comments on (users.user_id=comments.user_id) INNER JOIN followers ON (followers.id_following = users.user_id) WHERE comments.user_id IN (%s)" % placeholders
    cur.execute(query, list)
    rw = cur.fetchall()
    return rw
    # return comment_list


def insert_new_user(username, password):
    db = get_db()
    cur = db.cursor()
    with db:
        cur.execute("INSERT INTO users(username, password, profile_picture) VALUES (?,?,?)",
                    (username, password, 'default.jpeg'))
        db.commit


def get_users(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT username, profile_picture FROM users WHERE user_id NOT IN (?)",(id,))
    rows = cur.fetchall()
    return rows


def get_profile_picture(uid):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT profile_picture FROM users WHERE user_id=(?)", (uid,))
    rows = cur.fetchall()
    return rows

# def is_following():
#

if __name__ == '__main__':
    app.run(debug=True)
