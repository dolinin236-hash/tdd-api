# Catalogs Directory — Массовая регистрация API

Этот каталог содержит все инструменты и материалы для регистрации Test Data Generator API в API-каталогах.

## Структура

```
catalogs/
├── api_info.json                    # Основная информация об API (источник для всех каталогов)
├── rapidapi_openapi_spec.json       # OpenAPI 3.0 spec для RapidAPI Hub
├── submit_to_catalogs.py            # Скрипт массовой регистрации
├── submission_results.json          # Результаты автоматической регистрации
├── CATALOG_REGISTRATION_GUIDE.md    # Полное руководство по ручной регистрации
├── public-apis-pr.md                # Шаблоны PR для Public APIs (GitHub)
├── awesome-python-pr.md             # Шаблоны PR для awesome-python
└── README.md                        # Этот файл
```

## Быстрый старт

### 1. Автоматическая регистрация

```bash
# Список всех каталогов
python catalogs/submit_to_catalogs.py --list

# Попытаться автоматизировать регистрацию
python catalogs/submit_to_catalogs.py --auto

# Подготовить материалы для RapidAPI Hub
python catalogs/submit_to_catalogs.py --rapidapi

# Только с инструкциями
python catalogs/submit_to_catalogs.py --manual
```

### 2. Ручная регистрация

Следуйте пошаговым инструкциям в `CATALOG_REGISTRATION_GUIDE.md`.

### 3. GitHub PR

```bash
# Для Public APIs
# Скопируйте содержимое public-apis-pr.md и создайте PR в:
# https://github.com/public-apis/public-apis

# Для awesome-python
# Скопируйте содержимое awesome-python-pr.md и создайте PR в:
# https://github.com/avelino/awesome-python
```

## Каталог каталогов

| # | Каталог | Тип | Статус | URL |
|---|---------|-----|--------|-----|
| 1 | RapidAPI Hub | Partial | ✅ Spec готов | publisher.rapidapi.com |
| 2 | Product Hunt | Manual | ⬜ | producthunt.com |
| 3 | API List | Manual | ⬜ | apilist.fun |
| 4 | Public APIs (GitHub) | Manual | ⬜ PR готов | github.com/public-apis/public-apis |
| 5 | SaaSHub | Manual | ⬜ | saashub.com |
| 6 | AlternativeTo | Manual | ⬜ | alternativeto.net |
| 7 | BetaList | Partial | ⬜ |betalist.com |
| 8 | DevTools | Manual | ⬜ | devtol.rs |
| 9 | Capterra | Manual | ⬜ | capterra.com |
| 10 | G2 | Manual | ⬜ | g2.com |
| 11 | StackShare | Manual | ⬜ | stackshare.io |
| 12 | DataHub | Manual | ⬜ | datahub.io |
| 13 | Awesome Lists | Manual | ⬜ PR готов | github.com/avelino/awesome-python |
| 14 | ProgrammableWeb | Manual | ⬜ | programmableweb.com |
| 15 | FSF | Manual | ⬜ | directory.fsf |

## Приоритеты

1. 🔴 **Сегодня:** RapidAPI Hub + Product Hunt
2. 🟡 **Эта неделя:** API List, Public APIs, SaaSHub, DevTools
3. 🟢 **Этот месяц:** Остальные 8 каталогов

## Готовые тексты

Все тексты для копирования — в `CATALOG_REGISTRATION_GUIDE.md` (секция "Готовые данные для копирования").
