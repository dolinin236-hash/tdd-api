# 🚀 Полный гайд: запуск и монетизация Test Data Generator API

## Что создано

✅ **API** — 12 схем, 10 локалей, 44 теста проходят  
✅ **API Key система** — бесплатный тариф (100 req/day), премиум ($5)  
✅ **Крипто-оплата** — USDT TRC20 (рабочая в РФ)  
✅ **Защита** — все эндпоинты защищены ключами  
✅ **Документация** — Swagger UI, README  

---

## Шаг 1: Деплой на Render

1. Идём на **https://render.com** → Sign in с GitHub
2. **New +** → **Web Service**
3. Выбираем репозиторий: **dolinin236-hash/tdd-api**
4. Заполняем:

| Поле | Значение |
|---|---|
| **Name** | `test-data-generator` |
| **Region** | US West |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | **Free** |

5. Жмём **Create Web Service**
6. Ждём 2-3 минуты — API работает!

**Ваш URL:** `https://test-data-generator-xxxx.onrender.com`

---

## Шаг 2: Настройка крипто-оплаты

### Вариант A: NowPayments (автоматический)

1. Идём на **https://nowpayments.io** → Sign Up
2. Создаём API Key: **Settings → API Keys**
3. Копируем **API Key** и **IPN Secret**
4. В Render → **Environment Variables**:
   - `NOWPAYMENTS_API_KEY=ваш_ключ`
   - `NOWPAYMENTS_IPN_SECRET=ваш_секрет`
   - `SERVER_URL=https://ваш-url.onrender.com`

### Вариант B: Ручная оплата (без настройки)

Работает сразу. Клиент переводит на ваш адрес → пишет вам → получаете ключ.

Адрес кошелька (измените в `api_keys.py`):
```python
PAYMENT_ADDRESS = "ВАШ_USDT_TRC20_АДРЕС"
```

---

## Шаг 3: Регистрация в каталогах

**Клиенты придут сами** — регистрируйте API в каталогах:

| Каталог | Ссылка |
|---|---|
| **API List** | https://apilist.fun/submit-api |
| **Public APIs** | https://publicapis.io/submit-api |
| **Awesome APIs** | https://github.com/public-apis/public-apis |
| **Product Hunt** | https://www.producthunt.com/ |

**Каждый каталог = бесплатный трафик!**

---

## Шаг 4: Как клиенты используют ваш API

### Получение ключа (бесплатно):
```bash
curl -X POST https://ВАШ-URL.onrender.com/register \
  -d '{"email": "user@example.com"}'
```

### Использование:
```bash
curl -X POST https://ВАШ-URL.onrender.com/generate \
  -H "X-API-Key: КЛЮЧ_КЛИЕНТА" \
  -d '{"schema_type": "users", "count": 10, "locale": "ru_RU"}'
```

### Оплата Premium ($5 USDT):
```bash
curl -X POST https://ВАШ-URL.onrender.com/pay \
  -d '{"api_key": "КЛЮЧ_КЛИЕНТА"}'
```

Вернёт адрес кошелька и инструкции.

---

## 💰 Экономика

| Параметр | Значение |
|---|---|
| Стоимость хостинга | **$0/мес** (Render Free) |
| Стоимость API ключей | **$0** (JSON файл) |
| Комиссия NowPayments | **0.5%** |
| Цена Premium | **$5 USDT** |
| Чистая прибыль | **~$4.97 с клиента** |

**Прогноз:**
- 10 клиентов/мес → $49.70/мес
- 50 клиентов/мес → $248.50/мес
- 100 клиентов/мес → $497/мес

---

## 📊 Мониторинг

```bash
# Проверить здоровье API
curl https://ВАШ-URL.onrender.com/health

# Посмотреть все ключи
# (через Python)
from api_keys import key_store
keys = key_store.list_keys()
for k in keys:
    print(k)

# Посмотреть платежи
from api_keys import payment_store
payments = payment_store._data["payments"]
for p in payments:
    print(p)
```

---

## 🆘 Решение проблем

### Клиент не получает ключ
- Проверьте `api_keys_db.json` — должен существовать
- Проверьте логи Render

### Оплата не проходит
- Проверьте `NOWPAYMENTS_API_KEY` в переменных окружения
- Проверьте webhook: `/webhook/payment`

### API не запускается
- Проверьте `requirements.txt` — все зависимости
- Проверьте `SERVER_URL` — полный URL с https://

---

## 🎯 Итог

Вы сделали:
1. ✅ API с 12 схемами
2. ✅ Систему API ключей
3. ✅ Крипто-оплату
4. ✅ Защиту и лимиты

Осталось сделать:
1. Задеплоить на Render (5 минут)
2. Зарегистрировать в 2-3 каталогах (10 минут)
3. Подождать клиентов (авто)

**Всё работает полностью автономно!**
