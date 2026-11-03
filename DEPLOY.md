# 🚀 Инструкция по деплою и публикации на RapidAPI

## Состояние проекта

✅ Проект полностью готов в `C:\Users\Lenovo\test-data-generator-api`  
✅ 31 тест — все проходят  
✅ 12+ схем генерации тестовых данных  
✅ 10 локалей  
✅ Экспорт в JSON/CSV  
✅ Документация Swagger UI (/docs)  

---

## Шаг 1: Регистрация (1 минута)

1. **RapidAPI Hub**: [rapidapi.com](https://rapidapi.com/ auth) → Sign up с GitHub
2. **Stripe**: [stripe.com](https://stripe.com/) → Connect → Stripe Connect (для получения выплат)
   - Это ЕДИНСТВЕННЫЕ 2 регистрации, которые нужны
   - Никакого общения с клиентами

---

## Шаг 2: Деплой API-сервера (выбор одного способа)

### Вариант A: Render.com (РЕКОМЕНДУЮ, бесплатно)

```bash
# 1. Создайте репозиторий на GitHub
cd C:\Users\Lenovo\test-data-generator-api
git init
git add .
git commit -m "Test Data Generator API v2.0"
git branch -M main
git remote add origin https://github.com/ВАШ_НИК/test-data-generator-api.git
git push -u origin main

# 2. На Render.com:
#    - New Web Service
#    - Connect GitHub repo
#    - Region: choose closest
#    - Build command: pip install -r requirements.txt
#    - Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
#    - Instance type: Free
#    - Deploy!
```

Даст бесплатный URL: `https://test-data-generator.onrender.com`

### Вариант B: Railway.app (бесплатно, $5 credit)

```bash
# 1. Установите Railway CLI
npm install -g @railway/cli

# 2. Задеплойте
cd C:\Users\Lenovo\test-data-generator-api
railway init
railway up

# 3. Получите URL из dashboard
```

### Вариант C: Fly.io (бесплатный тариф)

```bash
# 1. Установите Fly CLI
# 2. Задеплойте
fly launch --now
```

### Вариант D: Docker + любой VPS

```bash
# Если есть VPS (от $3.5/мес)
docker build -t test-data-generator .
docker run -p 8000:8000 -d test-data-generator
```

---

## Шаг 3: Публикация на RapidAPI Hub

### 3.1: Регистрация в RapidAPI Hub

1. Зайдите на [hub.rapidapi.com](https://hub.rapidapi.com/)
2. Click "Publish your API"
3. Connect GitHub repo (или загрузите ZIP)

### 3.2: Настройка API в Hub

Заполните:

| Поле | Значение |
|---|---|
| **Name** | Test Data Generator API |
| **Description** | Generate realistic test data for development, QA, and ML. 12+ schemas, 10+ locales, custom fields. |
| **Category** | Developer Tools |
| **Subcategory** | Testing |
| **Website** | Ваш GitHub repo URL |

### 3.3: Конфигурация эндпоинтов

В Hub добавьте эндпоинты:

**Endpoint 1: Generate Data**
- Method: `POST`
- Path: `/generate`
- Request Body Schema:
```json
{
  "schema_type": "users",
  "count": 10,
  "locale": "en_US",
  "include_fields": ["name", "email", "username"],
  "exclude_fields": ["password", "ssn"]
}
```
- Response Schema (200):
```json
{
  "schema_type": "users",
  "count": 10,
  "locale": "en_US",
  "data": [{"name": "John Doe", "email": "john@example.com"}],
  "generated_at": "2025-01-01T00:00:00+00:00",
  "request_id": "abc123"
}
```

**Endpoint 2: List Schemas**
- Method: `GET`
- Path: `/schemas`

**Endpoint 3: Schema Details**
- Method: `GET`
- Path: `/schemas/{schema_type}`

**Endpoint 4: Health Check**
- Method: `GET`
- Path: `/health`

### 3.4: Цена и тарифы

```
Free Tier:
  - 500 requests/month
  - All features

Starter ($49/мес):
  - 10,000 requests/month
  - $0.001 overage

Growth ($149/мес):
  - 100,000 requests/month
  - $0.0008 overage
```

**Важно:** Начните с бесплатного тарифа. Когда появятся платные подписчики — включайте monetization.

### 3.5: Monetization

1. В Hub → Monetization → Enable
2. Выберите Free + Starter tiers
3. Подключите Stripe Connect
4. Установите цену:
   - Free: 500 req/month
   - Starter: $49/мес за 10K req

---

## Шаг 4: Тестирование после деплоя

```bash
# Проверка живого API
curl https://ВАШ-URL.onrender.com/health

# Тест генерации
curl -X POST https://ВАШ-URL.onrender.com/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_type": "users",
    "count": 3,
    "locale": "ru_RU",
    "exclude_fields": ["date_of_birth"]
  }'

# Тест схемы
curl https://ВАШ-URL.onrender.com/schemas

# Документация
open https://ВАШ-URL.onrender.com/docs
```

---

## Шаг 5: Автономная эксплуатация

После публикации API работает само:

```
Клиент делает запрос
       ↓
Ваш сервер обрабатывает (uvicorn)
       ↓
Faker генерирует данные
       ↓
RapidAPI обрабатывает биллинг
       ↓
Данные возвращаются клиенту
       ↓
Stripe получает деньги (ежемесячно)
```

**Ничего больше делать не нужно.**

### Мониторинг (раз в неделю):

1. RapidAPI Dashboard → Usage — посмотрите количество запросов
2. Render Dashboard → Health — проверьте аптайм
3. Stripe Dashboard → Revenue — посмотрите доход

---

## 📊 Прогноз дохода

| Месяц | Активных подписчиков | Ожидаемый доход |
|---|---|---|
| 1-2 | 5-15 | $0-50 |
| 3-4 | 15-50 | $50-200 |
| 5-6 | 50-100 | $200-500 |
| 6+ | 100+ | $500-2000+ |

**Ключевые факторы роста:**
- SEO каталога RapidAPI (API находится в поиске внутри платформы)
- Хорошее описание и примеры
- Репост на Hacker News, Reddit (один раз, без поддержки)
- Тэг "Testing" в RapidAPI — высокая категория

---

## 📦 Файлы проекта

```
test-data-generator-api/
├── main.py                  # FastAPI приложение (283 строки)
├── generator.py             # Ядро генерации (366 строк)
├── models.py                # Pydantic модели
├── config.py                # Настройки
├── test_main.py             # 31 тест (все проходят ✅)
├── requirements.txt         # Зависимости
├── Dockerfile               # Docker образ
├── docker-compose.yml       # Docker Compose
├── .env.example             # Переменные окружения
├── .gitignore
├── README.md                # Документация
└── DEPLOY.md                # Этот файл
```

## ⚡ Быстрый старт (итого)

```bash
# 1. Git + GitHub
cd C:\Users\Lenovo\test-data-generator-api
git init && git add . && git commit -m "v2.0" && git push origin main

# 2. Деплой на Render (2 минуты в браузере)
#    New Web Service → выберите репо → Deploy

# 3. Публикация на RapidAPI Hub (10 минут в браузере)
#    hub.rapidapi.com → Publish → заполните → Enable monetization

# ГОТОВО. Больше ничего делать не нужно.
```
