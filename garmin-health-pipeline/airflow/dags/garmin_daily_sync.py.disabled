# airflow/dags/garmin_daily_sync.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup
from airflow.utils.dates import days_ago
from airflow.sensors.external_task import ExternalTaskSensor
import sys
import os

# Add extraction module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../extraction'))
from garmin_extractor import GarminDataExtractor, GarminConfig

# Default arguments for the DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['admin@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'garmin_daily_sync',
    default_args=default_args,
    description='Daily sync of Garmin health data',
    schedule_interval='0 6 * * *',  # Run daily at 6 AM
    catchup=False,
    max_active_runs=1,
    tags=['garmin', 'health', 'daily'],
)

def extract_garmin_data(**context):
    """Extract data from Garmin Connect"""
    execution_date = context['execution_date']
    
    # Get configuration from Airflow Variables
    config = GarminConfig(
        email=Variable.get("garmin_email"),
        password=Variable.get("garmin_password"),
        db_connection_string=Variable.get("database_url"),
        data_retention_days=int(Variable.get("data_retention_days", 365))
    )
    
    # Initialize extractor
    extractor = GarminDataExtractor(config)
    extractor.connect()
    
    # Extract data for yesterday (most recent complete day)
    target_date = execution_date - timedelta(days=1)
    extractor.extract_full_day(target_date)
    
    return target_date.strftime("%Y-%m-%d")

def check_data_quality(**context):
    """Check data quality after extraction"""
    date = context['task_instance'].xcom_pull(task_ids='extract_data')
    
    hook = PostgresHook(postgres_conn_id='garmin_postgres')
    
    # Check if data was extracted for all key tables
    tables = ['staging_activities', 'staging_heart_rate', 'staging_sleep', 
              'staging_stress', 'staging_daily_summary']
    
    quality_issues = []
    for table in tables:
        result = hook.get_first(
            f"SELECT COUNT(*) FROM garmin.{table} WHERE DATE(extracted_at) = '{date}'"
        )
        if result[0] == 0:
            quality_issues.append(f"No data in {table}")
    
    if quality_issues:
        raise ValueError(f"Data quality issues: {', '.join(quality_issues)}")
    
    return True

def cleanup_old_staging_data(**context):
    """Clean up old staging data"""
    retention_days = int(Variable.get("staging_retention_days", 7))
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    hook = PostgresHook(postgres_conn_id='garmin_postgres')
    
    tables = ['staging_activities', 'staging_heart_rate', 'staging_sleep', 
              'staging_stress', 'staging_body_composition', 'staging_daily_summary']
    
    for table in tables:
        hook.run(
            f"DELETE FROM garmin.{table} WHERE extracted_at < '{cutoff_date}'"
        )

# Task definitions
with dag:
    # Extract data from Garmin
    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_garmin_data,
        provide_context=True,
    )
    
    # Data quality check
    quality_check = PythonOperator(
        task_id='data_quality_check',
        python_callable=check_data_quality,
        provide_context=True,
    )
    
    # Process activities with Spark
    with TaskGroup("spark_processing") as spark_group:
        process_activities = SparkSubmitOperator(
            task_id='process_activities',
            application='/opt/airflow/spark/jobs/process_activities.py',
            conn_id='spark_default',
            conf={
                'spark.executor.memory': '2g',
                'spark.executor.cores': '2',
                'spark.driver.memory': '2g'
            },
            application_args=['{{ ti.xcom_pull(task_ids="extract_data") }}'],
            dag=dag,
        )
        
        aggregate_metrics = SparkSubmitOperator(
            task_id='aggregate_daily_metrics',
            application='/opt/airflow/spark/jobs/aggregate_metrics.py',
            conn_id='spark_default',
            conf={
                'spark.executor.memory': '2g',
                'spark.executor.cores': '2',
                'spark.driver.memory': '2g'
            },
            application_args=['{{ ti.xcom_pull(task_ids="extract_data") }}'],
            dag=dag,
        )
    
    # Update materialized views
    refresh_views = PostgresOperator(
        task_id='refresh_materialized_views',
        postgres_conn_id='garmin_postgres',
        sql="SELECT garmin.refresh_materialized_views();",
    )
    
    # Calculate weekly metrics (only on Sundays)
    calculate_weekly = PostgresOperator(
        task_id='calculate_weekly_metrics',
        postgres_conn_id='garmin_postgres',
        sql="""
        INSERT INTO garmin.weekly_metrics (
            week_start, week_end, total_activities, total_distance_km,
            total_duration_hours, total_calories, avg_sleep_hours,
            avg_sleep_score, avg_resting_hr, avg_stress_level,
            total_steps, avg_daily_steps
        )
        SELECT 
            DATE_TRUNC('week', CURRENT_DATE - INTERVAL '1 day') as week_start,
            DATE_TRUNC('week', CURRENT_DATE - INTERVAL '1 day') + INTERVAL '6 days' as week_end,
            COUNT(DISTINCT a.activity_id) as total_activities,
            SUM(a.distance_km) as total_distance_km,
            SUM(a.duration_minutes) / 60 as total_duration_hours,
            SUM(a.calories) as total_calories,
            AVG(dm.sleep_duration_hours) as avg_sleep_hours,
            AVG(dm.sleep_score) as avg_sleep_score,
            AVG(dm.resting_heart_rate) as avg_resting_hr,
            AVG(dm.avg_stress_level) as avg_stress_level,
            SUM(dm.total_steps) as total_steps,
            AVG(dm.total_steps) as avg_daily_steps
        FROM garmin.daily_metrics dm
        LEFT JOIN garmin.activities a ON DATE(a.start_time) = dm.date
        WHERE dm.date >= DATE_TRUNC('week', CURRENT_DATE - INTERVAL '1 day')
            AND dm.date < DATE_TRUNC('week', CURRENT_DATE - INTERVAL '1 day') + INTERVAL '7 days'
        GROUP BY week_start, week_end
        ON CONFLICT (week_start) DO UPDATE SET
            total_activities = EXCLUDED.total_activities,
            total_distance_km = EXCLUDED.total_distance_km,
            updated_at = CURRENT_TIMESTAMP;
        """,
        trigger_rule='none_failed_or_skipped',
    )
    
    # Cleanup old staging data
    cleanup_staging = PythonOperator(
        task_id='cleanup_staging',
        python_callable=cleanup_old_staging_data,
        provide_context=True,
        trigger_rule='none_failed',
    )
    
    # Define task dependencies
    extract_task >> quality_check >> spark_group >> refresh_views >> calculate_weekly >> cleanup_staging

