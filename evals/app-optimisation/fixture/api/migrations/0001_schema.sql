CREATE TABLE IF NOT EXISTS posts (id bigserial PRIMARY KEY, user_id bigint NOT NULL, body text NOT NULL, created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS likes (post_id bigint NOT NULL REFERENCES posts(id), user_id bigint NOT NULL);
CREATE TABLE IF NOT EXISTS countries (code char(2) PRIMARY KEY, name text NOT NULL);
CREATE INDEX IF NOT EXISTS posts_user ON posts (user_id);
