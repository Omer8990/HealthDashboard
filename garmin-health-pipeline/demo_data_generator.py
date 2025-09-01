#!/usr/bin/env python3
"""
Demo data generator for Garmin health data
Creates realistic health metrics data for demo purposes
"""
import os
import random
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine
import json

# Database connection
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/longevity"

def generate_daily_metrics(start_date, days=30):
    """Generate realistic daily health metrics"""
    data = []
    base_resting_hr = 65 + random.randint(-5, 5)  # Individual baseline
    base_weight = 70 + random.randint(-10, 20)     # Individual baseline
    
    for i in range(days):
        date = start_date + timedelta(days=i)
        
        # Heart rate with realistic variation
        resting_hr = base_resting_hr + random.randint(-3, 3)
        avg_hr = resting_hr + random.randint(15, 25)
        max_hr = avg_hr + random.randint(30, 50)
        
        # Sleep with weekday/weekend variation
        is_weekend = date.weekday() >= 5
        base_sleep = 8.0 if is_weekend else 7.5
        sleep_duration = base_sleep + random.uniform(-1.5, 1.0)
        deep_sleep = sleep_duration * random.uniform(0.15, 0.25)
        rem_sleep = sleep_duration * random.uniform(0.20, 0.25)
        light_sleep = sleep_duration - deep_sleep - rem_sleep
        
        # Sleep score based on duration and efficiency
        sleep_score = min(100, int(70 + (sleep_duration - 6) * 10 + random.randint(-10, 10)))
        
        # Stress levels (higher on weekdays)
        base_stress = 35 if is_weekend else 45
        avg_stress = base_stress + random.randint(-10, 15)
        
        # Activity levels
        steps = random.randint(6000, 15000)
        distance = steps * random.uniform(0.0006, 0.0008)  # km
        active_minutes = random.randint(30, 120)
        intensity_minutes = random.randint(15, 60)
        
        # Calories
        bmr = 1600 + random.randint(-200, 200)
        active_calories = active_minutes * random.randint(8, 12)
        total_calories = bmr + active_calories
        
        # Weight fluctuation
        weight = base_weight + random.uniform(-0.5, 0.5)
        bmi = weight / (1.75 ** 2)  # Assuming 1.75m height
        body_fat = random.uniform(12, 18)  # Athletic range
        
        record = {
            'date': date.date(),
            'resting_heart_rate': resting_hr,
            'avg_heart_rate': round(avg_hr, 1),
            'max_heart_rate': max_hr,
            'min_heart_rate': resting_hr - random.randint(0, 5),
            'hrv_score': random.randint(35, 65),
            'sleep_duration_hours': round(sleep_duration, 2),
            'deep_sleep_hours': round(deep_sleep, 2),
            'light_sleep_hours': round(light_sleep, 2),
            'rem_sleep_hours': round(rem_sleep, 2),
            'sleep_efficiency': round(random.uniform(85, 95), 1),
            'sleep_score': sleep_score,
            'avg_stress_level': avg_stress,
            'max_stress_level': avg_stress + random.randint(10, 20),
            'low_stress_percentage': round(random.uniform(40, 60), 1),
            'medium_stress_percentage': round(random.uniform(25, 35), 1),
            'high_stress_percentage': round(random.uniform(5, 15), 1),
            'total_steps': steps,
            'distance_km': round(distance, 2),
            'floors_climbed': random.randint(5, 25),
            'active_minutes': active_minutes,
            'intensity_minutes': intensity_minutes,
            'sedentary_minutes': 1440 - active_minutes - int(sleep_duration * 60),
            'total_calories': total_calories,
            'active_calories': active_calories,
            'bmr_calories': bmr,
            'weight_kg': round(weight, 1),
            'bmi': round(bmi, 1),
            'body_fat_percentage': round(body_fat, 1),
            'muscle_mass_kg': round(weight * (1 - body_fat/100) * 0.45, 1),
            'body_battery': random.randint(60, 90),
            'training_readiness': random.randint(70, 95),
            'recovery_time_hours': random.randint(0, 24)
        }
        data.append(record)
    
    return data

