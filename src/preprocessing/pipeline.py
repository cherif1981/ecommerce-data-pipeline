"""
Preprocessing Pipeline - Extract, Transform, Load Pipeline
Handles train/validation/test split and feature engineering.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Tuple, List
from sklearn.model_selection import train_test_split

from .encoder import CategoricalEncoder
from .scaler import FeatureScaler

logger = logging.getLogger(__name__)


class PreprocessingPipeline:
    """
    Complete preprocessing pipeline for e-commerce data.
    Handles: Train/Val/Test split, feature identification, encoding, scaling.
    """
    
    def __init__(self, random_state: int = 42, test_size: float = 0.2, val_size: float = 0.1):
        """
        Initialize preprocessing pipeline.
        
        Args:
            random_state: Seed for reproducibility
            test_size: Proportion of test set (0.2 = 20%)
            val_size: Proportion of validation set (0.1 = 10% of train+val)
        """
        self.random_state = random_state
        self.test_size = test_size
        self.val_size = val_size
        
        self.encoder = CategoricalEncoder()
        self.scaler = FeatureScaler()
        
        self.categorical_features: List[str] = []
        self.numerical_features: List[str] = []
        self.feature_names: List[str] = []
        
        logger.info("✅ Preprocessing Pipeline initialized")
    
    def identify_features(self, df: pd.DataFrame, target_col: str) -> Tuple[List[str], List[str]]:
        """
        Identify categorical and numerical features.
        
        Args:
            df: Input DataFrame
            target_col: Target column name (excluded from features)
            
        Returns:
            Tuple of (numerical_cols, categorical_cols)
        """
        logger.info(f"Identifying feature types (excluding target: '{target_col}')...")
        
        # Get all columns except target
        feature_cols = [col for col in df.columns if col != target_col]
        
        # Identify types
        categorical = df[feature_cols].select_dtypes(include=['object', 'category']).columns.tolist()
        numerical = df[feature_cols].select_dtypes(include=[np.number]).columns.tolist()
        
        self.categorical_features = categorical
        self.numerical_features = numerical
        self.feature_names = numerical + categorical  # Numerical first (sklearn convention)
        
        logger.info(f"  📊 Numerical features ({len(numerical)}): {numerical}")
        logger.info(f"  📊 Categorical features ({len(categorical)}): {categorical}")
        
        return numerical, categorical
    
    def split_data(self, X: pd.DataFrame, y: pd.Series) -> Tuple[
        pd.DataFrame, pd.DataFrame, pd.DataFrame,
        pd.Series, pd.Series, pd.Series
    ]:
        """
        Split data into train/validation/test sets.
        
        Uses stratified split for classification targets.
        
        Returns:
            (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        logger.info("Splitting data into train/validation/test...")
        
        # Determine if target is classification or regression
        should_stratify = (y.dtype == 'object' or 
                          pd.api.types.is_categorical_dtype(y) or 
                          (len(y.unique()) < 20 and y.dtype in ['int64', 'int32']))
        
        # Step 1: Split test set (80% train+val, 20% test)
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y if should_stratify else None
        )
        
        # Step 2: Split validation from train (from the temp set)
        val_size_adjusted = self.val_size / (1 - self.test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp,
            test_size=val_size_adjusted,
            random_state=self.random_state,
            stratify=y_temp if should_stratify else None
        )
        
        # Log split info
        total = len(X)
        logger.info(f"📊 Data split completed:")
        logger.info(f"  🔹 Train:      {len(X_train):5d} samples ({len(X_train)/total*100:5.1f}%)")
        logger.info(f"  🔹 Validation: {len(X_val):5d} samples ({len(X_val)/total*100:5.1f}%)")
        logger.info(f"  🔹 Test:       {len(X_test):5d} samples ({len(X_test)/total*100:5.1f}%)")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def fit_transform_train(self, X_train: pd.DataFrame, X_val: pd.DataFrame, 
                           X_test: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Fit encoder and scaler on training data, then transform all sets.
        
        IMPORTANT: Encoder/Scaler are fit ONLY on training data.
        Validation and test are transformed using training parameters.
        
        Args:
            X_train: Training features
            X_val: Validation features
            X_test: Test features
            
        Returns:
            (X_train_processed, X_val_processed, X_test_processed)
        """
        logger.info("=" * 70)
        logger.info("PREPROCESSING: Fit on TRAIN, Transform on TRAIN+VAL+TEST")
        logger.info("=" * 70)
        
        # Step 1: Encode categorical features (fit on train only)
        if self.categorical_features:
            logger.info(f"\n1️⃣  Encoding categorical features...")
            self.encoder.fit(X_train, self.categorical_features)
            
            X_train = self.encoder.transform(X_train)
            X_val = self.encoder.transform(X_val)
            X_test = self.encoder.transform(X_test)
            logger.info("  ✅ Encoding completed")
        
        # Step 2: Scale numerical features (fit on train only)
        if self.numerical_features:
            logger.info(f"\n2️⃣  Scaling numerical features...")
            self.scaler.fit(X_train, self.numerical_features)
            
            X_train = self.scaler.transform(X_train)
            X_val = self.scaler.transform(X_val)
            X_test = self.scaler.transform(X_test)
            logger.info("  ✅ Scaling completed")
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ PREPROCESSING COMPLETED")
        logger.info("=" * 70)
        
        return X_train, X_val, X_test
    
    def fit_transform(self, df: pd.DataFrame, target_col: str) -> Dict[str, Any]:
        """
        Complete preprocessing pipeline.
        
        Args:
            df: Input DataFrame with features and target
            target_col: Target column name
            
        Returns:
            Dictionary with train/val/test splits and metadata
        """
        logger.info("\n" + "=" * 70)
        logger.info("STARTING PREPROCESSING PIPELINE")
        logger.info("=" * 70)
        
        # Step 1: Separate features and target
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        logger.info(f"Dataset shape: {X.shape}")
        logger.info(f"Target: {target_col} ({y.dtype})")
        
        # Step 2: Identify feature types
        self.identify_features(df, target_col)
        
        # Step 3: Split data
        X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(X, y)
        
        # Step 4: Fit transformers on train, apply to all
        X_train, X_val, X_test = self.fit_transform_train(X_train, X_val, X_test)
        
        # Return all data
        return {
            'X_train': X_train,
            'X_val': X_val,
            'X_test': X_test,
            'y_train': y_train,
            'y_val': y_val,
            'y_test': y_test,
            'feature_names': self.feature_names,
            'categorical_features': self.categorical_features,
            'numerical_features': self.numerical_features,
        }
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform new data using fitted encoder and scaler.
        Used for inference on unseen data.
        
        Args:
            X: Features to transform
            
        Returns:
            Transformed features
        """
        logger.info("Transforming new data for inference...")
        
        # Apply encoder
        if self.categorical_features:
            X = self.encoder.transform(X)
        
        # Apply scaler
        if self.numerical_features:
            X = self.scaler.transform(X)
        
        return X
    
    def save(self, path: str) -> None:
        """Save encoder and scaler."""
        import os
        os.makedirs(path, exist_ok=True)
        
        self.encoder.save(os.path.join(path, 'encoder.pkl'))
        self.scaler.save(os.path.join(path, 'scaler.pkl'))
        
        # Save metadata
        import json
        metadata = {
            'categorical_features': self.categorical_features,
            'numerical_features': self.numerical_features,
            'feature_names': self.feature_names,
        }
        with open(os.path.join(path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Pipeline saved to {path}")
    
    def load(self, path: str) -> None:
        """Load encoder and scaler."""
        import os
        import json
        
        self.encoder.load(os.path.join(path, 'encoder.pkl'))
        self.scaler.load(os.path.join(path, 'scaler.pkl'))
        
        # Load metadata
        with open(os.path.join(path, 'metadata.json'), 'r') as f:
            metadata = json.load(f)
            self.categorical_features = metadata['categorical_features']
            self.numerical_features = metadata['numerical_features']
            self.feature_names = metadata['feature_names']
        
        logger.info(f"✅ Pipeline loaded from {path}")
