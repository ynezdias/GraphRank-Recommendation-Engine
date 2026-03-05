CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT
);

CREATE TABLE connections (
    user_a INT,
    user_b INT
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INT,
    content TEXT,
    created_at TIMESTAMP
);

CREATE TABLE interactions (
    user_id INT,
    post_id INT,
    type TEXT,
    created_at TIMESTAMP
);

CREATE TABLE influence_scores (
    user_id INT,
    score FLOAT
);