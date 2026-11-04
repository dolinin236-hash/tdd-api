from __future__ import annotations

import json
import logging
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional, Any

from fastapi import FastAPI, HTTPException, Query, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api_keys import key_store, create_payment_link, handle_payment_webhook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Test Data Generator API",
    description=(
        "Generate realistic, customizable test datasets for development, "
        "QA, and ML training. Supports 12+ data schemas with multi-language "
        "localization and custom field definitions."
    ),
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ===================================================================
# Request/Response Models
# ===================================================================

class GenericDataRequest(BaseModel):
    schema_type: str
    count: int = Query(default=10, ge=1, le=10000, description="Number of records")
    locale: str = "en_US"
    include_fields: Optional[list[str]] = None
    exclude_fields: Optional[list[str]] = None
    fields: Optional[dict[str, str]] = None

class BulkRequest(BaseModel):
    requests: list[GenericDataRequest]

class GenerationResponse(BaseModel):
    schema_type: str
    count: int
    locale: str
    data: list[dict[str, Any]]
    generated_at: str
    request_id: str

class BulkResponse(BaseModel):
    results: list[GenerationResponse]
    total_records: int
    generated_at: str

class SchemaInfo(BaseModel):
    schema_type: str
    description: str
    available_fields: list[str]
    recommended_count_max: int

class SchemasResponse(BaseModel):
    available_schemas: list[SchemaInfo]
    total: int

class RegisterRequest(BaseModel):
    email: Optional[str] = None

class PaymentRequest(BaseModel):
    api_key: str
    amount: float = 5.0
    currency: str = "usdt"

class KeyInfoResponse(BaseModel):
    tier: str
    daily_limit: int
    requests_today: int
    total_requests: int
    is_active: bool
    expires_at: Optional[str] = None

class PaymentInfoResponse(BaseModel):
    payment_url: Optional[str] = None
    manual: bool
    address: Optional[str] = None
    amount: float
    currency: str
    message: Optional[str] = None

# ===================================================================
# Helpers
# ===================================================================

class _NullableJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (date,)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def _to_generation_response(schema_type: str, data, count: int, locale: str, request_id: str) -> GenerationResponse:
    return GenerationResponse(
        schema_type=schema_type,
        count=count,
        locale=locale,
        data=data,
        generated_at=datetime.now(timezone.utc).isoformat(),
        request_id=request_id,
    )

def _require_api_key(x_api_key: Optional[str]) -> tuple[bool, dict[str, Any]]:
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
                    "message": f"Daily limit exceeded. Upgrade to Premium for unlimited access.",
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

# ===================================================================
# Public Endpoints (no API key needed)
# ===================================================================

@app.get("/health", summary="Health check")
async def health() -> dict:
    return {
        "status": "ok",
        "version": "3.0.0",
        "api_keys_enabled": True,
        "crypto_payments": True,
    }

@app.get("/schemas", response_model=SchemasResponse)
async def list_schemas() -> SchemasResponse:
    from generator import SCHEMA_DEFINITIONS
    schemas = []
    for key, schema in SCHEMA_DEFINITIONS.items():
        schemas.append(SchemaInfo(
            schema_type=key,
            description=schema["description"],
            available_fields=schema["fields"],
            recommended_count_max=10000,
        ))
    return SchemasResponse(available_schemas=schemas, total=len(schemas))

@app.get("/register", summary="Register for free API key", response_model=KeyInfoResponse)
async def register(req: Optional[RegisterRequest] = None):
    """Get a free API key with 100 requests/day."""
    from api_keys import key_store
    key, info = key_store.create_key(
        email=req.email if req else None,
        tier="free",
    )
    return KeyInfoResponse(
        tier=info["tier"],
        daily_limit=info["daily_limit"],
        requests_today=info["requests_today"],
        total_requests=info["total_requests"],
        is_active=info["is_active"],
        expires_at=info.get("expires_at"),
    )

# ===================================================================
# Protected Endpoints (API key required)
# ===================================================================

