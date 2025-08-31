# spark/jobs/process_activities.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActivityProcessor:
    """Process activity data with Spark"""
    
    def __init__(self, spark: SparkSession, db_config: dict):
        self.spark = spark
        self.db_config = db_config
        
    def read_staging_data(self, start_date: str, end_date: str):
        """Read activity data from staging table"""
        query = f"""
        (SELECT * FROM garmin.staging_activities 
         WHERE DATE(start_time) BETWEEN '{start_date}' AND '{end_date}') AS activities
        """
        
        df = self.spark.read \
            .format("jdbc") \
            .option("url", self.db_config['url']) \
            .option("dbtable", query) \
            .option("user", self.db_config['user']) \
            .option("password", self.db_config['password']) \
            .option("driver", "org.postgresql.Driver") \
            .load()
            
        return df
    
    def calculate_pace_and_speed(self, df):
        """Calculate pace and speed metrics"""
        # Convert distance to km
        df = df.withColumn("distance_km", col("distance_meters") / 1000)
        
        # Calculate duration in minutes
        df = df.withColumn("duration_minutes", col("duration_seconds") / 60)
        
        # Calculate pace (min/km) for running and walking activities
        df = df.withColumn(
            "pace_min_per_km",
            when(
                (col("distance_km") > 0) & 
                (col("activity_type").isin(["running", "walking", "trail_running"])),
                col("duration_minutes") / col("distance_km")
            ).otherwise(None)
        )
        
        # Calculate speed (km/h) for cycling activities
        df = df.withColumn(
            "speed_kmh",
            when(
                (col("duration_minutes") > 0) & 
                (col("activity_type").isin(["cycling", "mountain_biking"])),
                (col("distance_km") * 60) / col("duration_minutes")
            ).otherwise(col("avg_speed") * 3.6)  # Convert m/s to km/h
        )
        
        return df
    
    def calculate_heart_rate_zones(self, df):
        """Calculate time spent in different heart rate zones"""
        # Define heart rate zones based on max HR percentage
        # Zone 1: 50-60%, Zone 2: 60-70%, Zone 3: 70-80%, Zone 4: 80-90%, Zone 5: 90-100%
        
        df = df.withColumn(
            "hr_zone",
            when(col("avg_heart_rate").isNull(), None)
            .when(col("avg_heart_rate") < col("max_heart_rate") * 0.6, 1)
            .when(col("avg_heart_rate") < col("max_heart_rate") * 0.7, 2)
            .when(col("avg_heart_rate") < col("max_heart_rate") * 0.8, 3)
            .when(col("avg_heart_rate") < col("max_heart_rate") * 0.9, 4)
            .otherwise(5)
        )
        
        # Create zone distribution as JSON
        df = df.withColumn(
            "heart_rate_zones",
            to_json(
                struct(
                    col("hr_zone").alias("primary_zone"),
                    col("avg_heart_rate").alias("avg_hr"),
                    col("max_heart_rate").alias("max_hr")
                )
            )
        )
        
        return df
    
    def calculate_training_metrics(self, df):
        """Calculate training load and recovery metrics"""
        # Simplified TRIMP (Training Impulse) calculation
        df = df.withColumn(
            "training_load",
            when(
                col("avg_heart_rate").isNotNull() & col("duration_minutes").isNotNull(),
                col("duration_minutes") * col("avg_heart_rate") / 100
            ).otherwise(None)
        )
        
        # Estimate recovery time based on training load
        df = df.withColumn(
            "recovery_time_hours",
            when(col("training_load") < 50, 12)
            .when(col("training_load") < 100, 24)
            .when(col("training_load") < 200, 48)
            .otherwise(72)
        )
        
        # Calculate end time
        df = df.withColumn(
            "end_time",
            col("start_time") + expr("INTERVAL duration_seconds SECONDS")
        )
        
        return df
    
    def detect_personal_records(self, df):
        """Identify personal records in activities"""
        # Window for each activity type
        window_spec = Window.partitionBy("activity_type").orderBy("start_time")
        
        # Calculate running maximums for distance and best pace
        df = df.withColumn(
            "is_distance_pr",
            col("distance_km") == max("distance_km").over(window_spec)
        )
        
        df = df.withColumn(
            "is_pace_pr",
            when(
                col("pace_min_per_km").isNotNull(),
                col("pace_min_per_km") == min("pace_min_per_km").over(window_spec)
            ).otherwise(False)
        )
        
        return df
    
    def estimate_vo2_max(self, df):
        """Estimate VO2 max from running activities"""
        # Simplified VO2 max estimation based on pace and heart rate
        # This is a very basic estimation - real VO2 max calculation is more complex
        
        df = df.withColumn(
            "vo2_max",
            when(
                (col("activity_type") == "running") & 
                (col("pace_min_per_km").isNotNull()) &
                (col("avg_heart_rate").isNotNull()),
                # Jack Daniels' VDOT approximation (simplified)
                65 - (col("pace_min_per_km") - 3) * 5
            ).otherwise(None)
        )
        
        return df
    
    def process_activities(self, start_date: str, end_date: str):
        """Main processing pipeline for activities"""
        logger.info(f"Processing activities from {start_date} to {end_date}")
        
        # Read staging data
        df = self.read_staging_data(start_date, end_date)
        
        # Apply transformations
        df = self.calculate_pace_and_speed(df)
        df = self.calculate_heart_rate_zones(df)
        df = self.calculate_training_metrics(df)
        df = self.detect_personal_records(df)
        df = self.estimate_vo2_max(df)
        
        # Convert elevation to meters (if in feet)
        df = df.withColumn("elevation_gain_m", col("elevation_gain"))
        df = df.withColumn("elevation_loss_m", col("elevation_loss"))
        
        # Select and rename columns for final table
        processed_df = df.select(
            col("activity_id"),
            col("activity_type"),
            col("activity_name"),
            col("start_time"),
            col("end_time"),
            col("duration_minutes"),
            col("distance_km"),
            col("pace_min_per_km"),
            col("speed_kmh"),
            col("calories"),
            col("avg_heart_rate"),
            col("max_heart_rate"),
            col("heart_rate_zones"),
            col("elevation_gain_m"),
            col("elevation_loss_m"),
            col("avg_cadence"),
            col("training_effect"),
            col("aerobic_effect"),
            col("anaerobic_effect"),
            col("training_load"),
            col("recovery_time_hours"),
            col("vo2_max")
        )
        
        # Write to processed table
        processed_df.write \
            .format("jdbc") \
            .option("url", self.db_config['url']) \
            .option("dbtable", "garmin.activities") \
            .option("user", self.db_config['user']) \
            .option("password", self.db_config['password']) \
            .option("driver", "org.postgresql.Driver") \
            .mode("append") \
            .save()
            
        # Extract personal records if any
        pr_df = df.filter(col("is_distance_pr") | col("is_pace_pr"))
        if pr_df.count() > 0:
            self.save_personal_records(pr_df)
            
        logger.info(f"Processed {df.count()} activities")
        
    def save_personal_records(self, df):
        """Save personal records to database"""
        # Prepare distance PRs
        distance_prs = df.filter(col("is_distance_pr")).select(
            col("activity_type"),
            lit("distance").alias("record_type"),
            col("distance_km").alias("record_value"),
            lit("km").alias("record_unit"),
            col("activity_id"),
            col("start_time").cast("date").alias("achieved_date")
        )
        
        # Prepare pace PRs
        pace_prs = df.filter(col("is_pace_pr")).select(
            col("activity_type"),
            lit("pace").alias("record_type"),
            col("pace_min_per_km").alias("record_value"),
            lit("min/km").alias("record_unit"),
            col("activity_id"),
            col("start_time").cast("date").alias("achieved_date")
        )
        
        # Union all PRs
        all_prs = distance_prs.union(pace_prs)
        
        # Write to personal records table
        all_prs.write \
            .format("jdbc") \
            .option("url", self.db_config['url']) \
            .option("dbtable", "garmin.personal_records") \
            .option("user", self.db_config['user']) \
            .option("password", self.db_config['password']) \
            .option("driver", "org.postgresql.Driver") \
            .mode("append") \
            .save()

