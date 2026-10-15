import os

import psycopg


def connect():
    return psycopg.connect(os.environ["DATABASE_URL"])


def run_migrations():
    db = connect()
    for name in sorted(os.listdir(os.path.join(os.path.dirname(__file__), "migrations"))):
        db.execute(open(os.path.join(os.path.dirname(__file__), "migrations", name)).read())
    db.commit()
