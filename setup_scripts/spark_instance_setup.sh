#!/bin/bash

# Install Java 11
sudo amazon-linux-extras install -y java-openjdk11

# Install Python dependencies
pip3 install pyspark==3.3.0
pip3 install vaderSentiment
pip3 install psycopg2-binary

# Configure AWS credentials
aws configure set region <INSERT_REGION>
aws configure set aws_access_key_id <INSERT_AWS_ACCESS_KEY_ID>
aws configure set aws_secret_access_key <INSERT_AWS_SECRET_ACCESS_KEY>

# Get the required files from an S3 bucket
aws s3 cp s3://<NAME_OF_YOUR_S3_BUCKET>/ETL/twitter_transform_load.py ./twitter_transform_load.py