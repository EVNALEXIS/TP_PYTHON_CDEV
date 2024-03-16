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


def get_connectDB(sql_query, param=None):
    cur = get_db().cursor()
    if param is not None:
        cur.execute(sql_query, param)
    else:
        cur.execute(sql_query)
    return cur


# Le password n'est pas hashé
def get_login(usn, pwd):
    sql_query = ("SELECT users.id, users.username, users.password FROM users WHERE users.active = True AND "
                 "users.username LIKE ? AND users.password LIKE ?")
    params = (usn, pwd)
    user = get_connectDB(sql_query, params).fetchone()
    if user:
        return user
    else:
        return None


def get_all_tasks():
    sql_query = ("SELECT tasks.id, tasks.title, tasks.content, users.username, tasks.date_task ,tasks.created FROM "
                 "tasks INNER JOIN users ON tasks.created_by = users.id")
    cur = get_connectDB(sql_query)
    res = cur.fetchall()
    return res


def get_all_users():
    sql_query = "SELECT users.id,users.username FROM users where users.active = True"
    res = get_connectDB(sql_query).fetchall()
    return res


def get_user_by_usn(usn):
    sql_query = "SELECT users.id,users.username FROM users where users.active = True and users.username=?"
    params = (usn,)
    res = get_connectDB(sql_query, params).fetchone()
    return res


def get_user_by_id(user_id):
    sql_query = "SELECT users.id,users.username FROM users where users.active = True and users.id=?"
    params = (user_id,)
    res = get_connectDB(sql_query, params).fetchone()
    return res


def add_user(username, password):
    sql_query = "INSERT INTO users (username, password) VALUES (?,?)"
    params = (username, password)
    get_connectDB(sql_query, params)
    get_db().commit()


# Que faire des tâches associés aux users desactivés ?
def deactivate_user(user_id):
    sql_query = "UPDATE users SET active = 0 WHERE id = ?"
    params = (user_id,)
    get_connectDB(sql_query, params)
    get_db().commit()


def get_tasks_by_user(user_id):
    sql_query = ("SELECT tasks.id, tasks.title, tasks.content, users.username, tasks.date_task ,tasks.created FROM "
                 "tasks INNER JOIN users ON tasks.created_by = users.id WHERE tasks.created_by = ?")
    params = (user_id,)
    res = get_connectDB(sql_query, params).fetchall()
    return res


def get_task_by_id(task_id):
    sql_query = (
        "SELECT tasks.id, tasks.title, tasks.content, users.username, tasks.date_task ,tasks.created FROM tasks INNER "
        "JOIN users ON tasks.created_by = users.id WHERE tasks.id = ?")
    params = (task_id,)
    res = get_connectDB(sql_query, params).fetchone()
    return res


def add_task(title, content, date_task, created_by):
    sql_query = "INSERT INTO tasks (title, content, date_task, created_by) VALUES (?,?,?, ?)"
    params = (title, content, date_task, created_by)
    get_connectDB(sql_query, params)
    get_db().commit()


def update_task(title, content, date_task, created_by, id_task):
    sql_query = "UPDATE tasks SET title=?, content=?, date_task=?, created_by=? WHERE id=?"
    params = (title, content, date_task, created_by, id_task)
    get_connectDB(sql_query, params)
    get_db().commit()


def delete_task(task_id):
    sql_query = "DELETE FROM tasks WHERE tasks.id=?"
    params = (task_id,)
    get_connectDB(sql_query, params)
    get_db().commit()


@app.route('/', methods=['GET', 'POST'])
def login():
    """
    Gérer l'authentification et afficher la page de login

    :return: la page de login
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_login(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for("index"))
        else:
            error_message = "Nom d'utilisateur ou mot de passe incorrect."
            return render_template('login.html', error_message=error_message)
    else:
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Gère l'inscription
    :return: Si OK, la page de login sinon un message d'erreur
    """
    if request.method == 'POST':
        username = request.form.get('username')
        pwd = request.form.get('password')
        confirmpwd = request.form.get('confirm_password')

        if pwd == confirmpwd:
            add_user(username, pwd)
            return redirect(url_for("login"))
        else:
            error_message = "Veuiller confirmer votre mot de passe"
            return render_template('register.html', error_message=error_message)
    else:
        return render_template('register.html')


@app.route('/logout', methods=['POST'])
def logout():
    """
    Permet de se déconnecter, on détruit la variable de session que l'on initialise à la connection
    :return: la page de connexion
    """
    session.clear()
    return redirect(url_for("login"))


@app.route('/profil/<int:user_id>', methods=['GET'])
def profile(user_id):
    user = get_user_by_id(user_id)
    return render_template('profil.html', user=user)


@app.route('/deleteuser/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    deactivate_user(user_id)
    return redirect(url_for("login"))


@app.route('/index', methods=['GET', 'POST'])
def index():
    """
    Affiche la page d'accueil et l'ajout de tâche
    :return: la page d'accueil
    """
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
    """
    Modifie les données d'une tâche
    :param task_id: identifiant entier unique d'une tâche
    :return: La page de modifcation ou La page d'accueil après modification
    """
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
    """
    Passe le champ activate à False
    :param task_id: identifiant entier unique d'une tâche
    :return: la page d'accueil après la supression de tâche
    """
    delete_task(task_id)
    return redirect(url_for('index'))


"""
Connexion à la db au lancement de l'app et Initialisation de la db si première fois
"""
if not Path(DATABASE).exists():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
