from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from faker import Faker


# ---------------------------------------------------------------------------
# Field resolver mapping: type string -> faker method / custom logic
# ---------------------------------------------------------------------------

FIELD_RESOLVERS: Dict[str, List[str]] = {
    "name": ["name"],
    "email": ["email"],
    "phone": ["phone_number"],
    "address": ["address"],
    "street_address": ["street_address"],
    "city": ["city"],
    "state": ["state"],
    "country": ["country"],
    "zipcode": ["zipcode"],
    "postcode": ["zipcode"],
    "latitude": ["latitude"],
    "longitude": ["longitude"],
    "company": ["company"],
    "job": ["job"],
    "text": ["text", 200],
    "sentence": ["sentence"],
    "paragraph": ["paragraph"],
    "word": ["word"],
    "number": ["random_int", 1, 999999],
    "integer": ["random_int", 1, 999999],
    "float": ["random_float", 0, 99999, 2],
    "boolean": ["boolean"],
    "currency": ["currency_name"],
    "price": ["random_int", 1, 999999],
    "url": ["uri"],
    "domain": ["uri"],
    "ipv4": ["ipv4"],
    "ipv6": ["ipv6"],
    "uuid": ["uuid4"],
    "color": ["color"],
    "date": ["date"],
    "date_time": ["date_time"],
    "time": ["time"],
    "datetime": ["date_time"],
    "product": ["product_name"],
    "category": ["product_category"],
    "tag": ["word"],
    "username": ["username"],
    "password": ["password"],
    "avatar": ["image_url"],
    "bio": ["text", 500],
    "company_prefix": ["company_prefix"],
    "company_suffix": ["company_suffix"],
    "ssn": ["ssn"],
    "bank": ["bank_country"],
    "iban": ["iban"],
    "bic": ["bic"],
    "credit_card": ["credit_card_number"],
    "credit_card_expiry": ["credit_card_expire"],
    "credit_card_provider": ["credit_card_provider"],
    "gender": ["sex"],
    "mac_address": ["mac_address"],
    "user_agent": ["user_agent"],
    "firefox": ["firefox"],
    "chrome": ["chrome"],
    "language": ["language_name"],
    "timezone": ["timezone"],
    "file_name": ["file_name"],
    "file_ext": ["file_extension"],
    "mime_type": ["mime_type"],
    "image_path": ["image_url"],
    "slug": ["word"],
}


def _resolve_faker(fake: Faker, field_type: str, *args: Any, **kwargs: Any) -> Any:
    """Resolve a field type string to a faker method and return a value."""
    resolver = FIELD_RESOLVERS.get(field_type)
    if not resolver:
        # Try direct faker method
        method = getattr(fake, field_type, None)
        if method and callable(method):
            try:
                return method(*args, **kwargs)
            except Exception:
                return fake.text(50)
        return f"_{field_type}_value"

    method_name = resolver[0]
    method = getattr(fake, method_name, None)
    if method and callable(method):
        try:
            return method(*resolver[1:], **kwargs)
        except Exception:
            return f"_{method_name}_value"
    return f"_{method_name}_value"


# ---------------------------------------------------------------------------
# Predefined schemas
# ---------------------------------------------------------------------------

