"""
Spark job to process sleep data and calculate sleep quality metrics
"""
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create Spark session with PostgreSQL connector"""
    return SparkSession.builder \
        .appName("GarminSleepProcessing") \
        .config("spark.jars", "/opt/bitnami/spark/jars/postgresql-42.6.0.jar") \
        .getOrCreate()

def get_postgres_properties():
    """Database connection properties"""
    return {
        "user": "postgres",
        "password": "postgres", 
        "driver": "org.postgresql.Driver"
    }

def calculate_sleep_efficiency(total_sleep_seconds, time_in_bed_seconds):
    """Calculate sleep efficiency percentage"""
    if not total_sleep_seconds or not time_in_bed_seconds or time_in_bed_seconds == 0:
        return None
    
    efficiency = (total_sleep_seconds / time_in_bed_seconds) * 100
    return min(100, round(efficiency, 2))

def calculate_sleep_architecture_score(deep_sleep_hours, rem_sleep_hours, total_sleep_hours):
    """Calculate sleep architecture quality score"""
    if not all([deep_sleep_hours, rem_sleep_hours, total_sleep_hours]) or total_sleep_hours == 0:
        return None
    
    # Ideal percentages: Deep sleep ~20%, REM ~25%
    deep_percentage = (deep_sleep_hours / total_sleep_hours) * 100
    rem_percentage = (rem_sleep_hours / total_sleep_hours) * 100
    
    # Score based on how close to ideal percentages
    deep_score = max(0, 50 - abs(deep_percentage - 20) * 2.5)
    rem_score = max(0, 50 - abs(rem_percentage - 25) * 2)
    
    architecture_score = (deep_score + rem_score)
    return round(min(100, architecture_score), 2)

def calculate_longevity_sleep_score(sleep_data):
    """Calculate comprehensive sleep score for longevity"""
    duration_score = 0
    efficiency_score = 0
    architecture_score = 0
    consistency_score = 50  # Default neutral score
    
    # Duration score (7-9 hours optimal)
    if sleep_data.get("sleep_duration_hours"):
        duration = sleep_data["sleep_duration_hours"]
        if 7 <= duration <= 9:
            duration_score = 100
        elif 6 <= duration < 7 or 9 < duration <= 10:
            duration_score = 80
        elif 5 <= duration < 6 or 10 < duration <= 11:
            duration_score = 60
        else:
            duration_score = 30
    
    # Efficiency score
    if sleep_data.get("sleep_efficiency"):
        efficiency = sleep_data["sleep_efficiency"]
        if efficiency >= 85:
            efficiency_score = 100
        elif efficiency >= 75:
            efficiency_score = 80
        elif efficiency >= 65:
            efficiency_score = 60
        else:
            efficiency_score = 30
    
    # Architecture score
    if sleep_data.get("architecture_score"):
        architecture_score = sleep_data["architecture_score"]
    
    # Weighted final score
    final_score = (
        duration_score * 0.35 +
        efficiency_score * 0.25 +
        architecture_score * 0.25 +
        consistency_score * 0.15
    )
    
    return round(final_score, 2)

def process_sleep_data(spark, process_date):
    """Process sleep data for longevity metrics"""
    jdbc_url = "jdbc:postgresql://postgres:5432/postgres"
    properties = get_postgres_properties()
    
    try:
        # Read staging sleep data
        staging_df = spark.read.jdbc(
            jdbc_url, "garmin.staging_sleep", properties=properties
        ).filter(col("date") == process_date)
        
        if staging_df.count() == 0:
            logger.warning(f"No sleep data found for {process_date}")
            return
        
        sleep_data = staging_df.collect()[0]
        
        # Convert seconds to hours
        total_sleep_hours = sleep_data.total_sleep_seconds / 3600 if sleep_data.total_sleep_seconds else None
        deep_sleep_hours = sleep_data.deep_sleep_seconds / 3600 if sleep_data.deep_sleep_seconds else None
        light_sleep_hours = sleep_data.light_sleep_seconds / 3600 if sleep_data.light_sleep_seconds else None
        rem_sleep_hours = sleep_data.rem_sleep_seconds / 3600 if sleep_data.rem_sleep_seconds else None
        awake_hours = sleep_data.awake_seconds / 3600 if sleep_data.awake_seconds else None
        
        # Calculate time in bed
        if sleep_data.sleep_start_time and sleep_data.sleep_end_time:
            start_time = datetime.fromisoformat(sleep_data.sleep_start_time.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(sleep_data.sleep_end_time.replace('Z', '+00:00'))
            time_in_bed_seconds = (end_time - start_time).total_seconds()
        else:
            time_in_bed_seconds = None
        
        # Calculate metrics
        sleep_efficiency = calculate_sleep_efficiency(
            sleep_data.total_sleep_seconds, 
            time_in_bed_seconds
        )
        
        architecture_score = calculate_sleep_architecture_score(
            deep_sleep_hours,
            rem_sleep_hours, 
            total_sleep_hours
        )
        
        # Prepare data for longevity score calculation
        sleep_metrics = {
            "sleep_duration_hours": total_sleep_hours,
            "sleep_efficiency": sleep_efficiency,
            "architecture_score": architecture_score
        }
        
        longevity_score = calculate_longevity_sleep_score(sleep_metrics)
        
        # Create processed sleep record
        processed_sleep = {
            "date": process_date,
            "sleep_duration_hours": total_sleep_hours,
            "deep_sleep_hours": deep_sleep_hours,
            "light_sleep_hours": light_sleep_hours,
            "rem_sleep_hours": rem_sleep_hours,
            "awake_hours": awake_hours,
            "sleep_efficiency": sleep_efficiency,
            "architecture_score": architecture_score,
            "longevity_sleep_score": longevity_score,
            "garmin_sleep_score": sleep_data.sleep_score,
            "sleep_start_time": sleep_data.sleep_start_time,
            "sleep_end_time": sleep_data.sleep_end_time,
            "avg_respiration": sleep_data.avg_respiration,
            "avg_spo2": sleep_data.avg_spo2,
            "sleep_quality_rating": rate_sleep_quality(longevity_score),
            "processed_at": datetime.now()
        }
        
        # Create DataFrame
        processed_df = spark.createDataFrame([processed_sleep])
        
        # Write to processed sleep table
        processed_df.write.jdbc(
            jdbc_url,
            "garmin.processed_sleep", 
            mode="append",
            properties=properties
        )
        
        logger.info(f"Successfully processed sleep data for {process_date}")
        
    except Exception as e:
        logger.error(f"Error processing sleep data: {str(e)}")
        raise

def rate_sleep_quality(longevity_score):
    """Rate sleep quality based on longevity score"""
    if not longevity_score:
        return "Unknown"
    
    if longevity_score >= 90:
        return "Excellent"
    elif longevity_score >= 80:
        return "Good"
    elif longevity_score >= 70:
        return "Fair"
    elif longevity_score >= 60:
        return "Poor"
    else:
        return "Very Poor"

def main():
    """Main execution function"""
    if len(sys.argv) > 1:
        process_date = sys.argv[1]
    else:
        process_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    logger.info(f"Starting sleep processing for date: {process_date}")
    
    spark = create_spark_session()
    try:
        process_sleep_data(spark, process_date)
        logger.info("Sleep processing completed successfully")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()