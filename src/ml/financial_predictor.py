import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import logging
from typing import Dict, List, Tuple, Optional
import joblib
import os

logger = logging.getLogger(__name__)

class FinancialPredictor:
    def __init__(self, model_dir: str = "models"):
        self.eps_model = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        self.revenue_model = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.model_dir = model_dir
        self.is_trained = False
        
        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
        
        # Try to load existing models
        self._load_models()
        
    def _load_models(self) -> None:
        """Load existing trained models if available."""
        try:
            eps_path = os.path.join(self.model_dir, "eps_model.joblib")
            revenue_path = os.path.join(self.model_dir, "revenue_model.joblib")
            scaler_path = os.path.join(self.model_dir, "scaler.joblib")
            
            if os.path.exists(eps_path) and os.path.exists(revenue_path) and os.path.exists(scaler_path):
                self.eps_model = joblib.load(eps_path)
                self.revenue_model = joblib.load(revenue_path)
                self.scaler = joblib.load(scaler_path)
                self.is_trained = True
                logger.info("Successfully loaded existing models")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
        
    def _save_models(self) -> None:
        """Save trained models to disk."""
        try:
            joblib.dump(self.eps_model, os.path.join(self.model_dir, "eps_model.joblib"))
            joblib.dump(self.revenue_model, os.path.join(self.model_dir, "revenue_model.joblib"))
            joblib.dump(self.scaler, os.path.join(self.model_dir, "scaler.joblib"))
            logger.info("Successfully saved models")
        except Exception as e:
            logger.error(f"Error saving models: {e}")
        
    def prepare_features(self, historical_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare features from historical financial data.
        """
        features = []
        eps_targets = []
        revenue_targets = []
        
        for i in range(len(historical_data) - 4):  # Use 4 quarters of data to predict next quarter
            quarter_data = historical_data[i:i+4]
            
            # Extract features
            feature_vector = []
            for q in quarter_data:
                feature_vector.extend([
                    q.get('revenue', 0),
                    q.get('net_income', 0),
                    q.get('eps', 0),
                    q.get('gross_profit', 0),
                    q.get('operating_income', 0),
                    q.get('total_assets', 0),
                    q.get('total_liabilities', 0),
                    q.get('cash_flow_operations', 0),
                    q.get('cash_flow_investing', 0),
                    q.get('cash_flow_financing', 0)
                ])
            
            # Calculate additional features
            feature_vector.extend([
                # Growth rates
                self._calculate_growth_rate(quarter_data, 'revenue'),
                self._calculate_growth_rate(quarter_data, 'net_income'),
                self._calculate_growth_rate(quarter_data, 'eps'),
                
                # Ratios
                self._calculate_ratio(quarter_data, 'net_income', 'revenue'),  # Net margin
                self._calculate_ratio(quarter_data, 'operating_income', 'revenue'),  # Operating margin
                self._calculate_ratio(quarter_data, 'gross_profit', 'revenue'),  # Gross margin
            ])
            
            # Get target values (next quarter)
            next_quarter = historical_data[i+4]
            eps_target = next_quarter.get('eps', 0)
            revenue_target = next_quarter.get('revenue', 0)
            
            features.append(feature_vector)
            eps_targets.append(eps_target)
            revenue_targets.append(revenue_target)
        
        return np.array(features), np.array(eps_targets), np.array(revenue_targets)
    
    def _calculate_growth_rate(self, data: List[Dict], metric: str) -> float:
        """Calculate the growth rate for a given metric."""
        if len(data) < 2:
            return 0
        current = data[0].get(metric, 0)
        previous = data[1].get(metric, 0)
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100
    
    def _calculate_ratio(self, data: List[Dict], numerator: str, denominator: str) -> float:
        """Calculate a ratio between two metrics."""
        if not data:
            return 0
        num = data[0].get(numerator, 0)
        den = data[0].get(denominator, 0)
        if den == 0:
            return 0
        return num / den
    
    def train(self, historical_data: List[Dict]) -> None:
        """
        Train the models on historical financial data.
        """
        try:
            if len(historical_data) < 8:
                logger.warning("Insufficient data for training")
                return
                
            X, y_eps, y_revenue = self.prepare_features(historical_data)
            
            if len(X) == 0:
                logger.warning("No training data available")
                return
                
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_eps_train, y_eps_test = train_test_split(
                X_scaled, y_eps, test_size=0.2, random_state=42
            )
            
            # Train models
            self.eps_model.fit(X_train, y_eps_train)
            self.revenue_model.fit(X_train, y_revenue)
            
            # Calculate and log model performance
            eps_pred = self.eps_model.predict(X_test)
            revenue_pred = self.revenue_model.predict(X_test)
            
            eps_mae = mean_absolute_error(y_eps_test, eps_pred)
            eps_rmse = np.sqrt(mean_squared_error(y_eps_test, eps_pred))
            eps_r2 = self.eps_model.score(X_test, y_eps_test)
            
            revenue_mae = mean_absolute_error(y_revenue_test, revenue_pred)
            revenue_rmse = np.sqrt(mean_squared_error(y_revenue_test, revenue_pred))
            revenue_r2 = self.revenue_model.score(X_test, y_revenue_test)
            
            logger.info(f"Model training completed:")
            logger.info(f"EPS - R²: {eps_r2:.3f}, MAE: {eps_mae:.3f}, RMSE: {eps_rmse:.3f}")
            logger.info(f"Revenue - R²: {revenue_r2:.3f}, MAE: {revenue_mae:.3f}, RMSE: {revenue_rmse:.3f}")
            
            self.is_trained = True
            self._save_models()
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
    
    def predict(self, recent_data: List[Dict]) -> Dict[str, Optional[float]]:
        """
        Make predictions for the next quarter's EPS and revenue.
        """
        try:
            if not self.is_trained:
                logger.warning("Models not trained yet")
                return {"eps": None, "revenue": None, "confidence": None}
                
            if len(recent_data) < 4:
                logger.warning("Insufficient data for prediction")
                return {"eps": None, "revenue": None, "confidence": None}
            
            # Prepare features from recent data
            features = []
            for q in recent_data[-4:]:
                features.extend([
                    q.get('revenue', 0),
                    q.get('net_income', 0),
                    q.get('eps', 0),
                    q.get('gross_profit', 0),
                    q.get('operating_income', 0),
                    q.get('total_assets', 0),
                    q.get('total_liabilities', 0),
                    q.get('cash_flow_operations', 0),
                    q.get('cash_flow_investing', 0),
                    q.get('cash_flow_financing', 0)
                ])
            
            # Calculate additional features
            features.extend([
                self._calculate_growth_rate(recent_data[-4:], 'revenue'),
                self._calculate_growth_rate(recent_data[-4:], 'net_income'),
                self._calculate_growth_rate(recent_data[-4:], 'eps'),
                self._calculate_ratio(recent_data[-4:], 'net_income', 'revenue'),
                self._calculate_ratio(recent_data[-4:], 'operating_income', 'revenue'),
                self._calculate_ratio(recent_data[-4:], 'gross_profit', 'revenue')
            ])
            
            # Scale features and make predictions
            features_scaled = self.scaler.transform([features])
            
            eps_prediction = self.eps_model.predict(features_scaled)[0]
            revenue_prediction = self.revenue_model.predict(features_scaled)[0]
            
            # Calculate confidence score based on feature importance
            eps_confidence = self._calculate_confidence(features_scaled, self.eps_model)
            revenue_confidence = self._calculate_confidence(features_scaled, self.revenue_model)
            
            return {
                "eps": round(eps_prediction, 2),
                "revenue": round(revenue_prediction, 2),
                "confidence": round((eps_confidence + revenue_confidence) / 2, 2)
            }
            
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            return {"eps": None, "revenue": None, "confidence": None}
            
    def _calculate_confidence(self, features: np.ndarray, model: RandomForestRegressor) -> float:
        """Calculate a confidence score based on feature importance and prediction variance."""
        try:
            # Get predictions from all trees
            predictions = np.array([tree.predict(features) for tree in model.estimators_])
            
            # Calculate prediction variance
            variance = np.var(predictions)
            
            # Calculate feature importance
            importance = model.feature_importances_
            
            # Combine variance and feature importance into a confidence score
            confidence = 1 / (1 + variance) * np.mean(importance)
            
            return min(max(confidence, 0), 1)  # Normalize between 0 and 1
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5  # Default confidence score 