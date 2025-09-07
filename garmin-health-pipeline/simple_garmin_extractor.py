#!/usr/bin/env python3
"""
Simplified Garmin extractor that focuses on getting key data reliably
"""
import os
import json
from datetime import datetime, timedelta
from garminconnect import Garmin
import pandas as pd
from sqlalchemy import create_engine

def extract_and_save_data():
    """Extract key Garmin data and save to database"""
    
    # Configuration
    email = "omer.haimovitz@gmail.com" 
    password = "Gunrvnkl2!"
    db_url = "postgresql://postgres:postgres@localhost:5432/longevity"
    
    print("🔗 Connecting to Garmin Connect...")
    client = Garmin(email, password)
    client.login()
    print("✅ Connected successfully!")
    
    # Connect to database
    engine = create_engine(db_url)
    
    # Extract data for last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    all_activities = []
    all_heart_rate = []
    all_daily_stats = []
    
    print(f"📊 Extracting data from {start_date.date()} to {end_date.date()}...")
    
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        
        print(f"  📅 Processing {date_str}...")
        
        try:
            # Get activities for this date
            activities = client.get_activities_by_date(date_str, date_str)
            for activity in activities:
                activity['extracted_date'] = date_str
                all_activities.append(activity)
            print(f"    🏃 Found {len(activities)} activities")
            
        except Exception as e:
            print(f"    ❌ Activities failed: {e}")
        
        try:
            # Get heart rate data
            hr_data = client.get_heart_rates(date_str)
            if hr_data:
                hr_data['date'] = date_str
                all_heart_rate.append(hr_data)
                print(f"    ❤️  Got heart rate data")
            
        except Exception as e:
            print(f"    ❌ Heart rate failed: {e}")
        
        try:
            # Get daily stats
            stats = client.get_stats(date_str)
            if stats:
                stats['date'] = date_str
                all_daily_stats.append(stats)
                print(f"    📈 Got daily stats")
                
        except Exception as e:
            print(f"    ❌ Daily stats failed: {e}")
    
    print(f"\n💾 Saving to database...")
    
    # Save activities
    if all_activities:
        activities_df = pd.DataFrame(all_activities)
        activities_df.to_sql('raw_activities', engine, schema='garmin', if_exists='replace', index=False)
        print(f"✅ Saved {len(all_activities)} activities")
    
    # Save heart rate data
    if all_heart_rate:
        hr_df = pd.DataFrame(all_heart_rate)
        hr_df.to_sql('raw_heart_rate', engine, schema='garmin', if_exists='replace', index=False)
        print(f"✅ Saved {len(all_heart_rate)} heart rate records")
    
    # Save daily stats
    if all_daily_stats:
        stats_df = pd.DataFrame(all_daily_stats)
        stats_df.to_sql('raw_daily_stats', engine, schema='garmin', if_exists='replace', index=False)
        print(f"✅ Saved {len(all_daily_stats)} daily stats records")
    
    print(f"\n🎉 Data extraction complete!")
    return len(all_activities), len(all_heart_rate), len(all_daily_stats)

if __name__ == "__main__":
    try:
        activities, heart_rate, stats = extract_and_save_data()
        print(f"\n📊 Summary:")
        print(f"   Activities: {activities}")
        print(f"   Heart Rate Records: {heart_rate}")  
        print(f"   Daily Stats: {stats}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()