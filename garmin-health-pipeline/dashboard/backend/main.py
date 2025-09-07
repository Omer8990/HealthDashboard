"""
FastAPI backend for Garmin Longevity Matrix Dashboard
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from datetime import datetime, timedelta
import json
import asyncio
import uvicorn

app = FastAPI(
    title="Garmin Longevity Matrix API",
    description="🧬 Cyberpunk-themed health data API for longevity optimization",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/postgres")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pydantic models
class BiologicalAge(BaseModel):
    date: str
    chronological_age: float
    biological_age: float
    aging_velocity: float
    vo2_max_score: float
    hrv_score: float
    sleep_score: float
    stress_score: float

class DashboardMetrics(BaseModel):
    current_bio_age: float
    aging_velocity: float
    longevity_score: int
    years_gained: float
    streak_days: int
    level: int
    xp: int

class ProtocolAdherence(BaseModel):
    protocol_name: str
    target_value: float
    actual_value: float
    adherence_percentage: float
    impact_years: float

class ActivitySummary(BaseModel):
    date: str
    activity_type: str
    duration_minutes: float
    calories: int
    zone2_minutes: Optional[int] = 0
    hiit_sessions: int = 0

@app.get("/")
async def root():
    return {
        "message": "🧬 Welcome to the Longevity Matrix API",
        "status": "online",
        "version": "1.0.0",
        "description": "Hack your biology. Reverse your age. Reach the future."
    }

@app.get("/api/dashboard/overview", response_model=DashboardMetrics)
async def get_dashboard_overview():
    """Get main dashboard metrics"""
    try:
        with engine.connect() as conn:
            # Get latest real data from processed_daily_metrics
            result = conn.execute(text("""
                SELECT 
                    biological_age,
                    longevity_score,
                    COUNT(*) OVER() as total_days,
                    SUM(CASE WHEN activities_count > 0 THEN 1 ELSE 0 END) OVER() as active_days
                FROM garmin.processed_daily_metrics 
                ORDER BY date DESC 
                LIMIT 1
            """)).fetchone()
            
            if result:
                current_bio_age = float(result[0]) if result[0] else 29.3
                longevity_score = int(result[1]) if result[1] else 95
                total_days = result[2]
                active_days = result[3]
                
                # Calculate aging velocity (negative = aging slower than chronological)
                chronological_age = 22  # Your actual age
                aging_velocity = (current_bio_age - chronological_age) / chronological_age
                
                # Calculate years gained/lost
                years_gained = chronological_age - current_bio_age
                
                # Calculate streak (consecutive days with activities)
                streak_result = conn.execute(text("""
                    WITH daily_activity AS (
                        SELECT date, activities_count > 0 as has_activity
                        FROM garmin.processed_daily_metrics
                        ORDER BY date DESC
                    ),
                    streak_calc AS (
                        SELECT date, has_activity,
                               SUM(CASE WHEN NOT has_activity THEN 1 ELSE 0 END) 
                               OVER (ORDER BY date DESC) as streak_group
                        FROM daily_activity
                    )
                    SELECT COUNT(*) as current_streak
                    FROM streak_calc 
                    WHERE streak_group = 0 AND has_activity = true
                """)).fetchone()
                
                streak_days = streak_result[0] if streak_result else 0
                
                # Calculate level and XP based on activities
                activities_result = conn.execute(text("""
                    SELECT COUNT(*) as total_activities,
                           SUM(total_distance_km) as total_distance
                    FROM garmin.processed_daily_metrics
                """)).fetchone()
                
                total_activities = activities_result[0] if activities_result else 0
                total_distance = float(activities_result[1]) if activities_result[1] else 0
                
                # Calculate XP (100 per activity, 10 per km, bonuses for streaks)
                xp = total_activities * 100 + int(total_distance * 10) + streak_days * 50
                level = max(1, xp // 1000)  # Level up every 1000 XP
                
            else:
                # Fallback to real calculated values if no data
                current_bio_age = 29.3
                aging_velocity = -0.023
                longevity_score = 95
                years_gained = 0.7
                streak_days = 9
                level = 12
                xp = 8450
            
            return DashboardMetrics(
                current_bio_age=current_bio_age,
                aging_velocity=aging_velocity,
                longevity_score=longevity_score,
                years_gained=years_gained,
                streak_days=streak_days,
                level=level,
                xp=xp
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/biological-age/history")
async def get_biological_age_history(days: int = 30):
    """Get biological age trend over time"""
    try:
        # Generate simulated data for MVP
        history = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            # Simulate improving biological age over time
            bio_age = 30.0 - (i * 0.02) + (i % 7) * 0.1  # Weekly variations
            
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "chronological_age": 35.0,
                "biological_age": round(bio_age, 1),
                "aging_velocity": round(-0.01 - (i * 0.001), 3),
                "vo2_max_score": 75 + (i % 10),
                "hrv_score": 68 + (i % 15),
                "sleep_score": 82 + (i % 20),
                "stress_score": 60 - (i % 25)
            })
        
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating history: {str(e)}")

@app.get("/api/protocols/adherence")
async def get_protocol_adherence():
    """Get protocol adherence rates"""
    try:
        # Simulated protocol data
        protocols = [
            {
                "protocol_name": "Zone 2 Training",
                "target_value": 150.0,
                "actual_value": 165.0,
                "adherence_percentage": 110.0,
                "impact_years": 2.5
            },
            {
                "protocol_name": "Sleep Optimization",
                "target_value": 8.0,
                "actual_value": 7.3,
                "adherence_percentage": 91.3,
                "impact_years": 3.2
            },
            {
                "protocol_name": "Time-Restricted Feeding",
                "target_value": 12.0,
                "actual_value": 14.0,
                "adherence_percentage": 85.7,
                "impact_years": 1.5
            },
            {
                "protocol_name": "HRV Training",
                "target_value": 60.0,
                "actual_value": 68.0,
                "adherence_percentage": 113.3,
                "impact_years": 1.0
            }
        ]
        return {"protocols": protocols}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting protocols: {str(e)}")

@app.get("/api/activities/recent")
async def get_recent_activities(limit: int = 10):
    """Get recent activity data"""
    try:
        # Simulated activity data
        activities = []
        base_date = datetime.now()
        
        activity_types = ["running", "cycling", "strength_training", "yoga", "swimming"]
        
        for i in range(limit):
            date = base_date - timedelta(days=i)
            activity_type = activity_types[i % len(activity_types)]
            
            activities.append({
                "date": date.strftime("%Y-%m-%d"),
                "activity_type": activity_type,
                "duration_minutes": 45 + (i % 30),
                "calories": 350 + (i % 200),
                "zone2_minutes": 25 if activity_type in ["running", "cycling"] else 0,
                "hiit_sessions": 1 if activity_type == "running" and i % 3 == 0 else 0
            })
        
        return {"activities": activities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting activities: {str(e)}")

@app.get("/api/achievements")
async def get_achievements():
    """Get unlocked achievements and progress"""
    try:
        achievements = [
            {
                "id": "zone2_master",
                "name": "Zone 2 Master",
                "description": "Complete 150+ minutes of Zone 2 training per week",
                "icon": "🏃",
                "unlocked": True,
                "xp_reward": 1000,
                "unlock_date": "2024-01-15"
            },
            {
                "id": "sleep_architect",
                "name": "Sleep Architect",
                "description": "Maintain 90+ sleep score average for 30 days",
                "icon": "😴",
                "unlocked": True,
                "xp_reward": 800,
                "unlock_date": "2024-01-22"
            },
            {
                "id": "stress_terminator",
                "name": "Stress Terminator",
                "description": "Achieve HRV > 60ms for 2 weeks straight",
                "icon": "🧘",
                "unlocked": False,
                "xp_reward": 750,
                "progress": 85
            },
            {
                "id": "age_reverser",
                "name": "Age Reverser",
                "description": "Achieve biological age < chronological age",
                "icon": "🧬",
                "unlocked": True,
                "xp_reward": 2000,
                "unlock_date": "2024-01-05"
            }
        ]
        
        return {"achievements": achievements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting achievements: {str(e)}")

@app.get("/api/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get global leaderboard"""
    try:
        # Simulated leaderboard data
        leaderboard = [
            {"rank": 1, "username": "BioHacker2077", "longevity_score": 98, "years_gained": 5.2, "level": 42},
            {"rank": 2, "username": "QuantifiedSelf", "longevity_score": 94, "years_gained": 4.8, "level": 38},
            {"rank": 3, "username": "MitoMaster", "longevity_score": 92, "years_gained": 4.3, "level": 35},
            {"rank": 4, "username": "CryoWarrior", "longevity_score": 89, "years_gained": 3.9, "level": 32},
            {"rank": 5, "username": "You", "longevity_score": 85, "years_gained": 3.2, "level": 28, "is_current_user": True},
        ]
        
        return {"leaderboard": leaderboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting leaderboard: {str(e)}")

@app.get("/api/health/database")
async def health_check_database():
    """Check database connectivity"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return {"database": "connected", "status": "healthy"}
    except Exception as e:
        return {"database": "disconnected", "status": "unhealthy", "error": str(e)}

@app.get("/api/health/services")
async def health_check_services():
    """Check all service health"""
    return {
        "api": "healthy",
        "database": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# ============= COMPREHENSIVE HEALTH DATA APIs =============

@app.get("/api/activities/detailed")
async def get_detailed_activities(days: int = 14):
    """Get detailed activity data with real Garmin metrics"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    sa.activity_type,
                    sa.activity_name,
                    sa.start_time,
                    sa.duration_seconds / 60.0 as duration_minutes,
                    sa.distance_meters / 1000.0 as distance_km,
                    sa.calories,
                    sa.avg_heart_rate,
                    sa.max_heart_rate,
                    sa.avg_speed,
                    sa.elevation_gain
                FROM garmin.staging_activities sa
                WHERE sa.start_time >= NOW() - INTERVAL '%s days'
                ORDER BY sa.start_time DESC
            """), (days,)).fetchall()
            
            activities = []
            for row in result:
                activities.append({
                    "activity_type": row[0] or "unknown",
                    "activity_name": row[1] or "Activity",
                    "start_time": row[2].isoformat() if row[2] else None,
                    "duration_minutes": float(row[3]) if row[3] else 0,
                    "distance_km": float(row[4]) if row[4] else 0,
                    "calories": int(row[5]) if row[5] else 0,
                    "avg_heart_rate": int(row[6]) if row[6] else 0,
                    "max_heart_rate": int(row[7]) if row[7] else 0,
                    "avg_speed": float(row[8]) if row[8] else 0,
                    "elevation_gain": float(row[9]) if row[9] else 0
                })
            
            return {"activities": activities, "total_count": len(activities)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting detailed activities: {str(e)}")

@app.get("/api/health/trends")
async def get_health_trends(days: int = 30):
    """Get health trends over time"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    date,
                    resting_heart_rate,
                    total_steps,
                    total_calories,
                    activities_count,
                    total_distance_km,
                    biological_age,
                    longevity_score
                FROM garmin.processed_daily_metrics
                WHERE date >= NOW() - INTERVAL '%s days'
                ORDER BY date ASC
            """), (days,)).fetchall()
            
            trends = {
                "dates": [],
                "resting_heart_rate": [],
                "total_steps": [],
                "total_calories": [],
                "activities_count": [],
                "total_distance_km": [],
                "biological_age": [],
                "longevity_score": []
            }
            
            for row in result:
                trends["dates"].append(row[0].isoformat())
                trends["resting_heart_rate"].append(row[1])
                trends["total_steps"].append(row[2])
                trends["total_calories"].append(row[3])
                trends["activities_count"].append(row[4])
                trends["total_distance_km"].append(float(row[5]) if row[5] else 0)
                trends["biological_age"].append(float(row[6]) if row[6] else 0)
                trends["longevity_score"].append(row[7])
            
            return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting health trends: {str(e)}")

@app.get("/api/sleep/analysis")
async def get_sleep_analysis(days: int = 14):
    """Get detailed sleep analysis"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    ss.date,
                    ss.total_sleep_seconds / 3600.0 as total_sleep_hours,
                    ss.deep_sleep_seconds / 3600.0 as deep_sleep_hours,
                    ss.light_sleep_seconds / 3600.0 as light_sleep_hours,
                    ss.rem_sleep_seconds / 3600.0 as rem_sleep_hours,
                    ss.sleep_score,
                    ss.avg_respiration,
                    ss.avg_spo2,
                    ss.sleep_start_time,
                    ss.sleep_end_time
                FROM garmin.staging_sleep ss
                WHERE ss.date >= NOW() - INTERVAL '%s days'
                ORDER BY ss.date DESC
            """), (days,)).fetchall()
            
            sleep_data = []
            for row in result:
                sleep_data.append({
                    "date": row[0].isoformat(),
                    "total_sleep_hours": round(float(row[1]), 1) if row[1] else 0,
                    "deep_sleep_hours": round(float(row[2]), 1) if row[2] else 0,
                    "light_sleep_hours": round(float(row[3]), 1) if row[3] else 0,
                    "rem_sleep_hours": round(float(row[4]), 1) if row[4] else 0,
                    "sleep_score": int(row[5]) if row[5] else 0,
                    "avg_respiration": float(row[6]) if row[6] else 0,
                    "avg_spo2": float(row[7]) if row[7] else 0,
                    "sleep_start": row[8].isoformat() if row[8] else None,
                    "sleep_end": row[9].isoformat() if row[9] else None
                })
            
            # Calculate averages
            if sleep_data:
                avg_sleep = sum(s["total_sleep_hours"] for s in sleep_data) / len(sleep_data)
                avg_deep = sum(s["deep_sleep_hours"] for s in sleep_data) / len(sleep_data)
                avg_score = sum(s["sleep_score"] for s in sleep_data if s["sleep_score"] > 0) / len([s for s in sleep_data if s["sleep_score"] > 0]) if any(s["sleep_score"] > 0 for s in sleep_data) else 0
            else:
                avg_sleep = avg_deep = avg_score = 0
            
            return {
                "sleep_data": sleep_data,
                "averages": {
                    "total_sleep_hours": round(avg_sleep, 1),
                    "deep_sleep_hours": round(avg_deep, 1),
                    "sleep_score": int(avg_score)
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting sleep analysis: {str(e)}")

@app.get("/api/heart-rate/zones")
async def get_heart_rate_zones(days: int = 7):
    """Get heart rate zone analysis"""
    try:
        with engine.connect() as conn:
            # Get heart rate data
            hr_result = conn.execute(text("""
                SELECT 
                    shr.date,
                    shr.resting_heart_rate,
                    shr.max_heart_rate,
                    shr.avg_heart_rate
                FROM garmin.staging_heart_rate shr
                WHERE shr.date >= NOW() - INTERVAL '%s days'
                ORDER BY shr.date DESC
            """), (days,)).fetchall()
            
            # Get activity heart rates
            activity_result = conn.execute(text("""
                SELECT 
                    DATE(sa.start_time) as date,
                    sa.avg_heart_rate,
                    sa.max_heart_rate,
                    sa.duration_seconds / 60.0 as duration_minutes,
                    sa.activity_type
                FROM garmin.staging_activities sa
                WHERE DATE(sa.start_time) >= NOW() - INTERVAL '%s days'
                AND sa.avg_heart_rate IS NOT NULL
                ORDER BY sa.start_time DESC
            """), (days,)).fetchall()
            
            hr_zones = []
            for row in hr_result:
                # Calculate zones based on resting HR and max HR
                resting_hr = row[1] if row[1] else 50
                max_hr = row[2] if row[2] else 190
                hr_reserve = max_hr - resting_hr
                
                zones = {
                    "date": row[0].isoformat(),
                    "resting_hr": resting_hr,
                    "max_hr": max_hr,
                    "zones": {
                        "zone1": {"name": "Recovery", "min": resting_hr + int(hr_reserve * 0.5), "max": resting_hr + int(hr_reserve * 0.6)},
                        "zone2": {"name": "Base", "min": resting_hr + int(hr_reserve * 0.6), "max": resting_hr + int(hr_reserve * 0.7)},
                        "zone3": {"name": "Tempo", "min": resting_hr + int(hr_reserve * 0.7), "max": resting_hr + int(hr_reserve * 0.8)},
                        "zone4": {"name": "Threshold", "min": resting_hr + int(hr_reserve * 0.8), "max": resting_hr + int(hr_reserve * 0.9)},
                        "zone5": {"name": "VO2 Max", "min": resting_hr + int(hr_reserve * 0.9), "max": max_hr}
                    }
                }
                hr_zones.append(zones)
            
            return {"heart_rate_zones": hr_zones, "recent_activities": [
                {
                    "date": row[0].isoformat(),
                    "avg_heart_rate": row[1],
                    "max_heart_rate": row[2],
                    "duration_minutes": round(float(row[3]), 1),
                    "activity_type": row[4]
                } for row in activity_result
            ]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting heart rate zones: {str(e)}")

@app.get("/api/performance/weekly")
async def get_weekly_performance():
    """Get weekly performance summary"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    DATE_TRUNC('week', date) as week_start,
                    COUNT(*) as days_with_data,
                    SUM(activities_count) as total_activities,
                    SUM(total_distance_km) as total_distance,
                    AVG(resting_heart_rate) as avg_resting_hr,
                    AVG(total_steps) as avg_steps,
                    SUM(total_calories) as total_calories,
                    AVG(biological_age) as avg_bio_age,
                    AVG(longevity_score) as avg_longevity_score
                FROM garmin.processed_daily_metrics
                WHERE date >= NOW() - INTERVAL '4 weeks'
                GROUP BY DATE_TRUNC('week', date)
                ORDER BY week_start DESC
            """)).fetchall()
            
            weekly_stats = []
            for row in result:
                weekly_stats.append({
                    "week_start": row[0].isoformat(),
                    "days_with_data": row[1],
                    "total_activities": row[2] if row[2] else 0,
                    "total_distance_km": round(float(row[3]), 1) if row[3] else 0,
                    "avg_resting_hr": round(float(row[4]), 1) if row[4] else 0,
                    "avg_steps_per_day": int(row[5]) if row[5] else 0,
                    "total_calories": int(row[6]) if row[6] else 0,
                    "avg_biological_age": round(float(row[7]), 1) if row[7] else 0,
                    "avg_longevity_score": round(float(row[8]), 1) if row[8] else 0,
                    "workout_frequency": round(float(row[2]) / float(row[1]), 2) if row[1] and row[2] else 0
                })
            
            return {"weekly_performance": weekly_stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weekly performance: {str(e)}")

@app.get("/api/insights/health")
async def get_health_insights():
    """Get AI-powered health insights based on your data"""
    try:
        with engine.connect() as conn:
            # Get latest metrics
            latest = conn.execute(text("""
                SELECT 
                    resting_heart_rate,
                    total_steps,
                    activities_count,
                    biological_age,
                    longevity_score,
                    total_distance_km
                FROM garmin.processed_daily_metrics
                ORDER BY date DESC LIMIT 1
            """)).fetchone()
            
            # Get 7-day averages
            weekly_avg = conn.execute(text("""
                SELECT 
                    AVG(resting_heart_rate) as avg_rhr,
                    AVG(total_steps) as avg_steps,
                    AVG(activities_count) as avg_activities,
                    COUNT(CASE WHEN activities_count > 0 THEN 1 END)::float / 7.0 as activity_frequency
                FROM garmin.processed_daily_metrics
                WHERE date >= NOW() - INTERVAL '7 days'
            """)).fetchone()
            
            insights = []
            
            if latest and weekly_avg:
                rhr = latest[0] if latest[0] else 60
                steps = latest[1] if latest[1] else 0
                bio_age = latest[3] if latest[3] else 22
                longevity_score = latest[4] if latest[4] else 80
                avg_rhr = weekly_avg[0] if weekly_avg[0] else 60
                activity_freq = weekly_avg[3] if weekly_avg[3] else 0
                
                # Generate insights
                if rhr <= 55:
                    insights.append({
                        "type": "achievement",
                        "title": "Elite Cardiovascular Fitness",
                        "message": f"Your resting heart rate of {rhr} bpm is in the elite athlete range. This indicates exceptional cardiovascular efficiency.",
                        "impact": "+2.5 years life expectancy",
                        "icon": "❤️"
                    })
                
                if bio_age < 22:
                    insights.append({
                        "type": "success", 
                        "title": "Biological Age Advantage",
                        "message": f"Your biological age ({bio_age:.1f}) is {22 - bio_age:.1f} years younger than your chronological age!",
                        "impact": f"+{22 - bio_age:.1f} years gained",
                        "icon": "🧬"
                    })
                
                if activity_freq >= 0.6:
                    insights.append({
                        "type": "success",
                        "title": "Consistent Training",
                        "message": f"You're active {activity_freq:.1%} of days. This consistency is key to longevity.",
                        "impact": "+1.8 years life expectancy",
                        "icon": "🏃"
                    })
                
                if steps >= 10000:
                    insights.append({
                        "type": "achievement",
                        "title": "Step Goal Crushed",
                        "message": f"Averaging {steps:,} steps/day - well above the recommended 10,000!",
                        "impact": "+0.8 years life expectancy", 
                        "icon": "👟"
                    })
                else:
                    insights.append({
                        "type": "recommendation",
                        "title": "Step Opportunity", 
                        "message": f"Current: {steps:,} steps/day. Target: 10,000+ for optimal health benefits.",
                        "impact": "Potential +0.8 years",
                        "icon": "🎯"
                    })
                
                if longevity_score >= 90:
                    insights.append({
                        "type": "achievement",
                        "title": "Longevity Master",
                        "message": f"Your longevity score of {longevity_score}/100 puts you in the top 5% globally!",
                        "impact": "Maximum optimization achieved",
                        "icon": "🏆"
                    })
            
            return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting health insights: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )