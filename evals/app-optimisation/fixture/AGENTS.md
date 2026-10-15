# Fixture repo
FastAPI app in `api/` over Postgres (`DATABASE_URL`). Run: `uvicorn api.main:app`. Tests: `pytest`.
The mobile client's home screen calls `GET /users/{id}/feed` on every open; `GET /countries` is called once at sign-up.
Typical users have 2,000 posts; a popular post has 50,000 likes. `countries` holds about 250 rows.
