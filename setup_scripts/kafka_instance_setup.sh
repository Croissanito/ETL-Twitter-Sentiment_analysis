#!/bin/bash

# Download Kafka, unzip it and change the folder name to 'kafka'
wget https://archive.apache.org/dist/kafka/3.2.1/kafka_2.13-3.2.1.tgz
tar -xzf kafka_2.13-3.2.1.tgz
mv kafka_2.13-3.2.1 kafka

# Install Java 11
sudo amazon-linux-extras install -y java-openjdk11

# Install Python dependencies
pip3 install tweepy
pip3 install kafka-python
pip3 install boto3

# Configure AWS credentials
aws configure set region <INSERT_REGION>
aws configure set aws_access_key_id <INSERT_AWS_ACCESS_KEY_ID>
aws configure set aws_secret_access_key <INSERT_AWS_SECRET_ACCESS_KEY>

# Get the required files from an S3 bucket
aws s3 cp s3://<NAME_OF_YOUR_S3_BUCKET>/ETL/twitter_config.cfg ./twitter_config.cfg
aws s3 cp s3://<NAME_OF_YOUR_S3_BUCKET>/ETL/aws_config.cfg ./aws_config.cfg
aws s3 cp s3://<NAME_OF_YOUR_S3_BUCKET>/ETL/twitter_extraction.py ./twitter_extraction.py