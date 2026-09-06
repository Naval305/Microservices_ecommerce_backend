from decimal import Decimal

from bson import ObjectId
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    sku: str = Field(min_length=1, max_length=45, pattern=r"^[A-Za-z0-9\-_]+$")
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal = Field(ge=0.01, max_digits=10, decimal_places=2)
    quantity: int = Field(default=1, ge=0)
    is_active: bool = True
    is_featured: bool = False
    category: str | None = None


class ProductOut(BaseModel):
    name: str
    sku: str = Field(alias="sku")
    price: float

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
