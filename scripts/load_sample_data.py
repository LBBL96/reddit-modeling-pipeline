import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.database import SessionLocal
from src.database.models import TrainingData
from datasets import load_dataset
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_sentiment_dataset():
    logger.info("Loading sentiment140 dataset...")
    dataset = load_dataset("sentiment140", split="train[:10000]")
    
    db = SessionLocal()
    try:
        count = 0
        for item in dataset:
            sentiment_map = {0: 'negative', 2: 'neutral', 4: 'positive'}
            label = sentiment_map.get(item['sentiment'], 'neutral')
            
            training_data = TrainingData(
                text=item['text'],
                label=label,
                source='sentiment140',
                used_for_training=False
            )
            db.add(training_data)
            count += 1
            
            if count % 1000 == 0:
                db.commit()
                logger.info(f"Loaded {count} samples...")
        
        db.commit()
        logger.info(f"Successfully loaded {count} training samples!")
    
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        db.rollback()
    finally:
        db.close()


def load_custom_samples():
    logger.info("Loading custom sample data...")
    
    samples = [
        ("I absolutely love this product! Best purchase ever!", "positive"),
        ("This is amazing! Highly recommend it to everyone.", "positive"),
        ("Great quality and fast shipping. Very satisfied!", "positive"),
        ("Terrible experience. Would not recommend.", "negative"),
        ("Worst product I've ever bought. Complete waste of money.", "negative"),
        ("Very disappointed with the quality. Not worth it.", "negative"),
        ("It's okay, nothing special but does the job.", "neutral"),
        ("Average product, met my expectations.", "neutral"),
        ("Not bad, not great. Just okay for the price.", "neutral"),
    ]
    
    db = SessionLocal()
    try:
        for text, label in samples:
            training_data = TrainingData(
                text=text,
                label=label,
                source='manual',
                used_for_training=False
            )
            db.add(training_data)
        
        db.commit()
        logger.info(f"Successfully loaded {len(samples)} custom samples!")
    
    except Exception as e:
        logger.error(f"Error loading custom samples: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Load sample data for training')
    parser.add_argument('--source', choices=['sentiment140', 'custom', 'both'],
                        default='both', help='Data source to load')
    
    args = parser.parse_args()
    
    if args.source in ['sentiment140', 'both']:
        try:
            load_sentiment_dataset()
        except Exception as e:
            logger.error(f"Failed to load sentiment140: {e}")
    
    if args.source in ['custom', 'both']:
        load_custom_samples()


if __name__ == "__main__":
    main()
