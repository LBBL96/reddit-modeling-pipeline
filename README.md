# Twitter Sentiment Analysis Pipeline

A comprehensive real-time sentiment analysis system for Twitter data with streaming ingestion, ML model training, automated retraining, and production-ready API deployment.

## Features

- **Real-Time Data Ingestion**: Stream tweets using Twitter API v2
- **Text Preprocessing**: Advanced NLP preprocessing with emoji handling, URL removal, and tokenization
- **Feature Engineering**: Extract meaningful features from text data
- **Model Training**: Fine-tune BERT/transformer models (DistilBERT by default)
- **Model Versioning**: Track model versions with MLflow and Weights & Biases
- **Automated Retraining**: Trigger retraining based on data drift and performance degradation
- **REST API**: FastAPI-based prediction endpoints with Prometheus metrics
- **Monitoring & Logging**: Integrated MLflow, W&B, Prometheus, and Grafana
- **CI/CD Pipeline**: GitHub Actions for testing, building, and deployment
- **Containerization**: Docker and Docker Compose for easy deployment

## Architecture

```
├── src/
│   ├── data_ingestion/       # Twitter streaming and data collection
│   ├── preprocessing/         # Text preprocessing and feature engineering
│   ├── model_training/        # Model training, versioning, and retraining
│   ├── api/                   # FastAPI application
│   ├── tasks/                 # Celery background tasks
│   └── database/              # Database models and connections
├── tests/                     # Unit and integration tests
├── scripts/                   # Utility scripts
├── .github/workflows/         # CI/CD pipelines
└── docker-compose.yml         # Docker orchestration
```

## Prerequisites

- Python 3.10+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional but recommended)
- Twitter API credentials (API Key, Secret, Access Token, Bearer Token)
- Weights & Biases account (optional)

## Quick Start

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd twitter-sentiment-analysis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
- `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET`, `TWITTER_BEARER_TOKEN`
- `DATABASE_URL` (PostgreSQL connection string)
- `REDIS_URL` (Redis connection string)
- `MLFLOW_TRACKING_URI` (MLflow server URL)
- `WANDB_API_KEY` (optional, for W&B tracking)

### 3. Initialize Database

```bash
python scripts/init_db.py
```

### 4. Start Services with Docker Compose

```bash
docker-compose up -d
```

This starts:
- FastAPI application (port 8000)
- PostgreSQL database (port 5432)
- Redis (port 6379)
- MLflow server (port 5000)
- Celery workers for background tasks
- Prometheus (port 9090)
- Grafana (port 3000)

### 5. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **MLflow UI**: http://localhost:5000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## Usage

### Stream Twitter Data

```python
from src.data_ingestion.twitter_streamer import TwitterStreamManager

manager = TwitterStreamManager()
keywords = ['technology', 'AI', 'machine learning']
manager.start_stream(keywords=keywords, save_to_db=True)
```

### Train a Model

```python
from src.model_training.trainer import SentimentModelTrainer

trainer = SentimentModelTrainer()
train_dataset, val_dataset, test_dataset = trainer.prepare_data(texts, labels)
trainer.train(train_dataset, val_dataset)
model_path = trainer.save_model('./trained_models', version='v1.0.0')
```

### Make Predictions via API

```bash
# Single prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this amazing product!"}'

# Batch prediction
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Great service!", "Terrible experience", "It was okay"]}'
```

### Trigger Retraining

