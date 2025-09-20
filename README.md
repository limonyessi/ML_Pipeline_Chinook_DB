# Pipeline supabase-api-ml

Comprehensive setup, installation, and usage instructions are in `manual.txt`.

Quick Start:

1. Create a `.env` with Supabase/Postgres credentials (see manual).
2. Build image: `docker build -t api-model:latest .`
3. Create external network if not present: `docker network create web`
4. Start services: `docker compose up -d`
5. Check health: `curl http://localhost:8000/api/health-check`
6. Predict (regression): POST `http://localhost:8000/api/model` with body `{ "sex": "M", "nuevo": 6 }`.
7. Predict genre: POST `http://localhost:8000/api/predict-genre` with customer data (see GENRE_PREDICTION_GUIDE.md).

## New Feature: Music Genre Prediction

Train genre classification model:
- `python app.py --app TrainModel --model-type genre`
- Or via Docker: `docker run --rm --env-file .env -v $(pwd)/assets:/app/assets api-model:latest python app.py --app TrainModel --model-type genre`

See `GENRE_PREDICTION_GUIDE.md` for detailed usage instructions.

See `manual.txt` for:

- Docker Desktop install (Windows)
- Using Supabase vs local Postgres
- Training flow and retraining
- Troubleshooting & extension ideas
