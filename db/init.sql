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

CREATE TABLE recommendation_engagements (
    id SERIAL PRIMARY KEY,
    user_id INT,
    recommended_user_id INT,
    experiment_variant VARCHAR(50),
    interaction_type VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);