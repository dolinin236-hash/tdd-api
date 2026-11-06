from __future__ import annotations

import json
import logging
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional, Any

from fastapi import FastAPI, HTTPException, Query, Header, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from api_keys import key_store, create_payment_link, handle_payment_webhook, SubscriptionTier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Test Data Generator API",
    description=(
        "Generate realistic, customizable test datasets for development, "
        "QA, and ML training. Supports 12+ data schemas with multi-language "
        "localization and custom field definitions."
    ),
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# ===================================================================
# Landing Page & Marketing
# ===================================================================

@app.get("/")
async def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register", summary="Register for free API key")
async def register(request: Request, email: Optional[str] = None):
    """Free tier registration."""
    key, info = key_store.create_key(
        email=email,
        tier="free",
    )
    return JSONResponse(content={
        "message": "API Key created successfully!",
        "api_key": key,  # In production, this should be sent via email
        "tier": info["tier"],
        "daily_limit": info["daily_limit"],
    })

# ===================================================================
# Protected Endpoints (API key required)
# ===================================================================

def _require_api_key(x_api_key: Optional[str]):
    """Validate API key. Returns (is_valid, key_info)."""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "api_key_required",
                "message": "API Key required. Register at /register to get one.",
                "register_url": "/register",
            },
        )

    from api_keys import key_store
    is_valid, info = key_store.verify_key(x_api_key)
    if not is_valid:
        if info:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": f"Daily limit exceeded ({info.get('daily_limit', 0)} req/day). Upgrade to Premium for unlimited access.",
                    "upgrade_url": "/pay",
                },
            )
        raise HTTPException(
            status_code=403,
            detail={
                "error": "invalid_key",
                "message": "Invalid API key. Register at /register",
            },
        )
    return True, info

@app.post("/generate", summary="Generate test data")
async def generate_data(
    req: dict,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> JSONResponse:
    _require_api_key(x_api_key)
    request_id = str(uuid.uuid4())

    from generator import DataGenerator
    gen = DataGenerator()
    try:
        data = gen.generate(
            schema_type=req["schema_type"],
            count=req["count"],
            locale=req["locale"],
            include_fields=req.get("include_fields"),
            exclude_fields=req.get("exclude_fields"),
            custom_fields=req.get("fields"),
        )
    except Exception as exc:
        logger.exception("Data generation failed")
        raise HTTPException(status_code=400, detail=str(exc))

    return JSONResponse(
        content={
            "schema_type": req["schema_type"],
            "count": len(data),
            "locale": req["locale"],
            "data": data,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )

@app.post("/generate/bulk", summary="Bulk generate")
async def generate_bulk(
    req: dict,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> JSONResponse:
    _require_api_key(x_api_key)
    results = []
    total = 0

    from generator import DataGenerator
    gen = DataGenerator()
    for sub_req in req.get("requests", []):
        request_id = str(uuid.uuid4())
        try:
            data = gen.generate(
                schema_type=sub_req["schema_type"],
                count=sub_req["count"],
                locale=sub_req["locale"],
                include_fields=sub_req.get("include_fields"),
                exclude_fields=sub_req.get("exclude_fields"),
                custom_fields=sub_req.get("fields"),
            )
            results.append({
                "schema_type": sub_req["schema_type"],
                "count": len(data),
                "locale": sub_req["locale"],
                "data": data,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "request_id": request_id,
            })
            total += len(data)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Schema '{sub_req.get('schema_type')}' failed: {exc}")

    return JSONResponse(content={
        "results": results,
        "total_records": total,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    })

# ===================================================================
# Public Endpoints (no key needed)
# ===================================================================

@app.get("/health", summary="Health check")
async def health() -> dict:
    return {
        "status": "ok",
        "version": "4.0.0",
        "api_keys_enabled": True,
        "crypto_payments": True,
    }

@app.get("/schemas", summary="List available schemas")
async def list_schemas():
    from generator import SCHEMA_DEFINITIONS
    schemas = []
    for key, schema in SCHEMA_DEFINITIONS.items():
        schemas.append({
            "schema_type": key,
            "description": schema["description"],
            "available_fields": schema["fields"],
            "recommended_count_max": 10000,
        })
    return {"available_schemas": schemas, "total": len(schemas)}

# ===================================================================
# Payment & Subscription Endpoints
# ===================================================================

@app.post("/pay", summary="Select payment tier")
async def select_payment_tier(req: dict):
    """Return payment instructions for a specific tier."""
    api_key = req.get("api_key")
    tier_name = req.get("tier", "growth")
    
    # Check if key exists
    key_info = key_store.get_key_info(api_key)
    if not key_info:
        raise HTTPException(status_code=400, detail="Invalid API key")

    # Map tier names to prices
    pricing = {
        "growth": {"amount": 99.0, "currency": "usdt", "period": "month", "limit": 200000},
        "enterprise": {"amount": 299.0, "currency": "usdt", "period": "month", "limit": -1},
    }

    tier_data = pricing.get(tier_name)
    if not tier_data:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {tier_name}")

    # Generate crypto invoice
    payment = create_payment_link(
        email=key_info.get("email"),
        api_key=api_key,
        amount=tier_data["amount"],
        currency=tier_data["currency"],
    )

    return JSONResponse(content={
        "tier": tier_name,
        "amount": tier_data["amount"],
        "currency": tier_data["currency"],
        "payment_instructions": payment.get("message"),
        "manual": payment.get("manual"),
        "address": payment.get("address"),
        "webhook_url": "/webhook/payment",
    })

@app.post("/webhook/payment", summary="Crypto payment webhook")
async def payment_webhook(request: Request):
    """Handle crypto payment webhook."""
    try:
        payload = await request.json()
        result = handle_payment_webhook(payload)
        return result
    except Exception as exc:
        logger.exception("Webhook error")
        return {"status": "error", "message": str(exc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)