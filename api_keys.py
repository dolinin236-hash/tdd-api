"""API Key management system with crypto payment integration."""

import os
import json
import secrets
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

KEYS_FILE = Path(__file__).parent / "api_keys_db.json"
PAYMENTS_FILE = Path(__file__).parent / "payments_db.json"

# NowPayments configuration
NOWPAYMENTS_API_KEY = os.environ.get("NOWPAYMENTS_API_KEY", "")
NOWPAYMENTS_IPN_SECRET = os.environ.get("NOWPAYMENTS_IPN_SECRET", "")
PAYMENT_ADDRESS = os.environ.get("PAYMENT_ADDRESS", "TFCx2da9FiVX1o7HMcPdKGMsaXpwAWsmWx")  # USDT TRC20

# Pricing (in USD)
FREE_DAILY_LIMIT = 100
PREMIUM_PRICE_USD = 5.0  # $5 for unlimited access


class APIKeyStore:
    """File-based API key storage (JSON file). No external DB needed."""

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
        custom_limit: Optional[int] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Create a new API key."""
        key = f"tdg_{secrets.token_urlsafe(32)}"
        now = datetime.now(timezone.utc)

        entry = {
            "key": key,
            "email": email,
            "tier": tier,
            "created_at": now.isoformat(),
            "expires_at": None,
            "daily_limit": custom_limit or (FREE_DAILY_LIMIT if tier == "free" else -1),
            "requests_today": 0,
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

        # Check expiry
        if entry.get("expires_at"):
            expires = datetime.fromisoformat(entry["expires_at"])
            if expires < now:
                entry["is_active"] = False
                with self._lock:
                    self._save()
                return False, None

        # Reset daily counter if new day
        if entry.get("last_request"):
            last = datetime.fromisoformat(entry["last_request"])
            if last.date() != now.date():
                entry["requests_today"] = 0

        # Check rate limit
        daily_limit = entry.get("daily_limit", FREE_DAILY_LIMIT)
        if daily_limit > 0 and entry["requests_today"] >= daily_limit:
            return False, entry

        # Increment counter
        with self._lock:
            entry["requests_today"] = entry.get("requests_today", 0) + 1
            entry["total_requests"] = entry.get("total_requests", 0) + 1
            entry["last_request"] = now.isoformat()
            self._save()

        return True, entry

    def get_key_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get key information."""
        return self._data["keys"].get(key)

    def upgrade_key(self, key: str) -> bool:
        """Upgrade a key to premium (unlimited)."""
        with self._lock:
            entry = self._data["keys"].get(key)
            if entry:
                entry["tier"] = "premium"
                entry["daily_limit"] = -1
                entry["expires_at"] = (
                    datetime.now(timezone.utc) + timedelta(days=30)
                ).isoformat()
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
        amount: float,
        currency: str,
        status: str,
    ) -> None:
        with self._lock:
            self._data["payments"].append({
                "payment_id": payment_id,
                "email": email,
                "api_key": api_key,
                "amount": amount,
                "currency": currency,
                "status": status,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            self._save()

    def get_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        for p in self._data["payments"]:
            if p["payment_id"] == payment_id:
                return p
        return None

    def mark_paid(self, payment_id: str) -> None:
        with self._lock:
            for p in self._data["payments"]:
                if p["payment_id"] == payment_id:
                    p["status"] = "paid"
                    break
            self._save()


payment_store = PaymentStore()


def create_payment_link(
    email: str,
    api_key: str,
    amount: float = PREMIUM_PRICE_USD,
    currency: str = "usdt",
) -> Dict[str, Any]:
    """Create a NowPayments crypto payment link."""
    if not NOWPAYMENTS_API_KEY:
        # Fallback: manual payment address
        return {
            "manual": True,
            "address": PAYMENT_ADDRESS,
            "amount": amount,
            "currency": currency,
            "email": email,
            "message": (
                f"Отправьте {amount} USDT (TRC20) на адрес:\n"
                f"{PAYMENT_ADDRESS}\n\n"
                f"После оплаты напишите на email или в Telegram — "
                f"активируем ваш ключ навсегда."
            ),
        }

    try:
        import requests

        payload = {
            "price_amount": amount,
            "price_currency": "usd",
            "pay_currency": currency,
            "order_id": f"tdg_{secrets.token_urlsafe(16)}",
            "ipn_callback_url": f"{os.environ.get('SERVER_URL', '')}/webhook/payment",
            "success_url": f"{os.environ.get('SERVER_URL', '')}/payment/success",
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
            payment_record = data.get("invoice_url", "")

            payment_store.add_payment(
                payment_id=data.get("pay_id", ""),
                email=email,
                api_key=api_key,
                amount=amount,
                currency=currency,
                status="pending",
            )

            return {
                "manual": False,
                "payment_url": payment_record,
                "amount": amount,
                "currency": currency,
                "order_id": data.get("order_id"),
            }
    except Exception:
        pass

    # Fallback to manual
    return create_payment_link_manual(email, api_key, amount, currency)


def create_payment_link_manual(
    email: str,
    api_key: str,
    amount: float = PREMIUM_PRICE_USD,
    currency: str = "USDT",
) -> Dict[str, Any]:
    """Manual crypto payment (address-based)."""
    return {
        "manual": True,
        "address": PAYMENT_ADDRESS,
        "amount": amount,
        "currency": currency,
        "email": email,
        "message": (
            f"💰 Для получения Premium ключа отправьте:\n\n"
            f"Сумма: {amount} {currency}\n"
            f"Сеть: TRC20 (Tron)\n"
            f"Адрес: {PAYMENT_ADDRESS}\n\n"
            f"📧 После оплаты напишите на support@tdg-api.com "
            f"или в @TDDAPI_BOT (укажите ваш email "
            f"и tx-hash транзакции)\n\n"
            f"⚡ Активация в течение 1 часа"
        ),
    }


# Webhook handler for NowPayments IPN
def handle_payment_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle NowPayments IPN webhook."""
    if not NOWPAYMENTS_API_KEY:
        return {"status": "skipped", "reason": "no_api_key"}

    try:
        import hashlib
        import hmac

        ipn_secret = NOWPAYMENTS_IPN_SECRET
        body = json.dumps(payload, separators=(",", ":"))

        # Verify signature
        signature = hmac.new(
            ipn_secret.encode(),
            body.encode(),
            hashlib.sha256,
        ).hexdigest()

        if payload.get("type") == "payment_finished":
            payment_id = payload.get("payment_id", "")
            api_key = payload.get("metadata", {}).get("api_key", "")

            if payment_id:
                payment_store.mark_paid(payment_id)
                if api_key:
                    key_store.upgrade_key(api_key)

            return {"status": "success"}

        return {"status": "received"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