@app.post("/generate", response_model=GenerationResponse, summary="Generate test data")
async def generate_data(
    req: GenericDataRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> JSONResponse:
    _require_api_key(x_api_key)
    request_id = str(uuid.uuid4())

    from generator import DataGenerator
    gen = DataGenerator()
    try:
        data = gen.generate(
            schema_type=req.schema_type,
            count=req.count,
            locale=req.locale,
            include_fields=req.include_fields,
            exclude_fields=req.exclude_fields,
            custom_fields=req.fields,
        )
    except Exception as exc:
        logger.exception("Data generation failed")
        raise HTTPException(status_code=400, detail=str(exc))

    resp = _to_generation_response(req.schema_type, data, req.count, req.locale, request_id)
    return JSONResponse(
        content=json.loads(json.dumps(resp.model_dump(), cls=_NullableJSONEncoder)),
        headers={
            "X-Request-ID": request_id,
            "X-API-Key-Info": json.dumps({
                "tier": "premium" if x_api_key and x_api_key.startswith("tdg_premium_") else "free",
                "requests_today": key_store.get_key_info(x_api_key or "")["requests_today"] if x_api_key else 0,
            }),
        },
    )

@app.post("/generate/bulk", response_model=BulkResponse, summary="Bulk generate")
async def generate_bulk(
    req: BulkRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> JSONResponse:
    _require_api_key(x_api_key)
    results = []
    total = 0

    from generator import DataGenerator
    gen = DataGenerator()
    for sub_req in req.requests:
        request_id = str(uuid.uuid4())
        try:
            data = gen.generate(
                schema_type=sub_req.schema_type,
                count=sub_req.count,
                locale=sub_req.locale,
                include_fields=sub_req.include_fields,
                exclude_fields=sub_req.exclude_fields,
                custom_fields=sub_req.fields,
            )
            results.append(_to_generation_response(sub_req.schema_type, data, sub_req.count, sub_req.locale, request_id))
            total += len(data)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Schema '{sub_req.schema_type}' failed: {exc}")

    return JSONResponse(
        content=json.loads(
            json.dumps(
                BulkResponse(results=results, total_records=total, generated_at=datetime.now(timezone.utc).isoformat()).model_dump(),
                cls=_NullableJSONEncoder,
            )
        ),
    )

@app.post("/export", summary="Export data (CSV/Excel)")
async def export_data(
    req: GenericDataRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    format: str = Query("json", pattern="^(json|csv)$", description="Export format"),
) -> JSONResponse:
    _require_api_key(x_api_key)
    import io

    from generator import DataGenerator
    gen = DataGenerator()
    data = gen.generate(
        schema_type=req.schema_type,
        count=req.count,
        locale=req.locale,
        include_fields=req.include_fields,
        exclude_fields=req.exclude_fields,
        custom_fields=req.fields,
    )

    if not data:
        raise HTTPException(status_code=400, detail="No data generated")

    fmt = format.lower()
    if fmt == "csv":
        import csv
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        output.seek(0)
        return JSONResponse(
            content={"format": "csv", "data": output.getvalue()},
            headers={"Content-Disposition": "attachment; filename=export.csv"},
        )

    return JSONResponse(
        content=json.loads(json.dumps({
            "format": "json",
            "count": len(data),
            "data": data,
        }, cls=_NullableJSONEncoder)),
    )

# ===================================================================
# Payment Endpoints
# ===================================================================

@app.post("/pay", summary="Create crypto payment for Premium upgrade", response_model=PaymentInfoResponse)
async def create_payment(req: PaymentRequest) -> PaymentInfoResponse:
    """Generate crypto payment link to upgrade to Premium."""
    from api_keys import key_store, create_payment_link
    key_info = key_store.get_key_info(req.api_key)
    if not key_info or not key_info.get("is_active"):
        raise HTTPException(status_code=400, detail="Invalid or expired API key")

    payment = create_payment_link(
        email=key_info.get("email", ""),
        api_key=req.api_key,
        amount=req.amount,
        currency=req.currency,
    )

    return PaymentInfoResponse(
        payment_url=payment.get("payment_url"),
        manual=payment.get("manual", False),
        address=payment.get("address"),
        amount=payment.get("amount"),
        currency=payment.get("currency"),
        message=payment.get("message"),
    )

@app.get("/key/{api_key}", summary="Get API key info", response_model=KeyInfoResponse)
async def get_key_info(api_key: str) -> KeyInfoResponse:
    info = key_store.get_key_info(api_key)
    if not info:
        raise HTTPException(status_code=404, detail="API key not found")
    return KeyInfoResponse(
        tier=info["tier"],
        daily_limit=info["daily_limit"],
        requests_today=info["requests_today"],
        total_requests=info["total_requests"],
        is_active=info["is_active"],
        expires_at=info.get("expires_at"),
    )

@app.post("/webhook/payment", summary="NowPayments webhook handler")
async def payment_webhook(request: Request):
    """Handle crypto payment webhook."""
    try:
        payload = await request.json()
        result = handle_payment_webhook(payload)
        return result
    except Exception as exc:
        logger.exception("Webhook error")
        return {"status": "error", "message": str(exc)}

# ===================================================================
# Run: uvicorn main:app --host 0.0.0.0 --port 8000
# ===================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
