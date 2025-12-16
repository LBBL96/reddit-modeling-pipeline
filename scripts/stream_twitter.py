import sys
import os
import argparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_ingestion.twitter_streamer import TwitterStreamManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Stream tweets and save to database')
    parser.add_argument('--keywords', nargs='+', required=True,
                        help='Keywords to track (e.g., --keywords "AI" "machine learning")')
    parser.add_argument('--no-db', action='store_true',
                        help='Do not save to database')
    
    args = parser.parse_args()
    
    logger.info(f"Starting Twitter stream for keywords: {args.keywords}")
    
    manager = TwitterStreamManager()
    
    try:
        manager.start_stream(
            keywords=args.keywords,
            save_to_db=not args.no_db,
            clear_existing=True
        )
    except KeyboardInterrupt:
        logger.info("\nStopping stream...")
        manager.stop_stream()
        logger.info("Stream stopped successfully")
    except Exception as e:
        logger.error(f"Error during streaming: {e}")
        manager.stop_stream()


if __name__ == "__main__":
    main()
