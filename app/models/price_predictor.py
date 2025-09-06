"""
ML Model Price Prediction Framework
Production-ready ML model with automated training and model management
"""

import joblib
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle

from ..config.settings import settings, get_model_path
from ..utils.monitoring import ModelMetrics

logger = logging.getLogger(__name__)

class PricePredictionModel:
    """
    Production-ready ML model for vehicle price prediction
    Supports training, inference, and model versioning
    """
    
    def __init__(self):
        self.model: Optional[RandomForestRegressor] = None
        self.scaler: Optional[StandardScaler] = None
        self.encoders: Dict[str, LabelEncoder] = {}
        self.feature_columns: List[str] = []
        self.model_version: str = "1.0.0"
        self.model_path = get_model_path()
        self.metrics = ModelMetrics()
        self.is_loaded = False
        
        # Model configuration
        self.model_config = {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 5,
            "min_samples_leaf": 2,
            "random_state": 42
        }
        
    async def load_model(self):
        """Load trained model from disk"""
        try:
            if self.model_path.exists():
                logger.info(f"📦 Loading model from {self.model_path}")
                
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.encoders = model_data['encoders']
                self.feature_columns = model_data['feature_columns']
                self.model_version = model_data.get('version', '1.0.0')
                
                self.is_loaded = True
                logger.info(f"✅ Model loaded successfully, version: {self.model_version}")
                
            else:
                logger.warning("⚠️ No trained model found, will train new model")
                await self._train_initial_model()
                
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            await self._train_initial_model()
    
    async def _train_initial_model(self):
        """Train initial model with sample data"""
        logger.info("🏋️ Training initial model...")
        
        # Generate sample training data for initial model
        sample_data = self._generate_sample_data()
        await self.train(sample_data)
    
    async def train(self, training_data: pd.DataFrame):
        """Train the ML model with new data"""
        try:
            logger.info(f"🏋️ Training model with {len(training_data)} samples")
            
            # Prepare features and target
            X, y = self._prepare_training_data(training_data)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            if self.scaler is None:
                self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = RandomForestRegressor(**self.model_config)
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_pred = self.model.predict(X_train_scaled)
            test_pred = self.model.predict(X_test_scaled)
            
            metrics = {
                "train_rmse": np.sqrt(mean_squared_error(y_train, train_pred)),
                "test_rmse": np.sqrt(mean_squared_error(y_test, test_pred)),
                "test_r2": r2_score(y_test, test_pred),
                "test_mae": mean_absolute_error(y_test, test_pred)
            }
            
            logger.info(f"📊 Model metrics: {metrics}")
            
            # Save model
            await self._save_model()
            
            # Update metrics
            await self.metrics.update_model_metrics(metrics)
            
            self.is_loaded = True
            logger.info("✅ Model training completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
            raise
    
    async def retrain(self, new_data: pd.DataFrame):
        """Retrain model with new data"""
        logger.info("🔄 Retraining model with new data...")
        
        # Backup current model
        backup_path = self.model_path.parent / f"model_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        if self.model_path.exists():
            import shutil
            shutil.copy2(self.model_path, backup_path)
        
        # Train with new data
        await self.train(new_data)
        
        # Update version
        version_parts = self.model_version.split('.')
        version_parts[-1] = str(int(version_parts[-1]) + 1)
        self.model_version = '.'.join(version_parts)
        
        await self._save_model()
    
    async def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Make price prediction"""
        if not self.is_loaded or self.model is None:
            raise ValueError("Model not loaded")
        
        try:
            # Prepare features
            feature_vector = self._prepare_features(features)
            
            # Scale features
            feature_vector_scaled = self.scaler.transform([feature_vector])
            
            # Make prediction
            prediction = self.model.predict(feature_vector_scaled)[0]
            
            # Calculate confidence (based on tree consensus)
            tree_predictions = [tree.predict(feature_vector_scaled)[0] for tree in self.model.estimators_]
            confidence = 1 - (np.std(tree_predictions) / np.mean(tree_predictions))
            confidence = max(0, min(1, confidence))  # Clamp between 0 and 1
            
            # Calculate price range
            price_std = np.std(tree_predictions)
            price_range = {
                "min": max(0, prediction - 2 * price_std),
                "max": prediction + 2 * price_std
            }
            
            result = {
                "price": float(prediction),
                "confidence": float(confidence),
                "price_range": price_range,
                "model_version": self.model_version
            }
            
            # Record prediction metrics
            await self.metrics.record_prediction(result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            raise
    
    async def predict_batch(self, features_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Make batch predictions"""
        if not self.is_loaded or self.model is None:
            raise ValueError("Model not loaded")
        
        results = []
        for features in features_list:
            result = await self.predict(features)
            results.append(result)
        
        return results
    
    def _prepare_training_data(self, data: pd.DataFrame) -> tuple:
        """Prepare training data for model"""
        # Define features and target
        feature_cols = ['vehicle_age', 'mileage', 'vehicle_type', 'brand', 'fuel_type', 'transmission', 'condition']
        target_col = 'price'
        
        # Handle missing columns
        for col in feature_cols:
            if col not in data.columns:
                data[col] = 'unknown'
        
        # Encode categorical features
        X = data[feature_cols].copy()
        for col in ['vehicle_type', 'brand', 'fuel_type', 'transmission', 'condition']:
            if col in X.columns:
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                    X[col] = self.encoders[col].fit_transform(X[col].astype(str))
                else:
                    # Handle unseen categories
                    known_categories = self.encoders[col].classes_
                    X[col] = X[col].astype(str)
                    X[col] = X[col].apply(lambda x: x if x in known_categories else 'unknown')
                    X[col] = self.encoders[col].transform(X[col])
        
        self.feature_columns = feature_cols
        y = data[target_col] if target_col in data.columns else pd.Series([20000] * len(data))
        
        return X.fillna(0), y
    
    def _prepare_features(self, features: Dict[str, Any]) -> List[float]:
        """Prepare features for prediction"""
        feature_vector = []
        
        for col in self.feature_columns:
            value = features.get(col, 'unknown')
            
            if col in self.encoders:
                # Encode categorical feature
                if str(value) in self.encoders[col].classes_:
                    encoded_value = self.encoders[col].transform([str(value)])[0]
                else:
                    # Handle unseen category
                    encoded_value = self.encoders[col].transform(['unknown'])[0]
                feature_vector.append(encoded_value)
            else:
                # Numerical feature
                feature_vector.append(float(value) if value is not None else 0.0)
        
        return feature_vector
    
    def _generate_sample_data(self) -> pd.DataFrame:
        """Generate sample training data for initial model"""
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'vehicle_age': np.random.randint(0, 20, n_samples),
            'mileage': np.random.randint(5000, 200000, n_samples),
            'vehicle_type': np.random.choice(['car', 'suv', 'truck'], n_samples),
            'brand': np.random.choice(['toyota', 'ford', 'honda', 'bmw', 'mercedes'], n_samples),
            'fuel_type': np.random.choice(['gasoline', 'diesel', 'electric'], n_samples),
            'transmission': np.random.choice(['automatic', 'manual'], n_samples),
            'condition': np.random.choice(['excellent', 'good', 'fair', 'poor'], n_samples)
        }
        
        # Generate realistic prices based on features
        df = pd.DataFrame(data)
        base_price = 25000
        df['price'] = (
            base_price 
            - df['vehicle_age'] * 1000 
            - df['mileage'] * 0.05
            + np.random.normal(0, 2000, n_samples)
        )
        df['price'] = np.maximum(df['price'], 5000)  # Minimum price
        
        return df
    
    async def _save_model(self):
        """Save model to disk"""
        try:
            # Create model directory if it doesn't exist
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'encoders': self.encoders,
                'feature_columns': self.feature_columns,
                'version': self.model_version,
                'saved_at': datetime.now()
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"💾 Model saved to {self.model_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save model: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if model is healthy and ready"""
        try:
            if not self.is_loaded or self.model is None:
                return False
            
            # Test prediction with sample data
            test_features = {
                'vehicle_age': 5,
                'mileage': 50000,
                'vehicle_type': 'car',
                'brand': 'toyota',
                'fuel_type': 'gasoline',
                'transmission': 'automatic',
                'condition': 'good'
            }
            
            result = await self.predict(test_features)
            return 'price' in result and result['price'] > 0
            
        except Exception as e:
            logger.error(f"Model health check failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup model resources"""
        logger.info("🧹 Cleaning up ML model resources...")
        self.model = None
        self.scaler = None
        self.encoders = {}
        self.is_loaded = False
