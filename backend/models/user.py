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

class UserBase(BaseModel):
    name: str
    email: str
    age: int = Field(..., ge=13, le=100)
    gender: str
    location: str
    income_level: str  # low, medium, high
    interests: List[str] = []
    persona_type: str  # budget_conscious, luxury_lover, tech_enthusiast, etc.
    
class UserCreate(UserBase):
    pass

class User(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    total_purchases: int = 0
    total_spent: float = 0.0
    favorite_categories: List[str] = []
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    age: int
    gender: str
    location: str
    income_level: str
    interests: List[str]
    persona_type: str
    total_purchases: int
    total_spent: float
    favorite_categories: List[str]
    created_at: datetime
    last_login: Optional[datetime]
