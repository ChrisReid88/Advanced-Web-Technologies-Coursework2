from flask import Flask, request, redirect, render_template, url_for, session
import sqlite3
import bcrypt
import os


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
                    if db_username == username and db_password==password:
                        valid = True
    return valid


@app.route('/wall', methods=['POST', 'GET'])
def wall():
    if request.method == 'POST':
        # session['comment'] = request.form['comment']
        return redirect(url_for('verse'))
    return render_template('wall.html')


@app.route('/verse', methods=['POST'])
def make_post():
    session['comment'] = request.form['comment']
    if session['comment']:

    return 'it worked {}'.format(session['comment'])


# @app.route('/register')
# def register():
#     render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
