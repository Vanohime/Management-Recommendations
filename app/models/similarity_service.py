"""
SimilarityService: поиск похожих наблюдений
"""
import numpy as np
from sklearn.neighbors import NearestNeighbors
from typing import Tuple


class SimilarityService:
    """
    K-nearest neighbors search in feature space
    Implements the similarity search for replication principle
    """
    
    def __init__(self, n_neighbors: int = 5):
        """
        Initialize SimilarityService
        
        Args:
            n_neighbors: Number of nearest neighbors to find
        """
        self.n_neighbors = n_neighbors
        self.knn_model = NearestNeighbors(
            n_neighbors=n_neighbors,
            metric='euclidean',
            algorithm='auto'
        )
        self.X_train = None
        self.y_train = None
        self.is_fitted = False
    
    def fit(self, X_train: np.ndarray, y_train: np.ndarray):
        """
        Fit the KNN model on training data
        
        Args:
            X_train: Training feature matrix
            y_train: Training target values (sales)
        """
        self.X_train = X_train
        self.y_train = y_train
        self.knn_model.fit(X_train)
        self.is_fitted = True
        print(f"✅ SimilarityService fitted on {len(X_train)} observations")
    
    def find_similar(self, x_target: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Find K nearest neighbors for target scenario
        
        Args:
            x_target: Target feature vector
            
        Returns:
            Tuple of (similar_sales, distances)
            - similar_sales: Sales values of K nearest neighbors
            - distances: Euclidean distances to neighbors
        """
        if not self.is_fitted:
            raise ValueError("SimilarityService not fitted. Call fit() first")
        
        # Ensure 2D array
        if len(x_target.shape) == 1:
            x_target = x_target.reshape(1, -1)
        
        # Find K nearest neighbors
        distances, indices = self.knn_model.kneighbors(x_target)
        
        # Get sales values of neighbors
        similar_y = self.y_train[indices[0]]
        
        return similar_y, distances[0]
    
    def get_benchmark_sales(self, x_target: np.ndarray) -> float:
        """
        Get benchmark (average) sales from similar observations
        
        Args:
            x_target: Target feature vector
            
        Returns:
            Average sales of K nearest neighbors
        """
        similar_y, _ = self.find_similar(x_target)
        return float(np.mean(similar_y))
    
    def get_similar_statistics(self, x_target: np.ndarray) -> dict:
        """
        Get statistics about similar observations
        
        Args:
            x_target: Target feature vector
            
        Returns:
            Dictionary with statistics
        """
        similar_y, distances = self.find_similar(x_target)
        
        return {
            'mean_sales': float(np.mean(similar_y)),
            'median_sales': float(np.median(similar_y)),
            'min_sales': float(np.min(similar_y)),
            'max_sales': float(np.max(similar_y)),
            'std_sales': float(np.std(similar_y)),
            'mean_distance': float(np.mean(distances)),
            'sales_values': similar_y.tolist(),
            'distances': distances.tolist()
        }

