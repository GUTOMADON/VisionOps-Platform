"""Backend-agnostic UUID column type.

Stores a native UUID on PostgreSQL and a CHAR(36) string on any other
dialect (SQLite, used by the test suite). This lets the same ORM models
back both the production database and fast in-memory tests without
diverging schemas.
"""

import uuid

from sqlalchemy import CHAR
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.types import TypeDecorator


class GUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgresUUID(as_uuid=False))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return str(value)


def new_uuid() -> str:
    return str(uuid.uuid4())
