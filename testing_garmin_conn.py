#!/usr/bin/env python3
"""
Comprehensive examples for extracting Garmin Connect data
Perfect for Airflow DAGs or scheduled pipelines
"""

from garminconnect import Garmin
from datetime import datetime, timedelta
import json
import pandas as pd

def setup_garmin_client(username, password):
    """Initialize and login to Garmin Connect"""
    try:
        client = Garmin(username, password)
        client.login()
        print("✅ Successfully logged in to Garmin Connect")
        return client
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def extract_daily_health_metrics(client, target_date=None):
    """Extract comprehensive daily health data"""
    if not target_date:
        target_date = datetime.now().date()
    
    data = {}
    
    try:
        # Use get_stats() for daily summary data
        stats = client.get_stats(target_date.strftime('%Y-%m-%d'))
        data['stats'] = stats
        
        # Try to get steps data - handle if it's a list
        try:
            steps = client.get_steps_data(target_date.strftime('%Y-%m-%d'))
            if isinstance(steps, list) and len(steps) > 0:
                steps = steps[0]  # Take first item if it's a list
            data['steps'] = steps
        except Exception as e:
            print(f"Steps data error: {e}")
            data['steps'] = None
        
        # Try heart rate data
        try:
            hr_data = client.get_heart_rates(target_date.strftime('%Y-%m-%d'))
            if isinstance(hr_data, list) and len(hr_data) > 0:
                hr_data = hr_data[0]
            data['heart_rate'] = hr_data
        except Exception as e:
            print(f"Heart rate data error: {e}")
            data['heart_rate'] = None
        
        # Try sleep data
        try:
            sleep = client.get_sleep_data(target_date.strftime('%Y-%m-%d'))
            if isinstance(sleep, list) and len(sleep) > 0:
                sleep = sleep[0]
            data['sleep'] = sleep
        except Exception as e:
            print(f"Sleep data error: {e}")
            data['sleep'] = None
        
        # Try body composition
        try:
            body = client.get_body_composition(target_date.strftime('%Y-%m-%d'))
            if isinstance(body, dict):
                data['body'] = body
            else:
                data['body'] = None
        except Exception as e:
            print(f"Body composition error: {e}")
            data['body'] = None
        
        return data
        
    except Exception as e:
        print(f"❌ Error extracting daily metrics: {e}")
        return None

def extract_recent_activities(client, limit=10):
    """Get recent activities with basic info"""
    try:
        activities = client.get_activities(0, limit)
        
        simplified_activities = []
        for activity in activities:
            # Just extract the basic data without trying to get detailed activity info
            activity_data = {
                'id': activity.get('activityId'),
                'name': activity.get('activityName'),
                'type': activity.get('activityType', {}).get('typeKey') if isinstance(activity.get('activityType'), dict) else None,
                'start_time': activity.get('startTimeLocal'),
                'duration': activity.get('duration'),
                'distance': activity.get('distance'),
                'calories': activity.get('calories'),
                'avg_heart_rate': activity.get('averageHR'),
                'max_heart_rate': activity.get('maxHR'),
                'elevation_gain': activity.get('elevationGain'),
                'avg_speed': activity.get('averageSpeed'),
                'max_speed': activity.get('maxSpeed')
            }
            
            simplified_activities.append(activity_data)
            
        return simplified_activities
        
    except Exception as e:
        print(f"❌ Error extracting activities: {e}")
        return []

def extract_user_profile(client):
    """Get user profile and device information"""
    try:
        profile = client.get_full_name()
        settings = client.get_user_settings()
        devices = client.get_device_settings()
        
        return {
            'profile': profile,
            'user_settings': settings,
            'devices': devices
        }
    except Exception as e:
        print(f"❌ Error extracting profile: {e}")
        return None

def extract_date_range_data(client, start_date, end_date):
    """Extract data for a date range - useful for backfilling"""
    all_data = []
    
    current_date = start_date
    while current_date <= end_date:
        print(f"📊 Extracting data for {current_date}")
        
        daily_data = extract_daily_health_metrics(client, current_date)
        if daily_data:
            daily_data['date'] = current_date.isoformat()
            all_data.append(daily_data)
            
        current_date += timedelta(days=1)
    
    return all_data

def airflow_compatible_extract(username, password, target_date=None):
    """
    Main function suitable for Airflow DAG
    Returns structured data ready for storage
    """
    if not target_date:
        target_date = datetime.now().date()
    
    client = setup_garmin_client(username, password)
    if not client:
        raise Exception("Failed to authenticate with Garmin Connect")
    
    # Extract all data
    daily_metrics = extract_daily_health_metrics(client, target_date)
    recent_activities = extract_recent_activities(client, 5)
    
    return {
        'extraction_date': datetime.now().isoformat(),
        'target_date': target_date.isoformat(),
        'daily_metrics': daily_metrics,
        'recent_activities': recent_activities
    }

# Example usage for testing
if __name__ == "__main__":
    # Replace with your credentials
    USERNAME = "<username>"
    PASSWORD = "<pass>"
    
    client = setup_garmin_client(USERNAME, PASSWORD)
    
    if client:
        # First, let's explore what methods are actually available
        print("=== AVAILABLE METHODS ===")
        methods = [method for method in dir(client) if not method.startswith('_')]
        print("Available client methods:", methods[:10])  # Show first 10
        
        # Example 1: Try get_stats method
        print("\n=== DAILY STATS ===")
        try:
            today_str = datetime.now().strftime('%Y-%m-%d')
            stats = client.get_stats(today_str)
            print("Stats data structure:", type(stats))
            if isinstance(stats, dict):
                print("Stats keys:", list(stats.keys())[:10])
            print(json.dumps(stats, indent=2, default=str)[:500] + "...")
        except Exception as e:
            print(f"Stats error: {e}")
        
        # Example 2: Activities data
        print("\n=== RECENT ACTIVITIES ===")
        try:
            activities = client.get_activities(0, 3)
            print(f"Found {len(activities)} activities")
            if activities:
                print("First activity keys:", list(activities[0].keys())[:10])
                for i, activity in enumerate(activities[:2]):
                    print(f"Activity {i+1}: {activity.get('activityName', 'Unknown')}")
        except Exception as e:
            print(f"Activities error: {e}")
        
        # Example 3: Simple daily data extraction
        print("\n=== SIMPLIFIED DAILY EXTRACTION ===")
        simple_data = extract_daily_health_metrics(client)
        if simple_data:
            print("Successfully extracted daily data!")
            print(json.dumps(simple_data, indent=2, default=str)[:800] + "...")
        else:
            print("Failed to extract daily data")
