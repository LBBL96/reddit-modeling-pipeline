from src.tasks.celery_app import celery_app
from src.model_training.retraining_pipeline import RetrainingPipeline
from src.database.database import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def check_and_retrain(self):
    logger.info("Checking if retraining is needed...")
    
    try:
        pipeline = RetrainingPipeline()
        result = pipeline.run_retraining_cycle()
        
        if result:
            logger.info(f"Retraining completed. New model version: {result['version']}")
            return {
                'status': 'success',
                'model_version': result['version'],
                'metrics': result['metrics']
            }
        else:
            logger.info("Retraining not needed")
            return {'status': 'skipped', 'message': 'Retraining not needed'}
    
    except Exception as e:
        logger.error(f"Error during retraining task: {e}")
        raise self.retry(exc=e, countdown=300)


@celery_app.task
def train_model_task(texts, labels, version=None):
    logger.info(f"Training model with {len(texts)} samples...")
    
    pipeline = RetrainingPipeline()
    result = pipeline.train_new_model(texts, labels, version)
    
    db = SessionLocal()
    try:
        pipeline.save_model_metrics(db, result)
    finally:
        db.close()
    
    return result
