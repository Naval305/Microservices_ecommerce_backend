import re
from typing import Annotated
import uuid

from bson import ObjectId
from pydantic import BeforeValidator


def validate_object_id(value: str) -> str:
    if not ObjectId.is_valid(value):
        raise ValueError("Invalid ObjectId")

    return str(value)


PyObjectId = Annotated[
    str,
    BeforeValidator(validate_object_id),
]


async def generate_sku(category: str | None = None) -> str:
    prefix: str = category[:3].upper() if category else "GEN"
    suffix: str = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-{suffix}"


async def normalize_name(name: str) -> str:
    return re.sub(r'\s+', ' ', name.strip().lower())