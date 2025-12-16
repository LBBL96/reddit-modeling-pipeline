import pytest
from src.model_training.trainer import (
    SentimentModelTrainer,
    label_to_sentiment,
    sentiment_to_label
)


def test_label_to_sentiment():
    assert label_to_sentiment(0) == 'negative'
    assert label_to_sentiment(1) == 'neutral'
    assert label_to_sentiment(2) == 'positive'
    assert label_to_sentiment(999) == 'unknown'


def test_sentiment_to_label():
    assert sentiment_to_label('negative') == 0
    assert sentiment_to_label('neutral') == 1
    assert sentiment_to_label('positive') == 2
    assert sentiment_to_label('POSITIVE') == 2
    assert sentiment_to_label('unknown') == 1


class TestSentimentModelTrainer:
    def test_trainer_initialization(self):
        trainer = SentimentModelTrainer()
        assert trainer.tokenizer is not None
        assert trainer.num_labels == 3
    
    def test_prepare_data(self):
        trainer = SentimentModelTrainer()
        texts = ["Great!", "Terrible!", "Okay"] * 50
        labels = [2, 0, 1] * 50
        
        train_dataset, val_dataset, test_dataset = trainer.prepare_data(
            texts, labels, test_size=0.2, val_size=0.1
        )
        
        assert len(train_dataset) > 0
        assert len(val_dataset) > 0
        assert len(test_dataset) > 0
