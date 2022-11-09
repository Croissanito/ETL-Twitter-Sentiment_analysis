# Command to submit the job to Spark. Must match both Kafka and Spark versions in the jar dependency.
# /home/$USER/.local/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 twitter_transform_load.py
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, FloatType, LongType, TimestampType, IntegerType, StringType, ArrayType
from pyspark.sql.functions import col, udf, from_json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import psycopg2



spark = SparkSession \
    .builder \
    .appName("TwitterStreamingPipeline") \
    .getOrCreate()

# Connection with Kafka. The values of KAFKA_TOPIC and KAFKA_BOOTSTRAP_SERVER should be
# the same that we input in the extraction script
KAFKA_TOPIC = '<INSERT_TOPIC_NAME>'
KAFKA_BOOTSTRAP_SERVER = '<IP:PORT>'
base_df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVER) \
  .option("subscribe", KAFKA_TOPIC) \
  .option("startingOffsets", "latest") \
  .load()


# The full schema of the tweets
schema = StructType() \
            .add("created_at", TimestampType()) \
            .add("edit_history_tweets", ArrayType(StringType())) \
            .add("id", StringType()) \
            .add("text", StringType()) \
            .add("public_metrics", StructType() \
                .add("like_count", IntegerType())
                .add("quote_count", IntegerType())
                .add("reply_count", IntegerType())
                .add("retweet_count", IntegerType()))


# It's time to define the dataframe where we will perform our transformations
# We drop (don't get) the 'edit_history_tweets' column as it doesn't provide any value
df = base_df \
    .selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", schema=schema).alias("tweet")) \
    .select("tweet.*") \
    .select('created_at', 'id', 'text', 'public_metrics.*')




### Sentiment analysis using vaderSentiment ###
analyzer = SentimentIntensityAnalyzer()
# More compact if using 'udf' decorator
@udf(returnType=FloatType()) 
def apply_sentiment_analysis(sentence):
    score = analyzer.polarity_scores((sentence))['compound']
    return score

df = df.withColumn("sentiment_score", apply_sentiment_analysis(col("text")))



# Enforce the data types of each column for consistency
df = df.withColumn("created_at", df['created_at'].cast(TimestampType()))
df = df.withColumn("id", df['id'].cast(LongType()))
df = df.withColumn("text", df['text'].cast(StringType()))
df = df.withColumn("like_count", df['like_count'].cast(IntegerType()))
df = df.withColumn("quote_count", df['quote_count'].cast(IntegerType()))
df = df.withColumn("reply_count", df['reply_count'].cast(IntegerType()))
df = df.withColumn("retweet_count", df['retweet_count'].cast(IntegerType()))
df = df.withColumn("sentiment_score", df['sentiment_score'].cast(FloatType()))



##### LOAD TO THE DATABASE #####
# Connect to an existing database
# If you get a 'Peer' error, try to use the same user
# for both the database and the OS session
conn = psycopg2.connect(
    dbname='<NAME_OF_THE_DATABASE>',
    user='<NAME_OF_THE_USER>',
    password='<INSERT_THE_PASSWORD>',
    host='<HOST_NAME>',
    port='<PORT>'
)
conn.autocommit=True
# Open a cursor to perform database operations
cur = conn.cursor()


# The function that Spark will apply to each tweet from the stream
# This is the load process per se
def foreach_batch_function(df, epoch_id):
    try:
        for row in df.collect():
            cur.execute(
            """ 
            INSERT INTO tweets
            (
                created_at, 
                tweet_id,
                tweet_text, 
                like_count, 
                quote_count, 
                reply_count,
                retweet_count,
                sentiment_score
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, 
            (
            row['created_at'],
            row['id'],
            row['text'],
            row['like_count'],
            row['quote_count'],
            row['reply_count'],
            row['retweet_count'],
            row['sentiment_score']
            )
        )
    # For whatever reason, Twitter sometimes send duplicated tweets, with the same id
    # Obviously the database doesn't like this, as 'tweet_id' is the primary key
    except psycopg2.errors.UniqueViolation:
        print('Duplicated key, ignoring current dataframe')


# Start streaming
df_write_stream = df \
    .writeStream \
    .foreachBatch(foreach_batch_function) \
    .start()
df_write_stream.awaitTermination()

# Commit the changes and close the connection to Postgres
conn.commit()
conn.close()