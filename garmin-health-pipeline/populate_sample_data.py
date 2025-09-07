#!/usr/bin/env python3
"""
Populate sample health data to see the dashboard working with realistic data
"""
import os
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import random
import json

def populate_sample_data():
    """Insert realistic sample health data for testing"""
    
    # Database connection
    db_url = "postgresql://postgres:postgres@localhost:5432/longevity"
    engine = create_engine(db_url)
    
    print("📊 Populating sample health data...")
    
    # Generate 30 days of realistic data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    activities_data = []
    heart_rate_data = []
    sleep_data = []
    stress_data = []
    daily_metrics = []
    
    for i in range(30):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Generate realistic activities (3-4 per week)
        if random.random() < 0.5:  # 50% chance of activity each day
            activity_types = ['running', 'cycling', 'strength_training', 'yoga', 'walking']
            activity_type = random.choice(activity_types)
            
            base_duration = {'running': 35, 'cycling': 60, 'strength_training': 45, 'yoga': 60, 'walking': 25}
            duration = base_duration.get(activity_type, 30) + random.randint(-10, 20)
            
            activities_data.append({
                'activity_id': f'fake_{i}_{activity_type}',
                'activity_type': activity_type,
                'activity_name': f'{activity_type.title()} Session',
                'start_time': current_date.replace(hour=random.randint(6, 19)),
                'duration_seconds': duration * 60,
                'distance_meters': random.randint(2000, 8000) if activity_type in ['running', 'cycling'] else 0,
                'calories': duration * random.randint(8, 15),
                'avg_heart_rate': random.randint(120, 170),
                'max_heart_rate': random.randint(160, 190),
                'avg_speed': random.uniform(2.0, 6.0) if activity_type == 'running' else 0,
                'elevation_gain': random.randint(0, 300),
                'extracted_at': datetime.now()
            })
        
        # Generate heart rate data
        base_rhr = 47 + random.randint(-3, 8)  # Your elite resting HR
        heart_rate_data.append({
            'date': current_date.date(),
            'resting_heart_rate': base_rhr,
            'min_heart_rate': base_rhr - random.randint(2, 5),
            'max_heart_rate': random.randint(175, 195),
            'avg_heart_rate': base_rhr + random.randint(30, 50),
            'extracted_at': datetime.now()
        })
        
        # Generate sleep data
        sleep_hours = 7.0 + random.uniform(-1.5, 1.5)
        deep_sleep_pct = random.uniform(0.15, 0.25)
        rem_sleep_pct = random.uniform(0.15, 0.25)
        light_sleep_pct = 1.0 - deep_sleep_pct - rem_sleep_pct - 0.05  # 5% awake
        
        total_sleep_sec = int(sleep_hours * 3600)
        sleep_data.append({
            'date': current_date.date(),
            'total_sleep_seconds': total_sleep_sec,
            'deep_sleep_seconds': int(total_sleep_sec * deep_sleep_pct),
            'light_sleep_seconds': int(total_sleep_sec * light_sleep_pct),
            'rem_sleep_seconds': int(total_sleep_sec * rem_sleep_pct),
            'awake_seconds': int(total_sleep_sec * 0.05),
            'sleep_score': random.randint(75, 95),
            'avg_respiration': random.uniform(14.0, 18.0),
            'avg_spo2': random.uniform(95.0, 98.5),
            'extracted_at': datetime.now()
        })
        
        # Generate stress data
        avg_stress = random.randint(15, 45)
        stress_data.append({
            'date': current_date.date(),
            'avg_stress_level': avg_stress,
            'max_stress_level': avg_stress + random.randint(10, 30),
            'stress_duration_seconds': random.randint(18000, 50400),  # 5-14 hours
            'low_stress_duration': random.randint(28800, 43200),    # 8-12 hours
            'medium_stress_duration': random.randint(7200, 18000),   # 2-5 hours
            'high_stress_duration': random.randint(0, 3600),        # 0-1 hour
            'extracted_at': datetime.now()
        })
        
        # Calculate processed daily metrics
        steps = random.randint(8000, 16000)
        distance_km = steps * 0.0008  # Rough conversion
        activities_count = len([a for a in activities_data if a['start_time'].date() == current_date.date()])
        
        # Calculate biological age (simplified algorithm)
        base_bio_age = 22  # Your chronological age
        
        # Adjustments based on metrics
        rhr_adjustment = (base_rhr - 45) * 0.1  # Lower RHR = younger bio age
        sleep_adjustment = (sleep_hours - 8) * 0.2  # Better sleep = younger
        activity_adjustment = -activities_count * 0.3  # More activity = younger
        stress_adjustment = (avg_stress - 20) * 0.05  # Lower stress = younger
        
        bio_age = base_bio_age + rhr_adjustment + sleep_adjustment + activity_adjustment + stress_adjustment
        bio_age = max(18, min(35, bio_age))  # Keep in reasonable range
        
        # Longevity score (0-100)
        longevity_score = max(70, min(100, 100 - (bio_age - 18) * 2))
        
        daily_metrics.append({
            'date': current_date.date(),
            'resting_heart_rate': base_rhr,
            'total_steps': steps,
            'total_distance_km': round(distance_km, 2),
            'total_calories': random.randint(2200, 3200),
            'activities_count': activities_count,
            'biological_age': round(bio_age, 1),
            'longevity_score': int(longevity_score),
            'sleep_score': sleep_data[-1]['sleep_score'],
            'stress_score': 100 - avg_stress,  # Inverse of stress level
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        })
    
    # Save to database
    print("💾 Saving to database...")
    
    # Activities
    if activities_data:
        df = pd.DataFrame(activities_data)
        df.to_sql('staging_activities', engine, schema='garmin', if_exists='replace', index=False)
        print(f"✅ Saved {len(activities_data)} activities")
    
    # Heart rate
    if heart_rate_data:
        df = pd.DataFrame(heart_rate_data)
        df.to_sql('staging_heart_rate', engine, schema='garmin', if_exists='replace', index=False)
        print(f"✅ Saved {len(heart_rate_data)} heart rate records")
    
    # Sleep
    if sleep_data:
        df = pd.DataFrame(sleep_data)
        df.to_sql('staging_sleep', engine, schema='garmin', if_exists='replace', index=False)
        print(f"✅ Saved {len(sleep_data)} sleep records")
    
    # Stress
    if stress_data:
        df = pd.DataFrame(stress_data)
        df.to_sql('staging_stress', engine, schema='garmin', if_exists='replace', index=False)
        print(f"✅ Saved {len(stress_data)} stress records")
    
    # Processed daily metrics
    if daily_metrics:
        df = pd.DataFrame(daily_metrics)
        df.to_sql('processed_daily_metrics', engine, schema='garmin', if_exists='replace', index=False)
        print(f"✅ Saved {len(daily_metrics)} processed daily metrics")
    
    # Generate some health insights
    with engine.connect() as conn:
        latest_metrics = daily_metrics[-1]
        conn.execute(text("""
            INSERT INTO garmin.health_insights (date, biological_age, aging_velocity, longevity_score, activity_consistency, recovery_score)
            VALUES (:date, :bio_age, :velocity, :longevity, :consistency, :recovery)
            ON CONFLICT (date) DO UPDATE SET
                biological_age = :bio_age,
                aging_velocity = :velocity,
                longevity_score = :longevity,
                activity_consistency = :consistency,
                recovery_score = :recovery,
                updated_at = CURRENT_TIMESTAMP
        """), {
            'date': latest_metrics['date'],
            'bio_age': latest_metrics['biological_age'],
            'velocity': round((latest_metrics['biological_age'] - 22) / 22, 3),
            'longevity': latest_metrics['longevity_score'],
            'consistency': 85,  # Based on activity frequency
            'recovery': latest_metrics['sleep_score']
        })
        conn.commit()
    
    print(f"\n🎉 Sample data population complete!")
    print(f"📊 Summary:")
    print(f"   Activities: {len(activities_data)}")
    print(f"   Heart Rate Records: {len(heart_rate_data)}")
    print(f"   Sleep Records: {len(sleep_data)}")
    print(f"   Daily Metrics: {len(daily_metrics)}")
    print(f"   Latest Bio Age: {daily_metrics[-1]['biological_age']}")
    print(f"   Latest Longevity Score: {daily_metrics[-1]['longevity_score']}")
    print(f"\n✨ Your dashboard should now show real data!")

if __name__ == "__main__":
    try:
        populate_sample_data()
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()