SCHEMA_DEFINITIONS = {
    "users": {
        "description": "User profiles with authentication and contact data",
        "fields": [
            "id", "name", "email", "username", "password", "phone",
            "avatar", "bio", "gender", "date_of_birth", "company", "job",
            "address", "city", "state", "country", "zipcode",
            "website", "ip_address", "language", "timezone",
            "is_active", "created_at", "updated_at", "last_login",
            "subscription_plan", "profile_views", "posts_count",
        ],
    },
    "transactions": {
        "description": "Financial transactions with payment details",
        "fields": [
            "transaction_id", "type", "amount", "currency",
            "from_account", "to_account", "sender_name", "receiver_name",
            "status", "method", "description", "category", "tags",
            "timestamp", "reference", "fee", "balance_after",
            "country", "city", "ip_address",
        ],
    },
    "products": {
        "description": "Product catalog with pricing and inventory",
        "fields": [
            "id", "name", "description", "category", "price", "compare_at_price",
            "cost", "weight", "sku", "barcode", "brand", "manufacturer",
            "rating", "reviews_count", "stock_quantity", "in_stock",
            "images", "tags", "variants", "created_at", "updated_at",
            "supplier", "warehouse_location",
        ],
    },
    "orders": {
        "description": "E-commerce orders with line items",
        "fields": [
            "order_id", "status", "customer_id", "customer_name", "customer_email",
            "items", "subtotal", "tax", "shipping", "total",
            "payment_method", "shipping_method", "tracking_number",
            "shipping_address", "billing_address", "notes",
            "created_at", "updated_at", "currency",
        ],
    },
    "reviews": {
        "description": "Product and service reviews with ratings",
        "fields": [
            "id", "user_id", "user_name", "product_id", "product_name",
            "rating", "title", "body", "verified_purchase", "helpful_count",
            "unhelpful_count", "images", "response", "created_at",
            "country", "language",
        ],
    },
    "employees": {
        "description": "Employee records with HR data",
        "fields": [
            "id", "first_name", "last_name", "full_name", "email", "phone",
            "department", "title", "level", "salary", "hire_date",
            "termination_date", "manager", "address", "city", "country",
            "skills", "education", "emergency_contact", "ssn",
            "is_active", "performance_score", "years_of_service",
        ],
    },
    "addresses": {
        "description": "Addresses in various international formats",
        "fields": [
            "id", "street", "city", "state", "country", "zipcode",
            "latitude", "longitude", "full_address", "address_type",
            "company_name", "apartment", "floor", "building",
        ],
    },
    "vehicles": {
        "description": "Vehicle registry with specifications",
        "fields": [
            "id", "make", "model", "year", "color", "body_type",
            "fuel_type", "transmission", "engine_size", "horsepower",
            "mileage", "price", "vin", "license_plate", "country",
            "owner_name", "registration_date", "insurance_type",
        ],
    },
    "medical_records": {
        "description": "Anonymized medical records (HIPAA-style)",
        "fields": [
            "patient_id", "patient_name", "date_of_birth", "gender",
            "blood_type", "height", "weight", "bmi", "blood_pressure",
            "heart_rate", "temperature", "diagnosis", "medications",
            "allergies", "doctor_name", "department", "admission_date",
            "discharge_date", "insurance_id", "status",
        ],
    },
    "social_media": {
        "description": "Social media profiles and posts",
        "fields": [
            "user_id", "username", "display_name", "bio", "avatar",
            "followers", "following", "posts_count", "verified",
            "email", "phone", "location", "website",
            "joined_date", "posts", "hashtags", "likes_received",
            "comments_received", "engagement_rate",
        ],
    },
    "ecommerce": {
        "description": "Full e-commerce dataset: products + orders + customers",
        "fields": [
            "customer_id", "customer_name", "customer_email", "customer_phone",
            "customer_address", "customer_city", "customer_country",
            "product_id", "product_name", "product_category", "product_price",
            "quantity", "total", "order_id", "order_status", "payment_method",
            "shipping_method", "order_date", "discount", "currency",
            "rating", "review",
        ],
    },
    "banking": {
        "description": "Banking data with accounts, transactions, cards",
        "fields": [
            "account_id", "account_type", "account_holder", "customer_id",
            "balance", "credit_limit", "interest_rate", "routing_number",
            "iban", "swift_code", "bic",
            "transactions", "debit_card_number", "credit_card_number",
            "card_expiry", "cvv", "pin",
            "loan_id", "loan_amount", "loan_type", "loan_status",
            "monthly_payment", "branch", "branch_manager",
        ],
    },
}


