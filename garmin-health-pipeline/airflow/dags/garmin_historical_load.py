"""
Airflow DAG for historical Garmin data loading
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.models import Variable
import sys
import os

# Add extraction module to path
sys.path.append('/opt/airflow/extraction')
from garmin_extractor import GarminDataExtractor, GarminConfig

default_args = {
    'owner': 'longevity-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def extract_historical_data(start_date_str, end_date_str, **context):
    """Extract historical Garmin data for date range"""
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Parse dates
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        
        # Create config and extractor
        config = GarminConfig.from_env()
        extractor = GarminDataExtractor(config)
        
        # Connect to Garmin
        extractor.connect()
        
        # Extract data for date range
        extractor.extract_date_range(start_date, end_date)
        
        logger.info(f"Historical extraction completed: {start_date_str} to {end_date_str}")
        
    except Exception as e:
        logger.error(f"Historical extraction failed: {str(e)}")
        raise

# Create DAG
dag = DAG(
    'garmin_historical_load',
    default_args=default_args,
    description='Load historical Garmin data',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=['garmin', 'historical', 'longevity']
)

# Data quality check
data_quality_check = PostgresOperator(
    task_id='data_quality_check',
    postgres_conn_id='postgres_default',
    sql="""
    SELECT garmin.check_data_quality('staging_activities', '{{ ds }}');
    SELECT garmin.check_data_quality('staging_heart_rate', '{{ ds }}');
    SELECT garmin.check_data_quality('staging_sleep', '{{ ds }}');
    """,
    dag=dag
)

# Extract historical data (configurable date range)
extract_data = PythonOperator(
    task_id='extract_historical_data',
    python_callable=extract_historical_data,
    op_kwargs={
        'start_date_str': '{{ dag_run.conf.get("start_date", "2024-01-01") }}',
        'end_date_str': '{{ dag_run.conf.get("end_date", "2024-01-31") }}'
    },
    dag=dag
)

# Process activities with Spark
process_activities = SparkSubmitOperator(
    task_id='process_activities',
    application='/opt/airflow/spark/jobs/process_activities.py',
    application_args=['{{ dag_run.conf.get("start_date", "2024-01-01") }}', '{{ dag_run.conf.get("end_date", "2024-01-31") }}'],
    conn_id='spark_default',
    dag=dag
)

# Process heart rate data
process_heart_rate = SparkSubmitOperator(
    task_id='process_heart_rate',
    application='/opt/airflow/spark/jobs/process_heart_rate.py',
    application_args=['{{ dag_run.conf.get("start_date", "2024-01-01") }}'],
    conn_id='spark_default',
    dag=dag
)

# Process sleep data
process_sleep = SparkSubmitOperator(
    task_id='process_sleep',
    application='/opt/airflow/spark/jobs/process_sleep.py',
    application_args=['{{ dag_run.conf.get("start_date", "2024-01-01") }}'],
    conn_id='spark_default',
    dag=dag
)

# Aggregate daily metrics
aggregate_metrics = SparkSubmitOperator(
    task_id='aggregate_daily_metrics',
    application='/opt/airflow/spark/jobs/aggregate_metrics.py',
    application_args=['{{ dag_run.conf.get("start_date", "2024-01-01") }}'],
    conn_id='spark_default',
    dag=dag
)

# Refresh materialized views
refresh_views = PostgresOperator(
    task_id='refresh_materialized_views',
    postgres_conn_id='postgres_default',
    sql="SELECT garmin.refresh_materialized_views();",
    dag=dag
)

# Set task dependencies
extract_data >> data_quality_check >> [process_activities, process_heart_rate, process_sleep] >> aggregate_metrics >> refresh_views