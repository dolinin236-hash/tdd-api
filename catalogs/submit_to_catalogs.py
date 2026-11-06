#!/usr/bin/env python3
"""
Массовая регистрация Test Data Generator API в каталогах.

Категории каталогов:
1. Автоматизированные — скрипт заполняет формы через requests/BeautifulSoup
2. Частично автоматизированные — скрипт генерирует данные для копирования
3. Ручные — скрипт создаёт инструкцию с готовым текстом

Запуск:
    python submit_to_catalogs.py --all          # Все каталоги
    python submit_to_catalogs.py --auto         # Только автоматизированные
    python submit_to_catalogs.py --manual       # Только с инструкциями
    python submit_to_catalogs.py --rapidapi     # Только RapidAPI Hub
    python submit_to_catalogs.py --list         # Список всех каталогов
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
API_INFO_FILE = BASE_DIR / "catalogs" / "api_info.json"
RESULTS_FILE = BASE_DIR / "catalogs" / "submission_results.json"


# ─── Загрузка данных API ───────────────────────────────────────────────────

def load_api_info() -> dict:
    """Загрузить информацию об API из JSON-файла."""
    with open(API_INFO_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ─── Категории каталогов ───────────────────────────────────────────────────

class CatalogType(str, Enum):
    AUTOMATED = "automated"       # Полностью автоматическая регистрация
    PARTIAL = "partial"           # Частичная (нужно доделать вручную)
    MANUAL = "manual"             # Только инструкция + готовые тексты


@dataclass
class Catalog:
    """Описание одного каталога."""
    name: str
    url: str
    submit_url: str
    type: CatalogType
    cost: str                     # "free", "paid", "freemium"
    requires_auth: bool
    category: str                 # Категория каталога
    priority: int                 # 1 = highest
    notes: str = ""               # Примечания по регистрации


# ─── Каталог каталогов ─────────────────────────────────────────────────────

CATALOGS: list[Catalog] = [
    # ── Приоритет 1: Максимальный трафик ──
    Catalog(
        name="RapidAPI Hub",
        url="https://rapidapi.com/",
        submit_url="https://rapidapi.com/developer",
        type=CatalogType.PARTIAL,
        cost="freemium",
        requires_auth=True,
        category="api-marketplace",
        priority=1,
        notes=(
            "Крупнейший маркетплейс API. publisher.rapidapi.com — панель управления. "
            "Нужна регистрация → Add API → подключить GitHub репозиторий. "
            "Скрипт подготовит OpenAPI spec и описания."
        ),
    ),
    Catalog(
        name="Product Hunt",
        url="https://www.producthunt.com/",
        submit_url="https://www.producthunt.com/products/submit",
        type=CatalogType.MANUAL,
        cost="free",
        requires_auth=True,
        category="product-launch",
        priority=2,
        notes=(
            "Мощный источник начального трафика. Создать аккаунт → Submit Product. "
            "Лучше всего — назначить Launch Day и собрать upvote'ы."
        ),
    ),
    Catalog(
        name="API List (apilist.fun)",
        url="https://apilist.fun/",
        submit_url="https://apilist.fun/submit-api",
        type=CatalogType.AUTOMATED,
        cost="free",
        requires_auth=False,
        category="api-directory",
        priority=3,
        notes="Бесплатный каталог API. Простая форма.",
    ),
    # ── Приоритет 2: SEO-авторитет ──
    Catalog(
        name="Public APIs (GitHub)",
        url="https://github.com/public-apis/public-apis",
        submit_url="https://github.com/public-apis/public-apis/pulls",
        type=CatalogType.MANUAL,
        cost="free",
        requires_auth=True,
        category="open-source-directory",
        priority=4,
        notes=(
            "100k+ звёзд. Нужен Pull Request в CSV. API должен быть публичным. "
            "Наш API — Freemium (с бесплатным tier), подходит."
        ),
    ),
    Catalog(
        name="SaaSHub (бывший Capterra Gateway)",
        url="https://www.saashub.com/",
        submit_url="https://www.saashub.com/submit",
        type=CatalogType.AUTOMATED,
        cost="free",
        requires_auth=False,
        category="saas-directory",
        priority=5,
        notes="Крупный каталог SaaS-продуктов.",
    ),
    Catalog(
        name="AlternativeTo",
        url="https://www.alternativeto.net/",
        submit_url="https://www.alternativeto.net/about/submit-a-product",
        type=CatalogType.AUTOMATED,
        cost="free",
        requires_auth=False,
        category="software-alternative",
        priority=6,
        notes="Каталог альтернатив софта. Можно позиционировать как альтернативу Mockaroo, JSONGenerator.",
    ),
    # ── Приоритет 3: Специализированные ──
    Catalog(
        name="BetaList",
        url="https://betalist.com/",
        submit_url="https://betalist.com/submit",
        type=CatalogType.AUTOMATED,
        cost="free",
        requires_auth=False,
        category="startup-directory",
        priority=7,
        notes="Каталог стартапов и новых продуктов.",
    ),
    Catalog(
        name="DataHub (datahub.io)",
        url="https://datahub.io/",
        submit_url="https://datahub.io/datasets",
        type=CatalogType.MANUAL,
        cost="free",
        requires_auth=False,
        category="data-registry",
        priority=8,
        notes="Реестр открытых дата-сетов. Можно добавить как generator tool.",
    ),
    Catalog(
        name="ProgrammableWeb (архивный)",
        url="https://www.programmableweb.com/",
        submit_url="https://www.programmablewecom/api-directory",
        type=CatalogType.MANUAL,
        cost="free",
        requires_auth=False,
        category="api-directory-archive",
        priority=9,
        notes="Бывший крупнейший каталог API. Сейчас архив. Если работает — добавить.",
    ),
    # ── Приоритет 4: Дополнительные ──
    Catalog(
        name="Capterra",
        url="https://www.capterra.com/",
        submit_url="https://www.capterra.com/partners/",
        type=CatalogType.MANUAL,
        cost="free",
        requires_auth=True,
        category="software-review",
        priority=10,
        notes="Нужна регистрация как партнёр Capterra.",
    ),
    Catalog(
        name="G2",
        url="https://www.g2.com/",
        submit_url="https://www.g2.com/products/add",
        type=CatalogType.MANUAL,
        cost="freemium",
        requires_auth=True,
        category="software-review",
        priority=11,
        notes="Крупная площадка отзывов. Бесплатная базовая страница.",
    ),
    Catalog(
        name="StackShare",
        url="https://stackoverflow.blog/2014/06/27/stackflows-developer-tools-directory/",
        submit_url="https://stackshare.io/",
        type=CatalogType.MANUAL,
        cost="free",
        requires_auth=True,
        category="tech-stack",
        priority=12,
        notes="Каталог инструментов разработки. Разработчики ищут здесь.",
    ),
    Catalog(
        name="DevTools",
        url="https://devtol.rs/",
        submit_url="https://devtol.rs/submit",
        type=CatalogType.AUTOMATED,
        cost="free",
        requires_auth=False,
        category="devtools-directory",
        priority=13,
        notes="Каталог devtools от DEV.community.",
    ),
    Catalog(
        name="Free Software Directory (FSF)",
        url="https://directory.fsf/",
        submit_url="https://directory.fsf/wiki/",
        type=CatalogType.MANUAL,
        cost="free",
        requires_auth=False,
        category="open-source-directory",
        priority=14,
        notes="Если код open-source — можно добавить.",
    ),
    Catalog(
        name="Awesome Lists (GitHub)",
        url="https://github.com/sindresorhus/awesome",
        submit_url="https://github.com/sindresorhus/awesome/blob/main/CONTRIBUTING.md",
        type=CatalogType.MANUAL,
        cost="free",
        requires_auth=True,
        category="awesome-list",
        priority=15,
        notes="Нужен PR в awesome-python или awesome-api. Высокий SEO-вес.",
    ),
]


# ─── Движок автоматизации ──────────────────────────────────────────────────

class CatalogSubmitter:
    """Отправка API в каталоги."""

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self, api_info: dict):
        self.api = api_info
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.results: list[dict] = []

    def _check_url_reachable(self, url: str, timeout: int = 10) -> bool:
        """Проверить, доступен ли URL каталога."""
        try:
            resp = self.session.get(url, timeout=timeout, allow_redirects=True)
            return resp.status_code == 200
        except Exception:
            return False

    def submit_to_apilist(self, catalog: Catalog) -> dict:
        """
        Регистрация на apilist.fun.
        Формат: частичная автоматизация через POST.
        """
        logger.info("  → apilist.fun: проверка доступности...")
        reachable = self._check_url_reachable(catalog.submit_url)

        if not reachable:
            logger.warning("  ✗ apilist.fun: недоступен")
            return {
                "catalog": catalog.name,
                "status": "unreachable",
                "submit_url": catalog.submit_url,
            }

        # Попробуем найти форму и заполнить
        logger.info("  → apilist.fun: анализ формы...")
        try:
            resp = self.session.get(catalog.submit_url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Ищем form и input fields
            form = soup.find("form")
            inputs = soup.find_all("input") if form else []

            if not form:
                # Форма может быть на отдельной странице или через JS
                logger.info("  → apilist.fun: форма не найдена, создаём инструкцию")
                return {
                    "catalog": catalog.name,
                    "status": "manual_needed",
                    "submit_url": catalog.submit_url,
                    "instructions": self._generate_instructions(catalog),
                }

            # Пытаемся автозаполнить
            fields = {}
            for inp in inputs:
                name = inp.get("name") or inp.get("id")
                if name:
                    fields[name] = self._field_value(name)

            logger.info(f"  → apilist.fun: найдено {len(fields)} полей")

            try:
                resp = self.session.post(
                    catalog.submit_url,
                    data=fields,
                    timeout=15,
                )
                if resp.status_code == 200:
                    logger.info("  ✓ apilist.fun: отправка успешна")
                    return {
                        "catalog": catalog.name,
                        "status": "submitted",
                        "submit_url": catalog.submit_url,
                        "response_code": resp.status_code,
                    }
            except Exception as e:
                logger.info(f"  → apilist.fun: автоотправка не удалась — {e}")

            return {
                "catalog": catalog.name,
                "status": "manual_needed",
                "submit_url": catalog.submit_url,
                "instructions": self._generate_instructions(catalog),
            }
        except Exception as e:
            logger.error(f"  ✗ apilist.fun: ошибка — {e}")
            return {
                "catalog": catalog.name,
                "status": "error",
                "error": str(e),
                "submit_url": catalog.submit_url,
            }

    def submit_to_saashub(self, catalog: Catalog) -> dict:
        """Регистрация на SaaSHub."""
        logger.info("  → SaaSHub: проверка доступности...")
        reachable = self._check_url_reachable(catalog.submit_url)

        if not reachable:
            return {
                "catalog": catalog.name,
                "status": "unreachable",
                "submit_url": catalog.submit_url,
            }

        logger.info("  → SaaSHub: анализ формы...")
        try:
            resp = self.session.get(catalog.submit_url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            form = soup.find("form")
            inputs = soup.find_all("input") if form else []

            fields = {}
            for inp in inputs:
                name = inp.get("name") or inp.get("id")
                if name:
                    fields[name] = self._field_value(name)

            if fields:
                try:
                    resp = self.session.post(
                        catalog.submit_url,
                        data=fields,
                        timeout=15,
                    )
                    if resp.status_code == 200:
                        logger.info("  ✓ SaaSHub: отправка успешна")
                        return {
                            "catalog": catalog.name,
                            "status": "submitted",
                            "submit_url": catalog.submit_url,
                            "response_code": resp.status_code,
                        }
                except Exception:
                    pass

            return {
                "catalog": catalog.name,
                "status": "manual_needed",
                "submit_url": catalog.submit_url,
                "instructions": self._generate_instructions(catalog),
            }
        except Exception as e:
            logger.error(f"  ✗ SaaSHub: ошибка — {e}")
            return {
                "catalog": catalog.name,
                "status": "error",
                "error": str(e),
            }

    def submit_to_alternativeto(self, catalog: Catalog) -> dict:
        """Регистрация на AlternativeTo."""
        logger.info("  → AlternativeTo: проверка доступности...")
        reachable = self._check_url_reachable(catalog.submit_url)

        if not reachable:
            return {
                "catalog": catalog.name,
                "status": "unreachable",
                "submit_url": catalog.submit_url,
            }

        logger.info("  → AlternativeTo: анализ формы...")
        try:
            resp = self.session.get(catalog.submit_url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            form = soup.find("form")
            inputs = soup.find_all("input") if form else []

            fields = {}
            for inp in inputs:
                name = inp.get("name") or inp.get("id")
                if name:
                    fields[name] = self._field_value(name)

            if fields:
                try:
                    resp = self.session.post(
                        catalog.submit_url,
                        data=fields,
                        timeout=15,
                    )
                    if resp.status_code == 200:
                        logger.info("  ✓ AlternativeTo: отправка успешна")
                        return {
                            "catalog": catalog.name,
                            "status": "submitted",
                            "submit_url": catalog.submit_url,
                        }
                except Exception:
                    pass

            return {
                "catalog": catalog.name,
                "status": "manual_needed",
                "submit_url": catalog.submit_url,
                "instructions": self._generate_instructions(catalog),
            }
        except Exception as e:
            logger.error(f"  ✗ AlternativeTo: ошибка — {e}")
            return {
                "catalog": catalog.name,
                "status": "error",
                "error": str(e),
            }

    def submit_to_betalist(self, catalog: Catalog) -> dict:
        """Регистрация на BetaList."""
        logger.info("  → BetaList: проверка доступности...")
        reachable = self._check_url_reachable(catalog.submit_url)

        if not reachable:
            return {
                "catalog": catalog.name,
                "status": "unreachable",
                "submit_url": catalog.submit_url,
            }

        logger.info("  → BetaList: анализ формы...")
        try:
            resp = self.session.get(catalog.submit_url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            form = soup.find("form")
            inputs = soup.find_all("input") if form else []

            fields = {}
            for inp in inputs:
                name = inp.get("name") or inp.get("id")
                if name:
                    fields[name] = self._field_value(name)

            if fields:
                try:
                    resp = self.session.post(
                        catalog.submit_url,
                        data=fields,
                        timeout=15,
                    )
                    if resp.status_code == 200:
                        logger.info("  ✓ BetaList: отправка успешна")
                        return {
                            "catalog": catalog.name,
                            "status": "submitted",
                            "submit_url": catalog.submit_url,
                        }
                except Exception:
                    pass

            return {
                "catalog": catalog.name,
                "status": "manual_needed",
                "submit_url": catalog.submit_url,
                "instructions": self._generate_instructions(catalog),
            }
        except Exception as e:
            logger.error(f"  ✗ BetaList: ошибка — {e}")
            return {
                "catalog": catalog.name,
                "status": "error",
                "error": str(e),
            }

    def submit_to_devtol(self, catalog: Catalog) -> dict:
        """Регистрация на DevTools (devtol.rs)."""
        logger.info("  → devtol.rs: проверка доступности...")
        reachable = self._check_url_reachable(catalog.submit_url)

        if not reachable:
            return {
                "catalog": catalog.name,
                "status": "unreachable",
                "submit_url": catalog.submit_url,
            }

        logger.info("  → devtol.rs: анализ формы...")
        try:
            resp = self.session.get(catalog.submit_url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            form = soup.find("form")
            inputs = soup.find_all("input") if form else []

            fields = {}
            for inp in inputs:
                name = inp.get("name") or inp.get("id")
                if name:
                    fields[name] = self._field_value(name)

            if fields:
                try:
                    resp = self.session.post(
                        catalog.submit_url,
                        data=fields,
                        timeout=15,
                    )
                    if resp.status_code == 200:
                        logger.info("  ✓ devtol.rs: отправка успешна")
                        return {
                            "catalog": catalog.name,
                            "status": "submitted",
                            "submit_url": catalog.submit_url,
                        }
                except Exception:
                    pass

            return {
                "catalog": catalog.name,
                "status": "manual_needed",
                "submit_url": catalog.submit_url,
                "instructions": self._generate_instructions(catalog),
            }
        except Exception as e:
            logger.error(f"  ✗ devtol.rs: ошибка — {e}")
            return {
                "catalog": catalog.name,
                "status": "error",
                "error": str(e),
            }

    def _field_value(self, field_name: str) -> str:
        """Маппинг имён полей формы → значения API."""
        name = field_name.lower().replace("-", "_").replace(" ", "_")

        mapping = {
            "name": self.api["name"],
            "product_name": self.api["name"],
            "title": self.api["name"],
            "tagline": self.api["tagline"],
            "description": self.api["description"],
            "short_description": self.api["short_description"],
            "url": self.api["url"],
            "website": self.api["url"],
            "api_url": self.api["api_base_url"],
            "docs_url": self.api["docs_url"],
            "github_url": self.api["github_url"],
            "email": self.api["author"]["email"],
            "category": self.api["categories"][0] if self.api["categories"] else "development tools",
            "tags": ", ".join(self.api["tags"]),
            "tag": ", ".join(self.api["tags"]),
            "tags_input": ", ".join(self.api["tags"]),
            "price_model": self.api["pricing_model"],
            "pricing": self.api["pricing_model"],
            "author": self.api["author"]["name"],
            "logo_url": self.api.get("logo_url", self.api["url"] + "/static/logo.png"),
            "image_url": self.api.get("logo_url", self.api["url"] + "/static/logo.png"),
            "thumbnail_url": self.api.get("logo_url", self.api["url"] + "/static/logo.png"),
        }

        return mapping.get(name, "")

    def _generate_instructions(self, catalog: Catalog) -> str:
        """Сгенерировать пошаговую инструкцию для ручной регистрации."""
        api = self.api
        return (
            f"📋 Инструкция по регистрации на {catalog.name}:\n\n"
            f"1. Перейдите: {catalog.submit_url}\n\n"
            f"2. Заполните поля:\n"
            f"   • Название:     {api['name']}\n"
            f"   • Слоган:       {api['tagline']}\n"
            f"   • Описание:     {api['short_description']}\n"
            f"   • URL:          {api['url']}\n"
            f"   • Docs URL:     {api['docs_url']}\n"
            f"   • GitHub:       {api['github_url']}\n"
            f"   • Email:        {api['author']['email']}\n"
            f"   • Категория:    {api['categories'][0]}\n"
            f"   • Теги:         {', '.join(api['tags'][:5])}\n"
            f"   • Тариф:        {api['pricing_model']}\n"
            f"   • Auth:         {api['authentication']}\n\n"
            f"3. Отправьте форму и проверьте email для верификации."
        )

    def generate_rapidapi_assets(self, catalog: Catalog) -> dict:
        """
        Подготовить все материалы для RapidAPI Hub.
        Это нельзя сделать полностью автоматически (нужен аккаунт),
        но можно сгенерировать OpenAPI spec и все описания.
        """
        logger.info("  → RapidAPI Hub: генерация материалов...")

        # Генерируем OpenAPI 3.0 spec
        openapi_spec = self._generate_openapi_spec()

        assets = {
            "openapi_spec": openapi_spec,
            "description": self.api["description"],
            "tagline": self.api["tagline"],
            "short_description": self.api["short_description"],
            "categories": self.api["categories"],
            "tags": self.api["tags"],
            "authentication": {
                "type": "apikey",
                "in": "header",
                "name": "X-API-Key",
            },
            "base_url": self.api["api_base_url"],
            "docs_url": self.api["docs_url"],
            "code_examples": self.api["code_examples"],
            "instructions": (
                f"📋 Регистрация на RapidAPI Hub:\n\n"
                f"1. Зайдите на https://publisher.rapidapi.com/\n"
                f"2. Sign in с GitHub\n"
                f"3. Нажмите 'Add API'\n"
                f"4. Подключите репозиторий: {self.api['github_url']}\n"
                f"5. Upload сгенерированный OpenAPI spec:\n"
                f"   {BASE_DIR / 'catalogs' / 'rapidapi_openapi_spec.json'}\n"
                f"6. Заполните описания из этого файла\n"
                f"7. Укажите base URL: {self.api['api_base_url']}\n"
                f"8. Настройте аутентификацию: API Key in header (X-API-Key)\n"
                f"9. Выберите категории: {', '.join(self.api['categories'][:3])}\n"
                f"10. Publish! 🚀"
            ),
        }

        # Сохраняем OpenAPI spec
        spec_path = BASE_DIR / "catalogs" / "rapidapi_openapi_spec.json"
        with open(spec_path, "w", encoding="utf-8") as f:
            json.dump(openapi_spec, f, indent=2, ensure_ascii=False)
        logger.info(f"  ✓ OpenAPI spec сохранён: {spec_path}")

        return assets

    def _generate_openapi_spec(self) -> dict:
        """Сгенерировать OpenAPI 3.0 спецификацию для RapidAPI."""
        base_url = self.api["api_base_url"]

        return {
            "openapi": "3.0.3",
            "info": {
                "title": self.api["name"],
                "version": "4.0.0",
                "description": self.api["description"],
                "contact": {
                    "name": self.api["author"]["name"],
                    "email": self.api["author"]["email"],
                    "url": self.api["url"],
                },
            },
            "externalDocs": {
                "url": self.api["docs_url"],
            },
            "servers": [
                {
                    "url": base_url,
                    "description": "Production",
                }
            ],
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health check",
                        "operationId": "healthCheck",
                        "tags": ["Public"],
                        "responses": {
                            "200": {
                                "description": "API is healthy",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "status": {"type": "string"},
                                                "version": {"type": "string"},
                                            }
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
                "/schemas": {
                    "get": {
                        "summary": "List available schemas",
                        "operationId": "listSchemas",
                        "tags": ["Public"],
                        "responses": {
                            "200": {
                                "description": "List of available schemas",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "available_schemas": {
                                                    "type": "array",
                                                    "items": {"type": "object"},
                                                },
                                                "total": {"type": "integer"},
                                            }
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
                "/register": {
                    "post": {
                        "summary": "Register for free API key",
                        "operationId": "registerApiKey",
                        "tags": ["Authentication"],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "email": {"type": "string", "format": "email"},
                                        }
                                    }
                                }
                            },
                        },
                        "responses": {
                            "200": {
                                "description": "API key created",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "message": {"type": "string"},
                                                "api_key": {"type": "string"},
                                                "tier": {"type": "string"},
                                                "daily_limit": {"type": "integer"},
                                            }
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
                "/generate": {
                    "post": {
                        "summary": "Generate test data",
                        "operationId": "generateData",
                        "tags": ["Generation"],
                        "security": [{"ApiKeyAuth": []}],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["schema_type", "count", "locale"],
                                        "properties": {
                                            "schema_type": {
                                                "type": "string",
                                                "enum": self.api["schema_types"],
                                                "description": "Data schema to generate",
                                            },
                                            "count": {
                                                "type": "integer",
                                                "minimum": 1,
                                                "maximum": 10000,
                                                "description": "Number of records",
                                            },
                                            "locale": {
                                                "type": "string",
                                                "enum": self.api["locales"],
                                                "description": "Localization",
                                            },
                                            "include_fields": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                            },
                                            "exclude_fields": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                            },
                                            "fields": {
                                                "type": "object",
                                                "description": "Custom field definitions",
                                            },
                                        },
                                    }
                                }
                            },
                        },
                        "responses": {
                            "200": {
                                "description": "Generated data",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "schema_type": {"type": "string"},
                                                "count": {"type": "integer"},
                                                "locale": {"type": "string"},
                                                "data": {"type": "array"},
                                                "generated_at": {"type": "string", "format": "date-time"},
                                                "request_id": {"type": "string"},
                                            }
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
                "/generate/bulk": {
                    "post": {
                        "summary": "Bulk generate test data",
                        "operationId": "bulkGenerate",
                        "tags": ["Generation"],
                        "security": [{"ApiKeyAuth": []}],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["requests"],
                                        "properties": {
                                            "requests": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "schema_type": {"type": "string"},
                                                        "count": {"type": "integer"},
                                                        "locale": {"type": "string"},
                                                    }
                                                },
                                            }
                                        },
                                    }
                                }
                            },
                        },
                        "responses": {
                            "200": {
                                "description": "Bulk generated data",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "results": {"type": "array"},
                                                "total_records": {"type": "integer"},
                                                "generated_at": {"type": "string", "format": "date-time"},
                                            }
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
            },
            "components": {
                "securitySchemes": {
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key",
                    }
                }
            },
        }

    def submit_to_catalog(self, catalog: Catalog) -> dict:
        """Запустить отправку в каталог (диспетчер)."""
        logger.info(f"[P{catalog.priority}] {catalog.name}...")

        if catalog.name == "RapidAPI Hub":
            return self.generate_rapidapi_assets(catalog)

        dispatch = {
            "API List (apilist.fun)": self.submit_to_apilist,
            "SaaSHub (бывший Capterra Gateway)": self.submit_to_saashub,
            "AlternativeTo": self.submit_to_alternativeto,
            "BetaList": self.submit_to_betalist,
            "DevTools (devtol.rs)": self.submit_to_devtol,
        }

        handler = dispatch.get(catalog.name)
        if handler:
            return handler(catalog)

        # Если нет обработчика — возвращаем инструкцию
        return {
            "catalog": catalog.name,
            "status": "manual_needed",
            "submit_url": catalog.submit_url,
            "instructions": self._generate_instructions(catalog),
        }

    def run(self, filter_type: Optional[str] = None) -> list[dict]:
        """Запустить регистрацию во все подходящие каталоги."""
        filtered = CATALOGS

        if filter_type == "auto":
            filtered = [c for c in CATALOGS if c.type == CatalogType.AUTOMATED]
        elif filter_type == "manual":
            filtered = [c for c in CATALOGS if c.type == CatalogType.MANUAL]

        # Сортируем по приоритету
        filtered.sort(key=lambda c: c.priority)

        logger.info(f"Начинаем регистрацию в {len(filtered)} каталогах...\n")

        for catalog in filtered:
            try:
                result = self.submit_to_catalog(catalog)
                self.results.append(result)
            except Exception as e:
                logger.error(f"  ✗ {catalog.name}: критическая ошибка — {e}")
                self.results.append({
                    "catalog": catalog.name,
                    "status": "error",
                    "error": str(e),
                })
            logger.info("")  # пустая строка между каталогами

        # Сохраняем результаты
        self._save_results()
        self._print_summary()

        return self.results

    def _save_results(self):
        """Сохранить результаты в JSON."""
        output = {
            "generated_at": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
            "total": len(self.results),
            "summary": {
                "submitted": sum(1 for r in self.results if r.get("status") == "submitted"),
                "manual_needed": sum(
                    1 for r in self.results if r.get("status") == "manual_needed"
                ),
                "unreachable": sum(
                    1 for r in self.results if r.get("status") == "unreachable"
                ),
                "error": sum(1 for r in self.results if r.get("status") == "error"),
            },
            "results": self.results,
        }

        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        logger.info(f"Результаты сохранены: {RESULTS_FILE}")

    def _print_summary(self):
        """Вывести краткую сводку."""
        summary = RESULTS_FILE
        if RESULTS_FILE.exists():
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            s = data["summary"]
        else:
            s = {"submitted": 0, "manual_needed": 0, "unreachable": 0, "error": 0}

        print("\n" + "=" * 50)
        print("RESULTS SUMMARY")
        print("=" * 50)
        print(f"  [OK] Submitted:      {s['submitted']}")
        print(f"  [MANUAL] Needs manual: {s['manual_needed']}")
        print(f"  [FAIL] Unreachable:  {s['unreachable']}")
        print(f"  [ERROR] Errors:      {s['error']}")
        print("=" * 50)


# ─── CLI ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Массовая регистрация API в каталогах",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python submit_to_catalogs.py --all           # Все каталоги
  python submit_to_catalogs.py --auto          # Только автоматизированные
  python submit_to_catalogs.py --manual        # Только с инструкциями
  python submit_to_catalogs.py --list          # Список каталогов
  python submit_to_catalogs.py --rapidapi      # Только RapidAPI Hub
        """,
    )
    parser.add_argument(
        "--all", action="store_true", help="Регистрация во все каталоги"
    )
    parser.add_argument(
        "--auto", action="store_true", help="Только автоматизированные каталоги"
    )
    parser.add_argument(
        "--manual", action="store_true", help="Только каталоги с инструкциями"
    )
    parser.add_argument(
        "--rapidapi", action="store_true", help="Только подготовить RapidAPI Hub"
    )
    parser.add_argument(
        "--list", action="store_true", help="Список всех каталогов"
    )

    args = parser.parse_args()

    if not any([args.all, args.auto, args.manual, args.rapidapi, args.list]):
        parser.print_help()
        sys.exit(1)

    api_info = load_api_info()
    submitter = CatalogSubmitter(api_info)

    if args.list:
        print("\n=== КАТАЛОГИ ДЛЯ РЕГИСТРАЦИИ ===\n")
        print(f"{'#':>3}  {'Приоритет':<10} {'Название':<30} {'Тип':<15} {'Стоимость':<10}")
        print("-" * 75)
        for i, cat in enumerate(CATALOGS, 1):
            type_map = {
                CatalogType.AUTOMATED: "[AUTO]   ",
                CatalogType.PARTIAL:    "[PARTIAL]",
                CatalogType.MANUAL:     "[MANUAL] ",
            }
            print(
                f"{i:>3}  {cat.priority:<10} {cat.name:<30} "
                f"{type_map[cat.type]:<15} {cat.cost:<10}"
            )
        print(f"\nВсего: {len(CATALOGS)} каталогов")
        return

    if args.rapidapi:
        submitter.generate_rapidapi_assets(CATALOGS[0])
        return

    filter_type = None
    if args.auto:
        filter_type = "auto"
    elif args.manual:
        filter_type = "manual"

    submitter.run(filter_type=filter_type)


if __name__ == "__main__":
    import os
    import sys

    # Fix Windows console encoding for UTF-8
    if os.name == "nt":
        os.environ["PYTHONIOENCODING"] = "utf-8"
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer)

    main()
