import uuid

from bson import ObjectId
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, handler: GetCoreSchemaHandler
    ) -> core_schema.PlainValidatorFunctionSchema:
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v) -> str:
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


async def generate_sku(category: str | None = None) -> str:
    prefix: str = category[:3].upper() if category else "GEN"
    suffix: str = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-{suffix}"