# airflow/dags/garmin_historical_load.py
"""
DAG for loading historical Garmin data
This DAG is triggered manually for initial data load or backfilling
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.models import Variable
from airflow.models.param import Param
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../extraction'))
from garmin_extractor import GarminDataExtractor, GarminConfig

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email': ['admin@example.com'],
    'email_on_failure': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

dag = DAG(
    'garmin_historical_load',
    default_args=default_args,
    description='Load historical Garmin data',
    schedule_interval=None,  # Manual trigger only
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['garmin', 'historical', 'backfill'],
    params={
        "start_date": Param(
            default=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            type='string',
            description='Start date for historical load (YYYY-MM-DD)'
        ),
        "end_date": Param(
            default=datetime.now().strftime("%Y-%m-%d"),
            type='string',
            description='End date for historical load (YYYY-MM-DD)'
        ),
        "batch_size": Param(
            default=7,
            type='integer',
            description='Number of days to process in each batch'
        ),
    },
)

def load_historical_batch(**context):
    """Load a batch of historical data"""
    params = context['params']
    start_date = datetime.strptime(params['start_date'], "%Y-%m-%d")
    end_date = datetime.strptime(params['end_date'], "%Y-%m-%d")
    batch_size = params['batch_size']
    
    # Get configuration
    config = GarminConfig(
        email=Variable.get("garmin_email"),
        password=Variable.get("garmin_password"),
        db_connection_string=Variable.get("database_url"),
        data_retention_days=365
    )
    
    # Initialize extractor
    extractor = GarminDataExtractor(config)
    extractor.connect()
    
    # Process in batches
    current_date = start_date
    while current_date <= end_date:
        batch_end = min(current_date + timedelta(days=batch_size - 1), end_date)
        
        print(f"Processing batch: {current_date} to {batch_end}")
        extractor.extract_date_range(current_date, batch_end)
        
        # Process the extracted data with Spark
        # This would trigger the Spark jobs for each day in the batch
        
        current_date = batch_end + timedelta(days=1)
    
    return {
        'start_date': start_date.strftime("%Y-%m-%d"),
        'end_date': end_date.strftime("%Y-%m-%d"),
        'records_processed': (end_date - start_date).days + 1
    }

def validate_historical_load(**context):
    """Validate the historical load completed successfully"""
    result = context['task_instance'].xcom_pull(task_ids='load_historical_data')
    
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    hook = PostgresHook(postgres_conn_id='garmin_postgres')
    
    # Check record counts
    count = hook.get_first(
        f"""
        SELECT COUNT(DISTINCT date) 
        FROM garmin.daily_metrics 
        WHERE date BETWEEN '{result['start_date']}' AND '{result['end_date']}'
        """
    )[0]
    
    expected = result['records_processed']
    if count < expected * 0.8:  # Allow for some missing days
        raise ValueError(f"Expected ~{expected} days, but only found {count}")
    
    print(f"Historical load validated: {count} days loaded")
    return True

with dag:
    # Load historical data
    load_task = PythonOperator(
        task_id='load_historical_data',
        python_callable=load_historical_batch,
        provide_context=True,
    )
    
    # Validate the load
    validate_task = PythonOperator(
        task_id='validate_load',
        python_callable=validate_historical_load,
        provide_context=True,
    )
    
    # Recalculate all aggregations
    recalculate_aggregations = PostgresOperator(
        task_id='recalculate_aggregations',
        postgres_conn_id='garmin_postgres',
        sql="""
        -- Recalculate weekly metrics
        DELETE FROM garmin.weekly_metrics 
        WHERE week_start >= '{{ params.start_date }}'::date;
        
        INSERT INTO garmin.weekly_metrics (
            week_start, week_end, total_activities, total_distance_km,
            total_duration_hours, total_calories
        )
        SELECT 
            DATE_TRUNC('week', date) as week_start,
            DATE_TRUNC('week', date) + INTERVAL '6 days' as week_end,
            COUNT(DISTINCT a.activity_id),
            SUM(a.distance_km),
            SUM(a.duration_minutes) / 60,
            SUM(a.calories)
        FROM garmin.daily_metrics dm
        LEFT JOIN garmin.activities a ON DATE(a.start_time) = dm.date
        WHERE dm.date >= '{{ params.start_date }}'::date
        GROUP BY DATE_TRUNC('week', date);
        
        -- Refresh materialized views
        SELECT garmin.refresh_materialized_views();
        """,
    )
    
    load_task >> validate_task >> recalculate_aggregations

# airflow/plugins/garmin_operators.py
"""
Custom Airflow operators for Garmin data pipeline
"""

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

class GarminExtractOperator(BaseOperator):
    """
    Custom operator for extracting Garmin data
    """
    template_fields = ['target_date']
    
    @apply_defaults
    def __init__(
        self,
        target_date: str,
        data_types: list = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.target_date = target_date
        self.data_types = data_types or [
            'activities', 'heart_rate', 'sleep', 
            'stress', 'body_composition', 'daily_summary'
        ]
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the extraction"""
        from garmin_extractor import GarminDataExtractor, GarminConfig
        from airflow.models import Variable
        from datetime import datetime
        
        # Get configuration
        config = GarminConfig(
            email=Variable.get("garmin_email"),
            password=Variable.get("garmin_password"),
            db_connection_string=Variable.get("database_url")
        )
        
        # Initialize and connect
        extractor = GarminDataExtractor(config)
        extractor.connect()
        
        # Parse target date
        target_date = datetime.strptime(self.target_date, "%Y-%m-%d")
        
        # Extract specified data types
        results = {}
        for data_type in self.data_types:
            logger.info(f"Extracting {data_type} for {self.target_date}")
            
            if data_type == 'activities':
                data = extractor.extract_activities(target_date, target_date)
                if data:
                    extractor.save_to_staging(data, 'activities')
                    results['activities'] = len(data)
            elif data_type == 'heart_rate':
                data = extractor.extract_heart_rate(target_date)
                if data:
                    extractor.save_to_staging([data], 'heart_rate')
                    results['heart_rate'] = 1
            elif data_type == 'sleep':
                data = extractor.extract_sleep(target_date)
                if data:
                    extractor.save_to_staging([data], 'sleep')
                    results['sleep'] = 1
            elif data_type == 'stress':
                data = extractor.extract_stress(target_date)
                if data:
                    extractor.save_to_staging([data], 'stress')
                    results['stress'] = 1
            elif data_type == 'body_composition':
                data = extractor.extract_body_composition(target_date)
                if data:
                    extractor.save_to_staging([data], 'body_composition')
                    results['body_composition'] = 1
            elif data_type == 'daily_summary':
                data = extractor.extract_daily_summary(target_date)
                if data:
                    extractor.save_to_staging([data], 'daily_summary')
                    results['daily_summary'] = 1
        
        return results

