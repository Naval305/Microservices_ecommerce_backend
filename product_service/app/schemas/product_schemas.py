from decimal import Decimal

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from app.utils.helpers import PyObjectId


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category_id: PyObjectId
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal = Field(ge=0.01, max_digits=10, decimal_places=2)
    quantity: int = Field(default=1, ge=0)
    is_active: bool = True
    is_featured: bool = False

    model_config = ConfigDict(extra="allow")


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    category_id: PyObjectId | None = None
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal | None = Field(
        default=None, ge=0.01, max_digits=10, decimal_places=2
    )
    quantity: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    is_featured: bool | None = None

    model_config = ConfigDict(extra="allow")


class ProductOut(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    normalized_name: str
    category_id: str
    description: str | None
    sku: str = Field(alias="sku")
    price: float
    quantity: int
    is_active: bool
    is_featured: bool

    model_config = ConfigDict(
        populate_by_name=True, 
        arbitrary_types_allowed=True # Necessary to handle third-party BSON types
    )
