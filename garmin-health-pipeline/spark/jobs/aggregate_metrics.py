"""
Spark job to aggregate daily metrics from staging tables
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
        .appName("GarminMetricsAggregation") \
        .config("spark.jars", "/opt/bitnami/spark/jars/postgresql-42.6.0.jar") \
        .getOrCreate()

def get_postgres_properties():
    """Database connection properties"""
    return {
        "user": "postgres",
        "password": "postgres", 
        "driver": "org.postgresql.Driver"
    }

def aggregate_daily_metrics(spark, process_date):
    """Aggregate all daily metrics for a specific date"""
    jdbc_url = "jdbc:postgresql://postgres:5432/postgres"
    properties = get_postgres_properties()
    
    try:
        # Read staging tables
        activities_df = spark.read.jdbc(
            jdbc_url, "garmin.staging_activities", properties=properties
        ).filter(date_format(col("start_time"), "yyyy-MM-dd") == process_date)
        
        heart_rate_df = spark.read.jdbc(
            jdbc_url, "garmin.staging_heart_rate", properties=properties
        ).filter(col("date") == process_date)
        
        sleep_df = spark.read.jdbc(
            jdbc_url, "garmin.staging_sleep", properties=properties
        ).filter(col("date") == process_date)
        
        stress_df = spark.read.jdbc(
            jdbc_url, "garmin.staging_stress", properties=properties
        ).filter(col("date") == process_date)
        
        body_comp_df = spark.read.jdbc(
            jdbc_url, "garmin.staging_body_composition", properties=properties
        ).filter(col("date") == process_date)
        
        daily_summary_df = spark.read.jdbc(
            jdbc_url, "garmin.staging_daily_summary", properties=properties
        ).filter(col("date") == process_date)
        
        # Aggregate activity metrics
        activity_metrics = activities_df.agg(
            sum("calories").alias("activity_calories"),
            sum("duration_seconds").alias("total_activity_seconds"),
            sum("distance_meters").alias("total_distance_meters"),
            avg("avg_heart_rate").alias("avg_activity_hr"),
            max("max_heart_rate").alias("max_activity_hr"),
            count("*").alias("total_activities")
        ).collect()[0] if activities_df.count() > 0 else None
        
        # Process heart rate data
        hr_metrics = heart_rate_df.select(
            "resting_heart_rate",
            "min_heart_rate", 
            "max_heart_rate",
            "avg_heart_rate"
        ).collect()[0] if heart_rate_df.count() > 0 else None
        
        # Process sleep data
        sleep_metrics = sleep_df.select(
            (col("total_sleep_seconds") / 3600).alias("sleep_duration_hours"),
            (col("deep_sleep_seconds") / 3600).alias("deep_sleep_hours"),
            (col("light_sleep_seconds") / 3600).alias("light_sleep_hours"),
            (col("rem_sleep_seconds") / 3600).alias("rem_sleep_hours"),
            "sleep_score"
        ).collect()[0] if sleep_df.count() > 0 else None
        
        # Process stress data
        stress_metrics = stress_df.select(
            "avg_stress_level",
            "max_stress_level",
            (col("low_stress_duration") / col("stress_duration_seconds") * 100).alias("low_stress_percentage"),
            (col("medium_stress_duration") / col("stress_duration_seconds") * 100).alias("medium_stress_percentage"),
            (col("high_stress_duration") / col("stress_duration_seconds") * 100).alias("high_stress_percentage")
        ).collect()[0] if stress_df.count() > 0 else None
        
        # Process body composition
        body_metrics = body_comp_df.select(
            "weight_kg",
            "bmi", 
            "body_fat_percentage",
            "muscle_mass_kg"
        ).collect()[0] if body_comp_df.count() > 0 else None
        
        # Process daily summary
        summary_metrics = daily_summary_df.select(
            "total_steps",
            (col("total_distance_meters") / 1000).alias("distance_km"),
            "floors_climbed",
            (col("active_seconds") / 60).alias("active_minutes"),
            "intensity_minutes",
            (col("sedentary_seconds") / 60).alias("sedentary_minutes"),
            "total_calories",
            "active_calories",
            "bmr_calories"
        ).collect()[0] if daily_summary_df.count() > 0 else None
        
        # Create aggregated daily metrics record
        daily_metrics = {
            "date": process_date,
            # Heart Rate
            "resting_heart_rate": hr_metrics.resting_heart_rate if hr_metrics else None,
            "avg_heart_rate": hr_metrics.avg_heart_rate if hr_metrics else None,
            "max_heart_rate": hr_metrics.max_heart_rate if hr_metrics else None,
            "min_heart_rate": hr_metrics.min_heart_rate if hr_metrics else None,
            # Sleep
            "sleep_duration_hours": sleep_metrics.sleep_duration_hours if sleep_metrics else None,
            "deep_sleep_hours": sleep_metrics.deep_sleep_hours if sleep_metrics else None,
            "light_sleep_hours": sleep_metrics.light_sleep_hours if sleep_metrics else None,
            "rem_sleep_hours": sleep_metrics.rem_sleep_hours if sleep_metrics else None,
            "sleep_score": sleep_metrics.sleep_score if sleep_metrics else None,
            # Stress
            "avg_stress_level": stress_metrics.avg_stress_level if stress_metrics else None,
            "max_stress_level": stress_metrics.max_stress_level if stress_metrics else None,
            "low_stress_percentage": stress_metrics.low_stress_percentage if stress_metrics else None,
            "medium_stress_percentage": stress_metrics.medium_stress_percentage if stress_metrics else None,
            "high_stress_percentage": stress_metrics.high_stress_percentage if stress_metrics else None,
            # Activity
            "total_steps": summary_metrics.total_steps if summary_metrics else None,
            "distance_km": summary_metrics.distance_km if summary_metrics else None,
            "floors_climbed": summary_metrics.floors_climbed if summary_metrics else None,
            "active_minutes": summary_metrics.active_minutes if summary_metrics else None,
            "intensity_minutes": summary_metrics.intensity_minutes if summary_metrics else None,
            "sedentary_minutes": summary_metrics.sedentary_minutes if summary_metrics else None,
            # Calories
            "total_calories": summary_metrics.total_calories if summary_metrics else None,
            "active_calories": summary_metrics.active_calories if summary_metrics else None,
            "bmr_calories": summary_metrics.bmr_calories if summary_metrics else None,
            # Body Metrics
            "weight_kg": body_metrics.weight_kg if body_metrics else None,
            "bmi": body_metrics.bmi if body_metrics else None,
            "body_fat_percentage": body_metrics.body_fat_percentage if body_metrics else None,
            "muscle_mass_kg": body_metrics.muscle_mass_kg if body_metrics else None,
            "processed_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Create DataFrame and write to processed table
        daily_metrics_df = spark.createDataFrame([daily_metrics])
        
        daily_metrics_df.write.jdbc(
            jdbc_url, 
            "garmin.daily_metrics",
            mode="append",
            properties=properties
        )
        
        logger.info(f"Successfully processed daily metrics for {process_date}")
        
    except Exception as e:
        logger.error(f"Error processing daily metrics for {process_date}: {str(e)}")
        raise

def main():
    """Main execution function"""
    if len(sys.argv) > 1:
        process_date = sys.argv[1]
    else:
        # Default to yesterday
        process_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    logger.info(f"Starting metrics aggregation for date: {process_date}")
    
    spark = create_spark_session()
    try:
        aggregate_daily_metrics(spark, process_date)
        logger.info("Metrics aggregation completed successfully")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()