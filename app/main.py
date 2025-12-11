"""
FastAPI application - REST API for recommendation system
"""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import os

from .database import get_db, init_db
from .schemas import PredictRequest, PredictResponse
from .models.sales_forecaster import SalesForecaster
from .models.feature_engineer import FeatureEngineer
from .models.similarity_service import SimilarityService
from .models.rule_engine import RuleEngine
from .models.recommendation_service import RecommendationService

# Initialize FastAPI app
app = FastAPI(
    title="Rossmann Sales Recommendation System",
    description="Система прогнозирования продаж и формирования управленческих рекомендаций для сети магазинов",
    version="1.0.0"
)

# Global service instance
recommendation_service = None


def get_recommendation_service() -> RecommendationService:
    """Get or create recommendation service instance"""
    global recommendation_service
    
    if recommendation_service is None:
        raise HTTPException(
            status_code=503,
            detail="Service not initialized. Please wait for startup to complete."
        )
    
    return recommendation_service


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    global recommendation_service
    
    print("\n" + "="*60)
    print("Starting Rossmann Sales Recommendation System")
    print("="*60)
    
    # Initialize database tables (if needed)
    init_db()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Initialize components
        model_path = "models/xgboost_model.pkl"
        
        forecaster = SalesForecaster(model_path=model_path)
        feature_engineer = FeatureEngineer()
        similarity = SimilarityService(n_neighbors=5)
        rules = RuleEngine()
        
        # Create recommendation service
        recommendation_service = RecommendationService(
            forecaster=forecaster,
            feature_engineer=feature_engineer,
            similarity=similarity,
            rules=rules
        )
        
        # Initialize (load data, fit transformers)
        recommendation_service.initialize(db)
        
        print("\n✅ System ready to accept requests!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during startup: {e}")
        raise
    finally:
        db.close()


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Rossmann Sales Recommendation System",
        "version": "1.0.0",
        "endpoints": {
            "POST /predict": "Get sales forecast and recommendations",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    service = get_recommendation_service()
    
    return {
        "status": "healthy",
        "service_ready": service.is_ready,
        "model_type": "mock" if service.forecaster.is_mock_model() else "trained"
    }


@app.post("/predict", response_model=PredictResponse)
async def predict_sales(
    request: PredictRequest,
    db: Session = Depends(get_db)
):
    """
    Прогноз продаж и формирование рекомендаций
    
    Endpoint реализует полный workflow системы:
    1. Создание признаков для целевого сценария
    2. Прогноз продаж с помощью модели
    3. Поиск похожих наблюдений
    4. Формирование рекомендаций
    
    Args:
        request: PredictRequest with store_id, date, promo
        db: Database session (injected)
        
    Returns:
        PredictResponse with forecast, benchmark, and recommendations
    """
    service = get_recommendation_service()
    
    try:
        # Get recommendation
        result = service.get_recommendation(
            store_id=request.store_id,
            date=request.date,
            promo_active=request.promo,
            db=db
        )
        
        # Format response
        response = PredictResponse(
            forecast_sales=result['forecast'],
            benchmark_sales=result['benchmark'],
            recommendations=result['recommendations']
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# Optional: Additional endpoint for detailed analysis
@app.post("/predict/detailed")
async def predict_sales_detailed(
    request: PredictRequest,
    db: Session = Depends(get_db)
):
    """
    Детальный прогноз с дополнительной статистикой
    
    Returns extended information including:
    - Similarity statistics
    - Performance comparison
    - Store information
    """
    service = get_recommendation_service()
    
    try:
        result = service.get_detailed_analysis(
            store_id=request.store_id,
            date=request.date,
            promo_active=request.promo,
            db=db
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

