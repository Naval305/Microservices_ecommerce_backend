from bson import ObjectId
from pydantic import BaseModel, Field, GetCoreSchemaHandler
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


# ---- Input schema (client-supplied, needs strict validation) ----
class CategoryCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    is_active: bool = True
    parent_id: PyObjectId | None = None


class CategoryUpdateSchema(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=40)
    is_active: bool | None = None
    parent_id: PyObjectId | None = None


# ---- Output schema (trusted, comes from DB) ----
class CategoryOut(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    is_active: bool
    parent_id: PyObjectId | None = None
    ancestors: list[str] = Field(
        default_factory=list
    )  # denormalized, for fast subtree queries

    model_config = {"populate_by_name": True}
