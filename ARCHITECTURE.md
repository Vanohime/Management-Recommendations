# Architecture Overview

Подробное описание архитектуры системы рекомендаций для сети магазинов Rossmann.

## Общая архитектура

Система построена по многослойной архитектуре согласно chapter3.tex:

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer (FastAPI)                       │
│                    Endpoints: /predict, /health                  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│              RecommendationService (Orchestration)               │
│    Координирует работу всех компонентов и управляет workflow    │
└─┬────────┬────────────┬──────────────┬────────────┬─────────────┘
  │        │            │              │            │
  │        │            │              │            │
  ▼        ▼            ▼              ▼            ▼
┌─────┐ ┌──────┐ ┌───────────┐ ┌────────────┐ ┌──────────┐
│Data │ │Feat. │ │Sales      │ │Similarity  │ │Rule      │
│Load │ │Eng.  │ │Forecaster │ │Service     │ │Engine    │
└──┬──┘ └──────┘ └─────┬─────┘ └──────┬─────┘ └──────────┘
   │                   │               │
   │                   │               │
   ▼                   ▼               ▼
┌────────────────────────────────────────────┐
│          PostgreSQL Database               │
│         (sales, stores tables)             │
└────────────────────────────────────────────┘
```

## Компоненты системы

### 1. Data Layer

**PostgreSQL Database** (`app/database.py`)
- Таблица `sales`: ежедневные продажи (~1M записей)
- Таблица `stores`: характеристики магазинов (~1K записей)
- SQLAlchemy ORM для работы с БД

**DataLoader** (`app/models/data_loader.py`)
- Загрузка данных из PostgreSQL
- Валидация: фильтрация закрытых дней и нулевых продаж
- Объединение данных продаж с характеристиками магазинов
- Предоставление информации о конкретном магазине

### 2. Feature/Preprocessing Layer

**FeatureEngineer** (`app/models/feature_engineer.py`)

Реализует принципы из chapter 2.2:

1. **Календарные признаки**:
   - Year, Month, Day, WeekOfYear
   - IsWeekend (выходной или нет)

2. **Признаки конкуренции**:
   - CompetitionMonthsOpen (месяцев с момента открытия конкурента)
   - HasCompetition, HasCompetitionData (индикаторы)

3. **Признаки промо**:
   - Promo2LastsForNWeeks (недель с момента начала Promo2)

4. **One-Hot кодирование**:
   - StoreType (a, b, c, d)
   - Assortment (a, b, c)
   - StateHoliday (0, a, b, c)

5. **Масштабирование**:
   - StandardScaler для числовых признаков

### 3. ML Model Layer

**SalesForecaster** (`app/models/sales_forecaster.py`)

- Обёртка для модели XGBoost
- Поддержка мок-модели для демонстрации
- Загрузка обученной модели из pickle файла
- Унифицированный интерфейс `predict(X)`

**Мок-модель**:
```python
predictions = base_sales + variation_from_features
```

**Реальная модель**: XGBoost регрессор, обученный на исторических данных

### 4. Similarity Service

**SimilarityService** (`app/models/similarity_service.py`)

Реализует алгоритм поиска K-ближайших соседей:

1. Индекс: sklearn NearestNeighbors
2. Метрика: Euclidean distance в пространстве признаков
3. K = 5 (по умолчанию)
4. Вход: вектор признаков целевого сценария
5. Выход: продажи K похожих наблюдений + расстояния

**Назначение**: найти исторические наблюдения с похожими условиями для оценки эталонного уровня эффективности.

### 5. Rule Engine

**RuleEngine** (`app/models/rule_engine.py`)

Реализует 4 правила из chapter 2.3:

#### Правило 1: Отставание от похожих
```python
if y_pred < mean_similar * 0.85:
    "Revenue is below typical. Explore practices of the best stores."
```

#### Правило 2: Промоактивность
```python
if promo == 0 and high_promo_ratio > 0.5:
    "75% of successful cases included a promotion. Consider launching."
```

#### Правило 3: Конкурентная среда
```python
if competition_close and y_pred < mean_similar * 0.9:
    "Operating in competitive environment. Review strategies."
```

#### Правило 4: Сезонность
```python
if is_weekend and y_pred < mean_similar * 0.95:
    "Weekend sales below typical. Ensure adequate staffing."
```

### 6. Orchestration Layer

**RecommendationService** (`app/models/recommendation_service.py`)

Высокоуровневый оркестратор, реализующий полный workflow:

```python
def get_recommendation(store_id, date, promo):
    # 1. Загрузить информацию о магазине
    store_info = data_loader.load_store_info(store_id)
    
    # 2. Создать вектор признаков
    x_target = feature_engineer.create_features(store_id, date, promo)
    
    # 3. Прогноз продаж
    y_pred = forecaster.predict(x_target)
    
    # 4. Найти похожие наблюдения
    similar_y, distances = similarity.find_similar(x_target)
    
    # 5. Сформировать рекомендации
    recommendations = rules.generate_recommendations(y_pred, similar_y)
    
    return {forecast, benchmark, recommendations}
```

### 7. API Layer

**FastAPI Application** (`app/main.py`)

REST API endpoints:

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/` | GET | Информация об API |
| `/health` | GET | Проверка состояния системы |
| `/predict` | POST | Прогноз и рекомендации |
| `/predict/detailed` | POST | Детальный прогноз с статистикой |

## Workflow выполнения запроса

1. **Инициализация** (при старте сервера):
   ```
   Загрузка данных → Обучение FeatureEngineer → Обучение SimilarityService
   ```

2. **Обработка запроса** `/predict`:
   ```
   POST {store_id, date, promo}
     ↓
   Загрузка info магазина из БД
     ↓
   Генерация вектора признаков
     ↓
   Прогноз модели XGBoost
     ↓
   KNN-поиск 5 похожих наблюдений
     ↓
   Применение правил → рекомендации
     ↓
   Формирование ответа JSON
   ```

## Алгоритмическая сложность

- **Инициализация**: O(n log n) для построения KNN-индекса
- **Запрос predict**: O(log n) для KNN-поиска
- **Память**: O(n × m), где n - кол-во наблюдений, m - кол-во признаков

## Масштабируемость

Система спроектирована с учётом масштабируемости:

1. **Слабая связанность модулей**: каждый компонент можно заменить независимо
2. **Кэширование**: можно добавить Redis для кэширования частых запросов
3. **Горизонтальное масштабирование**: FastAPI + PostgreSQL поддерживают репликацию
4. **Batch processing**: для массовых прогнозов можно добавить endpoint `/predict/batch`

## Безопасность

Рекомендации для продакшена:

- [ ] Добавить аутентификацию (JWT tokens)
- [ ] Валидация входных данных (расширенная)
- [ ] Rate limiting
- [ ] HTTPS
- [ ] Логирование запросов
- [ ] Мониторинг метрик

## Производительность

Типичные времена выполнения (на 1M записей):

- Инициализация: ~30-60 сек
- Запрос `/predict`: ~50-100 мс
- Запрос `/predict/detailed`: ~100-200 мс

## Тестирование

Используйте `test_api.py` для проверки всех endpoints:

```bash
python test_api.py
```

Или Swagger UI: http://localhost:8000/docs

