from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class Locale(str, Enum):
    en_US = "en_US"
    en_GB = "en_GB"
    ru_RU = "ru_RU"
    de_DE = "de_DE"
    fr_FR = "fr_FR"
    es_ES = "es_ES"
    ja_JP = "ja_JP"
    zh_CN = "zh_CN"
    pt_BR = "pt_BR"
    ko_KR = "ko_KR"


class UserType(str, Enum):
    basic = "basic"
    premium = "premium"
    enterprise = "enterprise"


class SchemaType(str, Enum):
    users = "users"
    transactions = "transactions"
    products = "products"
    orders = "orders"
    reviews = "reviews"
    employees = "employees"
    addresses = "addresses"
    vehicles = "vehicles"
    medical_records = "medical_records"
    social_media = "social_media"
    ecommerce = "ecommerce"
    banking = "banking"
    custom = "custom"


# --- Request Models ---

class UserRequest(BaseModel):
    schema_type: SchemaType = SchemaType.users
    count: int = Field(default=10, ge=1, le=10000, description="Number of records to generate")
    locale: Locale = Locale.en_US
    user_type: Optional[UserType] = None
    include_fields: Optional[List[str]] = None
    exclude_fields: Optional[List[str]] = None
    with_relationships: bool = Field(default=False, description="Generate related records")


class TransactionRequest(BaseModel):
    schema_type: SchemaType = SchemaType.transactions
    count: int = Field(default=10, ge=1, le=10000)
    locale: Locale = Locale.en_US
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    currencies: Optional[List[str]] = None
    transaction_types: Optional[List[str]] = None


class ProductRequest(BaseModel):
    schema_type: SchemaType = SchemaType.products
    count: int = Field(default=10, ge=1, le=10000)
    locale: Locale = Locale.en_US
    categories: Optional[List[str]] = None
    price_range: Optional[Dict[str, float]] = None


class OrderRequest(BaseModel):
    schema_type: SchemaType = SchemaType.orders
    count: int = Field(default=10, ge=1, le=10000)
    locale: Locale = Locale.en_US


class ReviewRequest(BaseModel):
    schema_type: SchemaType = SchemaType.reviews
    count: int = Field(default=10, ge=1, le=10000)
    locale: Locale = Locale.en_US
    rating_distribution: Optional[Dict[int, int]] = None


class AddressRequest(BaseModel):
    schema_type: SchemaType = SchemaType.addresses
    count: int = Field(default=10, ge=1, le=10000)
    locale: Locale = Locale.en_US


class VehicleRequest(BaseModel):
    schema_type: SchemaType = SchemaType.vehicles
    count: int = Field(default=10, ge=1, le=10000)
    locale: Locale = Locale.en_US


class EmployeeRequest(BaseModel):
    schema_type: SchemaType = SchemaType.employees
    count: int = Field(default=10, ge=1, le=10000)
    locale: Locale = Locale.en_US
    departments: Optional[List[str]] = None


class MedicalRecordRequest(BaseModel):
    schema_type: SchemaType = SchemaType.medical_records
    count: int = Field(default=10, ge=1, le=10000)
    locale: Locale = Locale.en_US


class SocialMediaRequest(BaseModel):
    schema_type: SchemaType = SchemaType.social_media
    count: int = Field(default=10, ge=1, le=10000)
    locale: Locale = Locale.en_US


class EcommerceRequest(BaseModel):
    schema_type: SchemaType = SchemaType.ecommerce
    count: int = Field(default=10, ge=1, le=10000)
    locale: Locale = Locale.en_US


class BankingRequest(BaseModel):
    schema_type: SchemaType = SchemaType.banking
    count: int = Field(default=10, ge=1, le=10000)
    locale: Locale = Locale.en_US


class CustomSchemaRequest(BaseModel):
    schema_type: SchemaType = SchemaType.custom
    count: int = Field(default=10, ge=1, le=10000)
    locale: Locale = Locale.en_US
    fields: Dict[str, str] = Field(
        ...,
        description="Field definitions: {field_name: type}. Types: name, email, phone, address, city, country, date, company, job, text, number, boolean, currency, price, url, ipv4, uuid, color, product, category, tag"
    )


# --- Unified request using generic model ---

class GenericDataRequest(BaseModel):
    schema_type: SchemaType = SchemaType.users
    count: int = Field(default=10, ge=1, le=10000, description="Number of records to generate")
    locale: Locale = Locale.en_US
    # Common parameters
    include_fields: Optional[List[str]] = None
    exclude_fields: Optional[List[str]] = None
    with_relationships: bool = False
    # Schema-specific overrides
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    currencies: Optional[List[str]] = None
    transaction_types: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    price_range: Optional[Dict[str, float]] = None
    user_type: Optional[str] = None
    departments: Optional[List[str]] = None
    rating_distribution: Optional[Dict[int, int]] = None
    # Custom schema
    fields: Optional[Dict[str, str]] = None


class BulkRequest(BaseModel):
    requests: List[GenericDataRequest] = Field(..., min_length=1, max_length=10)


# --- Response Models ---

class GenerationResponse(BaseModel):
    schema_type: str
    count: int
    locale: str
    data: List[Dict[str, Any]]
    generated_at: str
    request_id: str


class BulkResponse(BaseModel):
    results: List[GenerationResponse]
    total_records: int
    generated_at: str


class SchemaInfo(BaseModel):
    schema_type: str
    description: str
    available_fields: List[str]
    recommended_count_max: int


class SchemasResponse(BaseModel):
    available_schemas: List[SchemaInfo]
    total: int