def generate_activities(start_date, days=30):
    """Generate realistic activity data"""
    activities = []
    activity_types = ['running', 'cycling', 'swimming', 'walking', 'strength_training', 'yoga']
    
    for i in range(days):
        date = start_date + timedelta(days=i)
        
        # 70% chance of having an activity
        if random.random() < 0.7:
            activity_type = random.choice(activity_types)
            activity_id = int(f"{date.year}{date.month:02d}{date.day:02d}{random.randint(100, 999)}")
            
            if activity_type == 'running':
                duration = random.uniform(20, 90)  # minutes
                distance = duration * random.uniform(0.15, 0.25)  # km
                pace = duration / distance  # min/km
                calories = int(duration * random.uniform(10, 15))
                avg_hr = random.randint(150, 170)
                max_hr = avg_hr + random.randint(15, 25)
                
            elif activity_type == 'cycling':
                duration = random.uniform(30, 120)
                distance = duration * random.uniform(0.4, 0.8)
                pace = duration / distance
                calories = int(duration * random.uniform(8, 12))
                avg_hr = random.randint(135, 155)
                max_hr = avg_hr + random.randint(20, 30)
                
            elif activity_type == 'walking':
                duration = random.uniform(30, 90)
                distance = duration * random.uniform(0.08, 0.12)
                pace = duration / distance
                calories = int(duration * random.uniform(4, 6))
                avg_hr = random.randint(110, 130)
                max_hr = avg_hr + random.randint(10, 20)
                
            else:  # Other activities
                duration = random.uniform(30, 60)
                distance = 0
                pace = 0
                calories = int(duration * random.uniform(6, 10))
                avg_hr = random.randint(120, 150)
                max_hr = avg_hr + random.randint(15, 25)
            
            activity = {
                'activity_id': activity_id,
                'activity_type': activity_type,
                'activity_name': f"{activity_type.title()} Activity",
                'start_time': datetime.combine(date, datetime.min.time().replace(
                    hour=random.randint(6, 19), 
                    minute=random.randint(0, 59)
                )),
                'end_time': None,
                'duration_minutes': round(duration, 1),
                'distance_km': round(distance, 2) if distance > 0 else None,
                'pace_min_per_km': round(pace, 2) if distance > 0 else None,
                'speed_kmh': round(60/pace, 1) if distance > 0 and pace > 0 else None,
                'calories': calories,
                'avg_heart_rate': avg_hr,
                'max_heart_rate': max_hr,
                'elevation_gain_m': random.randint(0, 200) if activity_type in ['running', 'cycling'] else 0,
                'elevation_loss_m': random.randint(0, 200) if activity_type in ['running', 'cycling'] else 0,
                'avg_cadence': random.randint(160, 180) if activity_type == 'running' else None,
                'training_effect': random.choice(['Recovery', 'Base', 'Tempo', 'Threshold']),
                'aerobic_effect': round(random.uniform(1.0, 4.5), 1),
                'anaerobic_effect': round(random.uniform(0.0, 3.0), 1),
                'training_load': random.randint(50, 300),
                'recovery_time_hours': random.randint(6, 48),
                'vo2_max': round(random.uniform(45, 60), 1)
            }
            activities.append(activity)
    
    return activities

