from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class User:
    id: UUID
    role: str
    group_id: int | None = None

    name: str | None = None
    surname: str | None = None
    username: str | None = None
    phone_number: str | None = None
    email: str | None = None
    image_s3_path: str | None = None
    is_blocked: bool | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None

    is_authenticated: bool = True