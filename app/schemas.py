"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List


class PredictRequest(BaseModel):
    """Request schema for /predict endpoint"""
    store_id: int = Field(..., description="Store ID", ge=1)
    date: str = Field(..., description="Date in format YYYY-MM-DD")
    promo: int = Field(..., description="Promo active (0 or 1)", ge=0, le=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "store_id": 1,
                "date": "2015-08-01",
                "promo": 1
            }
        }


class PredictResponse(BaseModel):
    """Response schema for /predict endpoint"""
    forecast_sales: float = Field(..., description="Predicted daily sales")
    benchmark_sales: float = Field(..., description="Average sales of similar observations")
    recommendations: List[str] = Field(..., description="List of recommendations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "forecast_sales": 7500.50,
                "benchmark_sales": 8200.00,
                "recommendations": [
                    "Revenue is below typical (7500 vs 8200). Explore practices of the best stores.",
                    "75% of successful cases included a promotion. Consider the promotion."
                ]
            }
        }

