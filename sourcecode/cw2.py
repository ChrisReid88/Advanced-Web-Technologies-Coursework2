from flask import Flask, request, redirect, render_template, url_for, session, g
import sqlite3, os, time, bcrypt
from functools import wraps

app = Flask(__name__)

# Getting the absolute file path and setting the database to the file db.db
DB_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(DB_ROOT, 'static', 'db.db')

# Temporarily stored secret key.Needs moved!
app.secret_key = '\xfaHPA\xf9\x9e\xcbF\xec\xc3\t1\xa4-\r56\x1bK9\x15\xb6\xc4('
salt = bcrypt.gensalt()


# Function for getting access to the database
def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = sqlite3.connect(DATABASE)
        g.db = db
    return db


# Decorated function used to automatically close the db connection
# whenever needed
@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# Loads the schema (from console import and call function to reset database)
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('static/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit


# Decorator function that can be applied to any route that requires user to be
# logged in
def requires_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        status = session.get('logged_in', False)
        if not status:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# Login route. Checks if password and username match any in the database. If valid
# set the session username and password and login to True.
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


# Register route. Checks that the username does not exist in the database
# Encrypts the password. Inserts username and password into db and loads the login page.
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    username = []
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = bcrypt.hashpw(request.form['password'].encode('utf8'), salt)
        for row in rows:
            username.append(row[1])
        if new_username in username:
            error = 'Sorry, that username has been taken. Please try another.'
        else:
            insert_new_user(new_username, new_password)
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


# Home/Wall page. Requires login. Calls query functions and stores to lists.
# Carries out actions for each button click. (follow a user and make a post)
@app.route('/', methods=['POST', 'GET'])
@requires_login
def wall():
    id = session['user_id']
    comments = None
    follower_comments = None
    avatar = None
    followers = None
    users = get_users(id)
    own_details = get_own_details(id)

    if get_profile_picture(id):
        avatar = get_profile_picture(id)
    if get_following_comments(id):
        fc = get_following_comments(id)
        follower_comments = remove_dup(fc)
        print follower_comments
    if get_own_comments(id):
        comments = get_own_comments(id)
    if get_followers(id):
        followers = get_followers(id)

    if request.method == 'POST':
        if request.form['submit'] == 'make-comment':
            make_post(id)
            return redirect(url_for('wall'))
        for user in users:
            if request.form['submit'] in user:
                follow(id, request.form['submit'])
                return redirect(url_for('wall'))
    return render_template('wall.html',
                           comments=comments,
                           follower_comments=follower_comments,
                           users=users,
                           avatar=avatar,
                           followers=followers,
                           own_details=own_details)


# Log out
@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


# Profile page of logged in user.
@app.route('/profile', methods=['GET', 'POST'])
def profile():

    id = session['user_id']
    comments = None
    avatar = None
    user = get_own_details(id)

    if get_profile_picture(id):
        avatar = get_profile_picture(id)
    if get_own_comments(session['user_id']):
        comments = get_own_comments(session['user_id'])


    if request.method == 'POST':
        # make a post if the button value is make-comment
        if request.form['submit'] == 'make-comment':
            make_post(id)
            return redirect(url_for('profile'))
        # upload a picture taking from the input file
        elif request.form['submit'] == 'upload-picture':
            basedir = os.path.abspath(os.path.dirname(__file__))
            f = request.files['datafile']
            f.save(os.path.join(basedir, './static/imgs/%s' % f.filename))
            upload_profile_picture(id, f.filename)
            return redirect(url_for('profile'))
        # Edit user details. If none there set to None.
        elif request.form['submit'] == 'edit':
            first_name = request.form.get('first-name', None)
            last_name = request.form.get('last-name', None)
            bio = request.form.get('bio', None)
            update_info(first_name, last_name, bio, id)
            return redirect(url_for('profile'))
        # elif request.form['submit'] == 'delete':
        #     comment = request.form.get('comment-id')
    return render_template('account.html', comments=comments, avatar=avatar, user=user)


# Compares username with usernames in database, and hashed passwords with hashed passwords
# in the database.
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


# Delete a users comments. Not yet working. Need to find a way to retrieve the comment_id.
def delete_comment(user_id, comment_id):
    db = get_db()
    cur = db.cursor()
    with db:
        cur.execute("DELETE FROM comments WHERE user_id=(?) AND comment_id=(?)",(user_id, comment_id))
        db.commit()


# Updates a users profile details
def update_info(first, last, bio, id):
    db = get_db()
    cur = db.cursor()
    with db:
        cur.execute("UPDATE users SET first_name=?,last_name=?,bio=? WHERE user_id =?", (first, last, bio, id))
        db.commit()


# Update the database with the profile picture name
def upload_profile_picture(id, filename):
    db = get_db()
    cur = db.cursor()
    with db:
        cur.execute("UPDATE users SET profile_picture =(?) WHERE user_id = (?)", (filename, id))
        db.commit()


# Insert the users post into the database
def make_post(user_id):
    comment = request.form['comment']
    if comment:
        db = get_db()
        with db:
            cur = db.cursor()
            cur.execute("INSERT INTO comments(user_id, comment) VALUES (?,?)", (user_id, comment))
            db.commit()


# Retrieve the follewed users details, given their username (need to retrieve the user_id to insert
# into the following table). Then insert user id and following id into the table.
def follow(uid, fun):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT user_id FROM USERS WHERE username=(?)", (fun,))
    row = cur.fetchall()
    fid = row[0][0]

    with db:
        cur.execute("INSERT INTO followers(id_user, id_following) VALUES (?,?)", (uid, fid))
        db.commit()


# Retrieve all logged in users comments.
def get_own_comments(uid):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM users INNER JOIN comments on (users.user_id=comments.user_id) WHERE comments.user_id=(?)",
        (uid,))
    rows = cur.fetchall()
    return rows


