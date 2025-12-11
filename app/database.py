"""
Database connection and models for PostgreSQL
"""
import os
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/rossmann_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Sale(Base):
    """Sales table - daily sales data"""
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    Store = Column(Integer, index=True, nullable=False)
    Date = Column(Date, nullable=False)
    DayOfWeek = Column(Integer, nullable=False)
    Sales = Column(Float, nullable=False)
    Customers = Column(Integer, nullable=False)
    Open = Column(Integer, nullable=False)
    Promo = Column(Integer, nullable=False)
    StateHoliday = Column(String(10), nullable=False)
    SchoolHoliday = Column(Integer, nullable=False)


class Store(Base):
    """Stores table - store characteristics"""
    __tablename__ = "stores"
    
    Store = Column(Integer, primary_key=True, index=True)
    StoreType = Column(String(10), nullable=False)
    Assortment = Column(String(10), nullable=False)
    CompetitionDistance = Column(Float, nullable=True)
    CompetitionOpenSinceMonth = Column(Float, nullable=True)
    CompetitionOpenSinceYear = Column(Float, nullable=True)
    Promo2 = Column(Integer, nullable=False)
    Promo2SinceWeek = Column(Float, nullable=True)
    Promo2SinceYear = Column(Float, nullable=True)
    PromoInterval = Column(String(50), nullable=True)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

