# Quick Start Guide

Быстрая инструкция по запуску системы.

## Шаг 1: Установка зависимостей

```bash
cd project
pip install -r requirements.txt
```

## Шаг 2: Настройка PostgreSQL

Создайте базу данных:

```bash
createdb rossmann_db
```

Создайте файл `.env`:

```bash
echo "DATABASE_URL=postgresql://postgres:password@localhost:5432/rossmann_db" > .env
```

Замените `postgres:password` на ваши учетные данные.

## Шаг 3: Загрузка данных

```bash
python init_db.py
```

Ожидайте ~2-5 минут для загрузки ~1 млн записей.

## Шаг 4: Запуск сервера

```bash
python run_server.py
```

Или:

```bash
uvicorn app.main:app --reload
```

## Шаг 5: Тестирование

Откройте новый терминал:

```bash
python test_api.py
```

Или откройте в браузере:
- API docs: http://localhost:8000/docs
- Swagger UI для интерактивного тестирования

## Пример запроса

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"store_id": 1, "date": "2015-08-01", "promo": 1}'
```

## Использование обученной модели

После обучения модели в `train_models.py`:

```python
import pickle

# Сохраните модель
with open('project/models/xgboost_model.pkl', 'wb') as f:
    pickle.dump(xgb_model, f)
```

Перезапустите сервер - он автоматически загрузит обученную модель.

## Проблемы?

См. раздел Troubleshooting в README.md

