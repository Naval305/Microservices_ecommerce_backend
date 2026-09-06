from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreateSchema(BaseModel):
    name: str = Field(max_length=100)
    sku: str = Field(max_length=45)
    description: str | None = None
    price: Decimal = Field(ge=0.01, decimal_places=2)
    quantity: int = 1
    status: bool = True
    is_featured: bool = False
    category: str = None


class ProductModel(BaseModel):
    name: str
    sku: str
    description: str
    price: float
    quantity: int
    status: bool
    is_featured: bool
    category: dict