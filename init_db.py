"""
Script to initialize PostgreSQL database and load data from CSV files
"""
import pandas as pd
from sqlalchemy.orm import Session
from app.database import engine, Base, Sale, Store, SessionLocal
import sys
import os

# Add parent directory to path to import CSV files
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_csv_data():
    """Load CSV files"""
    print("Loading CSV files...")
    train_df = pd.read_csv('../train.csv')
    store_df = pd.read_csv('../store.csv')
    print(f"Loaded {len(train_df)} sales records and {len(store_df)} stores")
    return train_df, store_df


def init_database():
    """Initialize database and load data"""
    print("Creating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    # Load CSV data
    train_df, store_df = load_csv_data()
    
    # Convert date column
    train_df['Date'] = pd.to_datetime(train_df['Date'])
    
    # Fill NaN values in store_df
    store_df['CompetitionDistance'] = store_df['CompetitionDistance'].fillna(0)
    store_df['CompetitionOpenSinceMonth'] = store_df['CompetitionOpenSinceMonth'].fillna(0)
    store_df['CompetitionOpenSinceYear'] = store_df['CompetitionOpenSinceYear'].fillna(0)
    store_df['Promo2SinceWeek'] = store_df['Promo2SinceWeek'].fillna(0)
    store_df['Promo2SinceYear'] = store_df['Promo2SinceYear'].fillna(0)
    store_df['PromoInterval'] = store_df['PromoInterval'].fillna('')
    
    db = SessionLocal()
    
    try:
        # Insert stores
        print("Inserting store data...")
        for _, row in store_df.iterrows():
            store = Store(
                Store=int(row['Store']),
                StoreType=str(row['StoreType']),
                Assortment=str(row['Assortment']),
                CompetitionDistance=float(row['CompetitionDistance']),
                CompetitionOpenSinceMonth=float(row['CompetitionOpenSinceMonth']),
                CompetitionOpenSinceYear=float(row['CompetitionOpenSinceYear']),
                Promo2=int(row['Promo2']),
                Promo2SinceWeek=float(row['Promo2SinceWeek']),
                Promo2SinceYear=float(row['Promo2SinceYear']),
                PromoInterval=str(row['PromoInterval'])
            )
            db.add(store)
        
        db.commit()
        print(f"Inserted {len(store_df)} stores")
        
        # Insert sales (in batches for better performance)
        print("Inserting sales data...")
        batch_size = 10000
        for i in range(0, len(train_df), batch_size):
            batch = train_df.iloc[i:i+batch_size]
            sales_objects = []
            
            for _, row in batch.iterrows():
                sale = Sale(
                    Store=int(row['Store']),
                    Date=row['Date'],
                    DayOfWeek=int(row['DayOfWeek']),
                    Sales=float(row['Sales']),
                    Customers=int(row['Customers']),
                    Open=int(row['Open']),
                    Promo=int(row['Promo']),
                    StateHoliday=str(row['StateHoliday']),
                    SchoolHoliday=int(row['SchoolHoliday'])
                )
                sales_objects.append(sale)
            
            db.bulk_save_objects(sales_objects)
            db.commit()
            print(f"Inserted {min(i+batch_size, len(train_df))}/{len(train_df)} sales records")
        
        print("\n✅ Database initialization completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()

