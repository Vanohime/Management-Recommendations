"""
Script to test the API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_root():
    """Test root endpoint"""
    print("\n" + "="*60)
    print("Testing GET /")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Testing GET /health")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_predict():
    """Test predict endpoint"""
    print("\n" + "="*60)
    print("Testing POST /predict")
    print("="*60)
    
    request_data = {
        "store_id": 1,
        "date": "2015-08-01",
        "promo": 1
    }
    
    print(f"Request: {json.dumps(request_data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/predict",
        json=request_data
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Prediction successful!")
        print(f"Forecast Sales: {result['forecast_sales']:.2f}")
        print(f"Benchmark Sales: {result['benchmark_sales']:.2f}")
        print(f"Recommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
    else:
        print(f"❌ Error: {response.text}")


def test_predict_detailed():
    """Test detailed predict endpoint"""
    print("\n" + "="*60)
    print("Testing POST /predict/detailed")
    print("="*60)
    
    request_data = {
        "store_id": 1,
        "date": "2015-08-01",
        "promo": 1
    }
    
    response = requests.post(
        f"{BASE_URL}/predict/detailed",
        json=request_data
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Detailed prediction successful!")
        print(f"Forecast: {result['forecast']:.2f}")
        print(f"Benchmark: {result['benchmark']:.2f}")
        
        if 'similarity_statistics' in result:
            stats = result['similarity_statistics']
            print(f"\nSimilarity Statistics:")
            print(f"  Mean: {stats['mean_sales']:.2f}")
            print(f"  Median: {stats['median_sales']:.2f}")
            print(f"  Min: {stats['min_sales']:.2f}")
            print(f"  Max: {stats['max_sales']:.2f}")
        
        if 'performance_comparison' in result:
            comp = result['performance_comparison']
            print(f"\nPerformance: {comp['performance_category']}")
            print(f"Difference: {comp['difference_pct_mean']:.1f}%")
    else:
        print(f"❌ Error: {response.text}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("API Testing Script")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print("\nMake sure the server is running!")
    print("Start with: uvicorn app.main:app --reload")
    
    try:
        test_root()
        test_health()
        test_predict()
        test_predict_detailed()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

