from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration for X API v2 Sentiment Analysis Pipeline
    
    X API v2 Filtered Stream Requirements:
    - Bearer Token (App-Only) authentication - REQUIRED
    - Developer App associated with a Project
    - Minimum access level: Basic ($200/mo) for filtered stream
    - Pro ($5000/mo) recommended for production (1M posts/month)
    
    Get credentials at: https://developer.x.com/en/portal/dashboard
    """
    
    # X API v2 Bearer Token - REQUIRED for filtered stream
    twitter_bearer_token: str
    
    # Legacy OAuth 1.0a credentials (optional, for v1.1 endpoints only)
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_secret: str = ""
    
    wandb_api_key: str | None = None
    wandb_project: str = "twitter-sentiment-analysis"
    
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "sentiment-analysis"
    
    database_url: str = "postgresql://user:password@localhost:5432/twitter_sentiment"
    redis_url: str = "redis://localhost:6379/0"
    
    model_name: str = "distilbert-base-uncased"
    max_length: int = 128
    batch_size: int = 32
    learning_rate: float = 2e-5
    num_epochs: int = 3
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    min_samples_for_retrain: int = 1000
    retrain_interval_hours: int = 24
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