def calculate_biological_age_metrics(daily_metrics, activities):
    """Calculate realistic biological age metrics based on health data"""
    
    # Get recent data (last 30 days)
    recent_metrics = daily_metrics[-30:] if len(daily_metrics) >= 30 else daily_metrics
    recent_activities = activities[-30:] if len(activities) >= 30 else activities
    
    # Calculate averages
    avg_resting_hr = sum(m['resting_heart_rate'] for m in recent_metrics) / len(recent_metrics)
    avg_sleep_score = sum(m['sleep_score'] for m in recent_metrics) / len(recent_metrics)
    avg_stress = sum(m['avg_stress_level'] for m in recent_metrics) / len(recent_metrics)
    avg_steps = sum(m['total_steps'] for m in recent_metrics) / len(recent_metrics)
    
    # Activity frequency
    activity_days = len([a for a in recent_activities if a['duration_minutes'] > 20])
    activity_frequency = activity_days / 30.0
    
    # VO2 max estimate (simplified)
    if recent_activities:
        avg_vo2 = sum(a.get('vo2_max', 50) for a in recent_activities) / len(recent_activities)
    else:
        avg_vo2 = 45
    
    # Calculate biological age (simplified algorithm)
    chronological_age = 30  # Assuming 30 years old
    
    # Heart rate factor (lower resting HR = younger)
    hr_factor = (avg_resting_hr - 60) * 0.1
    
    # Sleep factor (better sleep = younger)
    sleep_factor = (80 - avg_sleep_score) * 0.05
    
    # Stress factor (lower stress = younger)
    stress_factor = (avg_stress - 30) * 0.05
    
    # Activity factor (more active = younger)
    activity_factor = (activity_frequency - 0.5) * -5
    
    # VO2 max factor (higher VO2 = younger)
    vo2_factor = (50 - avg_vo2) * 0.2
    
    biological_age = chronological_age + hr_factor + sleep_factor + stress_factor + activity_factor + vo2_factor
    biological_age = max(20, min(50, biological_age))  # Clamp between 20-50
    
    # Aging velocity (positive = aging faster, negative = aging slower)
    aging_velocity = (biological_age - chronological_age) / chronological_age
    
    # Longevity score (0-100)
    longevity_score = max(0, min(100, int(100 - (biological_age - chronological_age) * 2 + random.randint(-5, 5))))
    
    return {
        'chronological_age': chronological_age,
        'biological_age': round(biological_age, 1),
        'aging_velocity': round(aging_velocity, 3),
        'longevity_score': longevity_score,
        'vo2_max_score': round(avg_vo2, 1),
        'hrv_score': round(sum(m['hrv_score'] for m in recent_metrics) / len(recent_metrics), 1),
        'sleep_score': round(avg_sleep_score, 1),
        'stress_score': round(100 - avg_stress, 1)
    }

def main():
    print("🚀 Generating demo health data...")
    
    # Connect to database
    engine = create_engine(DATABASE_URL)
    
    # Generate data for last 60 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    print("📊 Generating daily metrics...")
    daily_metrics = generate_daily_metrics(start_date, 60)
    
    print("🏃 Generating activities...")
    activities = generate_activities(start_date, 60)
    
    print("🧬 Calculating biological age metrics...")
    bio_metrics = calculate_biological_age_metrics(daily_metrics, activities)
    
    # Save to database
    print("💾 Saving to database...")
    
    # Daily metrics
    daily_df = pd.DataFrame(daily_metrics)
    daily_df.to_sql('daily_metrics', engine, schema='garmin', if_exists='replace', index=False)
    
    # Activities
    if activities:
        activities_df = pd.DataFrame(activities)
        activities_df.to_sql('activities', engine, schema='garmin', if_exists='replace', index=False)
    
    print(f"✅ Generated data summary:")
    print(f"   📅 {len(daily_metrics)} days of daily metrics")
    print(f"   🏃 {len(activities)} activities")
    print(f"   🧬 Biological age: {bio_metrics['biological_age']} years (chronological: {bio_metrics['chronological_age']})")
    print(f"   📈 Longevity score: {bio_metrics['longevity_score']}/100")
    print(f"   ⚡ Aging velocity: {bio_metrics['aging_velocity']:+.3f}")
    print(f"\n🌐 Data is now available for the dashboard!")

if __name__ == "__main__":
    main()