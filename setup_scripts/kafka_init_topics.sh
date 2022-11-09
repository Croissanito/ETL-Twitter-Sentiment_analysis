#!/bin/bash
cd /home/$USER/kafka

# Since we are using t2.micro instances, we need
# to reduce the memory usage of Kafka
# We need two terminals, one for each command
KAFKA_HEAP_OPTS="-Xmx32M" bin/zookeeper-server-start.sh config/zookeeper.properties
KAFKA_HEAP_OPTS="-Xmx200M" bin/kafka-server-start.sh config/server.properties

# Create a topic
bin/kafka-topics.sh --create --topic <INSERT_TOPIC_NAME> --bootstrap-server <IP:PORT>