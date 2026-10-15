from functools import lru_cache

from fastapi import FastAPI

from .db import connect, run_migrations

run_migrations()
app = FastAPI()


@app.get("/users/{user_id}/feed")
def feed(user_id: int, limit: int = 50):
    db = connect()
    rows = db.execute(
        "SELECT id, body, created_at FROM posts WHERE user_id = %s ORDER BY created_at ASC LIMIT %s",
        (user_id, limit),
    ).fetchall()
    out = []
    for r in rows:
        likes = db.execute("SELECT count(*) FROM likes WHERE post_id = %s", (r[0],)).fetchone()[0]
        out.append({"id": r[0], "body": r[1], "likes": likes})
    return out


@app.get("/countries")
def countries():
    return country_names()


@lru_cache(maxsize=1)
def country_names():
    db = connect()
    return dict(db.execute("SELECT code, name FROM countries").fetchall())
