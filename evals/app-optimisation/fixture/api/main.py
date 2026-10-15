from functools import lru_cache

from .db import connect, run_migrations

run_migrations()


def feed(user_id, limit=50):
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


@lru_cache(maxsize=1024)
def country_names():
    db = connect()
    return dict(db.execute("SELECT code, name FROM countries").fetchall())
