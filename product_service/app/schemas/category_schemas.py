from pydantic import BaseModel, Field


class CategoryCreateSchema(BaseModel):
    name: str = Field(max_length=40)
    status: bool = True
    parent_id: str = None


class CategoryModel(BaseModel):
    name: str