# Test Data Generator API

> Генерация реалистичных тестовых данных для разработки, QA и ML-обучения.  
> 12+ готовых схем, мультиязычная локализация, кастомные поля.

## 📋 Возможности

- **12 встроенных схем**: users, transactions, products, orders, reviews, employees, addresses, vehicles, medical_records, social_media, ecommerce, banking
- **Кастомные схемы**: определяйте свои поля и типы
- **10 локалей**: en_US, en_GB, ru_RU, de_DE, fr_FR, es_ES, ja_JP, zh_CN, pt_BR, ko_KR
- **Экспорт**: JSON, CSV, Excel
- **Bulk-запросы**: генерация нескольких датасетов одним запросом
- **Автоматическая документация**: Swagger UI + ReDoc

## 🚀 Быстрый старт

### Локальный запуск

```bash
cd test-data-generator-api
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker-compose up --build
```

## 📖 API Endpoints

### POST `/generate` — Генерация данных

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_type": "users",
    "count": 10,
    "locale": "ru_RU"
  }'
```

### POST `/generate/bulk` — Мультигенерация

```bash
curl -X POST http://localhost:8000/generate/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {"schema_type": "users", "count": 5, "locale": "en_US"},
      {"schema_type": "transactions", "count": 10, "locale": "ru_RU"}
    ]
  }'
```

### GET `/schemas` — Доступные схемы

```bash
curl http://localhost:8000/schemas
```

### GET `/schemas/{schema_type}` — Инфо о схеме

```bash
curl http://localhost:8000/schemas/users
```

### POST `/export` — Экспорт в CSV/Excel

```bash
curl -X POST http://localhost:8000/export \
  -H "Content-Type: application/json" \
  -d '{
    "schema_type": "users",
    "count": 100,
    "locale": "en_US",
    "format": "csv"
  }'
```

### GET `/health` — Проверка статуса

```bash
curl http://localhost:8000/health
```

## 📊 Примеры схем

### Users
```json
{
  "id": "uuid",
  "name": "Иван Петров",
  "email": "ivan@example.com",
  "username": "ivan_p",
  "password": "hashed...",
  "phone": "+7 (999) 123-45-67",
  "avatar": "https://...",
  "company": "ООО Компания",
  "job": "Инженер-разработчик",
  "address": "...",
  "city": "Москва",
  "country": "Россия",
  "is_active": true,
  "subscription_plan": "pro"
}
```

### Transactions
```json
{
  "transaction_id": "TXN-A1B2C3D4E5F6",
  "type": "payment",
  "amount": 1500.00,
  "currency": "RUB",
  "status": "completed",
  "method": "card",
  "timestamp": "2025-03-15T10:30:00"
}
```

### Banking
```json
{
  "account_id": "ACC-...",
  "account_type": "checking",
  "account_holder": "Иван Петров",
  "balance": 150000.50,
  "iban": "RU0000000000000000000",
  "transactions": [...],
  "credit_card_number": "4XXX XXXX XXXX XXXX"
}
```

## 🧪 Запуск тестов

```bash
pip install pytest
pytest test_main.py -v
```

## 📦 Структура проекта

```
test-data-generator-api/
├── main.py              # FastAPI приложение
├── generator.py         # Ядро генерации данных
├── models.py            # Pydantic модели
├── config.py            # Конфигурация
├── test_main.py         # Тесты
├── requirements.txt     # Зависимости
├── Dockerfile           # Docker образ
├── docker-compose.yml   # Docker Compose
├── .env.example         # Переменные окружения
└── README.md
```

## 🔑 Ключевые отличия от аналогов

| Фича | Наш API | Typical Alternatives |
|---|---|---|
| Схем | 12+ | 3-5 |
| Мультиязычность | 10+ локалей | 1-2 |
| Кастомные поля | ✅ | ❌ |
| Экспорт CSV/Excel | ✅ | ❌ |
| Bulk-запросы | ✅ | ❌ |
| Связанные данные | ✅ | ❌ |

## 📄 License

MIT