# Additional fields that need special handling
SPECIAL_FIELDS = {
    "date_of_birth": lambda fake: fake.date_of_birth(minimum_age=18, maximum_age=70),
    "is_active": lambda fake: fake.boolean(70),
    "in_stock": lambda fake: fake.boolean(80),
    "verified_purchase": lambda fake: fake.boolean(60),
    "verified": lambda fake: fake.boolean(10),
    "tags": lambda fake: [fake.word() for _ in range(fake.random_int(2, 5))],
    "category": lambda fake: fake.random_element(["Electronics", "Clothing", "Books", "Home", "Sports", "Toys", "Food", "Beauty", "Automotive", "Health"]),
    "department": lambda fake: fake.random_element(["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Support", "Legal", "Research"]),
    "title": lambda fake: fake.random_element(
        ["Junior", "Mid", "Senior", "Lead", "Principal", "Manager", "Director", "VP", "CTO", "CEO"]
    ),
    "level": lambda fake: fake.random_element(["L3", "L4", "L5", "L6", "L7"]),
    "subscription_plan": lambda fake: fake.random_element(["free", "basic", "pro", "enterprise"]),
    "id": lambda fake: f"USR-{uuid.uuid4().hex[:12]}",
    "username": lambda fake: fake.user_name(),
    "gender": lambda fake: fake.random_element(["Male", "Female", "Other"]),
    "website": lambda fake: fake.uri(),
    "ip_address": lambda fake: fake.ipv4(),
    "created_at": lambda fake: fake.past_date().isoformat(),
    "updated_at": lambda fake: fake.past_date().isoformat(),
    "last_login": lambda fake: fake.past_datetime().isoformat(),
    "profile_views": lambda fake: fake.random_int(0, 50000),
    "posts_count": lambda fake: fake.random_int(0, 5000),
    "state": lambda fake: fake.random_element(["California", "New York", "Texas", "Florida", "Illinois", "Washington", "London", "Moscow", "Berlin", "Paris"]),
    "zipcode": lambda fake: fake.postcode(),
    "transaction_id": lambda fake: f"TXN-{uuid.uuid4().hex[:12].upper()}",
    "order_id": lambda fake: f"ORD-{fake.random_int(100000, 999999)}",
    "sku": lambda fake: f"SKU-{uuid.uuid4().hex[:8].upper()}",
    "vin": lambda fake: uuid.uuid4().hex[:17].upper(),
    "license_plate": lambda fake: f"{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}{fake.random_int(1000, 9999)}",
    "credit_card_number": lambda fake: fake.credit_card_number(card_type=None),
    "credit_card_expiry": lambda fake: fake.credit_card_expire(),
    "products": lambda fake: [{"product_id": f"PRD-{uuid.uuid4().hex[:8]}", "name": fake.word().capitalize(), "quantity": fake.random_int(1, 5), "price": round(fake.random_int(10, 999), 2)} for _ in range(fake.random_int(1, 4))],
    "items": lambda fake: [{"product_id": f"PRD-{uuid.uuid4().hex[:8]}", "name": fake.word().capitalize(), "quantity": fake.random_int(1, 3), "unit_price": round(fake.random_int(10, 500), 2)} for _ in range(fake.random_int(1, 5))],
    "transactions": lambda fake: [{"transaction_id": f"TXN-{uuid.uuid4().hex[:8].upper()}", "type": fake.random_element(["deposit", "withdrawal", "transfer", "payment"]), "amount": round(fake.random_int(1000, 1000000) / 100, 2), "date": fake.past_date().isoformat()} for _ in range(fake.random_int(1, 5))],
    "posts": lambda fake: [{"id": f"PST-{uuid.uuid4().hex[:6]}", "title": fake.sentence(), "body": fake.paragraph(), "likes": fake.random_int(0, 5000), "comments": fake.random_int(0, 200), "date": fake.past_date().isoformat()} for _ in range(fake.random_int(1, 10))],
    "images": lambda fake: [fake.image_url() for _ in range(fake.random_int(1, 3))],
    "medications": lambda fake: [fake.word() for _ in range(fake.random_int(1, 4))],
    "allergies": lambda fake: [fake.word() for _ in range(fake.random_int(0, 3))],
    "skills": lambda fake: [fake.word() for _ in range(fake.random_int(3, 8))],
    "variations": lambda fake: [{"size": fake.random_element(["S", "M", "L", "XL"]), "color": fake.color_name(), "price": round(fake.random_int(10, 500), 2)} for _ in range(fake.random_int(2, 4))],
    "variants": lambda fake: [{"size": fake.random_element(["S", "M", "L", "XL", "XXL"]), "color": fake.color_name(), "stock": fake.random_int(0, 100)} for _ in range(fake.random_int(2, 4))],
}


class DataGenerator:
    """Core data generation engine."""

    def __init__(self):
        self._fakers: Dict[str, Faker] = {}

    def _get_fake(self, locale: str) -> Faker:
        if locale not in self._fakers:
            self._fakers[locale] = Faker(locale)
        return self._fakers[locale]

    # ------------------------------------------------------------------
    # Core generation
    # ------------------------------------------------------------------

    def generate(
        self,
        schema_type: str,
        count: int,
        locale: str,
        include_fields: Optional[List[str]] = None,
        exclude_fields: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        fake = self._get_fake(locale)

        # Determine fields to generate
        if custom_fields:
            fields = list(custom_fields.keys())
        else:
            schema = SCHEMA_DEFINITIONS.get(schema_type)
            if not schema:
                # Fallback: random fields
                fields = self._random_fields(fake, count)
            else:
                fields = schema["fields"]

            if include_fields:
                fields = [f for f in fields if f in include_fields]
            if exclude_fields:
                fields = [f for f in fields if f not in exclude_fields]

        records: List[Dict[str, Any]] = []
        for _ in range(count):
            record = self._generate_record(fake, fields, custom_fields, schema_type, **kwargs)
            records.append(record)

        return records

    # ------------------------------------------------------------------
    # Single record
    # ------------------------------------------------------------------

    def _generate_record(
        self,
        fake: Faker,
        fields: List[str],
        custom_fields: Optional[Dict[str, str]],
        schema_type: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        record: Dict[str, Any] = {}

        for field in fields:
            if custom_fields and field in custom_fields:
                field_type = custom_fields[field]
                record[field] = _resolve_faker(fake, field_type)
            elif field in SPECIAL_FIELDS:
                record[field] = SPECIAL_FIELDS[field](fake)
            else:
                record[field] = _resolve_faker(fake, field)

        return record

    # ------------------------------------------------------------------
    # Random fields fallback
    # ------------------------------------------------------------------

    @staticmethod
    def _random_fields(fake: Faker, count: int) -> List[str]:
        all_fields = list(SPECIAL_FIELDS.keys())
        return [fake.random_element(all_fields) for _ in range(count)]

    # ------------------------------------------------------------------
    # Schema info
    # ------------------------------------------------------------------

    @classmethod
    def get_available_schemas(cls) -> List[Dict[str, Any]]:
        result = []
        for key, schema in SCHEMA_DEFINITIONS.items():
            result.append({
                "schema_type": key,
                "description": schema["description"],
                "available_fields": schema["fields"],
                "recommended_count_max": 10000,
            })
        return result
