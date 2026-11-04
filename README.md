# Test Data Generator API v3.0

> **Генерация реалистичных тестовых данных для разработки, QA и ML.**
> 12+ схем, 10 локалей, кастомные поля. **Бесплатно 100 запросов/день.**

## 🚀 Быстрый старт

### 1. Получите бесплатный API ключ

```bash
curl -X POST https://YOUR-URL.onrender.com/register \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com"}'
```

### 2. Используйте API

```bash
curl -X POST https://YOUR-URL.onrender.com/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY_HERE" \
  -d '{
    "schema_type": "users",
    "count": 10,
    "locale": "ru_RU"
  }'
```

## 📊 Тарифы

| Тариф | Цена | Лимит | Описание |
|---|---|---|---|
| **Free** | $0 | 100 req/day | Для тестирования |
| **Premium** | $5 (USDT TRC20) | Безлимит | Полностью безлимитный доступ |

## 💰 Оплата криптой

### Способ 1: Автоматический (NowPayments)

```bash
curl -X POST https://YOUR-URL.onrender.com/pay \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "YOUR_KEY",
    "amount": 5.0,
    "currency": "usdt"
  }'
```

### Способ 2: Ручной (TRC20 USDT)

```bash
curl -X POST https://YOUR-URL.onrender.com/pay \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_KEY"}'
```

Вернёт:
- Адрес кошелька для перевода
- Сумму: $5 USDT (TRC20)
- Инструкции по активации

**После оплаты напишите на support@tdg-api.com — ключ активируется в течение 1 часа.**

## 📚 API Endpoints

### Public (без ключа)

| Метод | Путь | Описание |
|---|---|---|
| GET | `/health` | Проверка здоровья |
| GET | `/schemas` | Список всех схем |
| GET | `/register` | Регистрация (получить ключ) |

### Protected (нужен X-API-Key)

| Метод | Путь | Описание |
|---|---|---|
| POST | `/generate` | Генерация данных |
| POST | `/generate/bulk` | Мультигенерация |
| POST | `/export` | Экспорт (JSON/CSV) |
| POST | `/pay` | Оплата Premium |

### Управление

| Метод | Путь | Описание |
|---|---|---|
| GET | `/key/{api_key}` | Информация о ключе |
| POST | `/webhook/payment` | Webhook для оплаты |

## 📋 Доступные схемы

### 1. users
Пользователи с аутентификацией и контактами.
- Поля: id, name, email, username, password, phone, avatar, bio, gender, company, job, address, city, state, country, zipcode, website, ip_address, is_active, subscription_plan, и др.

### 2. transactions
Финансовые транзакции с платёжными деталями.
- Поля: transaction_id, type, amount, currency, from_account, to_account, status, method, timestamp, и др.

### 3. products
Каталог товаров с ценами и остатками.
- Поля: id, name, description, category, price, compare_at_price, cost, weight, sku, barcode, brand, rating, stock_quantity, и др.

### 4. orders
Заказы e-commerce с позициями.
- Поля: order_id, status, customer_id, items, subtotal, tax, shipping, total, payment_method, tracking_number, и др.

### 5. reviews
Отзывы товаров и услуг с рейтингами.
- Поля: id, user_id, rating, title, body, verified_purchase, helpful_count, response, и др.

### 6. employees
Записи сотрудников с HR данными.
- Поля: id, first_name, last_name, email, department, title, salary, hire_date, performance_score, education, и др.

### 7. addresses
Адреса в международных форматах.
- Поля: id, street, city, state, country, zipcode, latitude, longitude, full_address, address_type, и др.

### 8. vehicles
Реестр автомобилей со спецификациями.
- Поля: id, make, model, year, color, body_type, fuel_type, engine_size, vin, license_plate, и др.

### 9. medical_records
Анонимизированные медицинские записи.
- Поля: patient_id, date_of_birth, blood_type, height, weight, bmi, blood_pressure, diagnosis, medications, и др.

### 10. social_media
Профили и посты соцсетей.
- Поля: user_id, username, display_name, followers, following, posts, hashtags, engagement_rate, и др.

### 11. ecommerce
Полный e-commerce: товары + заказы + покупатели.
- Поля: customer_id, product_id, order_id, quantity, total, payment_method, discount, и др.

### 12. banking
Данные банков: счета, транзакции, карты.
- Поля: account_id, account_type, balance, iban, swift_code, loan_id, credit_card_number, и др.

## 🌍 Локализации

| Код | Язык |
|---|---|
| en_US | Английский (США) |
| en_GB | Английский (Великобритания) |
| ru_RU | Русский |
| de_DE | Немецкий |
| fr_FR | Французский |
| es_ES | Испанский |
| ja_JP | Японский |
| zh_CN | Китайский |
| pt_BR | Португальский (Бразилия) |
| ko_KR | Корейский |

## 🧪 Локальный запуск

```bash
cd test-data-generator-api
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Документация: http://localhost:8000/docs

## 📦 Структура проекта

```
test-data-generator-api/
├── main.py              # FastAPI приложение (с API ключами)
├── api_keys.py          # Система API ключей и оплаты
├── generator.py         # Ядро генерации данных
├── models.py            # Pydantic модели
├── test_main.py         # Тесты генерации
├── test_api_keys.py     # Тесты API ключей
├── requirements.txt     # Зависимости
├── Dockerfile
├── docker-compose.yml
├── README.md            # Этот файл
└── DEPLOY.md            # Инструкция по деплою
```

## 📈 Регистрация в каталогах

Чтобы клиенты приходили сами — зарегистрируйте API в каталогах:

1. **apilist.fun** — https://apilist.fun/submit
2. **publicapis.io** — https://publicapis.io/submit-api
3. **awesome-apis** — https://github.com/ public-apis/public-apis (pull request)
4. **Product Hunt** — https://www.producthunt.com/

**Каждый каталог = бесплатный трафик разработчиков.**

## 💡 Использование в коде

### Python
```python
import requests

headers = {"X-API-Key": "YOUR_KEY"}
data = {
    "schema_type": "users",
    "count": 10,
    "locale": "ru_RU"
}

response = requests.post(
    "https://YOUR-URL.onrender.com/generate",
    json=data,
    headers=headers
)

users = response.json()["data"]
print(users[0]["name"])  # "Иван Петров"
```

### JavaScript
```javascript
fetch('https://YOUR-URL.onrender.com/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'YOUR_KEY'
  },
  body: JSON.stringify({
    schema_type: 'users',
    count: 10,
    locale: 'en_US'
  })
})
.then(r => r.json())
.then(data => console.log(data.data[0].name));
```

## 📜 License

MIT

## 🆘 Поддержка

- Email: support@tdg-api.com
- Telegram: @TDDAPI_BOT
- GitHub Issues: https://github.com/dolinin236-hash/tdd-api/issues
