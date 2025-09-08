#!/usr/bin/env python3
"""
Test script to check available Garmin Connect API methods
"""
import os
from garminconnect import Garmin
from datetime import datetime, timedelta

def main():
    # Get credentials
    email = "omer.haimovitz@gmail.com"
    password = "Gunrvnkl2!"
    
    try:
        # Connect to Garmin
        client = Garmin(email, password)
        client.login()
        print("✅ Successfully connected to Garmin Connect")
        
        # Test available methods
        print("\n📋 Available methods:")
        methods = [method for method in dir(client) if not method.startswith('_') and callable(getattr(client, method))]
        for method in sorted(methods)[:20]:  # Show first 20 methods
            print(f"   - {method}")
        
        # Try to get recent data
        print(f"\n📊 Testing data extraction...")
        
        # Test get_stats
        try:
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            stats = client.get_stats(yesterday.strftime("%Y-%m-%d"))
            print(f"✅ get_stats() works: {type(stats)}")
            if stats:
                print(f"   Keys: {list(stats.keys())[:10]}...")
        except Exception as e:
            print(f"❌ get_stats() failed: {e}")
        
        # Test get_heart_rates
        try:
            hr_data = client.get_heart_rates(yesterday.strftime("%Y-%m-%d"))
            print(f"✅ get_heart_rates() works: {type(hr_data)}")
            if hr_data:
                print(f"   Keys: {list(hr_data.keys())[:10]}...")
        except Exception as e:
            print(f"❌ get_heart_rates() failed: {e}")
            
        # Test get_activities
        try:
            activities = client.get_activities(0, 5)  # Get last 5 activities
            print(f"✅ get_activities() works: {len(activities)} activities found")
            if activities:
                print(f"   First activity keys: {list(activities[0].keys())[:10]}...")
        except Exception as e:
            print(f"❌ get_activities() failed: {e}")
            
        # Test get_sleep_data
        try:
            sleep_data = client.get_sleep_data(yesterday.strftime("%Y-%m-%d"))
            print(f"✅ get_sleep_data() works: {type(sleep_data)}")
            if sleep_data:
                print(f"   Keys: {list(sleep_data.keys())[:10]}...")
        except Exception as e:
            print(f"❌ get_sleep_data() failed: {e}")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    main()