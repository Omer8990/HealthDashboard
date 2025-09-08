"""
Celery tasks for background Garmin data extraction
"""
import os
import logging
from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab
from garminconnect import Garmin, GarminConnectAuthenticationError
from sqlalchemy import create_engine, text
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
app = Celery('garmin_tasks')
app.conf.broker_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
app.conf.result_backend = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Schedule daily data extraction at 6 AM
app.conf.beat_schedule = {
    'daily-garmin-sync': {
        'task': 'tasks.extract_daily_data',
        'schedule': crontab(hour=6, minute=0),
    },
}

app.conf.timezone = 'UTC'

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/longevity')

@app.task(bind=True, max_retries=3)
def extract_daily_data(self, date_str=None):
    """Extract Garmin data for a specific date (defaults to yesterday)"""
    try:
        if date_str is None:
            target_date = datetime.now() - timedelta(days=1)
        else:
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        date_str = target_date.strftime('%Y-%m-%d')
        logger.info(f"Starting Garmin data extraction for {date_str}")
        
        # Connect to Garmin
        # Temporarily hardcode credentials to bypass env var issue
        email = "omer.haimovitz@gmail.com"
        password = "Gunrvnkl2!"
        
        if not email or not password:
            raise ValueError("Garmin credentials not configured")
        
        client = Garmin(email, password)
        
        # Clear any existing session and login fresh
        try:
            client.logout()
        except:
            pass  # Ignore logout errors
            
        # Workaround for profile assertion bug in newer versions
        try:
            client.login()
        except AssertionError:
            # Profile assertion failed, try direct garth login
            client.garth.login(email, password)
            client.display_name = "User"  # Set a default display name
        logger.info("Connected to Garmin Connect")
        
        # Extract data
        activities = extract_activities(client, target_date)
        heart_rate = extract_heart_rate(client, target_date)
        sleep_data = extract_sleep(client, target_date)
        stress_data = extract_stress(client, target_date)
        body_comp = extract_body_composition(client, target_date)
        daily_stats = extract_daily_stats(client, target_date)
        
        # Save to database
        engine = create_engine(DATABASE_URL)
        
        if activities:
            save_activities(engine, activities)
        if heart_rate:
            save_heart_rate(engine, [heart_rate])
        if sleep_data:
            save_sleep(engine, [sleep_data])
        if stress_data:
            save_stress(engine, [stress_data])
        if body_comp:
            save_body_composition(engine, [body_comp])
        if daily_stats:
            save_daily_stats(engine, [daily_stats])
        
        # Calculate processed metrics
        calculate_daily_metrics(engine, target_date)
        
        logger.info(f"Successfully extracted data for {date_str}")
        return {
            'date': date_str,
            'activities': len(activities),
            'status': 'success'
        }
        
    except GarminConnectAuthenticationError as e:
        logger.error(f"Garmin authentication failed: {e}")
        logger.error(f"Using email: {email}")
        logger.error(f"Password length: {len(password) if password else 0}")
        raise self.retry(countdown=300)  # Retry in 5 minutes
    except Exception as e:
        logger.error(f"Data extraction failed: {e}")
        raise self.retry(countdown=60)  # Retry in 1 minute

def extract_activities(client, date):
    """Extract activities for a specific date"""
    try:
        date_str = date.strftime('%Y-%m-%d')
        activities_raw = client.get_activities_by_date(date_str, date_str)
        
        activities = []
        for activity in activities_raw:
            processed = {
                'activity_id': activity.get('activityId'),
                'activity_type': activity.get('activityType', {}).get('typeKey', 'unknown'),
                'activity_name': activity.get('activityName', 'Activity'),
                'start_time': datetime.strptime(activity.get('startTimeLocal'), '%Y-%m-%d %H:%M:%S') if activity.get('startTimeLocal') else None,
                'duration_seconds': activity.get('duration', 0),
                'distance_meters': activity.get('distance', 0),
                'calories': activity.get('calories', 0),
                'avg_heart_rate': activity.get('averageHR'),
                'max_heart_rate': activity.get('maxHR'),
                'avg_speed': activity.get('averageSpeed', 0),
                'elevation_gain': activity.get('elevationGain', 0),
                'extracted_at': datetime.now()
            }
            activities.append(processed)
        
        logger.info(f"Extracted {len(activities)} activities for {date_str}")
        return activities
        
    except Exception as e:
        logger.error(f"Failed to extract activities: {e}")
        return []

def extract_heart_rate(client, date):
    """Extract heart rate data for a specific date"""
    try:
        date_str = date.strftime('%Y-%m-%d')
        hr_data = client.get_heart_rates(date_str)
        
        if hr_data:
            return {
                'date': date.date(),
                'resting_heart_rate': hr_data.get('restingHeartRate'),
                'min_heart_rate': hr_data.get('minHeartRate'),
                'max_heart_rate': hr_data.get('maxHeartRate'),
                'extracted_at': datetime.now()
            }
    except Exception as e:
        logger.error(f"Failed to extract heart rate: {e}")
        return None

