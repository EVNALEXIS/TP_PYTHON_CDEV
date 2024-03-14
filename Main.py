from flask import Flask, g, url_for, render_template, request, redirect, session
from pathlib import Path
import sqlite3

app = Flask(__name__)

app.secret_key = 'S\xcb\t,E\xf2\xd7\x12\x0c\xbfk\x19\xb7\x06\xc1\x9d\xac\xd2z#5h\xcdH'

DATABASE = 'database.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def get_login(usn, pwd):
    cur = get_db().cursor()
    cur.execute(f"SELECT id, username, password FROM users WHERE username LIKE ? AND password LIKE ?", (usn, pwd))
    user = cur.fetchone()
    if user:
        return user
    else:
        return None


def get_all_tasks():
    cur = get_db().cursor()
    cur.execute("SELECT id, title, content, created_by, date_task ,created FROM tasks")
    res = cur.fetchall()
    return res


def get_task_by_day(date):
    cur = get_db().cursor()
    cur.execute("SELECT id, title, content, created_by, date_task ,created FROM tasks where date_task like ?", date)
    res = cur.fetchall()
    return res


def get_task_by_day_and_user(user_id, date):
    cur = get_db().cursor()
    cur.execute(
        "SELECT id, title, content, created_by, date_task ,created FROM tasks where date_task like ? and created_by = ?",
        (date, user_id))
    res = cur.fetchall()
    return res


def get_âll_tasks_by_user(id_user):
    cur = get_db().cursor()
    cur.execute("SELECT id, title, content, created_by, date_task ,created FROM tasks")
    res = cur.fetchall()
    return res


def add_task(name, content, date_task, ):
    cur = get_db().cursor()
    cur.execute("")
    res = cur.fetchone()
    return True


def delete_task():
    return True


def update_task(name):
    return True


@app.route('/', methods=['GET', 'POST'])
def login():
    """
    Gérer l'authentification et afficher la page de login

    :return: la page de login
    """
    if request.method == 'POST':
        print("Méthode POST login")
        username = request.form['username']
        password = request.form['password']
        user = get_login(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            print(session['user_id'], session['username'])
            return redirect(url_for("index"))
        else:
            error_message = "Nom d'utilisateur ou mot de passe incorrect."
            return render_template('login.html', error_message=error_message)

    else:
        return render_template('login.html')


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return render_template('update.html')

    else:
        tasks = get_all_tasks()
        return render_template('index.html', tasks=tasks)


@app.route('/update/', methods=['GET', 'POST'])
def update(id):
    if request.method == 'POST':

        return redirect(url_for('index'))
    else:
        return render_template('update.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for("login"))


if not Path(DATABASE).exists():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

with app.test_request_context():
    print(url_for('index'))
    print(url_for('login'))
