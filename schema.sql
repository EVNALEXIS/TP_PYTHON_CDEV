DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active BOOL NOT NULL DEFAULT TRUE
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    date_task DATE NOT NULL,
    created_by INTEGER NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id)
);


INSERT INTO users(username, password) VALUES ('admin', 'admin');
INSERT INTO users(username, password) VALUES ('root', 'root');
INSERT INTO tasks (title, content, date_task, created_by) VALUES
    ('Faire les courses', 'Acheter du lait, du pain et des œufs', '2024-03-15', 1),
    ('Préparer le rapport', 'Rédiger le rapport pour la réunion', '2024-03-16', 2),
    ('Nettoyer la maison', 'Passer l''aspirateur et faire la poussière', '2024-03-17', 1);
