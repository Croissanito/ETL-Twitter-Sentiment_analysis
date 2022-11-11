-- DROP TABLE IF EXISTS tweets;

CREATE TABLE IF NOT EXISTS tweets
(
    tweet_id BIGINT NOT NULL,
    tweet_text TEXT NOT NULL,
    like_count INTEGER,
    quote_count INTEGER,
    reply_count INTEGER,
    retweet_count INTEGER,
    sentiment_score REAL,
    created_at TIMESTAMP,
    PRIMARY KEY (tweet_id)
)
