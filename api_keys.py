"""API Key & Subscription management system with crypto payment integration."""

import os
import json
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

KEYS_FILE = Path(__file__).parent / "api_keys_db.json"
PAYMENTS_FILE = Path(__file__).parent / "payments_db.json"

# NowPayments configuration
NOWPAYMENTS_API_KEY = os.environ.get("NOWPAYMENTS_API_KEY", "")
NOWPAYMENTS_IPN_SECRET = os.environ.get("NOWPAYMENTS_IPN_SECRET", "")
PAYMENT_ADDRESS = os.environ.get("PAYMENT_ADDRESS", "TFCx2da9FiVX1o7HMcPdKGMsaXpwAWsmWx")  # USDT TRC20

# Pricing & Limits
FREE_DAILY_LIMIT = 100
GROWTH_MONTHLY_LIMIT = 200_000
ENTERPRISE_MONTHLY_LIMIT = -1  # Unlimited

class SubscriptionTier(Enum):
    FREE = "free"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"


class APIKeyStore:
    """File-based API key and subscription storage."""

    def __init__(self, keys_file: Path = KEYS_FILE):
        self.keys_file = keys_file
        self._lock = threading.Lock()
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.keys_file.exists():
            try:
                with open(self.keys_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"keys": {}}
        return {"keys": {}}

    def _save(self):
        with open(self.keys_file, "w") as f:
            json.dump(self._data, f, indent=2)

    def create_key(
        self,
        email: Optional[str] = None,
        tier: str = "free",
        daily_limit: Optional[int] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Create a new API key."""
        key = f"tdg_{secrets.token_urlsafe(32)}"
        now = datetime.now(timezone.utc)

        entry = {
            "key": key,
            "email": email,
            "tier": tier,
            "created_at": now.isoformat(),
            "subscribed_until": None,
            "daily_limit": daily_limit or FREE_DAILY_LIMIT,
            "monthly_limit": GROWTH_MONTHLY_LIMIT if tier == "growth" else ENTERPRISE_MONTHLY_LIMIT,
            "requests_today": 0,
            "requests_this_month": 0,
            "last_request": None,
            "total_requests": 0,
            "is_active": True,
        }

        with self._lock:
            self._data["keys"][key] = entry
            self._save()

        return key, entry

    def verify_key(self, key: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Verify API key and check rate limits."""
        with self._lock:
            entry = self._data["keys"].get(key)

        if not entry or not entry.get("is_active", False):
            return False, None

        now = datetime.now(timezone.utc)

        # Check subscription expiry
        if entry.get("subscribed_until"):
            expires = datetime.fromisoformat(entry["subscribed_until"])
            if expires < now:
                # Downgrade to free if subscription expired
                entry["tier"] = "free"
                entry["subscribed_until"] = None
                entry["monthly_limit"] = None
                entry["daily_limit"] = FREE_DAILY_LIMIT
                with self._lock:
                    self._save()

        # Reset daily counter if new day
        if entry.get("last_request"):
            last = datetime.fromisoformat(entry["last_request"])
            if last.date() != now.date():
                entry["requests_today"] = 0

        # Check daily rate limit
        daily_limit = entry.get("daily_limit", FREE_DAILY_LIMIT)
        if daily_limit > 0 and entry["requests_today"] >= daily_limit:
            return False, entry

        # Increment counter
        with self._lock:
            entry["requests_today"] = entry.get("requests_today", 0) + 1
            entry["requests_this_month"] = entry.get("requests_this_month", 0) + 1
            entry["total_requests"] = entry.get("total_requests", 0) + 1
            entry["last_request"] = now.isoformat()
            self._save()

        return True, entry

    def get_key_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get key information."""
        return self._data["keys"].get(key)

    def upgrade_key(self, key: str, tier: str = "growth") -> bool:
        """Upgrade a key to a subscription tier."""
        with self._lock:
            entry = self._data["keys"].get(key)
            if entry:
                entry["tier"] = tier
                entry["subscribed_until"] = (
                    datetime.now(timezone.utc) + __import__("datetime").timedelta(days=30)
                ).isoformat()
                
                if tier == "growth":
                    entry["monthly_limit"] = GROWTH_MONTHLY_LIMIT
                    entry["daily_limit"] = -1  # Unlimited daily for growth
                elif tier == "enterprise":
                    entry["monthly_limit"] = ENTERPRISE_MONTHLY_LIMIT
                    entry["daily_limit"] = -1

                self._save()
                return True
        return False

    def list_keys(self) -> List[Dict[str, Any]]:
        """List all keys (admin only)."""
        return list(self._data["keys"].values())

# Singleton instance
key_store = APIKeyStore()


class PaymentStore:
    """Store payment records."""

    def __init__(self, payments_file: Path = PAYMENTS_FILE):
        self.payments_file = payments_file
        self._lock = threading.Lock()
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.payments_file.exists():
            try:
                with open(self.payments_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"payments": []}
        return {"payments": []}

    def _save(self):
        with open(self.payments_file, "w") as f:
            json.dump(self._data, f, indent=2)

    def add_payment(
        self,
        payment_id: str,
        email: str,
        api_key: str,
        tier: str,
        amount: float,
        currency: str,
        status: str,
    ) -> None:
        with self._lock:
            self._data["payments"].append({
                "payment_id": payment_id,
                "email": email,
                "api_key": api_key,
                "tier": tier,
                "amount": amount,
                "currency": currency,
                "status": status,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            self._save()

    def mark_paid(self, payment_id: str) -> None:
        with self._lock:
            for p in self._data["payments"]:
                if p["payment_id"] == payment_id:
                    p["status"] = "paid"
                    # Automatically activate subscription
                    key_store.upgrade_key(p["api_key"], p.get("tier", "growth"))
                    break
            self._save()


payment_store = PaymentStore()


def create_payment_link(
    email: str,
    api_key: str,
    amount: float = 99.0,
    currency: str = "usdt",
    tier: str = "growth",
) -> Dict[str, Any]:
    """Create a NowPayments crypto payment link."""
    if not NOWPAYMENTS_API_KEY:
        # Fallback: manual payment address
        return {
            "manual": True,
            "address": PAYMENT_ADDRESS,
            "amount": amount,
            "currency": currency,
            "tier": tier,
            "message": (
                f"💰 Для получения тарифа {tier.upper()} отправьте:\n\n"
                f"Сумма: {amount} {currency}\n"
                f"Сеть: TRC20 (Tron)\n"
                f"Адрес: {PAYMENT_ADDRESS}\n\n"
                f"📧 После оплаты напишите на support@tdg-api.com — "
                f"активируем ваш ключ автоматически."
            ),
        }

    try:
        import requests

        payload = {
            "price_amount": amount,
            "price_currency": "usd",
            "pay_currency": currency,
            "order_id": f"tdg_{tier}_{secrets.token_urlsafe(16)}",
            "ipn_callback_url": f"{os.environ.get('SERVER_URL', '')}/webhook/payment",
            "metadata": {"api_key": api_key, "tier": tier},
        }

        headers = {
            "x-api-key": NOWPAYMENTS_API_KEY,
            "Content-Type": "application/json",
        }

        response = requests.post(
            "https://api.nowpayments.io/v1/pay",
            json=payload,
            headers=headers,
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            payment_store.add_payment(
                payment_id=data.get("pay_id", ""),
                email=email,
                api_key=api_key,
                tier=tier,
                amount=amount,
                currency=currency,
                status="pending",
            )

            return {
                "manual": False,
                "payment_url": data.get("invoice_url", ""),
                "amount": amount,
                "currency": currency,
                "tier": tier,
                "order_id": data.get("order_id"),
            }
    except Exception:
        pass

    # Fallback to manual
    return {
        "manual": True,
        "address": PAYMENT_ADDRESS,
        "amount": amount,
        "currency": currency,
        "tier": tier,
        "message": (
            f"💰 Для получения тарифа {tier.upper()} отправьте:\n\n"
            f"Сумма: {amount} {currency}\n"
            f"Сеть: TRC20 (Tron)\n"
            f"Адрес: {PAYMENT_ADDRESS}\n\n"
            f"📧 После оплаты напишите на support@tdg-api.com — "
            f"активируем ваш ключ автоматически."
        ),
    }


# Webhook handler for NowPayments IPN
def handle_payment_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle NowPayments IPN webhook."""
    if payload.get("type") == "payment_finished":
        payment_id = payload.get("payment_id", "")
        # The tier and api_key are stored in metadata
        metadata = payload.get("metadata", {})
        api_key = metadata.get("api_key", "")
        tier = metadata.get("tier", "growth")

        if payment_id:
            payment_store.mark_paid(payment_id)
            if api_key:
                key_store.upgrade_key(api_key, tier)

        return {"status": "success"}

    return {"status": "received"}
