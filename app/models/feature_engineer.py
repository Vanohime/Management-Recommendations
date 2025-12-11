"""
FeatureEngineer: генерация признаков
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List


class FeatureEngineer:
    """
    Feature engineering: generates temporal, competition, and promo features
    Implements principles from chapter 2.2
    """
    
    def __init__(self):
        """Initialize FeatureEngineer"""
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.numerical_cols = None
        self.is_fitted = False
    
    def generate_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate calendar features from date
        
        Args:
            df: DataFrame with Date column
            
        Returns:
            DataFrame with added temporal features
        """
        df = df.copy()
        
        # Ensure Date is datetime
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            df['Date'] = pd.to_datetime(df['Date'])
        
        # Calendar features
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['Day'] = df['Date'].dt.day
        df['WeekOfYear'] = df['Date'].dt.isocalendar().week.astype(int)
        df['IsWeekend'] = (df['DayOfWeek'] >= 5).astype(int)
        
        return df
    
    def generate_competition_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate competition features
        
        Args:
            df: DataFrame with competition data
            
        Returns:
            DataFrame with added competition features
        """
        df = df.copy()
        
        # Has competition data
        df['HasCompetition'] = df['CompetitionDistance'].notna().astype(int)
        df['CompetitionDistance'] = df['CompetitionDistance'].fillna(0)
        
        # Months since competition opened
        df['CompetitionMonthsOpen'] = (
            (df['Year'] - df['CompetitionOpenSinceYear']) * 12 +
            (df['Month'] - df['CompetitionOpenSinceMonth'])
        ).fillna(0).clip(lower=0).astype(int)
        
        df['HasCompetitionData'] = (
            df['CompetitionOpenSinceYear'].notna() & 
            df['CompetitionOpenSinceMonth'].notna()
        ).astype(int)
        
        return df
    
    def generate_promo_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate promo features
        
        Args:
            df: DataFrame with promo data
            
        Returns:
            DataFrame with added promo features
        """
        df = df.copy()
        
        # Weeks since Promo2 started
        df['Promo2LastsForNWeeks'] = np.where(
            df['Promo2'] == 1,
            np.maximum(0, (df['Year'] - df['Promo2SinceYear']) * 52 + 
                       (df['WeekOfYear'] - df['Promo2SinceWeek'])),
            0
        ).astype(int)
        
        return df
    
    def encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        One-hot encode categorical features
        
        Args:
            df: DataFrame with categorical features
            
        Returns:
            DataFrame with encoded features
        """
        df = df.copy()
        
        cat_cols = ['StoreType', 'Assortment', 'StateHoliday']
        
        # One-hot encoding
        df_encoded = pd.get_dummies(df, columns=cat_cols, drop_first=False, dtype=int)
        
        return df_encoded
    
    def select_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Select relevant features for model
        
        Args:
            df: DataFrame with all features
            
        Returns:
            DataFrame with selected features
        """
        # Features to drop (not useful for model)
        useless_features = [
            'id', 'Store', 'Date', 'Open', 'Sales', 'Customers',
            'CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear',
            'Promo2SinceWeek', 'Promo2SinceYear', 'PromoInterval',
            'Year', 'WeekOfYear'
        ]
        
        # Drop useless features
        features = df.copy()
        cols_to_drop = [col for col in useless_features if col in features.columns]
        features = features.drop(columns=cols_to_drop, errors='ignore')
        
        return features
    
    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        """
        Fit scaler and transform data
        
        Args:
            df: DataFrame with raw data
            
        Returns:
            Scaled feature matrix
        """
        df = self.generate_temporal_features(df)
        df = self.generate_competition_features(df)
        df = self.generate_promo_features(df)
        df = self.encode_categorical(df)
        features = self.select_features(df)
        
        # Store feature columns
        self.feature_columns = features.columns.tolist()
        
        # Identify numerical columns for scaling
        self.numerical_cols = features.select_dtypes(include=[np.number]).columns.tolist()
        
        # Fit and transform
        X = features.copy()
        X[self.numerical_cols] = self.scaler.fit_transform(X[self.numerical_cols])
        
        self.is_fitted = True
        
        return X.values
    
    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """
        Transform new data using fitted scaler
        
        Args:
            df: DataFrame with raw data
            
        Returns:
            Scaled feature matrix
        """
        if not self.is_fitted:
            raise ValueError("FeatureEngineer not fitted. Call fit_transform() first")
        
        df = self.generate_temporal_features(df)
        df = self.generate_competition_features(df)
        df = self.generate_promo_features(df)
        df = self.encode_categorical(df)
        features = self.select_features(df)
        
        # Ensure same columns as training
        for col in self.feature_columns:
            if col not in features.columns:
                features[col] = 0
        
        # Select only training columns in same order
        features = features[self.feature_columns]
        
        # Transform
        X = features.copy()
        X[self.numerical_cols] = self.scaler.transform(X[self.numerical_cols])
        
        return X.values
    
    def create_features_for_scenario(self, store_id: int, date: str, promo: int, 
                                     store_info: pd.Series) -> np.ndarray:
        """
        Create feature vector for a specific scenario
        
        Args:
            store_id: Store identifier
            date: Date string (YYYY-MM-DD)
            promo: Promo active (0 or 1)
            store_info: Store characteristics from database
            
        Returns:
            Feature vector for prediction
        """
        # Create DataFrame with scenario
        scenario_data = {
            'Store': [store_id],
            'Date': [pd.to_datetime(date)],
            'DayOfWeek': [pd.to_datetime(date).dayofweek + 1],
            'Open': [1],
            'Promo': [promo],
            'StateHoliday': ['0'],
            'SchoolHoliday': [0],
            'StoreType': [store_info['StoreType']],
            'Assortment': [store_info['Assortment']],
            'CompetitionDistance': [store_info['CompetitionDistance']],
            'CompetitionOpenSinceMonth': [store_info['CompetitionOpenSinceMonth']],
            'CompetitionOpenSinceYear': [store_info['CompetitionOpenSinceYear']],
            'Promo2': [store_info['Promo2']],
            'Promo2SinceWeek': [store_info['Promo2SinceWeek']],
            'Promo2SinceYear': [store_info['Promo2SinceYear']],
            'PromoInterval': [store_info['PromoInterval']]
        }
        
        df_scenario = pd.DataFrame(scenario_data)
        
        # Transform
        X_scenario = self.transform(df_scenario)
        
        return X_scenario[0]  # Return single vector

