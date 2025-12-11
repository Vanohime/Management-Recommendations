"""
Simple script to run the server
"""
import uvicorn

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Starting Rossmann Sales Recommendation System")
    print("="*60)
    print("\nServer will be available at:")
    print("  - http://localhost:8000")
    print("  - API docs: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

