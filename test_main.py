from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# ===================================================================
# Health check
# ===================================================================

class TestHealth:
    def test_health_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data


# ===================================================================
# Schemas endpoints
# ===================================================================

class TestSchemas:
    def test_list_schemas(self):
        resp = client.get("/schemas")
        assert resp.status_code == 200
        data = resp.json()
        assert "available_schemas" in data
        assert "total" in data
        assert data["total"] > 0

    def test_get_existing_schema(self):
        resp = client.get("/schemas/users")
        assert resp.status_code == 200
        data = resp.json()
        assert data["schema_type"] == "users"
        assert "available_fields" in data

    def test_get_nonexistent_schema(self):
        resp = client.get("/schemas/nonexistent_schema_xyz")
        assert resp.status_code == 404


# ===================================================================
# Generate endpoint — predefined schemas
# ===================================================================

class TestGenerate:
    def test_generate_users(self):
        resp = client.post("/generate", json={
            "schema_type": "users",
            "count": 5,
            "locale": "en_US",
            "exclude_fields": ["date_of_birth"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 5
        assert len(data["data"]) == 5
        assert "name" in data["data"][0]
        assert "email" in data["data"][0]
        assert "X-Request-ID" in resp.headers

    def test_generate_transactions(self):
        resp = client.post("/generate", json={
            "schema_type": "transactions",
            "count": 3,
            "locale": "en_US",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 3
        assert "amount" in data["data"][0]

    def test_generate_products(self):
        resp = client.post("/generate", json={
            "schema_type": "products",
            "count": 2,
            "locale": "en_US",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 2
        assert "name" in data["data"][0]

    def test_generate_orders(self):
        resp = client.post("/generate", json={
            "schema_type": "orders",
            "count": 2,
            "locale": "en_US",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 2

    def test_generate_reviews(self):
        resp = client.post("/generate", json={
            "schema_type": "reviews",
            "count": 3,
            "locale": "en_US",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 3
        assert "rating" in data["data"][0]

    def test_generate_employees(self):
        resp = client.post("/generate", json={
            "schema_type": "employees",
            "count": 2,
            "locale": "en_US",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 2

    def test_generate_addresses(self):
        resp = client.post("/generate", json={
            "schema_type": "addresses",
            "count": 2,
            "locale": "en_US",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 2

    def test_generate_vehicles(self):
        resp = client.post("/generate", json={
            "schema_type": "vehicles",
            "count": 2,
            "locale": "en_US",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 2

    def test_generate_medical_records(self):
        resp = client.post("/generate", json={
            "schema_type": "medical_records",
            "count": 2,
            "locale": "en_US",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 2

    def test_generate_social_media(self):
        resp = client.post("/generate", json={
            "schema_type": "social_media",
            "count": 2,
            "locale": "en_US",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 2

    def test_generate_ecommerce(self):
        resp = client.post("/generate", json={
            "schema_type": "ecommerce",
            "count": 2,
            "locale": "en_US",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 2

    def test_generate_banking(self):
        resp = client.post("/generate", json={
            "schema_type": "banking",
            "count": 2,
            "locale": "en_US",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 2


# ===================================================================
# Generate — locale support
# ===================================================================

class TestLocales:
    def test_ru_RU(self):
        resp = client.post("/generate", json={
            "schema_type": "transactions",
            "count": 2,
            "locale": "ru_RU",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 2

    def test_de_DE(self):
        resp = client.post("/generate", json={
            "schema_type": "transactions",
            "count": 2,
            "locale": "de_DE",
        })
        assert resp.status_code == 200

    def test_fr_FR(self):
        resp = client.post("/generate", json={
            "schema_type": "transactions",
            "count": 2,
            "locale": "fr_FR",
        })
        assert resp.status_code == 200

    def test_ja_JP(self):
        resp = client.post("/generate", json={
            "schema_type": "transactions",
            "count": 2,
            "locale": "ja_JP",
        })
        assert resp.status_code == 200

    def test_zh_CN(self):
        resp = client.post("/generate", json={
            "schema_type": "transactions",
            "count": 2,
            "locale": "zh_CN",
        })
        assert resp.status_code == 200


# ===================================================================
# Generate — custom fields
# ===================================================================

class TestCustomFields:
    def test_custom_fields(self):
        resp = client.post("/generate", json={
            "schema_type": "custom",
            "count": 5,
            "locale": "en_US",
            "fields": {
                "username": "username",
                "email": "email",
                "score": "number",
                "active": "boolean",
            },
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 5
        record = data["data"][0]
        assert "username" in record
        assert "email" in record
        assert "score" in record
        assert "active" in record

    def test_include_fields(self):
        resp = client.post("/generate", json={
            "schema_type": "users",
            "count": 3,
            "locale": "en_US",
            "include_fields": ["name", "email"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert set(data["data"][0].keys()) == {"name", "email"}

    def test_exclude_fields(self):
        resp = client.post("/generate", json={
            "schema_type": "transactions",
            "count": 3,
            "locale": "en_US",
            "exclude_fields": ["timestamp"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "timestamp" not in data["data"][0]


# ===================================================================
# Bulk endpoint
# ===================================================================

class TestBulk:
    def test_bulk_generate(self):
        resp = client.post("/generate/bulk", json={
            "requests": [
                {"schema_type": "users", "count": 2, "locale": "en_US"},
                {"schema_type": "products", "count": 3, "locale": "de_DE"},
            ],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert len(data["results"]) == 2
        assert data["total_records"] == 5


# ===================================================================
# Validation
# ===================================================================

class TestValidation:
    def test_count_too_low(self):
        resp = client.post("/generate", json={
            "schema_type": "users",
            "count": 0,
            "locale": "en_US",
        })
        assert resp.status_code == 422

    def test_count_too_high(self):
        resp = client.post("/generate", json={
            "schema_type": "users",
            "count": 100001,
            "locale": "en_US",
        })
        assert resp.status_code == 422

    def test_invalid_schema(self):
        resp = client.post("/generate", json={
            "schema_type": "nonexistent",
            "count": 1,
            "locale": "en_US",
        })
        # 422 = validation error (Pydantic rejects the schema value)
        assert resp.status_code in (400, 422)

    def test_missing_count(self):
        resp = client.post("/generate", json={
            "schema_type": "users",
            "locale": "en_US",
            "exclude_fields": ["date_of_birth"],
        })
        # count has default so this should work
        assert resp.status_code == 200


# ===================================================================
# Export endpoint
# ===================================================================

class TestExport:
    def test_export_json(self):
        resp = client.post("/export", json={
            "schema_type": "transactions",
            "count": 3,
            "locale": "en_US",
            "format": "json",
        })
        assert resp.status_code == 200

    def test_export_csv(self):
        resp = client.post("/export", json={
            "schema_type": "users",
            "count": 3,
            "locale": "en_US",
            "format": "csv",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "name" in data["data"]  # CSV headers in content
