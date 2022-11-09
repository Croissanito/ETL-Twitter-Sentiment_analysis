# ETL Twitter - Sentiment analysis with Kafka and Spark

*(Currently creating the readme...)*

ETL streaming pipeline that gets tweets, applies sentiment analysis and uploads to Postgres and S3. You can customize it to your own needs, changing which tweets are requested. 

The project is fully deployed on AWS using EC2, S3 and RDS. It was built with scalability in mind as its main priority.

![arquitectura - copia drawio](https://user-images.githubusercontent.com/99673961/200962245-090db4d6-b1e3-428d-81be-9d9d5dbe8bb3.png)

Our tools:
- [Python](https://docs.python.org/3/library/)
- [Bash](https://en.wikipedia.org/wiki/Bash_(Unix_shell))
- [Apache Kafka](https://kafka.apache.org)
- [Apache Spark](https://spark.apache.org)
- [PostgreSQL](https://www.postgresql.org)
- [AWS S3](https://aws.amazon.com/s3)
- [AWS EC2](https://aws.amazon.com/ec2)
- [AWS RDS](https://aws.amazon.com/rds)

## How it works
The project uses two EC2 instances and one RDS instance:
1. **Apache Kafka**. Extract data from Twitter API, upload to S3, parse to a Kafka producer.
2. **Apache Spark**. Consume data from a Kafka producer, apply sentiment analysis, load into PostgreSQL.
3. **PostgreSQL**. Relational database where we will store the output from Spark.
