"""
Spark job to process heart rate data and calculate HRV metrics
"""
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime, timedelta
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create Spark session with PostgreSQL connector"""
    return SparkSession.builder \
        .appName("GarminHeartRateProcessing") \
        .config("spark.jars", "/opt/bitnami/spark/jars/postgresql-42.6.0.jar") \
        .getOrCreate()

def get_postgres_properties():
    """Database connection properties"""
    return {
        "user": "postgres",
        "password": "postgres", 
        "driver": "org.postgresql.Driver"
    }

def calculate_hrv_score(resting_hr, avg_hr, age=35):
    """Calculate HRV score based on heart rate metrics"""
    if not resting_hr or not avg_hr:
        return None
    
    # Simplified HRV calculation based on resting HR
    # Lower resting HR typically indicates better HRV
    base_score = max(0, 100 - (resting_hr - 40))
    
    # Age adjustment
    age_factor = max(0.7, 1 - (age - 25) * 0.01)
    
    hrv_score = min(100, base_score * age_factor)
    return round(hrv_score, 2)

def process_heart_rate_data(spark, process_date):
    """Process heart rate data for longevity metrics"""
    jdbc_url = "jdbc:postgresql://postgres:5432/postgres"
    properties = get_postgres_properties()
    
    try:
        # Read staging heart rate data
        staging_df = spark.read.jdbc(
            jdbc_url, "garmin.staging_heart_rate", properties=properties
        ).filter(col("date") == process_date)
        
        if staging_df.count() == 0:
            logger.warning(f"No heart rate data found for {process_date}")
            return
        
        # Process heart rate time series data
        processed_data = staging_df.select(
            col("date"),
            col("resting_heart_rate"),
            col("min_heart_rate"),
            col("max_heart_rate"),
            col("avg_heart_rate"),
            col("heart_rate_zones"),
            col("time_series")
        ).collect()[0]
        
        # Calculate HRV score
        hrv_score = calculate_hrv_score(
            processed_data.resting_heart_rate,
            processed_data.avg_heart_rate
        )
        
        # Parse heart rate zones for analysis
        hr_zones = {}
        if processed_data.heart_rate_zones:
            try:
                hr_zones = json.loads(processed_data.heart_rate_zones)
            except:
                hr_zones = {}
        
        # Calculate time in each zone (simplified)
        zone_analysis = analyze_hr_zones(processed_data.time_series)
        
        # Create processed heart rate record
        processed_hr = {
            "date": process_date,
            "resting_heart_rate": processed_data.resting_heart_rate,
            "avg_heart_rate": processed_data.avg_heart_rate,
            "max_heart_rate": processed_data.max_heart_rate,
            "min_heart_rate": processed_data.min_heart_rate,
            "hrv_score": hrv_score,
            "zone1_minutes": zone_analysis.get("zone1_minutes", 0),
            "zone2_minutes": zone_analysis.get("zone2_minutes", 0),
            "zone3_minutes": zone_analysis.get("zone3_minutes", 0),
            "zone4_minutes": zone_analysis.get("zone4_minutes", 0),
            "zone5_minutes": zone_analysis.get("zone5_minutes", 0),
            "recovery_quality": calculate_recovery_quality(processed_data.resting_heart_rate),
            "processed_at": datetime.now()
        }
        
        # Create DataFrame
        processed_df = spark.createDataFrame([processed_hr])
        
        # Write to processed heart rate table (you'd need to create this table)
        processed_df.write.jdbc(
            jdbc_url,
            "garmin.processed_heart_rate", 
            mode="append",
            properties=properties
        )
        
        logger.info(f"Successfully processed heart rate data for {process_date}")
        
    except Exception as e:
        logger.error(f"Error processing heart rate data: {str(e)}")
        raise

def analyze_hr_zones(time_series_json):
    """Analyze time spent in different heart rate zones"""
    if not time_series_json:
        return {}
    
    try:
        time_series = json.loads(time_series_json)
        # Simplified zone analysis - would need actual zone thresholds
        return {
            "zone1_minutes": len([hr for hr in time_series if hr and 50 <= hr < 100]) // 60,
            "zone2_minutes": len([hr for hr in time_series if hr and 100 <= hr < 120]) // 60,
            "zone3_minutes": len([hr for hr in time_series if hr and 120 <= hr < 140]) // 60,
            "zone4_minutes": len([hr for hr in time_series if hr and 140 <= hr < 160]) // 60,
            "zone5_minutes": len([hr for hr in time_series if hr and hr >= 160]) // 60
        }
    except:
        return {}

def calculate_recovery_quality(resting_hr):
    """Calculate recovery quality based on resting heart rate"""
    if not resting_hr:
        return None
    
    # Simplified recovery quality assessment
    if resting_hr < 50:
        return "Excellent"
    elif resting_hr < 60:
        return "Good" 
    elif resting_hr < 70:
        return "Fair"
    else:
        return "Poor"

def main():
    """Main execution function"""
    if len(sys.argv) > 1:
        process_date = sys.argv[1]
    else:
        process_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    logger.info(f"Starting heart rate processing for date: {process_date}")
    
    spark = create_spark_session()
    try:
        process_heart_rate_data(spark, process_date)
        logger.info("Heart rate processing completed successfully")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()