```bash
curl -X POST "http://localhost:8000/retrain" \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check and model status |
| `/predict` | POST | Single text sentiment prediction |
| `/predict/batch` | POST | Batch sentiment predictions |
| `/retrain` | POST | Trigger model retraining |
| `/model/info` | GET | Current and recent model information |
| `/data/quality` | GET | Data quality and drift monitoring |
| `/metrics` | GET | Prometheus metrics |

## Model Training & Versioning

The system uses MLflow and Weights & Biases for experiment tracking:

1. **Automatic Logging**: All training runs are logged with hyperparameters and metrics
2. **Model Registry**: Models are versioned and stored with metadata
3. **Experiment Comparison**: Compare different model versions in MLflow/W&B UI
4. **Artifact Storage**: Model checkpoints and artifacts are stored and versioned

## Automated Retraining

The retraining pipeline automatically triggers when:

1. **Data Threshold**: Accumulation of N new unlabeled samples (configurable)
2. **Time-Based**: After X hours since last training (configurable)
3. **Performance Degradation**: When model confidence drops below threshold
4. **Data Drift**: When significant distribution shift is detected

Configure thresholds in `.env`:
```
MIN_SAMPLES_FOR_RETRAIN=1000
RETRAIN_INTERVAL_HOURS=24
```

## Monitoring & Observability

### Prometheus Metrics

- `sentiment_predictions_total`: Total number of predictions
- `sentiment_prediction_duration_seconds`: Prediction latency
- `sentiment_prediction_confidence`: Model confidence distribution

### MLflow Tracking

- Training metrics (loss, accuracy, F1-score)
- Model parameters and hyperparameters
- Model artifacts and checkpoints

### Data Quality Monitoring

- Sentiment distribution tracking
- Prediction confidence monitoring
- Data drift detection
- Model performance degradation alerts

## CI/CD Pipeline

GitHub Actions workflows:

1. **CI Pipeline** (`.github/workflows/ci.yml`):
   - Code linting (flake8, black)
   - Type checking (mypy)
   - Unit tests with coverage
   - Security scanning (Trivy)
   - Docker image build

2. **CD Pipeline** (`.github/workflows/cd.yml`):
   - Docker image build and push
   - Automated deployment
   - Model retraining trigger

### Required GitHub Secrets

- `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET`, `TWITTER_BEARER_TOKEN`
- `DOCKER_USERNAME`, `DOCKER_PASSWORD`
- `DEPLOY_KEY`, `DEPLOY_HOST`
- `MLFLOW_TRACKING_URI`, `WANDB_API_KEY`
- `DATABASE_URL`

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_preprocessing.py
```

## Development

### Code Formatting

```bash
# Format code
black src/

# Check formatting
black --check src/

# Lint code
flake8 src/
```

### Type Checking

```bash
mypy src/ --ignore-missing-imports
```

## Deployment

### Production Deployment

1. **Update environment variables** for production
2. **Build Docker image**:
   ```bash
   docker build -t sentiment-analysis:latest .
   ```
3. **Deploy using docker-compose** or orchestration tool (Kubernetes, ECS, etc.)
4. **Set up monitoring and alerting**
5. **Configure backup and disaster recovery**

### Scaling Considerations

- Use Redis for caching and rate limiting
- Deploy multiple API instances behind a load balancer
- Use Celery for distributed task processing
- Consider using GPU instances for model training
- Implement horizontal scaling for API workers

## Configuration

Key configuration options in `config.py`:

- `MODEL_NAME`: Base transformer model (default: distilbert-base-uncased)
- `MAX_LENGTH`: Maximum sequence length for tokenization
- `BATCH_SIZE`: Training and inference batch size
- `LEARNING_RATE`: Model training learning rate
- `NUM_EPOCHS`: Number of training epochs
- `MIN_SAMPLES_FOR_RETRAIN`: Minimum samples to trigger retraining
- `RETRAIN_INTERVAL_HOURS`: Hours between automatic retraining

## Troubleshooting

### Common Issues

1. **Twitter API Rate Limits**: Implement exponential backoff and respect rate limits
2. **Memory Issues**: Reduce batch size or use gradient accumulation
3. **Database Connection Errors**: Check PostgreSQL is running and credentials are correct
4. **Model Loading Errors**: Ensure model files exist and are not corrupted

### Logs

```bash
# API logs
docker-compose logs api

# Celery worker logs
docker-compose logs celery_worker

# MLflow logs
docker-compose logs mlflow
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass and code is formatted
5. Submit a pull request

## License

See LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review MLflow and W&B dashboards for model insights

## Roadmap

- [ ] Add support for multiple languages
- [ ] Implement active learning for label efficiency
- [ ] Add model interpretability (SHAP, LIME)
- [ ] Support for custom sentiment categories
- [ ] Real-time dashboard for predictions
- [ ] A/B testing framework for model versions
- [ ] Advanced data augmentation techniques
