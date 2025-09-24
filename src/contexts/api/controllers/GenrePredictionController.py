import os
import joblib
import numpy as np
import psycopg2
from typing import Dict, Any
from dotenv import load_dotenv

from src.contexts.api.models.GenrePredictionRequest import (
    GenrePredictionRequest, 
    GenrePredictionResponse
)
from src.contexts.train_model.TrainGenreModel import TrainGenreModel


class GenrePredictionController:
    def execute(self, request: GenrePredictionRequest):
        print(f"Genre prediction request: {request}")
        
        try:
            # Load the trained genre model
            model_path = os.getenv("MODELO_GENERO_ENTRENADO", "/app/assets/modelo_genero_entrenado.pkl")
            
            if not os.path.exists(model_path):
                return {
                    "status": "ERROR", 
                    "message": "Genre model not found. Please train the model first.",
                    "prediction": None,
                    "customer_profile": None
                }
            
            # Load model and encoders
            model_data = joblib.load(model_path)
            model = model_data['model']
            encoders = model_data['label_encoders']
            feature_columns = model_data['feature_columns']
            genre_classes = model_data['genre_classes']
            
            # Extract features from database using customer_id
            customer_features, customer_profile = self._get_features_from_customer_id(request.customer_id)
            if customer_features is None:
                return {
                    "error": f"Customer with ID {request.customer_id} not found."
                }
            
            # Make prediction
            prediction_encoded = model.predict([customer_features])[0]
            
            # Decode the prediction
            predicted_genre = encoders['genre'].inverse_transform([prediction_encoded])[0]
            
            # Create simplified response
            response = GenrePredictionResponse(Genre=predicted_genre)
            
            print(f"Predicted genre: {predicted_genre} for customer {request.customer_id}")
            
            return response.dict()
            
        except Exception as e:
            print(f"Error in genre prediction: {str(e)}")
            return {
                "error": f"Prediction failed: {str(e)}"
            }
    
    def _get_features_from_customer_id(self, customer_id: int):
        """
        Extract customer features from database using customer_id.
        Returns tuple of (features_list, customer_profile_dict)
        """
        try:
            # Load environment variables for database connection
            load_dotenv("/app/.env")
            USER = os.getenv("SUPABASE_USER")
            PASSWORD = os.getenv("SUPABASE_PASSWORD")
            HOST = os.getenv("SUPABASE_HOST")
            PORT = os.getenv("SUPABASE_PORT")
            DBNAME = os.getenv("SUPABASE_DBNAME")
            
            if not all([USER, PASSWORD, HOST, PORT, DBNAME]):
                print("Error: Database environment variables not loaded")
                return None, None
            
            with psycopg2.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                port=PORT,
                dbname=DBNAME
            ) as connection:
                
                customer_data = TrainGenreModel.get_customer_features(customer_id, connection)
                
                if customer_data is None:
                    return None, None
                
                # Prepare features in the same order as training
                features = [
                    customer_data['total_spent'],
                    customer_data['total_tracks_bought'],
                    customer_data['genre_spending_ratio']
                ]
                
                customer_profile = {
                    "customer_id": customer_data['customer_id'],
                    "total_spent": customer_data['total_spent'],
                    "total_tracks_bought": customer_data['total_tracks_bought'],
                    "genre_spending_ratio": customer_data['genre_spending_ratio']
                }
                
                return features, customer_profile
                
        except Exception as e:
            print(f"Error extracting customer features from database: {e}")
            return None, None