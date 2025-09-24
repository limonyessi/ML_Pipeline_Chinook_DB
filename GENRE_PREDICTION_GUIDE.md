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
- Trains on features like spending habits and genre preferences
- Saves the trained model for predictions

### 3. Prediction Process

When predicting for a customer:

- Takes customer ID as input
- Uses the trained model to predict preferred genre
- Returns the predicted genre in a simple format

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

**Endpoint**: `POST /api/model`

**Request Body**:

```json
{
  "customer_id": 12
}
```

**Response**:

```json
{
  "Genre": "Rock"
}
```

**Error Response**:

```json
{
  "error": "Customer with ID 999 not found."
}
```

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_id` | int | Yes | The customer ID from your database |

## Example Usage

### cURL Example

```bash
curl -X POST http://localhost:8000/api/model \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 12
  }'
```

### Python Example

```python
import requests

url = "http://localhost:8000/api/model"
data = {
    "customer_id": 25
}

response = requests.post(url, json=data)
result = response.json()

print(f"Predicted genre: {result['Genre']}")
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

Note: The API returns only the predicted genre for simplicity, but the model internally calculates confidence scores during training and evaluation.

## Troubleshooting

### Common Issues

1. **"Genre model not found"**
   - Solution: Train the model first using the training command above

2. **"Customer with ID X not found"**
   - The customer doesn't exist in your database
   - Check that the customer_id is correct

3. **Empty or unexpected response**
   - May indicate the customer has limited purchase history
   - Check that the model has been trained with sufficient data
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

1. **Customer Onboarding**: For existing customers, predict their preferred genre to recommend initial music
2. **Marketing**: Target customers with genre-specific promotions based on their predicted preferences  
3. **Inventory**: Stock popular genres based on customer base predictions
4. **Recommendations**: Combine with collaborative filtering for better recommendations
5. **Customer Support**: Help support agents understand customer music preferences quickly
6. **Analytics**: Analyze customer segments by predicted genre preferences
7. **Personalization**: Customize the UI/UX based on predicted musical tastes

## Benefits of the Simplified Approach

- **Automatic Feature Extraction**: No need to manually calculate customer statistics
- **Real-time Data**: Uses the latest customer purchase data from the database
- **Consistency**: Eliminates human error in feature calculation
- **Simplicity**: Requires only the customer ID and returns only the essential prediction
- **Scalability**: Can be easily integrated into existing customer workflows
- **Lightweight Response**: Minimal data transfer for better performance
- **Easy Integration**: Simple JSON response format that's easy to parse

## Data Requirements

For best results, ensure your database has:

- At least 100+ customers with purchase history
- Multiple genres with sufficient purchase data
- Customers with varied spending patterns
- Rich purchase history across different music genres

The model performs better with more diverse and comprehensive training data.