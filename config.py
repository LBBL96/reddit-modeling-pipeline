from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    twitter_api_key: str
    twitter_api_secret: str
    twitter_access_token: str
    twitter_access_secret: str
    twitter_bearer_token: str
    
    wandb_api_key: Optional[str] = None
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