def extract_sleep(client, date):
    """Extract sleep data for a specific date"""
    try:
        date_str = date.strftime('%Y-%m-%d')
        sleep_data = client.get_sleep_data(date_str)
        
        if sleep_data and isinstance(sleep_data, list):
            sleep_data = sleep_data[0]
        
        if sleep_data:
            sleep_levels = sleep_data.get('sleepLevels', {})
            return {
                'date': date.date(),
                'total_sleep_seconds': sleep_data.get('sleepTimeSeconds'),
                'deep_sleep_seconds': sleep_levels.get('deep', {}).get('seconds'),
                'light_sleep_seconds': sleep_levels.get('light', {}).get('seconds'),
                'rem_sleep_seconds': sleep_levels.get('rem', {}).get('seconds'),
                'sleep_score': sleep_data.get('sleepScores', {}).get('overall'),
                'extracted_at': datetime.now()
            }
    except Exception as e:
        logger.error(f"Failed to extract sleep data: {e}")
        return None

def extract_daily_stats(client, date):
    """Extract daily summary statistics using comprehensive approach"""
    try:
        date_str = date.strftime('%Y-%m-%d')
        stats = client.get_stats(date_str)
        
        if stats:
            return {
                'date': date.date(),
                'total_steps': stats.get('totalSteps'),
                'total_distance_meters': stats.get('totalDistance'),
                'highly_active_seconds': stats.get('highlyActiveSeconds'),
                'active_seconds': stats.get('activeSeconds'),
                'sedentary_seconds': stats.get('sedentarySeconds'),
                'sleeping_seconds': stats.get('sleepingSeconds'),
                'total_calories': stats.get('totalKilocalories'),
                'active_calories': stats.get('activeKilocalories'),
                'bmr_calories': stats.get('bmrKilocalories'),
                'floors_climbed': stats.get('floorsAscended'),
                'floors_descended': stats.get('floorsDescended'),
                'intensity_minutes_goal': stats.get('intensityMinutesGoal'),
                'intensity_minutes': stats.get('moderateIntensityMinutes'),
                'vigorous_intensity_minutes': stats.get('vigorousIntensityMinutes'),
                'extracted_at': datetime.now()
            }
    except Exception as e:
        # Handle privacy protection and other data access issues
        if 'privacyProtected' in str(e):
            logger.warning(f"Daily stats for {date.strftime('%Y-%m-%d')} are privacy protected")
        else:
            logger.error(f"Failed to extract daily stats: {e}")
        return None

def extract_stress(client, date):
    """Extract stress data for a specific date"""
    try:
        date_str = date.strftime('%Y-%m-%d')
        stress_data = client.get_stress_data(date_str)
        
        if stress_data:
            stress_values = stress_data.get('stressValuesArray', [])
            
            return {
                'date': date.date(),
                'avg_stress_level': stress_data.get('averageStressLevel'),
                'max_stress_level': stress_data.get('maxStressLevel'),
                'stress_duration_seconds': stress_data.get('stressDuration'),
                'rest_stress_duration': stress_data.get('restStressDuration'),
                'activity_stress_duration': stress_data.get('activityStressDuration'),
                'low_stress_duration': stress_data.get('lowStressDuration'),
                'medium_stress_duration': stress_data.get('mediumStressDuration'),
                'high_stress_duration': stress_data.get('highStressDuration'),
                'extracted_at': datetime.now()
            }
    except Exception as e:
        logger.error(f"Failed to extract stress data: {e}")
        return None

def extract_body_composition(client, date):
    """Extract body composition data"""
    try:
        date_str = date.strftime('%Y-%m-%d')
        body_data = client.get_body_composition(date_str)
        
        if body_data:
            return {
                'date': date.date(),
                'weight_kg': body_data.get('weight'),
                'bmi': body_data.get('bmi'),
                'body_fat_percentage': body_data.get('bodyFatPercentage'),
                'muscle_mass_kg': body_data.get('muscleMass'),
                'bone_mass_kg': body_data.get('boneMass'),
                'body_water_percentage': body_data.get('bodyWaterPercentage'),
                'metabolic_age': body_data.get('metabolicAge'),
                'visceral_fat': body_data.get('visceralFatRating'),
                'extracted_at': datetime.now()
            }
    except Exception as e:
        logger.error(f"Failed to extract body composition data: {e}")
        return None

def save_activities(engine, activities):
    """Save activities to database"""
    try:
        df = pd.DataFrame(activities)
        df.to_sql('staging_activities', engine, schema='garmin', if_exists='append', index=False)
        logger.info(f"Saved {len(activities)} activities")
    except Exception as e:
        logger.error(f"Failed to save activities: {e}")

def save_heart_rate(engine, heart_rate_data):
    """Save heart rate data to database"""
    try:
        df = pd.DataFrame(heart_rate_data)
        df.to_sql('staging_heart_rate', engine, schema='garmin', if_exists='append', index=False)
        logger.info("Saved heart rate data")
    except Exception as e:
        logger.error(f"Failed to save heart rate: {e}")

