# Примеры использования системы

## Пример 1: Базовый запрос прогноза

### cURL
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": 1,
    "date": "2015-08-01",
    "promo": 1
  }'
```

### Ответ
```json
{
  "forecast_sales": 7542.30,
  "benchmark_sales": 8125.50,
  "recommendations": [
    "Revenue is below typical (7542 vs 8125). Explore practices of the best stores.",
    "75% of successful cases included a promotion. Consider the promotion."
  ]
}
```

## Пример 2: Python requests

```python
import requests
import json

url = "http://localhost:8000/predict"

# Запрос для магазина 25 на понедельник без промо
payload = {
    "store_id": 25,
    "date": "2015-09-14",
    "promo": 0
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Прогноз продаж: ${result['forecast_sales']:.2f}")
print(f"Средний уровень похожих магазинов: ${result['benchmark_sales']:.2f}")
print("\nРекомендации:")
for i, rec in enumerate(result['recommendations'], 1):
    print(f"{i}. {rec}")
```

## Пример 3: Детальный анализ

```python
import requests

url = "http://localhost:8000/predict/detailed"

payload = {
    "store_id": 10,
    "date": "2015-12-24",  # Канун Рождества
    "promo": 1
}

response = requests.post(url, json=payload)
result = response.json()

# Основной прогноз
print(f"Прогноз: ${result['forecast']:.2f}")
print(f"Бенчмарк: ${result['benchmark']:.2f}")

# Статистика по похожим магазинам
stats = result['similarity_statistics']
print(f"\nСтатистика похожих наблюдений:")
print(f"  Среднее: ${stats['mean_sales']:.2f}")
print(f"  Медиана: ${stats['median_sales']:.2f}")
print(f"  Минимум: ${stats['min_sales']:.2f}")
print(f"  Максимум: ${stats['max_sales']:.2f}")
print(f"  Стд. откл: ${stats['std_sales']:.2f}")

# Сравнение производительности
comp = result['performance_comparison']
print(f"\nКатегория производительности: {comp['performance_category']}")
print(f"Отклонение от среднего: {comp['difference_pct_mean']:.1f}%")

# Рекомендации
print("\nРекомендации:")
for rec in result['recommendations']:
    print(f"  • {rec}")
```

## Пример 4: Массовый анализ магазинов

```python
import requests
import pandas as pd

url = "http://localhost:8000/predict"

# Анализируем топ-10 магазинов на одну дату
stores = range(1, 11)
date = "2015-08-15"

results = []

for store_id in stores:
    # С промо
    response_promo = requests.post(url, json={
        "store_id": store_id,
        "date": date,
        "promo": 1
    })
    
    # Без промо
    response_no_promo = requests.post(url, json={
        "store_id": store_id,
        "date": date,
        "promo": 0
    })
    
    if response_promo.status_code == 200 and response_no_promo.status_code == 200:
        promo_result = response_promo.json()
        no_promo_result = response_no_promo.json()
        
        promo_impact = promo_result['forecast_sales'] - no_promo_result['forecast_sales']
        promo_impact_pct = (promo_impact / no_promo_result['forecast_sales']) * 100
        
        results.append({
            'store_id': store_id,
            'forecast_with_promo': promo_result['forecast_sales'],
            'forecast_no_promo': no_promo_result['forecast_sales'],
            'promo_impact': promo_impact,
            'promo_impact_pct': promo_impact_pct
        })

# Создаём DataFrame для анализа
df = pd.DataFrame(results)
print(df)

# Находим магазин с наибольшим эффектом от промо
best_promo_store = df.loc[df['promo_impact_pct'].idxmax()]
print(f"\nМагазин с наибольшим эффектом от промо:")
print(f"Store #{int(best_promo_store['store_id'])}: +{best_promo_store['promo_impact_pct']:.1f}%")
```

## Пример 5: Сравнение выходных и будних дней

```python
import requests
from datetime import datetime, timedelta

url = "http://localhost:8000/predict"
store_id = 5

# Понедельник
monday = "2015-08-03"
# Суббота
saturday = "2015-08-08"

def get_forecast(date, promo=1):
    response = requests.post(url, json={
        "store_id": store_id,
        "date": date,
        "promo": promo
    })
    return response.json()

monday_result = get_forecast(monday)
saturday_result = get_forecast(saturday)

print(f"Магазин #{store_id} - Сравнение дней недели\n")

print(f"Понедельник ({monday}):")
print(f"  Прогноз: ${monday_result['forecast_sales']:.2f}")
print(f"  Бенчмарк: ${monday_result['benchmark_sales']:.2f}")

print(f"\nСуббота ({saturday}):")
print(f"  Прогноз: ${saturday_result['forecast_sales']:.2f}")
print(f"  Бенчмарк: ${saturday_result['benchmark_sales']:.2f}")

difference = saturday_result['forecast_sales'] - monday_result['forecast_sales']
difference_pct = (difference / monday_result['forecast_sales']) * 100

print(f"\nРазница: ${difference:.2f} ({difference_pct:+.1f}%)")
```

## Пример 6: Health check и мониторинг

```python
import requests
import time

def check_service_health():
    """Проверка состояния сервиса"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Сервис работает")
            print(f"   Статус: {health['status']}")
            print(f"   Готовность: {health['service_ready']}")
            print(f"   Тип модели: {health['model_type']}")
            return True
        else:
            print(f"❌ Сервис недоступен (код {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к сервису")
        return False
    except requests.exceptions.Timeout:
        print("❌ Таймаут подключения")
        return False

# Проверка с retry
max_retries = 3
for i in range(max_retries):
    if check_service_health():
        break
    print(f"Попытка {i+1}/{max_retries}, ждём 5 секунд...")
    time.sleep(5)
```

## Пример 7: Обработка ошибок

```python
import requests

url = "http://localhost:8000/predict"

def safe_predict(store_id, date, promo):
    """Безопасный запрос с обработкой ошибок"""
    try:
        response = requests.post(url, json={
            "store_id": store_id,
            "date": date,
            "promo": promo
        }, timeout=10)
        
        if response.status_code == 200:
            return {
                'success': True,
                'data': response.json()
            }
        elif response.status_code == 400:
            return {
                'success': False,
                'error': 'Некорректные входные данные',
                'detail': response.json().get('detail', 'Unknown error')
            }
        elif response.status_code == 404:
            return {
                'success': False,
                'error': f'Магазин {store_id} не найден'
            }
        else:
            return {
                'success': False,
                'error': f'Ошибка сервера: {response.status_code}'
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'Превышено время ожидания'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': 'Не удалось подключиться к серверу'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Неожиданная ошибка: {str(e)}'
        }

# Использование
result = safe_predict(store_id=999999, date="2015-08-01", promo=1)

if result['success']:
    print(f"Прогноз: ${result['data']['forecast_sales']:.2f}")
else:
    print(f"Ошибка: {result['error']}")
    if 'detail' in result:
        print(f"Детали: {result['detail']}")
```

## Пример 8: Swagger UI

Откройте в браузере:

```
http://localhost:8000/docs
```

Интерактивный интерфейс позволяет:
- Просматривать все доступные endpoints
- Тестировать запросы прямо в браузере
- Видеть схемы запросов и ответов
- Получать примеры использования

## Пример 9: ReDoc документация

```
http://localhost:8000/redoc
```

Альтернативное представление документации API.

## Пример 10: Интеграция в существующую систему

```python
class RossmannClient:
    """Клиент для работы с Rossmann Recommendation API"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_recommendation(self, store_id, date, promo):
        """Получить рекомендацию для магазина"""
        response = self.session.post(
            f"{self.base_url}/predict",
            json={
                "store_id": store_id,
                "date": date,
                "promo": promo
            }
        )
        response.raise_for_status()
        return response.json()
    
    def check_health(self):
        """Проверить состояние сервиса"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()

# Использование
client = RossmannClient()

# Проверка
if client.check_health()['status'] == 'healthy':
    # Получение рекомендации
    result = client.get_recommendation(
        store_id=1,
        date="2015-08-01",
        promo=1
    )
    print(result)
```

---

Все примеры предполагают, что сервер запущен на `localhost:8000`.

