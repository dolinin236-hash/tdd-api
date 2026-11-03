from __future__ import annotations

import json
import logging
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class _NullableJSONEncoder(json.JSONEncoder):
    """Serialize date, Decimal, and None safely."""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (date,)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

from generator import DataGenerator, SCHEMA_DEFINITIONS
from models import (
    BulkRequest,
    BulkResponse,
    EcommerceRequest,
    GenericDataRequest,
    GenerationResponse,
    BankingRequest,
    CustomSchemaRequest,
    EmployeeRequest,
    AddressRequest,
    VehicleRequest,
    MedicalRecordRequest,
    OrderRequest,
    ProductRequest,
    ReviewRequest,
    SchemaInfo,
    SchemasResponse,
    SocialMediaRequest,
    TransactionRequest,
    UserRequest,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Test Data Generator API",
    description=(
        "Generate realistic, customizable test datasets for development, "
        "QA, and ML training. Supports 12+ data schemas with multi-language "
        "localization and custom field definitions."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

generator = DataGenerator()


# ===================================================================
# Helpers
# ===================================================================

def _to_generation_response(schema_type: str, data, count: int, locale: str, request_id: str) -> GenerationResponse:
    return GenerationResponse(
        schema_type=schema_type,
        count=count,
        locale=locale,
        data=data,
        generated_at=datetime.now(timezone.utc).isoformat(),
        request_id=request_id,
    )


# ===================================================================
# Endpoint: generate
# ===================================================================

@app.post("/generate", response_model=GenerationResponse, summary="Generate test data")
async def generate_data(req: GenericDataRequest) -> JSONResponse:
    """Generate a dataset based on predefined or custom schema."""
    request_id = str(uuid.uuid4())

    try:
        data = generator.generate(
            schema_type=req.schema_type,
            count=req.count,
            locale=req.locale.value if hasattr(req.locale, "value") else req.locale,
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
        headers={"X-Request-ID": request_id},
    )


# ===================================================================
# Endpoint: bulk generate
# ===================================================================

@app.post("/generate/bulk", response_model=BulkResponse, summary="Bulk generate multiple datasets")
async def generate_bulk(req: BulkRequest) -> JSONResponse:
    """Generate multiple datasets in a single request."""
    results = []
    total = 0

    for sub_req in req.requests:
        request_id = str(uuid.uuid4())
        try:
            data = generator.generate(
                schema_type=sub_req.schema_type,
                count=sub_req.count,
                locale=sub_req.locale.value if hasattr(sub_req.locale, "value") else sub_req.locale,
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


# ===================================================================
# Endpoint: schemas
# ===================================================================

@app.get("/schemas", response_model=SchemasResponse, summary="List available schemas")
async def list_schemas() -> SchemasResponse:
    """Get all available data schemas with their fields."""
    schemas = []
    for key, schema in SCHEMA_DEFINITIONS.items():
        schemas.append(SchemaInfo(
            schema_type=key,
            description=schema["description"],
            available_fields=schema["fields"],
            recommended_count_max=10000,
        ))
    return SchemasResponse(available_schemas=schemas, total=len(schemas))


# ===================================================================
# Endpoint: schema info
# ===================================================================

@app.get("/schemas/{schema_type}", summary="Get schema details")
async def get_schema(schema_type: str) -> JSONResponse:
    """Get detailed information about a specific schema."""
    schema = SCHEMA_DEFINITIONS.get(schema_type)
    if not schema:
        available = list(SCHEMA_DEFINITIONS.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Schema '{schema_type}' not found. Available: {available}",
        )
    return JSONResponse(content={
        "schema_type": schema_type,
        "description": schema["description"],
        "available_fields": schema["fields"],
        "recommended_count_max": 10000,
        "usage_example": f"/generate with schema_type={schema_type}&count=10",
    })


# ===================================================================
# Endpoint: health
# ===================================================================

@app.get("/health", summary="Health check")
async def health() -> dict:
    """API health check endpoint."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "uptime_check": "API is running",
        "supported_schemas": len(SCHEMA_DEFINITIONS),
    }


# ===================================================================
# Endpoint: export (convenience)
# ===================================================================

class ExportRequest(BaseModel):
    schema_type: str = "users"
    count: int = 10
    locale: str = "en_US"
    format: str = Query("json", pattern="^(json|csv|excel)$", description="Export format")
    include_fields: Optional[list[str]] = None
    exclude_fields: Optional[list[str]] = None
    fields: Optional[dict[str, str]] = None


@app.post("/export", summary="Generate and export data")
async def export_data(req: ExportRequest) -> JSONResponse:
    """Generate data and optionally export as CSV or Excel."""
    import io

    data = generator.generate(
        schema_type=req.schema_type,
        count=req.count,
        locale=req.locale,
        include_fields=req.include_fields,
        exclude_fields=req.exclude_fields,
        custom_fields=req.fields,
    )

    if not data:
        raise HTTPException(status_code=400, detail="No data generated")

    fmt = req.format.lower()

    if fmt == "csv":
        try:
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
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"CSV export failed: {exc}")

    if fmt == "excel":
        try:
            import pandas as pd
            from fastapi.responses import Response
            df = pd.DataFrame(data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            output.seek(0)
            return Response(
                content=output.getvalue(),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=export.xlsx"},
            )
        except ImportError:
            raise HTTPException(status_code=500, detail="pandas and openpyxl required for Excel export. Install: pip install pandas openpyxl")

    # Default: JSON
    return JSONResponse(
        content=json.loads(json.dumps({
            "format": "json",
            "count": len(data),
            "data": data,
        }, cls=_NullableJSONEncoder)),
    )


# ===================================================================
# Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
# ===================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
