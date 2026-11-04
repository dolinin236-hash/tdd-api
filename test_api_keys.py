"""Tests for API key system and crypto payments."""

import json
import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ===================================================================
# Register endpoints
# ===================================================================

class TestRegister:
    def test_register_without_email(self):
        resp = client.get("/register")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tier"] == "free"
        assert data["daily_limit"] == 100
        assert data["is_active"] is True

    def test_register_returns_key_info(self):
        """Register returns key info, key is stored in file."""
        resp = client.get("/register")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tier"] == "free"
        # Key itself is not in response, but stored internally


# ===================================================================
# API key authentication
# ===================================================================

class TestAuth:
    def _get_last_key(self):
        from api_keys import key_store
        keys = list(key_store._data["keys"].items())
        return keys[-1][0] if keys else None

    def test_generate_without_key_rejected(self):
        resp = client.post("/generate", json={
            "schema_type": "users",
            "count": 2,
            "locale": "en_US",
        })
        assert resp.status_code == 401
        detail = resp.json()["detail"]
        assert "api_key_required" in detail.get("error", "")

    def test_generate_with_invalid_key_rejected(self):
        resp = client.post("/generate", json={
            "schema_type": "users",
            "count": 2,
            "locale": "en_US",
        }, headers={"X-API-Key": "invalid_key_xyz"})
        assert resp.status_code == 403
        detail = resp.json()["detail"]
        assert "invalid_key" in detail.get("error", "")

    def test_generate_with_valid_key(self):
        # Register first
        client.get("/register")
        api_key = self._get_last_key()
        assert api_key is not None

        resp = client.post("/generate", json={
            "schema_type": "users",
            "count": 2,
            "locale": "en_US",
        }, headers={"X-API-Key": api_key})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 2
        assert "name" in data["data"][0]
        assert "email" in data["data"][0]

    def test_generate_rate_limit(self):
        # Register and set limit to 1
        client.get("/register")
        api_key = self._get_last_key()

        from api_keys import key_store
        with key_store._lock:
            key_store._data["keys"][api_key]["daily_limit"] = 1
            key_store._save()

        # First request should succeed
        resp1 = client.post("/generate", json={
            "schema_type": "transactions",
            "count": 1,
            "locale": "en_US",
        }, headers={"X-API-Key": api_key})
        assert resp1.status_code == 200

        # Second request should be rate limited
        resp2 = client.post("/generate", json={
            "schema_type": "transactions",
            "count": 1,
            "locale": "en_US",
        }, headers={"X-API-Key": api_key})
        assert resp2.status_code == 429
        detail = resp2.json()["detail"]
        assert "rate_limit" in detail.get("error", "")


# ===================================================================
# Key info endpoint
# ===================================================================

class TestKeyInfo:
    def _get_last_key(self):
        from api_keys import key_store
        keys = list(key_store._data["keys"].items())
        return keys[-1][0] if keys else None

    def test_key_info_valid(self):
        client.get("/register")
        api_key = self._get_last_key()
        assert api_key is not None

        resp = client.get(f"/key/{api_key}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tier"] == "free"

    def test_key_info_invalid(self):
        resp = client.get("/key/nonexistent_key_xyz_123")
        assert resp.status_code == 404


# ===================================================================
# Payment endpoints
# ===================================================================

class TestPayment:
    def _get_last_key(self):
        from api_keys import key_store
        keys = list(key_store._data["keys"].items())
        return keys[-1][0] if keys else None

    def test_payment_with_invalid_key(self):
        resp = client.post("/pay", json={
            "api_key": "invalid_key_123",
            "amount": 5.0,
            "currency": "usdt",
        })
        assert resp.status_code == 400

    def test_payment_with_valid_key(self):
        client.get("/register")
        api_key = self._get_last_key()
        assert api_key is not None

        resp = client.post("/pay", json={
            "api_key": api_key,
            "amount": 5.0,
            "currency": "usdt",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["amount"] == 5.0
        assert "manual" in data or "payment_url" in data


# ===================================================================
# Webhook endpoint
# ===================================================================

class TestWebhook:
    def test_webhook_success(self):
        resp = client.post("/webhook/payment", json={
            "type": "payment_finished",
            "payment_id": "test_123",
            "metadata": {"api_key": "test_key"},
        })
        assert resp.status_code == 200


# ===================================================================
# Public endpoints (no key needed)
# ===================================================================

class TestPublicEndpoints:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["api_keys_enabled"] is True

    def test_schemas(self):
        resp = client.get("/schemas")
        assert resp.status_code == 200
        data = resp.json()
        assert "available_schemas" in data
        assert data["total"] > 0
