"""
RuleEngine: формирование рекомендаций
"""
import numpy as np
from typing import List, Dict


class RuleEngine:
    """
    Rule-based recommendation engine
    Implements 4 rules from chapter 2.3
    """
    
    def __init__(self):
        """Initialize RuleEngine"""
        pass
    
    def generate_recommendations(
        self, 
        y_pred: float, 
        similar_y: np.ndarray,
        target_features: Dict[str, any]
    ) -> List[str]:
        """
        Generate recommendations based on prediction and similar observations
        
        Args:
            y_pred: Predicted sales value
            similar_y: Sales values of K nearest neighbors
            target_features: Dictionary with target scenario features
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        mean_similar = np.mean(similar_y)
        max_similar = np.max(similar_y)
        percentile_75 = np.percentile(similar_y, 75)
        
        # Rule 1: Lagging behind similar stores
        if y_pred < mean_similar * 0.85:
            recommendations.append(
                f"Revenue is below typical ({y_pred:.0f} vs {mean_similar:.0f}). "
                f"Explore practices of the best stores."
            )
        
        # Rule 2: Promo recommendation
        if target_features.get('Promo', 0) == 0:
            # Count high-performing cases with promo
            high_performers = similar_y[similar_y > percentile_75]
            
            if len(high_performers) > 0:
                # In real scenario, would check if these had promo active
                # For now, use simple heuristic
                high_promo_ratio = 0.75  # Mock value
                
                if high_promo_ratio > 0.5:
                    recommendations.append(
                        f"{high_promo_ratio*100:.0f}% of successful cases "
                        f"included a promotion. Consider launching a promotion."
                    )
        
        # Rule 3: Competition environment
        comp_distance = target_features.get('CompetitionDistance', 0)
        if comp_distance > 0 and comp_distance < 1000:  # Close competition
            if y_pred < mean_similar * 0.9:
                recommendations.append(
                    f"Operating in competitive environment (competitor at {comp_distance:.0f}m). "
                    f"Review pricing and assortment strategies."
                )
        
        # Rule 4: Seasonality and preparation
        is_weekend = target_features.get('IsWeekend', 0)
        day_of_week = target_features.get('DayOfWeek', 0)
        
        if is_weekend == 1 and y_pred < mean_similar * 0.95:
            recommendations.append(
                f"Weekend sales forecast is below typical. "
                f"Ensure adequate staffing and inventory."
            )
        
        # Additional rule: Strong performance
        if y_pred > mean_similar * 1.15:
            recommendations.append(
                f"Forecast shows strong performance ({y_pred:.0f} vs {mean_similar:.0f}). "
                f"Prepare for increased customer flow."
            )
        
        # If no specific recommendations, provide general feedback
        if len(recommendations) == 0:
            recommendations.append(
                f"Forecast aligns with similar stores ({y_pred:.0f} vs {mean_similar:.0f}). "
                f"Continue current practices."
            )
        
        return recommendations
    
    def analyze_promo_impact(
        self, 
        similar_y: np.ndarray,
        percentile: float = 75.0
    ) -> Dict[str, float]:
        """
        Analyze promo impact from similar observations
        
        Args:
            similar_y: Sales values of neighbors
            percentile: Percentile threshold for high performers
            
        Returns:
            Dictionary with promo analysis
        """
        threshold = np.percentile(similar_y, percentile)
        high_performers = similar_y[similar_y > threshold]
        
        return {
            'threshold': float(threshold),
            'high_performer_count': int(len(high_performers)),
            'high_performer_ratio': float(len(high_performers) / len(similar_y)),
            'high_performer_mean': float(np.mean(high_performers)) if len(high_performers) > 0 else 0.0
        }
    
    def compare_to_benchmark(
        self,
        y_pred: float,
        similar_y: np.ndarray
    ) -> Dict[str, any]:
        """
        Compare prediction to benchmark from similar observations
        
        Args:
            y_pred: Predicted value
            similar_y: Similar observations
            
        Returns:
            Dictionary with comparison metrics
        """
        mean_similar = np.mean(similar_y)
        median_similar = np.median(similar_y)
        
        return {
            'prediction': float(y_pred),
            'benchmark_mean': float(mean_similar),
            'benchmark_median': float(median_similar),
            'difference_mean': float(y_pred - mean_similar),
            'difference_pct_mean': float((y_pred / mean_similar - 1) * 100),
            'difference_median': float(y_pred - median_similar),
            'difference_pct_median': float((y_pred / median_similar - 1) * 100),
            'performance_category': self._categorize_performance(y_pred, mean_similar)
        }
    
    def _categorize_performance(self, y_pred: float, benchmark: float) -> str:
        """
        Categorize performance relative to benchmark
        
        Args:
            y_pred: Predicted value
            benchmark: Benchmark value
            
        Returns:
            Category string
        """
        ratio = y_pred / benchmark if benchmark > 0 else 1.0
        
        if ratio < 0.85:
            return "significantly_below"
        elif ratio < 0.95:
            return "below"
        elif ratio <= 1.05:
            return "on_target"
        elif ratio <= 1.15:
            return "above"
        else:
            return "significantly_above"

