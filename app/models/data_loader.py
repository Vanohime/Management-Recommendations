"""
DataLoader: загрузка и валидация данных
"""
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Tuple


class DataLoader:
    """Loads and validates data from PostgreSQL database"""
    
    def __init__(self, db: Session):
        """
        Initialize DataLoader with database session
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.sales = None
        self.stores = None
        self.merged_data = None
    
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Loads and merges data from database
        
        Returns:
            Tuple of (merged_data, stores_data)
        """
        # Load sales data
        query = text("SELECT * FROM sales")
        self.sales = pd.read_sql(query, self.db.bind)
        
        # Load stores data
        query = text("SELECT * FROM stores")
        self.stores = pd.read_sql(query, self.db.bind)
        
        # Merge sales with store characteristics
        self.merged_data = pd.merge(self.sales, self.stores, on='Store', how='left')
        
        # Convert Date to datetime
        self.merged_data['Date'] = pd.to_datetime(self.merged_data['Date'])
        
        print(f"Loaded {len(self.sales)} sales records and {len(self.stores)} stores")
        
        return self.merged_data, self.stores
    
    def load_store_info(self, store_id: int) -> pd.Series:
        """
        Load information for specific store
        
        Args:
            store_id: Store identifier
            
        Returns:
            Series with store information
        """
        if self.stores is None:
            query = text("SELECT * FROM stores")
            self.stores = pd.read_sql(query, self.db.bind)
        
        store_info = self.stores[self.stores['Store'] == store_id]
        
        if len(store_info) == 0:
            raise ValueError(f"Store {store_id} not found in database")
        
        return store_info.iloc[0]
    
    def validate_data(self) -> bool:
        """
        Validate loaded data: filter closed days and zero sales
        
        Returns:
            True if validation passed
        """
        if self.merged_data is None:
            raise ValueError("Data not loaded. Call load_data() first")
        
        initial_count = len(self.merged_data)
        
        # Filter: only open stores
        self.merged_data = self.merged_data[self.merged_data['Open'] == 1]
        
        # Filter: only positive sales
        self.merged_data = self.merged_data[self.merged_data['Sales'] > 0]
        
        final_count = len(self.merged_data)
        
        print(f"Validation: {initial_count} -> {final_count} records "
              f"({initial_count - final_count} filtered)")
        
        return final_count > 0
    
    def get_merged_data(self) -> pd.DataFrame:
        """
        Get merged and validated data
        
        Returns:
            Merged DataFrame
        """
        if self.merged_data is None:
            raise ValueError("Data not loaded. Call load_data() first")
        
        return self.merged_data

