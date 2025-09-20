# Music Genre Prediction Feature

This document explains the new music genre classification feature that predicts what kind of music genre a customer will prefer based on their profile and purchase history.

## Overview

The genre prediction system analyzes customer data from a music store database (using the Chinook database schema) to predict which music genre a customer is most likely to prefer. It uses machine learning classification to make these predictions.

## How It Works

### 1. Data Analysis

The system analyzes:

- **Purchase History**: Total amount spent, number of tracks bought

- **Genre Preferences**: Historical genre spending patterns

### 2. Training Process

The model uses a **Random Forest Classifier** that:

- Extracts customer purchase patterns by genre
- Identifies each customer's most preferred genre based on spending
- Trains on features like location, spending habits, and genre preferences
- Saves the trained model for predictions

### 3. Prediction Process

When predicting for a new customer:

- Takes customer spending information

- Uses the trained model to predict preferred genre
- Returns the predicted genre with confidence scores

## Database Schema Requirements

Your database should have these tables (standard Chinook schema):

- `customer` - Customer information
- `invoice` - Purchase invoices
- `invoice_line` - Individual track purchases
- `track` - Music track details
- `genre` - Music genres
- `album` - Album information
- `artist` - Artist information

## Setup Instructions

### 1. Environment Variables

Add to your `.env` file:

```env

MODELO_GENERO_ENTRENADO=/app/assets/modelo_genero_entrenado.pkl
```

### 2. Training the Model

#### Option A: Using Docker

```bash
# Train the genre model
docker run --rm -v $(pwd)/.env:/app/.env -v $(pwd)/assets:/app/assets api-model:latest python app.py --app TrainModel --model-type genre

# Or with docker-compose (modify the command)
docker run --rm --env-file .env -v $(pwd)/assets:/app/assets api-model:latest python app.py --app TrainModel --model-type genre
```

#### Option B: Manual Training

```bash
# If running locally
python app.py --app TrainModel --model-type genre
```

### 3. Using the API

#### Train Model Endpoint (if needed)

You can trigger training manually via the API by running the training container.

#### Genre Prediction Endpoint

**Endpoint**: `POST /api/predict-genre`

**Request Body**:

```json
{
  "total_spent": 45.50,
  "total_tracks_bought": 15,
  "genre_spending_ratio": 0.6
}
```

**Response**:

```json
{
  "status": "OK",
  "prediction": {
    "genre": "Rock",
    "confidence": 0.85,
    "all_probabilities": {
      "Rock": 0.85,
      "Pop": 0.10,
      "Jazz": 0.03,
      "Classical": 0.02
    }
  },
  "customer_profile": {
    "total_spent": 45.50,
    "total_tracks_bought": 15,
    "genre_spending_ratio": 0.6
  }
}
```

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `total_spent` | float | No | Total amount spent by customer (defaults to 0.0) |
| `total_tracks_bought` | int | No | Total tracks purchased (defaults to 0) |
| `genre_spending_ratio` | float | No | Ratio of spending on preferred genre (0.0-1.0, defaults to 0.0) |

## Example Usage

### cURL Example

```bash
curl -X POST http://localhost:8000/api/predict-genre \
  -H "Content-Type: application/json" \
  -d '{
    "total_spent": 125.75,
    "total_tracks_bought": 42,
    "genre_spending_ratio": 0.4
  }'
```

### Python Example

```python
import requests

url = "http://localhost:8000/api/predict-genre"
data = {
    "total_spent": 89.99,
    "total_tracks_bought": 28,
    "genre_spending_ratio": 0.7
}

response = requests.post(url, json=data)
result = response.json()

print(f"Predicted genre: {result['prediction']['genre']}")
print(f"Confidence: {result['prediction']['confidence']:.2%}")
```

## Scheduled Training

You can set up automatic retraining using the provided cron file:

### Using the Genre Training Cron

1. Modify your docker-compose.yml to use the genre training cron:

```yaml
environment:
  - CRON_FILE_NAME=TrainGenreModel
```

2.This will retrain the model daily at 2 AM using the schedule in `src/tasks/crontab.

TrainGenreModel`

## Model Features

The classification model uses these features:

1. **Total Spent** (numeric)
2. **Total Tracks Bought** (numeric)
3. **Genre Spending Ratio** (numeric)

## Performance Metrics

When training, the model will output:

- **Accuracy Score**: Overall prediction accuracy
- **Classification Report**: Precision, recall, F1-score per genre
- **Feature Importance**: Which features matter most for predictions

## Troubleshooting

### Common Issues

1. **"Genre model not found"**
   - Solution: Train the model first using the training command above

2. **"Unknown country/state/city" warnings**
   - These are normal for new locations not seen during training
   - The model uses default encodings for unknown locations

3. **Low prediction confidence**
   - May indicate need for more training data
   - Consider retraining with more diverse customer data

### Logs

Check the training logs:

```bash
docker logs train-model -f
```

Check API logs:

```bash  
docker logs api -f
```

## Integration Ideas

1. **Customer Onboarding**: Use for new customers to recommend initial music
2. **Marketing**: Target customers with genre-specific promotions
3. **Inventory**: Stock popular genres based on customer base predictions
4. **Recommendations**: Combine with collaborative filtering for better recommendations

## Data Requirements

For best results, ensure your database has:

- At least 100+ customers with purchase history
- Diverse geographic locations
- Multiple genres with sufficient purchase data
- Customers with varied spending patterns

The model performs better with more diverse and comprehensive training data.