class DataQualityOperator(BaseOperator):
    """
    Operator for checking data quality
    """
    
    @apply_defaults
    def __init__(
        self,
        table_name: str,
        date_column: str = 'date',
        checks: Dict[str, Any] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.table_name = table_name
        self.date_column = date_column
        self.checks = checks or {}
    
    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute data quality checks"""
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        
        hook = PostgresHook(postgres_conn_id='garmin_postgres')
        
        # Run quality checks
        issues = []
        
        # Check for nulls in critical columns
        if 'null_checks' in self.checks:
            for column in self.checks['null_checks']:
                result = hook.get_first(
                    f"""
                    SELECT COUNT(*) 
                    FROM garmin.{self.table_name} 
                    WHERE {column} IS NULL
                    """
                )
                if result[0] > 0:
                    issues.append(f"{result[0]} null values in {column}")
        
        # Check for duplicates
        if 'unique_checks' in self.checks:
            for column in self.checks['unique_checks']:
                result = hook.get_first(
                    f"""
                    SELECT COUNT(*) - COUNT(DISTINCT {column})
                    FROM garmin.{self.table_name}
                    """
                )
                if result[0] > 0:
                    issues.append(f"{result[0]} duplicate values in {column}")
        
        # Check value ranges
        if 'range_checks' in self.checks:
            for column, (min_val, max_val) in self.checks['range_checks'].items():
                result = hook.get_first(
                    f"""
                    SELECT COUNT(*)
                    FROM garmin.{self.table_name}
                    WHERE {column} < {min_val} OR {column} > {max_val}
                    """
                )
                if result[0] > 0:
                    issues.append(f"{result[0]} values outside range for {column}")
        
        if issues:
            logger.warning(f"Data quality issues found: {issues}")
            if len(issues) > self.checks.get('max_issues', 5):
                raise ValueError(f"Too many data quality issues: {issues}")
        
        return len(issues) == 0
