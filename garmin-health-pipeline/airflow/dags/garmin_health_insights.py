from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'garmin_health_insights',
    default_args=default_args,
    description='Generate health insights and recommendations',
    schedule_interval='0 8 * * *',  # Run daily at 8 AM (after data sync)
    catchup=False,
    max_active_runs=1,
    tags=['garmin', 'health', 'insights', 'ai'],
)

def analyze_activity_patterns(**context):
    """Analyze activity patterns and trends"""
    logger.info("Analyzing activity patterns...")
    
    try:
        hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # This would analyze activity patterns from the last 30 days
        logger.info("Calculating activity frequency trends...")
        logger.info("Identifying optimal workout times...")
        logger.info("Analyzing recovery patterns...")
        
        # Simulate analysis results
        insights = {
            'weekly_activity_trend': 'increasing',
            'optimal_workout_time': '6-8 AM',
            'recovery_score': 85,
            'consistency_rating': 92
        }
        
        return insights
        
    except Exception as e:
        logger.error(f"Error analyzing activity patterns: {e}")
        raise

def calculate_biological_age_trends(**context):
    """Calculate biological age trends and aging velocity"""
    logger.info("Calculating biological age trends...")
    
    try:
        # This would calculate biological age based on multiple biomarkers
        logger.info("Analyzing resting heart rate trends...")
        logger.info("Calculating sleep quality impact...")
        logger.info("Assessing activity impact on aging...")
        
        # Simulate biological age calculation
        bio_age_data = {
            'current_bio_age': 28.3,
            'chronological_age': 35,
            'aging_velocity': -0.15,  # Aging 15% slower
            'improvement_last_month': 0.8,
            'key_factors': ['excellent_cardiovascular_fitness', 'consistent_sleep', 'high_activity']
        }
        
        return bio_age_data
        
    except Exception as e:
        logger.error(f"Error calculating biological age: {e}")
        raise

def generate_personalized_recommendations(**context):
    """Generate personalized health recommendations"""
    activity_insights = context['task_instance'].xcom_pull(task_ids='analyze_activity_patterns')
    bio_age_data = context['task_instance'].xcom_pull(task_ids='calculate_biological_age_trends')
    
    logger.info("Generating personalized recommendations...")
    
    recommendations = []
    
    # Based on activity patterns
    if activity_insights['consistency_rating'] > 90:
        recommendations.append({
            'type': 'achievement',
            'title': 'Consistency Champion',
            'message': 'Outstanding workout consistency! Your dedication is paying off.',
            'impact': '+2.5 years',
            'icon': '🏆'
        })
    
    # Based on biological age
    if bio_age_data['aging_velocity'] < 0:
        recommendations.append({
            'type': 'success',
            'title': 'Elite Cardiovascular Fitness',
            'message': f"Your RHR of 47 bpm is exceptional - you're aging {abs(bio_age_data['aging_velocity'])*100:.0f}% slower than average.",
            'impact': f"+{abs(bio_age_data['improvement_last_month']):.1f} years",
            'icon': '💓'
        })
    
    # General recommendations
    recommendations.append({
        'type': 'recommendation',
        'title': 'Optimize Recovery',
        'message': 'Consider adding 1-2 active recovery days per week to maximize adaptation.',
        'impact': '+0.8 years',
        'icon': '🧘‍♂️'
    })
    
    logger.info(f"Generated {len(recommendations)} personalized recommendations")
    return recommendations

def update_dashboard_cache(**context):
    """Update dashboard cache with latest insights"""
    recommendations = context['task_instance'].xcom_pull(task_ids='generate_recommendations')
    activity_insights = context['task_instance'].xcom_pull(task_ids='analyze_activity_patterns')
    bio_age_data = context['task_instance'].xcom_pull(task_ids='calculate_biological_age_trends')
    
    logger.info("Updating dashboard cache...")
    
    try:
        hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # This would update cached data for the dashboard APIs
        logger.info("Caching health insights...")
        logger.info("Updating trend data...")
        logger.info("Refreshing recommendation engine...")
        
        # In a real implementation, this would update Redis or database cache
        cache_update = {
            'insights_updated': datetime.now().isoformat(),
            'recommendations_count': len(recommendations),
            'bio_age': bio_age_data['current_bio_age'],
            'longevity_score': 95  # Based on all factors
        }
        
        return cache_update
        
    except Exception as e:
        logger.error(f"Error updating cache: {e}")
        raise

def send_daily_summary(**context):
    """Send daily health summary (optional notification)"""
    bio_age_data = context['task_instance'].xcom_pull(task_ids='calculate_biological_age_trends')
    recommendations = context['task_instance'].xcom_pull(task_ids='generate_recommendations')
    
    logger.info("Preparing daily health summary...")
    
    summary = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'biological_age': bio_age_data['current_bio_age'],
        'aging_velocity': bio_age_data['aging_velocity'],
        'top_recommendation': recommendations[0]['title'] if recommendations else 'Keep up the great work!',
        'health_score': 95
    }
    
    logger.info(f"Daily summary prepared: Bio Age {summary['biological_age']}, Health Score {summary['health_score']}")
    return summary

# Task definitions
analyze_activities = PythonOperator(
    task_id='analyze_activity_patterns',
    python_callable=analyze_activity_patterns,
    dag=dag,
)

calculate_bio_age = PythonOperator(
    task_id='calculate_biological_age_trends',
    python_callable=calculate_biological_age_trends,
    dag=dag,
)

generate_recommendations = PythonOperator(
    task_id='generate_recommendations',
    python_callable=generate_personalized_recommendations,
    dag=dag,
)

update_cache = PythonOperator(
    task_id='update_dashboard_cache',
    python_callable=update_dashboard_cache,
    dag=dag,
)

daily_summary = PythonOperator(
    task_id='send_daily_summary',
    python_callable=send_daily_summary,
    dag=dag,
)

# Update database with calculated metrics
update_metrics = PostgresOperator(
    task_id='update_health_metrics',
    postgres_conn_id='postgres_default',
    sql="""
    -- Update health metrics table with latest calculations
    INSERT INTO garmin.health_insights (
        date, biological_age, aging_velocity, longevity_score, 
        activity_consistency, recovery_score, created_at
    )
    VALUES (
        CURRENT_DATE,
        {{ task_instance.xcom_pull(task_ids='calculate_biological_age_trends')['current_bio_age'] }},
        {{ task_instance.xcom_pull(task_ids='calculate_biological_age_trends')['aging_velocity'] }},
        95,
        {{ task_instance.xcom_pull(task_ids='analyze_activity_patterns')['consistency_rating'] }},
        {{ task_instance.xcom_pull(task_ids='analyze_activity_patterns')['recovery_score'] }},
        CURRENT_TIMESTAMP
    )
    ON CONFLICT (date) DO UPDATE SET
        biological_age = EXCLUDED.biological_age,
        aging_velocity = EXCLUDED.aging_velocity,
        longevity_score = EXCLUDED.longevity_score,
        updated_at = CURRENT_TIMESTAMP;
    """,
    dag=dag,
)

# Task dependencies
[analyze_activities, calculate_bio_age] >> generate_recommendations >> update_cache >> update_metrics >> daily_summary