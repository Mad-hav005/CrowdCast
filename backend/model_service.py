import os
import joblib
import pandas as pd
from typing import Dict, Any, Tuple
from backend.schemas import PredictionRequest
from backend.feature_engineering import engineer_features

# Resolve the absolute path of the model file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "..", "models", "crowdcast_model_v3.pkl")

class ModelService:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        """Loads the serialized ML pipeline from disk once on startup."""
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Trained model not found at path: {MODEL_PATH}")
        
        try:
            self.model = joblib.load(MODEL_PATH)
            print(f"Successfully loaded CrowdCast model from {MODEL_PATH}")
        except Exception as e:
            raise RuntimeError(f"Error loading model: {str(e)}")

    def predict_risk(self, request: PredictionRequest) -> Tuple[float, int, str]:
        """
        Takes raw request parameters, constructs features, passes them
        through the model, and determines the risk level.
        Returns:
            demand_probability (float): predicted probability of high demand
            prediction (int): binary class (1 for High Demand, 0 otherwise)
            risk_level (str): UI interpretation label ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        # 1. Convert input to dict and run feature engineering to obtain aligned DataFrame
        raw_data = request.model_dump()
        df_input = engineer_features(raw_data)

        # 2. Predict probability
        # predict_proba returns a 2D array: [ [prob_class_0, prob_class_1] ]
        probabilities = self.model.predict_proba(df_input)
        demand_probability = float(probabilities[0][1])

        # 3. Predict binary label (using standard model threshold of 0.5)
        prediction = int(self.model.predict(df_input)[0])

        # 4. Map probability to UI risk level
        # LOW: < 0.30
        # MODERATE: 0.30 <= P < 0.60
        # HIGH: 0.60 <= P < 0.80
        # CRITICAL: >= 0.80
        if demand_probability < 0.30:
            risk_level = "LOW"
        elif demand_probability < 0.60:
            risk_level = "MODERATE"
        elif demand_probability < 0.80:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        return demand_probability, prediction, risk_level

# Singleton instance of model service
model_service = ModelService()
