from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from faker import Faker


# ---------------------------------------------------------------------------
# Field resolver mapping: type string -> faker method / custom logic
# ---------------------------------------------------------------------------

FIELD_RESOLVERS: Dict[str, List[Any]] = {
    "name": ["name"],
    "email": ["email"],
    "phone": ["phone_number"],
    "address": ["address"],
    "street_address": ["street_address"],
    "city": ["city"],
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
    "username": ["user_name"],
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
                return f"_{field_type}_value"
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


# ---------------------------------------------------------------------------
# Special field generators — ALL use fake.random_int() (no random_float)
# ---------------------------------------------------------------------------

def _rminmax(fake: Faker, lo: int, hi: int, div: int = 1, dec: int = 2) -> Any:
    """Generate a float from random_int: round(random_int(lo*div, hi*div)/div, dec)."""
    return round(fake.random_int(lo * div, hi * div) / div, dec)


SPECIAL_FIELDS: Dict[str, Any] = {
    # Common
    "date_of_birth": lambda fake: fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
    "is_active": lambda fake: fake.boolean(70),
    "in_stock": lambda fake: fake.boolean(80),
    "verified_purchase": lambda fake: fake.boolean(60),
    "verified": lambda fake: fake.boolean(10),
    "tags": lambda fake: [fake.word() for _ in range(fake.random_int(2, 5))],
    "category": lambda fake: fake.random_element(["Electronics", "Clothing", "Books", "Home", "Sports", "Toys", "Food", "Beauty", "Automotive", "Health"]),
    "department": lambda fake: fake.random_element(["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Support", "Legal", "Research"]),
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

    # Transactions
    "type": lambda fake: fake.random_element(["deposit", "withdrawal", "transfer", "payment", "refund"]),
    "amount": lambda fake: _rminmax(fake, 100, 1000000, 1, 2),
    "status": lambda fake: fake.random_element(["completed", "pending", "failed", "cancelled", "processing"]),
    "method": lambda fake: fake.random_element(["card", "bank_transfer", "crypto", "paypal", "cash", "mobile"]),
    "description": lambda fake: fake.sentence(),
    "timestamp": lambda fake: fake.past_datetime().isoformat(),
    "reference": lambda fake: f"REF-{uuid.uuid4().hex[:10].upper()}",
    "fee": lambda fake: _rminmax(fake, 50, 5000, 100, 2),
    "balance_after": lambda fake: _rminmax(fake, 10000, 50000000, 100, 2),
    "from_account": lambda fake: f"ACC-{uuid.uuid4().hex[:12].upper()}",
    "to_account": lambda fake: f"ACC-{uuid.uuid4().hex[:12].upper()}",
    "sender_name": lambda fake: fake.name(),
    "receiver_name": lambda fake: fake.name(),

    # Social media
    "display_name": lambda fake: fake.name(),
    "followers": lambda fake: fake.random_int(0, 1000000),
    "following": lambda fake: fake.random_int(0, 100000),
    "engagement_rate": lambda fake: _rminmax(fake, 10, 9500, 100, 2),
    "hashtags": lambda fake: [f"#{fake.word()}" for _ in range(fake.random_int(1, 5))],
    "likes_received": lambda fake: fake.random_int(0, 50000),
    "comments_received": lambda fake: fake.random_int(0, 5000),
    "user_id": lambda fake: f"USR-{uuid.uuid4().hex[:12]}",
    "location": lambda fake: fake.city() + ", " + fake.country(),
    "joined_date": lambda fake: fake.past_date().isoformat(),

    # Banking
    "account_type": lambda fake: fake.random_element(["checking", "savings", "credit", "investment"]),
    "account_holder": lambda fake: fake.name(),
    "balance": lambda fake: _rminmax(fake, 100000, 1000000000, 100, 2),
    "credit_limit": lambda fake: _rminmax(fake, 100000, 50000000, 100, 2),
    "interest_rate": lambda fake: _rminmax(fake, 100, 2500, 100, 2),
    "routing_number": lambda fake: f"{fake.random_int(10000000, 99999999)}",
    "branch": lambda fake: fake.company() + " Branch",
    "branch_manager": lambda fake: fake.name(),
    "loan_id": lambda fake: f"LN-{uuid.uuid4().hex[:10].upper()}",
    "loan_amount": lambda fake: _rminmax(fake, 100000, 500000000, 100, 2),
    "loan_type": lambda fake: fake.random_element(["personal", "mortgage", "auto", "student", "business"]),
    "loan_status": lambda fake: fake.random_element(["active", "paid", "default", "pending"]),
    "monthly_payment": lambda fake: _rminmax(fake, 10000, 1000000, 100, 2),
    "debit_card_number": lambda fake: fake.credit_card_number(card_type=None),
    "cvv": lambda fake: f"{fake.random_int(100, 999)}",
    "pin": lambda fake: f"{fake.random_int(1000, 9999)}",
    "iban": lambda fake: fake.iban(),
    "swift_code": lambda fake: f"{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}{fake.country()[:2].upper()}{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}{fake.random_int(10, 99)}",
    "emergency_contact": lambda fake: fake.name() + " - " + fake.phone_number(),

    # Medical
    "patient_id": lambda fake: f"PT-{uuid.uuid4().hex[:12].upper()}",
    "patient_name": lambda fake: fake.name(),
    "blood_type": lambda fake: fake.random_element(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
    "height": lambda fake: fake.random_int(140, 210),
    "weight": lambda fake: fake.random_int(40, 150),
    "bmi": lambda fake: round(fake.random_int(160, 450) / 10, 1),
    "blood_pressure": lambda fake: f"{fake.random_int(90, 180)}/{fake.random_int(60, 120)}",
    "heart_rate": lambda fake: fake.random_int(50, 120),
    "temperature": lambda fake: _rminmax(fake, 3550, 4000, 100, 1),
    "diagnosis": lambda fake: fake.word().capitalize(),
    "medications": lambda fake: [fake.word() for _ in range(fake.random_int(1, 4))],
    "allergies": lambda fake: [fake.word() for _ in range(fake.random_int(0, 3))],
    "doctor_name": lambda fake: fake.name(),
    "admission_date": lambda fake: fake.past_date().isoformat(),
    "discharge_date": lambda fake: fake.future_date().isoformat(),
    "insurance_id": lambda fake: f"INS-{uuid.uuid4().hex[:10].upper()}",

    # Vehicles
    "make": lambda fake: fake.random_element(["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Nissan", "Chevrolet", "Hyundai"]),
    "model": lambda fake: fake.random_element(["Camry", "Civic", "F-150", "3 Series", "E-Class", "Altima", "Silverado"]),
    "year": lambda fake: fake.random_int(2015, 2026),
    "color": lambda fake: fake.color_name(),
    "body_type": lambda fake: fake.random_element(["Sedan", "SUV", "Hatchback", "Truck", "Coupe", "Van"]),
    "fuel_type": lambda fake: fake.random_element(["gasoline", "diesel", "electric", "hybrid"]),
    "transmission": lambda fake: fake.random_element(["automatic", "manual", "cvt"]),
    "engine_size": lambda fake: round(fake.random_int(100, 600) / 100, 1),
    "horsepower": lambda fake: fake.random_int(100, 600),
    "mileage": lambda fake: fake.random_int(0, 200000),
    "owner_name": lambda fake: fake.name(),
    "registration_date": lambda fake: fake.past_date().isoformat(),
    "insurance_type": lambda fake: fake.random_element(["liability", "comprehensive", "collision", "full"]),
    "vin": lambda fake: uuid.uuid4().hex[:17].upper(),

    # Employees
    "first_name": lambda fake: fake.first_name(),
    "last_name": lambda fake: fake.last_name(),
    "full_name": lambda fake: fake.name(),
    "salary": lambda fake: fake.random_int(30000, 200000),
    "hire_date": lambda fake: fake.past_date().isoformat(),
    "termination_date": lambda fake: fake.future_date().isoformat(),
    "manager": lambda fake: fake.name(),
    "performance_score": lambda fake: round(fake.random_int(100, 500) / 100, 1),
    "years_of_service": lambda fake: fake.random_int(0, 35),
    "education": lambda fake: fake.random_element(["High School", "Bachelor", "Master", "PhD", "MBA"]),
    "skills": lambda fake: [fake.word() for _ in range(fake.random_int(3, 8))],
    "title": lambda fake: fake.random_element(["Junior", "Mid", "Senior", "Lead", "Principal", "Manager", "Director", "VP", "CTO", "CEO"]),

    # Orders
    "order_id": lambda fake: f"ORD-{fake.random_int(100000, 999999)}",
    "order_status": lambda fake: fake.random_element(["pending", "processing", "shipped", "delivered", "cancelled"]),
    "customer_id": lambda fake: f"CUST-{uuid.uuid4().hex[:12]}",
    "customer_name": lambda fake: fake.name(),
    "customer_email": lambda fake: fake.email(),
    "items": lambda fake: [{"product_id": f"PRD-{uuid.uuid4().hex[:8]}", "name": fake.word().capitalize(), "quantity": fake.random_int(1, 3), "unit_price": round(fake.random_int(1000, 50000) / 100, 2)} for _ in range(fake.random_int(1, 5))],
    "subtotal": lambda fake: _rminmax(fake, 1000, 50000, 100, 2),
    "tax": lambda fake: _rminmax(fake, 100, 10000, 100, 2),
    "shipping": lambda fake: _rminmax(fake, 500, 5000, 100, 2),
    "total": lambda fake: _rminmax(fake, 2000, 100000, 100, 2),
    "payment_method": lambda fake: fake.random_element(["credit_card", "debit_card", "bank_transfer", "crypto", "paypal"]),
    "shipping_method": lambda fake: fake.random_element(["standard", "express", "overnight", "economy"]),
    "tracking_number": lambda fake: f"TRK-{uuid.uuid4().hex[:14].upper()}",
    "shipping_address": lambda fake: fake.address(),
    "billing_address": lambda fake: fake.address(),
    "notes": lambda fake: fake.sentence(),

    # Products
    "name": lambda fake: fake.word().capitalize(),
    "description": lambda fake: fake.paragraph(),
    "compare_at_price": lambda fake: _rminmax(fake, 1000, 100000, 100, 2),
    "cost": lambda fake: _rminmax(fake, 100, 10000, 100, 2),
    "weight": lambda fake: _rminmax(fake, 10, 5000, 100, 2),
    "sku": lambda fake: f"SKU-{uuid.uuid4().hex[:8].upper()}",
    "barcode": lambda fake: f"978-{uuid.uuid4().hex[:12]}",
    "brand": lambda fake: fake.company(),
    "manufacturer": lambda fake: fake.company(),
    "rating": lambda fake: round(fake.random_int(100, 500) / 100, 1),
    "reviews_count": lambda fake: fake.random_int(0, 10000),
    "stock_quantity": lambda fake: fake.random_int(0, 5000),
    "supplier": lambda fake: fake.company(),
    "warehouse_location": lambda fake: f"Aisle-{fake.random_int(1,50)}-Shelf-{fake.random_int(1,20)}",
    "images": lambda fake: [fake.image_url() for _ in range(fake.random_int(1, 3))],
    "variants": lambda fake: [{"size": fake.random_element(["S", "M", "L", "XL", "XXL"]), "color": fake.color_name(), "stock": fake.random_int(0, 100)} for _ in range(fake.random_int(2, 4))],

    # Reviews
    "user_name": lambda fake: fake.name(),
    "product_id": lambda fake: f"PRD-{uuid.uuid4().hex[:8]}",
    "product_name": lambda fake: fake.word().capitalize(),
    "rating": lambda fake: fake.random_int(1, 5),
    "title_review": lambda fake: fake.sentence(),
    "body": lambda fake: fake.paragraph(),
    "helpful_count": lambda fake: fake.random_int(0, 5000),
    "unhelpful_count": lambda fake: fake.random_int(0, 500),
    "response": lambda fake: fake.sentence() if fake.boolean(30) else None,
    "id_review": lambda fake: f"REV-{uuid.uuid4().hex[:12].upper()}",

    # Addresses
    "street": lambda fake: fake.street_address(),
    "full_address": lambda fake: fake.address(),
    "address_type": lambda fake: fake.random_element(["home", "work", "shipping", "billing"]),
    "company_name": lambda fake: fake.company(),
    "apartment": lambda fake: f"Apt {fake.random_int(1, 500)}",
    "floor": lambda fake: fake.random_int(1, 50),
    "building": lambda fake: f"Building {fake.random_int(1, 100)}",
    "id_addr": lambda fake: f"ADR-{uuid.uuid4().hex[:12]}",

    # Ecommerce
    "customer_phone": lambda fake: fake.phone_number(),
    "customer_address": lambda fake: fake.address(),
    "customer_city": lambda fake: fake.city(),
    "customer_country": lambda fake: fake.country(),
    "product_price": lambda fake: _rminmax(fake, 1000, 50000, 100, 2),
    "quantity": lambda fake: fake.random_int(1, 10),
    "order_status_ecom": lambda fake: fake.random_element(["pending", "processing", "shipped", "delivered", "cancelled"]),
    "discount": lambda fake: _rminmax(fake, 0, 5000, 100, 2),
    "review_text": lambda fake: fake.paragraph(),
    "rating_ecom": lambda fake: fake.random_int(1, 5),

    # Products helper
    "price": lambda fake: _rminmax(fake, 100, 50000, 100, 2),
}


class DataGenerator:
    """Core data generation engine."""

    def __init__(self):
        self._fakers: Dict[str, Faker] = {}

    def _get_fake(self, locale: str) -> Faker:
        if locale not in self._fakers:
            self._fakers[locale] = Faker(locale)
        return self._fakers[locale]

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
                all_special = list(SPECIAL_FIELDS.keys())
                all_resolver = list(FIELD_RESOLVERS.keys())
                pool = all_special + all_resolver
                fields = [fake.random_element(pool) for _ in range(count)]
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
