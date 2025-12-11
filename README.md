# Rossmann Sales Recommendation System

Система прогнозирования продаж и формирования управленческих рекомендаций для сети магазинов Rossmann.

## Описание

Система реализует архитектуру из курсовой работы и включает:

- **DataLoader**: загрузка и валидация данных из PostgreSQL
- **FeatureEngineer**: генерация признаков (календарные, конкурентные, промо)
- **SalesForecaster**: прогнозирование продаж с помощью XGBoost
- **SimilarityService**: поиск похожих наблюдений (K-ближайших соседей)
- **RuleEngine**: формирование интерпретируемых рекомендаций
- **RecommendationService**: оркестрация всех компонентов
- **REST API**: FastAPI endpoint для получения прогнозов

## Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                      REST API (FastAPI)                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│              RecommendationService (Orchestrator)            │
├──────────────┬──────────────┬──────────────┬─────────────────┤
│ DataLoader   │ FeatureEng.  │ Forecaster   │ Similarity      │
│              │              │ (XGBoost)    │ (KNN)           │
└──────────────┴──────────────┴──────────────┴─────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                  PostgreSQL Database                         │
│              (sales table, stores table)                     │
└─────────────────────────────────────────────────────────────┘
```

## Установка

### 1. Предварительные требования

- Python 3.9+
- PostgreSQL 12+
- pip

### 2. Установка зависимостей

```bash
cd project
pip install -r requirements.txt
```

### 3. Настройка базы данных

Создайте файл `.env` в папке `project/`:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/rossmann_db
```

Замените `user`, `password` на ваши учетные данные PostgreSQL.

### 4. Создание базы данных

```bash
# В PostgreSQL
createdb rossmann_db

# Или через psql
psql -U postgres
CREATE DATABASE rossmann_db;
\q
```

### 5. Загрузка данных в БД

```bash
cd project
python init_db.py
```

Этот скрипт:
- Создаст таблицы `sales` и `stores`
- Загрузит данные из `train.csv` и `store.csv`
- Проверит целостность данных

## Использование модели

### Вариант 1: Использование мок-модели (по умолчанию)

Система будет работать с заглушкой модели, которая генерирует простые предсказания.

### Вариант 2: Использование обученной модели

Обучите модель с помощью `train_models.py` и сохраните её:

```python
# В train_models.py после обучения
import pickle

with open('project/models/xgboost_model.pkl', 'wb') as f:
    pickle.dump(xgb_model, f)
```

Также сохраните scaler и другие необходимые объекты.

## Запуск сервера

```bash
cd project
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Сервер запустится на `http://localhost:8000`

## API Endpoints

### GET `/`
Информация об API

### GET `/health`
Проверка состояния системы

**Ответ:**
```json
{
  "status": "healthy",
  "service_ready": true,
  "model_type": "mock"
}
```

### POST `/predict`
Прогноз продаж и рекомендации

**Запрос:**
```json
{
  "store_id": 1,
  "date": "2015-08-01",
  "promo": 1
}
```

**Ответ:**
```json
{
  "forecast_sales": 7500.50,
  "benchmark_sales": 8200.00,
  "recommendations": [
    "Revenue is below typical (7500 vs 8200). Explore practices of the best stores.",
    "75% of successful cases included a promotion. Consider the promotion."
  ]
}
```

### POST `/predict/detailed`
Детальный прогноз с дополнительной статистикой

**Запрос:** (такой же как `/predict`)

**Ответ:** (расширенный с дополнительными метриками)

## Примеры использования

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

### Python requests

```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={
        "store_id": 1,
        "date": "2015-08-01",
        "promo": 1
    }
)

result = response.json()
print(f"Прогноз: {result['forecast_sales']:.2f}")
print(f"Бенчмарк: {result['benchmark_sales']:.2f}")
print("Рекомендации:")
for rec in result['recommendations']:
    print(f"  - {rec}")
```

### Swagger UI

Откройте в браузере: `http://localhost:8000/docs`

Интерактивная документация API с возможностью тестирования endpoints.

## Структура проекта

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI приложение
│   ├── database.py                # Подключение к PostgreSQL
│   ├── schemas.py                 # Pydantic схемы
│   └── models/
│       ├── __init__.py
│       ├── data_loader.py         # Загрузка данных
│       ├── feature_engineer.py    # Генерация признаков
│       ├── sales_forecaster.py    # Модель прогноза
│       ├── similarity_service.py  # Поиск похожих
│       ├── rule_engine.py         # Правила рекомендаций
│       └── recommendation_service.py  # Оркестратор
├── models/
│   ├── .gitkeep
│   └── README.md                  # Инструкции по моделям
├── init_db.py                     # Инициализация БД
├── requirements.txt               # Зависимости
└── README.md                      # Этот файл
```

## Принцип работы системы

Согласно алгоритму из chapter2.tex:

1. **Загрузка данных**: Извлечение информации о магазине из БД
2. **Генерация признаков**: Создание вектора признаков для целевого сценария
3. **Прогноз**: Применение модели XGBoost для предсказания продаж
4. **Поиск похожих**: KNN-поиск 5 ближайших исторических наблюдений
5. **Формирование рекомендаций**: Применение 4 правил на основе принципа репликации

## Правила рекомендаций

1. **Отставание от похожих**: Если прогноз < 85% среднего по соседям
2. **Промоактивность**: Анализ успешных случаев с промо
3. **Конкурентная среда**: Учёт близости конкурентов
4. **Сезонность**: Рекомендации по подготовке к пикам