from dataclasses import dataclass
from uuid import UUID


@dataclass
class User:
    id: UUID
    role: str
    group_id: int | None = None
    is_authenticated: bool = True