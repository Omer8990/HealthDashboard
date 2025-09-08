#!/usr/bin/env python3
"""
Direct test of Garmin Connect authentication
Run this locally to debug auth issues
"""
import os
import sys
from datetime import datetime, timedelta

try:
    from garminconnect import Garmin, GarminConnectAuthenticationError
except ImportError:
    print("❌ garminconnect not installed. Run: pip install garminconnect")
    sys.exit(1)

def test_garmin_auth():
    """Test Garmin authentication with various approaches"""
    
    # Try to load from .env file
    env_path = "/Users/omer8990/PythonProjects/HealthDashboard/mvp/.env"
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('GARMIN_EMAIL='):
                    email = line.split('=', 1)[1].strip()
                elif line.startswith('GARMIN_PASSWORD='):
                    password = line.split('=', 1)[1].strip()
    else:
        email = input("Enter Garmin email: ").strip()
        password = input("Enter Garmin password: ").strip()
    
    if not email or not password:
        print("❌ Email and password are required")
        return False
    
    print(f"🔐 Testing authentication for: {email}")
    
    try:
        # Test with latest garminconnect
        print("📡 Connecting to Garmin Connect...")
        client = Garmin(email, password)
        
        # Try logout first to clear any session
        try:
            client.logout()
            print("🔄 Cleared any existing session")
        except:
            pass
        
        # Attempt login
        print("🔑 Attempting login...")
        client.login()
        print("✅ Login successful!")
        
        # Test a simple API call
        print("📊 Testing API access...")
        profile = client.get_user_profile()
        print(f"👤 Welcome {profile.get('displayName', 'User')}!")
        
        # Test activity data access
        yesterday = datetime.now() - timedelta(days=1)
        activities = client.get_activities_by_date(yesterday, yesterday)
        print(f"🏃 Found {len(activities)} activities for {yesterday.strftime('%Y-%m-%d')}")
        
        return True
        
    except GarminConnectAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\n🔍 Troubleshooting tips:")
        print("1. Check if your Garmin email and password are correct")
        print("2. Disable two-factor authentication temporarily")
        print("3. Check if your account is locked due to failed attempts")
        print("4. Try logging into connect.garmin.com manually first")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_garmin_auth()
    sys.exit(0 if success else 1)