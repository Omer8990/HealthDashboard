#!/bin/bash
echo "🚀 Starting Airflow with proper initialization..."

# Stop existing containers
docker-compose stop airflow-webserver airflow-scheduler 2>/dev/null

# Remove existing containers  
docker-compose rm -f airflow-webserver airflow-scheduler 2>/dev/null

# Initialize database
docker run --rm \
  --network garmin-health-pipeline_default \
  -e AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow \
  -e AIRFLOW__CORE__EXECUTOR=LocalExecutor \
  apache/airflow:2.7.0-python3.9 \
  airflow db migrate

# Create admin user
docker run --rm \
  --network garmin-health-pipeline_default \
  -e AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow \
  -e AIRFLOW__CORE__EXECUTOR=LocalExecutor \
  apache/airflow:2.7.0-python3.9 \
  airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin

echo "✅ Airflow initialized! Starting webserver..."

# Start webserver
docker run -d \
  --name garmin-airflow-webserver \
  --network garmin-health-pipeline_default \
  -p 8080:8080 \
  -e AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow \
  -e AIRFLOW__CORE__EXECUTOR=LocalExecutor \
  -e AIRFLOW__WEBSERVER__EXPOSE_CONFIG=true \
  apache/airflow:2.7.0-python3.9 \
  airflow webserver

echo "🎉 Airflow webserver started! Access at http://localhost:8080"
echo "   Username: admin"  
echo "   Password: admin"