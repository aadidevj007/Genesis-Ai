from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class ProductBase(BaseModel):
    name: str
    category: str
    subcategory: str
    price: float = Field(..., gt=0)
    description: str
    brand: str
    tags: List[str] = []
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    review_count: int = Field(default=0, ge=0)
    stock_quantity: int = Field(default=0, ge=0)
    is_featured: bool = False
    discount_percentage: float = Field(default=0.0, ge=0.0, le=100.0)

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    total_sold: int = 0
    revenue_generated: float = 0.0
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ProductResponse(BaseModel):
    id: str
    name: str
    category: str
    subcategory: str
    price: float
    description: str
    brand: str
    tags: List[str]
    rating: float
    review_count: int
    stock_quantity: int
    is_featured: bool
    discount_percentage: float
    total_sold: int
    revenue_generated: float
    created_at: datetime
    updated_at: datetime
