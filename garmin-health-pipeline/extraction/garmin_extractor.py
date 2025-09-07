# extraction/garmin_extractor.py
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
from dataclasses import dataclass
from garminconnect import Garmin, GarminConnectAuthenticationError
import pandas as pd

from sqlalchemy import create_engine
from retrying import retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GarminConfig:
    """Configuration for Garmin Connect"""
    email: str
    password: str
    db_connection_string: str
    data_retention_days: int = 365
    
    @classmethod
    def from_env(cls):
        return cls(
            email=os.getenv('GARMIN_EMAIL'),
            password=os.getenv('GARMIN_PASSWORD'),
            db_connection_string=os.getenv('DATABASE_URL'),
            data_retention_days=int(os.getenv('DATA_RETENTION_DAYS', 365))
        )

class GarminDataExtractor:
    """Extract health metrics from Garmin Connect"""
    
    def __init__(self, config: GarminConfig):
        self.config = config
        self.client = None
        self.db_engine = create_engine(config.db_connection_string)
        
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def connect(self) -> None:
        """Establish connection to Garmin Connect"""
        try:
            self.client = Garmin(self.config.email, self.config.password)
            self.client.login()
            logger.info("Successfully connected to Garmin Connect")
        except GarminConnectAuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise
    
    def extract_activities(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Extract activity data for date range"""
        activities = []
        try:
            # Get activities list using available method
            activities_list = self.client.get_activities_by_date(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            
            for activity in activities_list:
                activity_id = activity['activityId']
                
                # Get additional activity details if available
                detailed = None
                try:
                    detailed = self.client.get_activity(activity_id)
                except Exception:
                    pass
                
                processed_activity = {
                    'activity_id': activity_id,
                    'activity_type': activity.get('activityType', {}).get('typeKey', 'unknown'),
                    'activity_name': activity.get('activityName', 'Activity'),
                    'start_time': activity.get('startTimeLocal'),
                    'duration_seconds': activity.get('duration', 0),
                    'distance_meters': activity.get('distance', 0),
                    'calories': activity.get('calories', 0),
                    'avg_heart_rate': activity.get('averageHR', 0),
                    'max_heart_rate': activity.get('maxHR', 0),
                    'avg_speed': activity.get('averageSpeed', 0),
                    'max_speed': activity.get('maxSpeed', 0),
                    'elevation_gain': activity.get('elevationGain', 0),
                    'elevation_loss': activity.get('elevationLoss', 0),
                    'avg_cadence': activity.get('averageRunningCadenceInStepsPerMinute', 0),
                    'training_effect': detailed.get('trainingEffectLabel') if detailed else None,
                    'aerobic_effect': detailed.get('aerobicTrainingEffect') if detailed else None,
                    'anaerobic_effect': detailed.get('anaerobicTrainingEffect') if detailed else None,
                    'extracted_at': datetime.now()
                }
                activities.append(processed_activity)
                
            logger.info(f"Extracted {len(activities)} activities")
        except Exception as e:
            logger.error(f"Failed to extract activities: {e}")
            raise
            
        return activities
    
    def extract_heart_rate(self, date: datetime) -> Dict:
        """Extract heart rate data for a specific date"""
        try:
            hr_data = self.client.get_heart_rates(date.strftime("%Y-%m-%d"))
            
            if hr_data:
                # Process heart rate time series
                hr_values = hr_data.get('heartRateValues', [])
                
                processed_hr = {
                    'date': date.strftime("%Y-%m-%d"),
                    'resting_heart_rate': hr_data.get('restingHeartRate'),
                    'min_heart_rate': hr_data.get('minHeartRate'),
                    'max_heart_rate': hr_data.get('maxHeartRate'),
                    'avg_heart_rate': self._calculate_avg_hr(hr_values),
                    'heart_rate_zones': json.dumps(hr_data.get('heartRateZones', [])),
                    'time_series': json.dumps(hr_values),
                    'extracted_at': datetime.now()
                }
                
                logger.info(f"Extracted heart rate data for {date}")
                return processed_hr
        except Exception as e:
            logger.error(f"Failed to extract heart rate data: {e}")
            raise
            
        return {}
    
    def extract_sleep(self, date: datetime) -> Dict:
        """Extract sleep data for a specific date"""
        try:
            sleep_data = self.client.get_sleep_data(date.strftime("%Y-%m-%d"))
            
            if sleep_data:
                # Handle the case where sleep_data might be a list or different structure
                if isinstance(sleep_data, list):
                    sleep_data = sleep_data[0] if sleep_data else {}
                
                sleep_levels = sleep_data.get('sleepLevels', {})
                
                processed_sleep = {
                    'date': date.strftime("%Y-%m-%d"),
                    'total_sleep_seconds': sleep_data.get('sleepTimeSeconds'),
                    'deep_sleep_seconds': sleep_levels.get('deep', {}).get('seconds'),
                    'light_sleep_seconds': sleep_levels.get('light', {}).get('seconds'),
                    'rem_sleep_seconds': sleep_levels.get('rem', {}).get('seconds'),
                    'awake_seconds': sleep_levels.get('awake', {}).get('seconds'),
                    'sleep_start_time': sleep_data.get('sleepStartTimestampLocal'),
                    'sleep_end_time': sleep_data.get('sleepEndTimestampLocal'),
                    'sleep_quality': sleep_data.get('sleepQualityType'),
                    'sleep_score': sleep_data.get('sleepScores', {}).get('overall'),
                    'avg_respiration': sleep_data.get('avgSleepRespiration'),
                    'avg_spo2': sleep_data.get('avgSleepSpO2'),
                    'sleep_movement': json.dumps(sleep_data.get('sleepMovement', [])),
                    'extracted_at': datetime.now()
                }
                
                logger.info(f"Extracted sleep data for {date}")
                return processed_sleep
        except Exception as e:
            logger.error(f"Failed to extract sleep data: {e}")
            raise
            
        return {}
    
    def extract_stress(self, date: datetime) -> Dict:
        """Extract stress data for a specific date"""
        try:
            stress_data = self.client.get_stress_data(date.strftime("%Y-%m-%d"))
            
            if stress_data:
                stress_values = stress_data.get('stressValuesArray', [])
                
                processed_stress = {
                    'date': date.strftime("%Y-%m-%d"),
                    'avg_stress_level': stress_data.get('averageStressLevel'),
                    'max_stress_level': stress_data.get('maxStressLevel'),
                    'stress_duration_seconds': stress_data.get('stressDuration'),
                    'rest_stress_duration': stress_data.get('restStressDuration'),
                    'activity_stress_duration': stress_data.get('activityStressDuration'),
                    'low_stress_duration': stress_data.get('lowStressDuration'),
                    'medium_stress_duration': stress_data.get('mediumStressDuration'),
                    'high_stress_duration': stress_data.get('highStressDuration'),
                    'stress_values': json.dumps(stress_values),
                    'extracted_at': datetime.now()
                }
                
                logger.info(f"Extracted stress data for {date}")
                return processed_stress
        except Exception as e:
            logger.error(f"Failed to extract stress data: {e}")
            raise
            
        return {}
    
    def extract_body_composition(self, date: datetime) -> Dict:
        """Extract body composition data"""
        try:
            body_data = self.client.get_body_composition(date.strftime("%Y-%m-%d"))
            
            if body_data:
                processed_body = {
                    'date': date.strftime("%Y-%m-%d"),
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
                
                logger.info(f"Extracted body composition data for {date}")
                return processed_body
        except Exception as e:
            logger.error(f"Failed to extract body composition data: {e}")
            raise
            
        return {}
    
    def extract_daily_summary(self, date: datetime) -> Dict:
        """Extract daily summary metrics"""
        try:
            summary = self.client.get_stats(date.strftime("%Y-%m-%d"))
            
            if summary:
                processed_summary = {
                    'date': date.strftime("%Y-%m-%d"),
                    'total_steps': summary.get('totalSteps'),
                    'total_distance_meters': summary.get('totalDistance'),
                    'highly_active_seconds': summary.get('highlyActiveSeconds'),
                    'active_seconds': summary.get('activeSeconds'),
                    'sedentary_seconds': summary.get('sedentarySeconds'),
                    'sleeping_seconds': summary.get('sleepingSeconds'),
                    'total_calories': summary.get('totalKilocalories'),
                    'active_calories': summary.get('activeKilocalories'),
                    'bmr_calories': summary.get('bmrKilocalories'),
                    'floors_climbed': summary.get('floorsAscended'),
                    'floors_descended': summary.get('floorsDescended'),
                    'intensity_minutes_goal': summary.get('intensityMinutesGoal'),
                    'intensity_minutes': summary.get('moderateIntensityMinutes'),
                    'vigorous_intensity_minutes': summary.get('vigorousIntensityMinutes'),
                    'extracted_at': datetime.now()
                }
                
                logger.info(f"Extracted daily summary for {date}")
                return processed_summary
        except Exception as e:
            logger.error(f"Failed to extract daily summary: {e}")
            raise
            
        return {}
    
    def save_to_staging(self, data: List[Dict], table_name: str) -> None:
        """Save extracted data to staging tables"""
        if not data:
            logger.warning(f"No data to save for {table_name}")
            return
            
        try:
            df = pd.DataFrame(data)
            df.to_sql(
                f'staging_{table_name}',
                self.db_engine,
                schema='garmin',
                if_exists='append',
                index=False
            )
            logger.info(f"Saved {len(data)} records to garmin.staging_{table_name}")
        except Exception as e:
            logger.error(f"Failed to save data to staging: {e}")
            raise
    
    def extract_full_day(self, date: datetime) -> None:
        """Extract all available data for a specific day"""
        logger.info(f"Starting full extraction for {date}")
        
        # Extract all data types
        activities = self.extract_activities(date, date)
        heart_rate = self.extract_heart_rate(date)
        sleep = self.extract_sleep(date)
        stress = self.extract_stress(date)
        body_comp = self.extract_body_composition(date)
        daily_summary = self.extract_daily_summary(date)
        
        # Save to staging tables
        if activities:
            self.save_to_staging(activities, 'activities')
        if heart_rate:
            self.save_to_staging([heart_rate], 'heart_rate')
        if sleep:
            self.save_to_staging([sleep], 'sleep')
        if stress:
            self.save_to_staging([stress], 'stress')
        if body_comp:
            self.save_to_staging([body_comp], 'body_composition')
        if daily_summary:
            self.save_to_staging([daily_summary], 'daily_summary')
            
        logger.info(f"Completed full extraction for {date}")
    
    def extract_date_range(self, start_date: datetime, end_date: datetime) -> None:
        """Extract data for a date range"""
        current_date = start_date
        
        while current_date <= end_date:
            try:
                self.extract_full_day(current_date)
                current_date += timedelta(days=1)
            except Exception as e:
                logger.error(f"Failed to extract data for {current_date}: {e}")
                current_date += timedelta(days=1)
                continue
    
    def _calculate_avg_hr(self, hr_values: List) -> Optional[float]:
        """Calculate average heart rate from time series"""
        if not hr_values:
            return None
        
        # Handle different data structures    
        try:
            if isinstance(hr_values, list):
                # Handle list of values or list of dicts
                valid_values = []
                for v in hr_values:
                    if isinstance(v, dict) and 'value' in v:
                        if v['value'] and v['value'] > 0:
                            valid_values.append(v['value'])
                    elif isinstance(v, (int, float)) and v > 0:
                        valid_values.append(v)
                
                if valid_values:
                    return sum(valid_values) / len(valid_values)
            return None
        except Exception:
            return None

if __name__ == "__main__":
    # Example usage
    config = GarminConfig.from_env()
    extractor = GarminDataExtractor(config)
    
    # Connect to Garmin
    extractor.connect()
    
    # Extract last 7 days of data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    extractor.extract_date_range(start_date, end_date)