# Retrieve list of all the follwers. Retrieve all the comments for the users in that list and return it.
# placeholders used to update the query depending on how many users are in the list.
def get_following_comments(uid):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id_following FROM followers WHERE id_user=(?)", (uid,))
    rows = cur.fetchall()
    clist = [r[0] for r in rows]
    placeholder = '?'
    placeholders = ', '.join(placeholder for id in  clist)
    query = "SELECT username, profile_picture, comment FROM users INNER JOIN comments on (users.user_id=comments.user_id) INNER JOIN followers ON\
        (followers.id_following = users.user_id) WHERE comments.user_id IN (%s)" % placeholders
    cur.execute(query, clist)
    rw = cur.fetchall()
    return rw


# For registration. Inserts the username, password and link to the default profile picture.
def insert_new_user(username, password):
    db = get_db()
    cur = db.cursor()
    with db:
        cur.execute("INSERT INTO users(username, password, profile_picture) VALUES (?,?,?)",
                    (username, password, 'default.jpeg'))
        db.commit


# Get all other users to display people may know.
def get_users(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT username, profile_picture, user_id FROM users WHERE user_id NOT IN (?)",(id,))
    rows = cur.fetchall()
    return rows


# Retreive all own details
def get_own_details(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT username, profile_picture, user_id, first_name, last_name, bio \
                    FROM users WHERE user_id=(?)",(id,))
    rows = cur.fetchall()
    return rows


# Return profile picture
def get_profile_picture(uid):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT profile_picture FROM users WHERE user_id=(?)", (uid,))
    rows = cur.fetchall()
    return rows


# Get a list of all the followers
def get_followers(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id_following FROM followers WHERE id_user =(?)", (id,))
    rows = cur.fetchall()
    list = [r[0] for r in rows]
    return list


def remove_dup(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

if __name__ == '__main__':
    app.run(debug=True)
