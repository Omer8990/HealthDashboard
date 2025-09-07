#!/usr/bin/env python3
"""
Save Garmin data to the Docker database
"""
import json
from datetime import datetime, timedelta
from garminconnect import Garmin
import psycopg2

def save_garmin_data():
    """Extract and save Garmin data directly to Docker database"""
    
    # Configuration  
    email = "omer.haimovitz@gmail.com"
    password = "Gunrvnkl2!"
    
    print("🔗 Connecting to Garmin Connect...")
    client = Garmin(email, password)
    client.login()
    print("✅ Connected to Garmin!")
    
    # Connect to Docker PostgreSQL
    print("🔗 Connecting to Docker PostgreSQL...")
    conn = psycopg2.connect(
        host="localhost",
        port="5432", 
        database="longevity",
        user="postgres",
        password="postgres"
    )
    cur = conn.cursor()
    print("✅ Connected to database!")
    
    # Extract data for last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"📊 Processing data from {start_date.date()} to {end_date.date()}...")
    
    activities_saved = 0
    hr_saved = 0
    stats_saved = 0
    
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        
        print(f"  📅 Processing {date_str}...")
        
        try:
            # Get and save activities
            activities = client.get_activities_by_date(date_str, date_str)
            for activity in activities:
                cur.execute("""
                    INSERT INTO garmin.staging_activities 
                    (activity_id, activity_type, activity_name, start_time, duration_seconds, 
                     distance_meters, calories, avg_heart_rate, max_heart_rate, extracted_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (activity_id) DO NOTHING
                """, (
                    activity['activityId'],
                    activity.get('activityType', {}).get('typeKey', 'unknown'),
                    activity.get('activityName', 'Activity'),
                    activity.get('startTimeLocal'),
                    activity.get('duration', 0),
                    activity.get('distance', 0),
                    activity.get('calories', 0),
                    activity.get('averageHR', 0) or None,
                    activity.get('maxHR', 0) or None,
                    datetime.now()
                ))
                activities_saved += 1
            
            print(f"    🏃 Saved {len(activities)} activities")
            
        except Exception as e:
            print(f"    ❌ Activities failed: {e}")
        
        try:
            # Get and save heart rate data
            hr_data = client.get_heart_rates(date_str)
            if hr_data:
                cur.execute("""
                    INSERT INTO garmin.staging_heart_rate 
                    (date, resting_heart_rate, min_heart_rate, max_heart_rate, extracted_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (date) DO UPDATE SET
                    resting_heart_rate = EXCLUDED.resting_heart_rate,
                    min_heart_rate = EXCLUDED.min_heart_rate,
                    max_heart_rate = EXCLUDED.max_heart_rate,
                    extracted_at = EXCLUDED.extracted_at
                """, (
                    current_date.date(),
                    hr_data.get('restingHeartRate'),
                    hr_data.get('minHeartRate'),
                    hr_data.get('maxHeartRate'),
                    datetime.now()
                ))
                hr_saved += 1
                print(f"    ❤️  Saved heart rate data")
        
        except Exception as e:
            print(f"    ❌ Heart rate failed: {e}")
        
        try:
            # Get and save daily stats
            stats = client.get_stats(date_str)
            if stats:
                cur.execute("""
                    INSERT INTO garmin.staging_daily_summary 
                    (date, total_steps, total_calories, active_calories, bmr_calories, 
                     total_distance_meters, floors_climbed, intensity_minutes, extracted_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (date) DO UPDATE SET
                    total_steps = EXCLUDED.total_steps,
                    total_calories = EXCLUDED.total_calories,
                    active_calories = EXCLUDED.active_calories,
                    bmr_calories = EXCLUDED.bmr_calories,
                    total_distance_meters = EXCLUDED.total_distance_meters,
                    floors_climbed = EXCLUDED.floors_climbed,
                    intensity_minutes = EXCLUDED.intensity_minutes,
                    extracted_at = EXCLUDED.extracted_at
                """, (
                    current_date.date(),
                    stats.get('totalSteps', 0),
                    stats.get('totalKilocalories', 0),
                    stats.get('activeKilocalories', 0), 
                    stats.get('bmrKilocalories', 0),
                    stats.get('totalDistance', 0) * 1000 if stats.get('totalDistance') else 0,  # Convert to meters
                    stats.get('floorsAscended', 0),
                    stats.get('intensityMinutesGoal', 0),
                    datetime.now()
                ))
                stats_saved += 1
                print(f"    📈 Saved daily stats")
                
        except Exception as e:
            print(f"    ❌ Daily stats failed: {e}")
    
    # Commit all changes
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"\n🎉 Data extraction complete!")
    print(f"   Activities: {activities_saved}")
    print(f"   Heart Rate Records: {hr_saved}")
    print(f"   Daily Stats: {stats_saved}")
    
    return activities_saved, hr_saved, stats_saved

if __name__ == "__main__":
    try:
        save_garmin_data()
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()