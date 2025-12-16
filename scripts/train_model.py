import sys
import os
import argparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model_training.retraining_pipeline import RetrainingPipeline
from src.database.database import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Train sentiment analysis model')
    parser.add_argument('--check-retraining', action='store_true',
                        help='Check if retraining is needed and trigger if necessary')
    parser.add_argument('--force', action='store_true',
                        help='Force retraining even if not needed')
    
    args = parser.parse_args()
    
    pipeline = RetrainingPipeline()
    
    if args.check_retraining:
        logger.info("Checking if retraining is needed...")
        db = SessionLocal()
        try:
            if args.force or pipeline.check_retraining_needed(db):
                logger.info("Starting retraining cycle...")
                result = pipeline.run_retraining_cycle()
                if result:
                    logger.info(f"Retraining completed successfully!")
                    logger.info(f"Model version: {result['version']}")
                    logger.info(f"Model path: {result['model_path']}")
                    logger.info(f"Metrics: {result['metrics']}")
                else:
                    logger.info("Retraining was not completed")
            else:
                logger.info("Retraining not needed at this time")
        finally:
            db.close()
    else:
        logger.info("Running retraining cycle...")
        result = pipeline.run_retraining_cycle()
        if result:
            logger.info(f"Training completed! Model version: {result['version']}")
        else:
            logger.info("Training was not completed")


if __name__ == "__main__":
    main()
