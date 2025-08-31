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

class PurchaseItem(BaseModel):
    product_id: PyObjectId
    product_name: str
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    total_price: float = Field(..., gt=0)
    discount_applied: float = Field(default=0.0, ge=0.0)

class PurchaseBase(BaseModel):
    user_id: PyObjectId
    items: List[PurchaseItem]
    total_amount: float = Field(..., gt=0)
    discount_amount: float = Field(default=0.0, ge=0.0)
    final_amount: float = Field(..., gt=0)
    payment_method: str
    shipping_address: str
    status: str = "completed"  # pending, completed, cancelled, refunded

class PurchaseCreate(PurchaseBase):
    pass

class Purchase(PurchaseBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PurchaseResponse(BaseModel):
    id: str
    user_id: str
    items: List[PurchaseItem]
    total_amount: float
    discount_amount: float
    final_amount: float
    payment_method: str
    shipping_address: str
    status: str
    created_at: datetime
    session_id: Optional[str]
