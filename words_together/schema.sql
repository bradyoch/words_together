DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    partner INTEGER UNIQUE,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    FOREIGN KEY (partner) REFERENCES user (id)
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY,
    author_id INTEGER UNIQUE NOT NULL,
    created INTEGER NOT NULL DEFAULT (cast(julianday('now', 'localtime') as INTEGER)),
    body TEXT,
    FOREIGN KEY (author_id) REFERENCES user (id)
);
