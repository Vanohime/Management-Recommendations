"""
RecommendationService: оркестрация всех компонентов системы
"""
import numpy as np
from typing import Dict, List
from sqlalchemy.orm import Session

from .data_loader import DataLoader
from .feature_engineer import FeatureEngineer
from .sales_forecaster import SalesForecaster
from .similarity_service import SimilarityService
from .rule_engine import RuleEngine


class RecommendationService:
    """
    High-level orchestrator that combines all components
    Implements the full workflow from chapter 3
    """
    
    def __init__(
        self,
        forecaster: SalesForecaster,
        feature_engineer: FeatureEngineer,
        similarity: SimilarityService,
        rules: RuleEngine
    ):
        """
        Initialize RecommendationService
        
        Args:
            forecaster: Sales forecasting model
            feature_engineer: Feature engineering module
            similarity: Similarity search service
            rules: Rule-based recommendation engine
        """
        self.forecaster = forecaster
        self.feature_engineer = feature_engineer
        self.similarity = similarity
        self.rules = rules
        self.is_ready = False
    
    def initialize(self, db: Session):
        """
        Initialize service: load data, fit feature engineer and similarity service
        
        Args:
            db: Database session
        """
        print("\n" + "="*60)
        print("Initializing RecommendationService...")
        print("="*60)
        
        # Load data
        data_loader = DataLoader(db)
        data_loader.load_data()
        data_loader.validate_data()
        merged_data = data_loader.get_merged_data()
        
        print(f"Loaded {len(merged_data)} valid observations")
        
        # Prepare features and target
        X = self.feature_engineer.fit_transform(merged_data)
        y = merged_data['Sales'].values
        
        print(f"Feature matrix shape: {X.shape}")
        
        # Fit similarity service
        self.similarity.fit(X, y)
        
        self.is_ready = True
        print("✅ RecommendationService initialized successfully")
        print("="*60 + "\n")
    
    def get_recommendation(
        self,
        store_id: int,
        date: str,
        promo_active: int,
        db: Session
    ) -> Dict:
        """
        Get recommendation for specific scenario
        
        Args:
            store_id: Store identifier
            date: Date string (YYYY-MM-DD)
            promo_active: Whether promo is active (0 or 1)
            db: Database session
            
        Returns:
            Dictionary with forecast, benchmark, and recommendations
        """
        if not self.is_ready:
            raise ValueError("Service not initialized. Call initialize() first")
        
        # Step 1: Load store information
        data_loader = DataLoader(db)
        store_info = data_loader.load_store_info(store_id)
        
        # Step 2: Create feature vector for target scenario
        x_target = self.feature_engineer.create_features_for_scenario(
            store_id=store_id,
            date=date,
            promo=promo_active,
            store_info=store_info
        )
        
        # Step 3: Forecast sales
        y_pred = self.forecaster.predict_single(x_target)
        
        # Step 4: Find similar observations
        similar_y, distances = self.similarity.find_similar(x_target)
        
        # Step 5: Calculate benchmark
        benchmark_sales = np.mean(similar_y)
        
        # Step 6: Generate recommendations
        target_features = {
            'Promo': promo_active,
            'CompetitionDistance': store_info['CompetitionDistance'],
            'StoreType': store_info['StoreType'],
            'Assortment': store_info['Assortment'],
            'DayOfWeek': int(date.split('-')[2]),  # Simplified
            'IsWeekend': 1 if int(date.split('-')[2]) >= 5 else 0
        }
        
        recommendations = self.rules.generate_recommendations(
            y_pred=y_pred,
            similar_y=similar_y,
            target_features=target_features
        )
        
        # Return result
        result = {
            'forecast': float(y_pred),
            'benchmark': float(benchmark_sales),
            'recommendations': recommendations,
            'similar_stores': similar_y.tolist(),
            'store_info': {
                'store_id': int(store_id),
                'store_type': str(store_info['StoreType']),
                'assortment': str(store_info['Assortment'])
            },
            'model_type': 'mock' if self.forecaster.is_mock_model() else 'trained'
        }
        
        return result
    
    def get_detailed_analysis(
        self,
        store_id: int,
        date: str,
        promo_active: int,
        db: Session
    ) -> Dict:
        """
        Get detailed analysis with additional statistics
        
        Args:
            store_id: Store identifier
            date: Date string (YYYY-MM-DD)
            promo_active: Whether promo is active (0 or 1)
            db: Database session
            
        Returns:
            Dictionary with detailed analysis
        """
        # Get basic recommendation
        result = self.get_recommendation(store_id, date, promo_active, db)
        
        # Reconstruct target features
        data_loader = DataLoader(db)
        store_info = data_loader.load_store_info(store_id)
        x_target = self.feature_engineer.create_features_for_scenario(
            store_id, date, promo_active, store_info
        )
        
        # Get similarity statistics
        similar_stats = self.similarity.get_similar_statistics(x_target)
        
        # Get performance comparison
        similar_y = np.array(result['similar_stores'])
        comparison = self.rules.compare_to_benchmark(
            y_pred=result['forecast'],
            similar_y=similar_y
        )
        
        # Combine results
        result['similarity_statistics'] = similar_stats
        result['performance_comparison'] = comparison
        
        return result

