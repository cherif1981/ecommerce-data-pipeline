"""Categorical encoder for handling categorical features."""

import pickle
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import logging

logger = logging.getLogger(__name__)


class CategoricalEncoder:
    """Encode categorical features using LabelEncoder with proper fit/transform separation."""
    
    def __init__(self):
        self.encoders: Dict[str, LabelEncoder] = {}
        self.categorical_features: List[str] = []
        self.fitted = False
    
    def fit(self, X: pd.DataFrame, categorical_cols: List[str]) -> 'CategoricalEncoder':
        """
        Fit the encoder on training data.
        
        Args:
            X: DataFrame containing categorical features
            categorical_cols: List of categorical column names
            
        Returns:
            Self for method chaining
        """
        logger.info(f"Fitting encoder on {len(categorical_cols)} categorical features...")
        
        self.categorical_features = categorical_cols
        self.encoders = {}
        
        for col in categorical_cols:
            if col not in X.columns:
                raise ValueError(f"Column '{col}' not found in DataFrame")
            
            le = LabelEncoder()
            le.fit(X[col].astype(str))
            self.encoders[col] = le
            
            logger.info(f"  ✅ Fitted '{col}' with {len(le.classes_)} classes: {le.classes_.tolist()[:5]}...")
        
        self.fitted = True
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform categorical features using fitted encoders.
        
        Args:
            X: DataFrame to transform
            
        Returns:
            Transformed DataFrame
        """
        if not self.fitted:
            raise ValueError("Encoder must be fitted before transform")
        
        X_transformed = X.copy()
        
        for col in self.categorical_features:
            if col not in X.columns:
                raise ValueError(f"Column '{col}' not found in DataFrame")
            
            try:
                X_transformed[col] = self.encoders[col].transform(X[col].astype(str))
            except ValueError as e:
                # Handle unseen categories by replacing with -1
                logger.warning(f"Unseen categories in '{col}': {e}")
                X_transformed[col] = X[col].astype(str).apply(
                    lambda x: self.encoders[col].transform([x])[0] 
                    if x in self.encoders[col].classes_ 
                    else -1
                )
        
        return X_transformed
    
    def fit_transform(self, X: pd.DataFrame, categorical_cols: List[str]) -> pd.DataFrame:
        """
        Fit the encoder and transform data in one step.
        
        Args:
            X: DataFrame containing categorical features
            categorical_cols: List of categorical column names
            
        Returns:
            Transformed DataFrame
        """
        return self.fit(X, categorical_cols).transform(X)
    
    def save(self, path: str) -> None:
        """Save encoder to disk."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'encoders': self.encoders,
                'categorical_features': self.categorical_features,
                'fitted': self.fitted
            }, f)
        logger.info(f"✅ Encoder saved to {path}")
    
    def load(self, path: str) -> 'CategoricalEncoder':
        """Load encoder from disk."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.encoders = data['encoders']
            self.categorical_features = data['categorical_features']
            self.fitted = data['fitted']
        logger.info(f"✅ Encoder loaded from {path}")
        return self
    
    def get_feature_names(self) -> List[str]:
        """Get list of categorical features."""
        return self.categorical_features
    
    def get_classes(self, col: str) -> np.ndarray:
        """Get classes for a specific feature."""
        if col not in self.encoders:
            raise ValueError(f"Column '{col}' not found in fitted encoders")
        return self.encoders[col].classes_
