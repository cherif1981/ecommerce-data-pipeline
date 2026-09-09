"""Feature scaler for numerical features."""

import pickle
from pathlib import Path
from typing import List
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class FeatureScaler:
    """Scale numerical features using StandardScaler with proper fit/transform separation."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.numerical_features: List[str] = []
        self.fitted = False
    
    def fit(self, X: pd.DataFrame, numerical_cols: List[str]) -> 'FeatureScaler':
        """
        Fit the scaler on training data.
        
        Args:
            X: DataFrame containing numerical features
            numerical_cols: List of numerical column names
            
        Returns:
            Self for method chaining
        """
        if len(numerical_cols) == 0:
            logger.warning("No numerical features to scale")
            self.fitted = True
            return self
        
        logger.info(f"Fitting scaler on {len(numerical_cols)} numerical features...")
        
        self.numerical_features = numerical_cols
        self.scaler.fit(X[numerical_cols])
        
        logger.info(f"  ✅ Scaler fitted with mean: {self.scaler.mean_[:3]}...")
        logger.info(f"  ✅ Scaler fitted with std: {self.scaler.scale_[:3]}...")
        
        self.fitted = True
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform numerical features using fitted scaler.
        
        Args:
            X: DataFrame to transform
            
        Returns:
            Transformed DataFrame
        """
        if not self.fitted:
            raise ValueError("Scaler must be fitted before transform")
        
        if len(self.numerical_features) == 0:
            return X.copy()
        
        X_transformed = X.copy()
        X_transformed[self.numerical_features] = self.scaler.transform(X[self.numerical_features])
        
        return X_transformed
    
    def fit_transform(self, X: pd.DataFrame, numerical_cols: List[str]) -> pd.DataFrame:
        """
        Fit the scaler and transform data in one step.
        
        Args:
            X: DataFrame containing numerical features
            numerical_cols: List of numerical column names
            
        Returns:
            Transformed DataFrame
        """
        return self.fit(X, numerical_cols).transform(X)
    
    def inverse_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Inverse transform scaled features back to original scale.
        
        Args:
            X: Scaled DataFrame
            
        Returns:
            DataFrame with original scale
        """
        if not self.fitted:
            raise ValueError("Scaler must be fitted before inverse_transform")
        
        if len(self.numerical_features) == 0:
            return X.copy()
        
        X_inverse = X.copy()
        X_inverse[self.numerical_features] = self.scaler.inverse_transform(X[self.numerical_features])
        
        return X_inverse
    
    def save(self, path: str) -> None:
        """Save scaler to disk."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'scaler': self.scaler,
                'numerical_features': self.numerical_features,
                'fitted': self.fitted
            }, f)
        logger.info(f"✅ Scaler saved to {path}")
    
    def load(self, path: str) -> 'FeatureScaler':
        """Load scaler from disk."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.scaler = data['scaler']
            self.numerical_features = data['numerical_features']
            self.fitted = data['fitted']
        logger.info(f"✅ Scaler loaded from {path}")
        return self
    
    def get_feature_names(self) -> List[str]:
        """Get list of numerical features."""
        return self.numerical_features
    
    def get_mean(self) -> np.ndarray:
        """Get mean values used for scaling."""
        if not self.fitted:
            raise ValueError("Scaler must be fitted first")
        return self.scaler.mean_
    
    def get_std(self) -> np.ndarray:
        """Get standard deviation values used for scaling."""
        if not self.fitted:
            raise ValueError("Scaler must be fitted first")
        return self.scaler.scale_
