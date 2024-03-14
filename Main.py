from flask import Flask, g, url_for, render_template, request, redirect

import sqlite3

app = Flask(__name__)

DATABASE = '/path/to/database.db'


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


def get_all_tasks():
    conn = get_db()
    tasks = conn.execute("")
    close_connection()
    return tasks


def add_task(name, content, priority):
    conn = get_db()

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
        return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return render_template('index.html')

    else:
        tasks = get_all_tasks()
        return render_template('index.html', tasks=tasks)


@app.route('/update/', methods=['GET', 'POST'])
def update(id):
    if request.method == 'POST':

        return redirect(url_for('index'))
    else:
        return render_template('update.html')


with app.test_request_context():
    print(url_for('index'))
    print(url_for('login'))


def valid_login(usn, pwd):
    return True
