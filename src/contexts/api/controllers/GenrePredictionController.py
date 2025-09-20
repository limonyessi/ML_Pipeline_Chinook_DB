import os
import joblib
import numpy as np
from typing import Dict, Any

from src.contexts.api.models.GenrePredictionRequest import (
    GenrePredictionRequest, 
    GenrePredictionResponse, 
    GenrePrediction
)


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
            
            # Prepare customer features
            customer_features = self._prepare_features(request, encoders)
            
            # Make prediction
            prediction_encoded = model.predict([customer_features])[0]
            prediction_probabilities = model.predict_proba([customer_features])[0]
            
            # Decode the prediction
            predicted_genre = encoders['genre'].inverse_transform([prediction_encoded])[0]
            confidence = max(prediction_probabilities)
            
            # Create probability dictionary
            all_probabilities = {}
            for i, genre in enumerate(genre_classes):
                all_probabilities[genre] = float(prediction_probabilities[i])
            
            # Sort probabilities by confidence
            sorted_probs = dict(sorted(all_probabilities.items(), 
                                     key=lambda x: x[1], reverse=True))
            
            # Create response
            prediction_obj = GenrePrediction(
                genre=predicted_genre,
                confidence=float(confidence),
                all_probabilities=sorted_probs
            )
            
            customer_profile = {
                "total_spent": request.total_spent,
                "total_tracks_bought": request.total_tracks_bought,
                "genre_spending_ratio": request.genre_spending_ratio
            }
            
            response = GenrePredictionResponse(
                status="OK",
                prediction=prediction_obj,
                customer_profile=customer_profile
            )
            
            print(f"Predicted genre: {predicted_genre} with confidence: {confidence:.3f}")
            
            return response.dict()
            
        except Exception as e:
            print(f"Error in genre prediction: {str(e)}")
            return {
                "status": "ERROR",
                "message": f"Prediction failed: {str(e)}",
                "prediction": None,
                "customer_profile": None
            }
    
    def _prepare_features(self, request: GenrePredictionRequest, encoders: Dict[str, Any]) -> list:
        """
        Prepare customer features for the model prediction.
        Feature order: ['total_spent', 'total_tracks_bought', 'genre_spending_ratio']
        """
        try:
            # Prepare feature vector (no geographic features needed)
            features = [
                float(request.total_spent),
                int(request.total_tracks_bought),
                float(request.genre_spending_ratio)
            ]
            
            return features
            
        except Exception as e:
            print(f"Error preparing features: {str(e)}")
            # Return default features if there's an error
            return [0.0, 0, 0.0]