def save_sleep(engine, sleep_data):
    """Save sleep data to database"""
    try:
        df = pd.DataFrame(sleep_data)
        df.to_sql('staging_sleep', engine, schema='garmin', if_exists='append', index=False)
        logger.info("Saved sleep data")
    except Exception as e:
        logger.error(f"Failed to save sleep: {e}")

def save_daily_stats(engine, daily_stats):
    """Save daily stats to database"""
    try:
        df = pd.DataFrame(daily_stats)
        df.to_sql('staging_daily_stats', engine, schema='garmin', if_exists='append', index=False)
        logger.info("Saved daily stats")
    except Exception as e:
        logger.error(f"Failed to save daily stats: {e}")

def save_stress(engine, stress_data):
    """Save stress data to database"""
    try:
        df = pd.DataFrame(stress_data)
        df.to_sql('staging_stress', engine, schema='garmin', if_exists='append', index=False)
        logger.info("Saved stress data")
    except Exception as e:
        logger.error(f"Failed to save stress: {e}")

def save_body_composition(engine, body_comp_data):
    """Save body composition data to database"""
    try:
        df = pd.DataFrame(body_comp_data)
        df.to_sql('staging_body_composition', engine, schema='garmin', if_exists='append', index=False)
        logger.info("Saved body composition data")
    except Exception as e:
        logger.error(f"Failed to save body composition: {e}")

def calculate_daily_metrics(engine, date):
    """Calculate processed daily metrics"""
    try:
        date_str = date.strftime('%Y-%m-%d')
        
        with engine.connect() as conn:
            # Calculate biological age and other metrics
            # This is a simplified version - you can enhance this later
            
            # Get basic metrics for the date
            result = conn.execute(text("""
                SELECT 
                    shr.resting_heart_rate,
                    COUNT(sa.id) as activities_count,
                    SUM(sa.distance_meters)/1000.0 as total_distance_km,
                    SUM(sa.duration_seconds)/60.0 as total_activity_minutes
                FROM garmin.staging_heart_rate shr
                LEFT JOIN garmin.staging_activities sa ON DATE(sa.start_time) = shr.date
                WHERE shr.date = :date
                GROUP BY shr.date, shr.resting_heart_rate
            """), {"date": date_str}).fetchone()
            
            if result:
                rhr, activities_count, total_distance, activity_minutes = result
                
                # Simple biological age calculation
                base_age = 25  # Assume base age
                rhr_adjustment = (rhr - 50) * 0.1 if rhr else 0
                activity_adjustment = -activities_count * 0.2
                
                bio_age = base_age + rhr_adjustment + activity_adjustment
                longevity_score = max(70, min(100, 100 - abs(bio_age - 22) * 2))
                
                # Insert processed metrics
                conn.execute(text("""
                    INSERT INTO garmin.processed_daily_metrics 
                    (date, resting_heart_rate, activities_count, total_distance_km, 
                     total_activity_duration_minutes, biological_age, longevity_score, processed_at)
                    VALUES (:date, :rhr, :activities, :distance, :duration, :bio_age, :longevity, NOW())
                    ON CONFLICT (date) DO UPDATE SET
                        resting_heart_rate = :rhr,
                        activities_count = :activities,
                        total_distance_km = :distance,
                        total_activity_duration_minutes = :duration,
                        biological_age = :bio_age,
                        longevity_score = :longevity,
                        processed_at = NOW()
                """), {
                    "date": date_str,
                    "rhr": rhr,
                    "activities": activities_count or 0,
                    "distance": total_distance or 0,
                    "duration": activity_minutes or 0,
                    "bio_age": round(bio_age, 1),
                    "longevity": int(longevity_score)
                })
                conn.commit()
                
                logger.info(f"Calculated metrics for {date_str}: bio_age={bio_age:.1f}")
        
    except Exception as e:
        logger.error(f"Failed to calculate daily metrics: {e}")

@app.task
def extract_historical_data(days=7):
    """Extract historical data for the past N days"""
    logger.info(f"Starting historical extraction for {days} days")
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i+1)
        date_str = date.strftime('%Y-%m-%d')
        extract_daily_data.delay(date_str)
    
    return f"Queued historical extraction for {days} days"

@app.task
def test_connection():
    """Test Garmin connection"""
    try:
        # Temporarily hardcode credentials to bypass env var issue
        email = "omer.haimovitz@gmail.com"
        password = "Gunrvnkl2!"
        
        client = Garmin(email, password)
        
        # Clear any existing session and login fresh
        try:
            client.logout()
        except:
            pass  # Ignore logout errors
            
        # Workaround for profile assertion bug in newer versions
        try:
            client.login()
        except AssertionError:
            # Profile assertion failed, try direct garth login
            client.garth.login(email, password)
            client.display_name = "User"  # Set a default display name
        
        logger.info("Garmin connection test successful")
        return {"status": "success", "message": "Connected to Garmin"}
        
    except Exception as e:
        logger.error(f"Garmin connection test failed: {e}")
        return {"status": "error", "message": str(e)}