# spark/jobs/aggregate_metrics.py
class MetricsAggregator:
    """Aggregate metrics for daily, weekly, and monthly summaries"""
    
    def __init__(self, spark: SparkSession, db_config: dict):
        self.spark = spark
        self.db_config = db_config
        
    def calculate_daily_metrics(self, date: str):
        """Calculate daily aggregated metrics"""
        
        # Read all staging tables for the date
        heart_rate_df = self.read_table_for_date("staging_heart_rate", date)
        sleep_df = self.read_table_for_date("staging_sleep", date)
        stress_df = self.read_table_for_date("staging_stress", date)
        body_df = self.read_table_for_date("staging_body_composition", date)
        summary_df = self.read_table_for_date("staging_daily_summary", date)
        
        # Read activities for the date
        activities_df = self.read_activities_for_date(date)
        
        # Aggregate activity metrics
        activity_metrics = activities_df.agg(
            count("activity_id").alias("activity_count"),
            sum("distance_km").alias("total_activity_distance"),
            sum("calories").alias("total_activity_calories"),
            avg("training_load").alias("avg_training_load"),
            max("recovery_time_hours").alias("max_recovery_time")
        ).collect()[0] if activities_df.count() > 0 else None
        
        # Build daily metrics record
        daily_metrics = {
            "date": date,
            # Heart Rate metrics
            "resting_heart_rate": heart_rate_df.select("resting_heart_rate").first()[0] if heart_rate_df.count() > 0 else None,
            "avg_heart_rate": heart_rate_df.select("avg_heart_rate").first()[0] if heart_rate_df.count() > 0 else None,
            "max_heart_rate": heart_rate_df.select("max_heart_rate").first()[0] if heart_rate_df.count() > 0 else None,
            "min_heart_rate": heart_rate_df.select("min_heart_rate").first()[0] if heart_rate_df.count() > 0 else None,
            # Sleep metrics
            "sleep_duration_hours": sleep_df.select(col("total_sleep_seconds") / 3600).first()[0] if sleep_df.count() > 0 else None,
            "deep_sleep_hours": sleep_df.select(col("deep_sleep_seconds") / 3600).first()[0] if sleep_df.count() > 0 else None,
            "light_sleep_hours": sleep_df.select(col("light_sleep_seconds") / 3600).first()[0] if sleep_df.count() > 0 else None,
            "rem_sleep_hours": sleep_df.select(col("rem_sleep_seconds") / 3600).first()[0] if sleep_df.count() > 0 else None,
            "sleep_score": sleep_df.select("sleep_score").first()[0] if sleep_df.count() > 0 else None,
            # Stress metrics
            "avg_stress_level": stress_df.select("avg_stress_level").first()[0] if stress_df.count() > 0 else None,
            "max_stress_level": stress_df.select("max_stress_level").first()[0] if stress_df.count() > 0 else None,
            # Activity metrics from summary
            "total_steps": summary_df.select("total_steps").first()[0] if summary_df.count() > 0 else None,
            "distance_km": summary_df.select(col("total_distance_meters") / 1000).first()[0] if summary_df.count() > 0 else None,
            "floors_climbed": summary_df.select("floors_climbed").first()[0] if summary_df.count() > 0 else None,
            "active_minutes": summary_df.select(col("active_seconds") / 60).first()[0] if summary_df.count() > 0 else None,
            "intensity_minutes": summary_df.select("intensity_minutes").first()[0] if summary_df.count() > 0 else None,
            # Calories
            "total_calories": summary_df.select("total_calories").first()[0] if summary_df.count() > 0 else None,
            "active_calories": summary_df.select("active_calories").first()[0] if summary_df.count() > 0 else None,
            "bmr_calories": summary_df.select("bmr_calories").first()[0] if summary_df.count() > 0 else None,
            # Body metrics
            "weight_kg": body_df.select("weight_kg").first()[0] if body_df.count() > 0 else None,
            "bmi": body_df.select("bmi").first()[0] if body_df.count() > 0 else None,
            "body_fat_percentage": body_df.select("body_fat_percentage").first()[0] if body_df.count() > 0 else None,
            "muscle_mass_kg": body_df.select("muscle_mass_kg").first()[0] if body_df.count() > 0 else None,
            # Performance metrics from activities
            "training_readiness": self.calculate_training_readiness(activity_metrics, sleep_df, stress_df),
            "recovery_time_hours": activity_metrics["max_recovery_time"] if activity_metrics else None
        }
        
        # Create DataFrame and save
        df = self.spark.createDataFrame([daily_metrics])
        
        df.write \
            .format("jdbc") \
            .option("url", self.db_config['url']) \
            .option("dbtable", "garmin.daily_metrics") \
            .option("user", self.db_config['user']) \
            .option("password", self.db_config['password']) \
            .option("driver", "org.postgresql.Driver") \
            .mode("append") \
            .save()
            
    def calculate_training_readiness(self, activity_metrics, sleep_df, stress_df):
        """Calculate training readiness score (0-100)"""
        score = 50  # Base score
        
        # Adjust based on sleep
        if sleep_df.count() > 0:
            sleep_score = sleep_df.select("sleep_score").first()[0]
            if sleep_score:
                score += (sleep_score - 50) * 0.3
                
        # Adjust based on stress
        if stress_df.count() > 0:
            stress_level = stress_df.select("avg_stress_level").first()[0]
            if stress_level:
                score -= (stress_level - 50) * 0.2
                
        # Adjust based on recovery time
        if activity_metrics and activity_metrics["max_recovery_time"]:
            if activity_metrics["max_recovery_time"] > 48:
                score -= 20
            elif activity_metrics["max_recovery_time"] > 24:
                score -= 10
                
        return max(0, min(100, int(score)))
    
    def read_table_for_date(self, table_name: str, date: str):
        """Read data from staging table for specific date"""
        query = f"(SELECT * FROM garmin.{table_name} WHERE date = '{date}') AS {table_name}"
        
        return self.spark.read \
            .format("jdbc") \
            .option("url", self.db_config['url']) \
            .option("dbtable", query) \
            .option("user", self.db_config['user']) \
            .option("password", self.db_config['password']) \
            .option("driver", "org.postgresql.Driver") \
            .load()
    
    def read_activities_for_date(self, date: str):
        """Read processed activities for specific date"""
        query = f"(SELECT * FROM garmin.activities WHERE DATE(start_time) = '{date}') AS activities"
        
        return self.spark.read \
            .format("jdbc") \
            .option("url", self.db_config['url']) \
            .option("dbtable", query) \
            .option("user", self.db_config['user']) \
            .option("password", self.db_config['password']) \
            .option("driver", "org.postgresql.Driver") \
            .load()

if __name__ == "__main__":
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("GarminDataProcessing") \
        .config("spark.jars", "/path/to/postgresql-42.2.24.jar") \
        .getOrCreate()
    
    # Database configuration
    db_config = {
        "url": os.getenv("DATABASE_URL", "jdbc:postgresql://localhost:5432/garmin"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "password")
    }
    
    # Process activities for today
    processor = ActivityProcessor(spark, db_config)
    today = datetime.now().strftime("%Y-%m-%d")
    processor.process_activities(today, today)
    
    # Calculate daily metrics
    aggregator = MetricsAggregator(spark, db_config)
    aggregator.calculate_daily_metrics(today)
    
    spark.stop()
