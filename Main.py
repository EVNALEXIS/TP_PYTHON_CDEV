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
    cur.execute(
        "SELECT tasks.id, tasks.title, tasks.content, users.username, tasks.date_task ,tasks.created FROM tasks INNER JOIN users ON tasks.created_by = users.id")
    res = cur.fetchall()
    return res


def get_all_users():
    cur = get_db().cursor()
    cur.execute("SELECT id,username FROM users where active = True")
    res = cur.fetchall()
    return res


def get_user_by_usn(usn):
    cur = get_db().cursor()
    cur.execute("SELECT id,username FROM users where active = True and username=?", (usn,))
    res = cur.fetchone()
    return res


def add_user():
    return True


def get_tasks_by_user(user_id):
    cur = get_db().cursor()
    cur.execute(
        "SELECT tasks.id, tasks.title, tasks.content, users.username, tasks.date_task ,tasks.created FROM tasks INNER JOIN users ON tasks.created_by = users.id WHERE created_by = ?",
        (user_id,))
    res = cur.fetchall()
    return res


def get_task_by_id(task_id):
    cur = get_db().cursor()
    cur.execute(
        "SELECT tasks.id, tasks.title, tasks.content, users.username, tasks.date_task ,tasks.created FROM tasks INNER JOIN users ON tasks.created_by = users.id WHERE tasks.id = ?",
        (task_id,))
    res = cur.fetchone()
    return res


def add_task(title, content, date_task, created_by):
    cur = get_db().cursor()
    cur.execute("INSERT INTO tasks (title, content, date_task, created_by) VALUES (?,?,?, ?)",
                (title, content, date_task, created_by))
    get_db().commit()


def update_task(title, content, date_task, created_by, id_task):
    cur = get_db().cursor()
    cur.execute("UPDATE tasks SET title=?, content=?, date_task=?, created_by=? WHERE id=?",
                (title, content, date_task, created_by, id_task))
    get_db().commit()


def delete_task(task_id):
    cur = get_db().cursor()
    cur.execute("DELETE FROM tasks WHERE tasks.id=?",
                (task_id,))
    get_db().commit()


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
    user_id = request.args.get('user_id')
    all_tasks = get_all_tasks()
    all_users = get_all_users()

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        date_task = request.form.get('date')
        add_task(title=title, content=content, date_task=date_task, created_by=session['user_id'])
        return redirect(url_for('index'))
    else:
        if user_id:
            user_id = int(user_id)
            user_tasks = get_tasks_by_user(user_id)
            return render_template('index.html', all_tasks=user_tasks, all_users=all_users,
                                   user_id=user_id)
        else:
            return render_template('index.html', all_tasks=all_tasks, all_users=all_users)


@app.route('/update/<int:task_id>', methods=['GET', 'POST'])
def update(task_id):
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        date = request.form.get('date')
        created_by = get_user_by_usn(request.form.get('username'))['id']
        update_task(title=title, content=content, date_task=date, created_by=created_by, id_task=task_id)
        return redirect(url_for('index'))
    else:
        task = get_task_by_id(task_id)
        return render_template('update.html', task=task)


@app.route('/delete/<int:task_id>')
def delete(task_id):
    delete_task(task_id)
    return redirect(url_for('index'))


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
