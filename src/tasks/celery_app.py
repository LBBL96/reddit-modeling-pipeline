from celery import Celery
from celery.schedules import crontab
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    'sentiment_analysis',
    broker=settings.redis_url,
    backend=settings.redis_url
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    'check-retraining-every-hour': {
        'task': 'src.tasks.training_tasks.check_and_retrain',
        'schedule': crontab(minute=0),
    },
    'monitor-data-quality': {
        'task': 'src.tasks.monitoring_tasks.monitor_data_quality',
        'schedule': crontab(minute='*/30'),
    },
}


@celery_app.task
def test_task():
    logger.info("Test task executed successfully")
    return "Task completed"
