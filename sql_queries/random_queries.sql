-- How many tweets are in the database
SELECT COUNT(*) FROM tweets;


-- List the tweets with the highest 'like' count
SELECT tweet_text, like_count FROM tweets ORDER BY like_count DESC LIMIT 10;


-- What's the the average sentiment?
SELECT AVG(sentiment_score) FROM tweets;


-- Tweets with 'some' amount of activity or influence
SELECT * FROM tweets WHERE 
						like_count>0 OR 
						quote_count>0 OR
						reply_count>0 OR
						retweet_count>0


-- Average sentiment and public metrics on October 28
SELECT
	AVG(sentiment_score), 
	SUM(like_count),
	SUM(quote_count),
	SUM(retweet_count),
	SUM(reply_count)
FROM
	tweets
WHERE
	created_at BETWEEN '2022-10-28 0:00' AND '2022-10-28 23:59'
