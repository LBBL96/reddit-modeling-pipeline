import tweepy
import logging
from collections.abc import Callable
from datetime import datetime
from config import settings
from src.database.models import Tweet
from src.database.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XStreamListener(tweepy.StreamingClient):
    """
    X API v2 Filtered Stream Listener
    
    Uses OAuth 2.0 Bearer Token (App-Only) authentication to connect to
    X API v2 filtered stream endpoint: https://api.x.com/2/tweets/search/stream
    
    Requires a Developer App associated with a Project.
    Access levels: Basic ($200/mo), Pro ($5000/mo), or Enterprise
    """
    
    def __init__(
        self,
        bearer_token: str,
        callback: Callable | None = None,
        save_to_db: bool = True,
        **kwargs
    ):
        super().__init__(bearer_token, **kwargs)
        self.callback = callback
        self.save_to_db = save_to_db
        self.post_count = 0
        
    def on_tweet(self, tweet):
        """
        Process incoming posts (tweets) from X API v2 stream.
        
        Note: X API v2 uses 'posts' terminology, but the object is still 
        referred to as 'tweet' in the tweepy library for compatibility.
        """
        try:
            post_data = {
                'tweet_id': str(tweet.id),
                'text': tweet.text,
                'created_at': datetime.utcnow(),
                'author_id': str(tweet.author_id) if hasattr(tweet, 'author_id') else None,
                'lang': tweet.lang if hasattr(tweet, 'lang') else None,
            }
            
            self.post_count += 1
            logger.info(f"Received post #{self.post_count}: {post_data['tweet_id']}")
            
            if self.save_to_db:
                self._save_to_database(post_data)
            
            if self.callback:
                self.callback(post_data)
                
        except Exception as e:
            logger.error(f"Error processing post: {e}")
    
    def _save_to_database(self, post_data: dict):
        db = SessionLocal()
        try:
            tweet = Tweet(**post_data)
            db.add(tweet)
            db.commit()
            logger.debug(f"Saved post {post_data['tweet_id']} to database")
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            db.rollback()
        finally:
            db.close()
    
    def on_errors(self, errors):
        logger.error(f"Stream errors: {errors}")
        return True
    
    def on_connection_error(self):
        logger.error("Connection error occurred")
    
    def on_request_error(self, status_code):
        logger.error(f"Request error: HTTP {status_code}")
        if status_code == 429:
            logger.error("Rate limit exceeded - consider upgrading access level")
        return True


class XStreamManager:
    """
    X API v2 Filtered Stream Manager
    
    Manages stream rules and connections for X API v2 filtered stream.
    Supports multiple persistent rules that can be updated without disconnecting the stream.
    
    Key features:
    - Multiple simultaneous filtering rules
    - Persistent rules across connections
    - Real-time rule management
    - Enhanced error handling
    
    Access requirements:
    - Basic: 10,000 posts/month read limit
    - Pro: 1,000,000 posts/month GET, includes filtered stream
    - Enterprise: Complete stream access with advanced features
    """
    
    def __init__(self):
        self.stream = None
        self.rules = []
        
    def setup_stream(
        self,
        callback: Callable | None = None,
        save_to_db: bool = True
    ) -> XStreamListener:
        """Initialize X API v2 stream client with Bearer Token authentication."""
        self.stream = XStreamListener(
            bearer_token=settings.twitter_bearer_token,
            callback=callback,
            save_to_db=save_to_db
        )
        return self.stream
    
    def add_rules(self, keywords: list[str], tag: str | None = None):
        """
        Add filtering rules to X API v2 filtered stream.
        
        Rules use X API v2 operators and can be added without disconnecting the stream.
        Each rule filters posts in real-time based on the specified criteria.
        
        Args:
            keywords: List of keywords or phrases to filter
            tag: Optional tag to identify rules (defaults to keyword)
        """
        rules = []
        for keyword in keywords:
            # X API v2 rule format with operators
            rule_value = f"{keyword} lang:en -is:retweet"
            rule = tweepy.StreamRule(value=rule_value, tag=tag or keyword)
            rules.append(rule)
        
        if self.stream:
            try:
                self.stream.add_rules(rules)
                logger.info(f"Added {len(rules)} rules to X API v2 filtered stream")
                self.rules.extend(rules)
            except Exception as e:
                logger.error(f"Error adding rules to stream: {e}")
                if "429" in str(e):
                    logger.error("Rate limit exceeded - check your access level limits")
    
    def clear_rules(self):
        """Remove all existing rules from the filtered stream."""
        if self.stream:
            try:
                existing_rules = self.stream.get_rules()
                if existing_rules.data:
                    rule_ids = [rule.id for rule in existing_rules.data]
                    self.stream.delete_rules(rule_ids)
                    logger.info(f"Cleared {len(rule_ids)} existing rules")
                    self.rules = []
            except Exception as e:
                logger.error(f"Error clearing rules: {e}")
    
    def start_stream(
        self,
        keywords: list[str],
        callback: Callable | None = None,
        save_to_db: bool = True,
        clear_existing: bool = True
    ):
        """
        Start X API v2 filtered stream with specified keywords.
        
        Args:
            keywords: List of keywords to filter posts
            callback: Optional callback function for each post
            save_to_db: Whether to save posts to database
            clear_existing: Whether to clear existing rules first
        """
        if not self.stream:
            self.setup_stream(callback=callback, save_to_db=save_to_db)
        
        if clear_existing:
            self.clear_rules()
        
        self.add_rules(keywords)
        
        logger.info("Starting X API v2 filtered stream...")
        # X API v2 fields and expansions
        self.stream.filter(
            tweet_fields=['author_id', 'created_at', 'lang', 'public_metrics', 'conversation_id'],
            expansions=['author_id'],
            user_fields=['username', 'name', 'verified']
        )
    
    def stop_stream(self):
        """Disconnect from the X API v2 stream."""
        if self.stream:
            self.stream.disconnect()
            logger.info("X API v2 stream stopped")


def create_batch_collector(batch_size: int = 100):
    """
    Create a batch collector for efficient post processing.
    
    Useful for batching posts before sending to model for sentiment analysis.
    
    Args:
        batch_size: Number of posts to collect before processing
        
    Returns:
        Callable that collects posts and returns batch when size is reached
    """
    batch = []
    
    def collect_batch(post_data: dict):
        batch.append(post_data)
        if len(batch) >= batch_size:
            logger.info(f"Batch of {len(batch)} posts ready for processing")
            processed_batch = batch.copy()
            batch.clear()
            return processed_batch
        return None
    
    return collect_batch
