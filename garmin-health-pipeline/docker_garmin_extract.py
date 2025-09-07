#!/usr/bin/env python3
"""
Extract Garmin data and save to database - designed to run inside Docker container
"""
import json
from datetime import datetime, timedelta
from garminconnect import Garmin
import psycopg2
import os

def save_garmin_data():
    """Extract and save Garmin data to database"""
    
    # Get credentials from environment
    email = os.getenv('GARMIN_EMAIL', 'omer.haimovitz@gmail.com')
    password = os.getenv('GARMIN_PASSWORD', 'Gunrvnkl2!')
    
    print("🔗 Connecting to Garmin Connect...")
    client = Garmin(email, password)
    client.login()
    print("✅ Connected to Garmin!")
    
    # Connect to PostgreSQL (using Docker internal networking)
    print("🔗 Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host="postgres",  # Docker service name
        port="5432", 
        database="longevity",
        user="postgres",
        password="postgres"
    )
    cur = conn.cursor()
    print("✅ Connected to database!")
    
    # Create a summary table to store processed metrics
    cur.execute("""
        CREATE TABLE IF NOT EXISTS garmin.processed_daily_metrics (
            date DATE PRIMARY KEY,
            total_steps INTEGER,
            total_calories INTEGER,
            active_calories INTEGER,
            resting_heart_rate INTEGER,
            max_heart_rate INTEGER,
            activities_count INTEGER,
            total_distance_km DECIMAL(10,2),
            total_activity_duration_minutes INTEGER,
            biological_age DECIMAL(5,2),
            longevity_score INTEGER,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Extract data for last 14 days to get a good dataset
    end_date = datetime.now()
    start_date = end_date - timedelta(days=14)
    
    print(f"📊 Processing data from {start_date.date()} to {end_date.date()}...")
    
    total_activities = 0
    total_days = 0
    
    daily_metrics = []
    
    for i in range(14):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        
        print(f"  📅 Processing {date_str}...")
        
        day_data = {
            'date': current_date.date(),
            'total_steps': 0,
            'total_calories': 0,
            'active_calories': 0,
            'resting_heart_rate': None,
            'max_heart_rate': None,
            'activities_count': 0,
            'total_distance_km': 0,
            'total_activity_duration_minutes': 0
        }
        
        try:
            # Get activities for this day
            activities = client.get_activities_by_date(date_str, date_str)
            day_data['activities_count'] = len(activities)
            
            total_distance = 0
            total_duration = 0
            
            for activity in activities:
                # Save individual activity
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
                    activity.get('averageHR') or None,
                    activity.get('maxHR') or None,
                    datetime.now()
                ))
                
                # Accumulate for daily summary
                total_distance += activity.get('distance', 0) or 0
                total_duration += activity.get('duration', 0) or 0
            
            day_data['total_distance_km'] = round(total_distance / 1000, 2)
            day_data['total_activity_duration_minutes'] = round(total_duration / 60)
            total_activities += len(activities)
            
            print(f"    🏃 {len(activities)} activities")
            
        except Exception as e:
            print(f"    ❌ Activities failed: {e}")
        
        try:
            # Get heart rate data
            hr_data = client.get_heart_rates(date_str)
            if hr_data:
                day_data['resting_heart_rate'] = hr_data.get('restingHeartRate')
                day_data['max_heart_rate'] = hr_data.get('maxHeartRate')
                
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
                print(f"    ❤️  Heart rate data")
        
        except Exception as e:
            print(f"    ❌ Heart rate failed: {e}")
        
        try:
            # Get daily stats
            stats = client.get_stats(date_str)
            if stats:
                day_data['total_steps'] = stats.get('totalSteps', 0)
                day_data['total_calories'] = stats.get('totalKilocalories', 0)
                day_data['active_calories'] = stats.get('activeKilocalories', 0)
                
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
                    stats.get('totalDistance', 0) * 1000 if stats.get('totalDistance') else 0,
                    stats.get('floorsAscended', 0),
                    stats.get('intensityMinutesGoal', 0),
                    datetime.now()
                ))
                print(f"    📈 Daily stats")
                
        except Exception as e:
            print(f"    ❌ Daily stats failed: {e}")
        
        daily_metrics.append(day_data)
        total_days += 1
    
    # Calculate biological age and longevity metrics
    print("\n🧬 Calculating health metrics...")
    
    # Simple biological age calculation based on real data
    avg_resting_hr = sum(d['resting_heart_rate'] for d in daily_metrics if d['resting_heart_rate']) / \
                     len([d for d in daily_metrics if d['resting_heart_rate']])
    avg_steps = sum(d['total_steps'] for d in daily_metrics) / len(daily_metrics)
    activity_frequency = sum(1 for d in daily_metrics if d['activities_count'] > 0) / len(daily_metrics)
    
    # Biological age calculation (simplified)
    chronological_age = 30  # Assuming 30 years old
    hr_factor = max(0, (avg_resting_hr - 60) * 0.1)  # Lower RHR = younger
    activity_factor = (10000 - avg_steps) / 1000 * 0.1  # More steps = younger
    exercise_factor = (0.5 - activity_frequency) * 5  # More exercise days = younger
    
    biological_age = chronological_age + hr_factor + activity_factor + exercise_factor
    biological_age = max(20, min(45, biological_age))  # Clamp between 20-45
    
    longevity_score = max(60, min(95, int(100 - (biological_age - chronological_age) * 3)))
    
    print(f"📊 Health Analysis:")
    print(f"   Average Resting HR: {avg_resting_hr:.1f} bpm")
    print(f"   Average Steps: {avg_steps:.0f}/day")
    print(f"   Activity Frequency: {activity_frequency:.1%}")
    print(f"   Biological Age: {biological_age:.1f} years")
    print(f"   Longevity Score: {longevity_score}/100")
    
    # Save processed daily metrics
    for day_data in daily_metrics:
        cur.execute("""
            INSERT INTO garmin.processed_daily_metrics 
            (date, total_steps, total_calories, active_calories, resting_heart_rate, 
             max_heart_rate, activities_count, total_distance_km, total_activity_duration_minutes,
             biological_age, longevity_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (date) DO UPDATE SET
            total_steps = EXCLUDED.total_steps,
            total_calories = EXCLUDED.total_calories,
            active_calories = EXCLUDED.active_calories,
            resting_heart_rate = EXCLUDED.resting_heart_rate,
            max_heart_rate = EXCLUDED.max_heart_rate,
            activities_count = EXCLUDED.activities_count,
            total_distance_km = EXCLUDED.total_distance_km,
            total_activity_duration_minutes = EXCLUDED.total_activity_duration_minutes,
            biological_age = EXCLUDED.biological_age,
            longevity_score = EXCLUDED.longevity_score,
            processed_at = EXCLUDED.processed_at
        """, (
            day_data['date'],
            day_data['total_steps'],
            day_data['total_calories'],
            day_data['active_calories'],
            day_data['resting_heart_rate'],
            day_data['max_heart_rate'],
            day_data['activities_count'],
            day_data['total_distance_km'],
            day_data['total_activity_duration_minutes'],
            biological_age,
            longevity_score
        ))
    
    # Commit all changes
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"\n🎉 Data extraction complete!")
    print(f"   📅 Days processed: {total_days}")
    print(f"   🏃 Activities: {total_activities}")
    print(f"   🧬 Biological age: {biological_age:.1f}")
    print(f"   📈 Longevity score: {longevity_score}")
    
    return total_activities, total_days, biological_age, longevity_score

if __name__ == "__main__":
    try:
        save_garmin_data()
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()