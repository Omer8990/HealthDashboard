#!/bin/bash
# Download PostgreSQL JDBC driver for Spark
cd /opt/bitnami/spark/jars/
wget -O postgresql-42.6.0.jar https://jdbc.postgresql.org/download/postgresql-42.6.0.jar
chmod 644 postgresql-42.6.0.jar