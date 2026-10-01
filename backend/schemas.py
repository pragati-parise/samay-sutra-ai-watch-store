from typing import Optional
from pydantic import BaseModel, EmailStr, Field
class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120); email: EmailStr; password: str = Field(min_length=8, max_length=72); address: str = Field(min_length=5, max_length=500); contact_number: str = Field(min_length=8, max_length=30)
class LoginIn(BaseModel): email: EmailStr; password: str = Field(min_length=1, max_length=72)
class CartIn(BaseModel): productId: int = Field(gt=0); quantity: int = Field(default=1, ge=1, le=20)
class QuantityIn(BaseModel): quantity: int = Field(ge=0, le=20)
class ReviewIn(BaseModel): rating: int = Field(ge=1, le=5); comment: str = Field(default="", max_length=800)
class AiAskIn(BaseModel): question: str = Field(min_length=3, max_length=500)
class AiRecommendIn(BaseModel):
    budget: Optional[float] = Field(default=None, gt=0, le=10000000); watch_type: str = Field(default="", max_length=80); style: str = Field(default="", max_length=80); occasion: str = Field(default="", max_length=80); strap: str = Field(default="", max_length=80); color: str = Field(default="", max_length=80)
class DescriptionIn(BaseModel):
    name: str = Field(min_length=2, max_length=160); brand: str = Field(min_length=2, max_length=100); category: str = Field(min_length=2, max_length=100); strap: str = Field(default="", max_length=60); color: str = Field(default="", max_length=60)
class DescriptionUpdateIn(BaseModel): description: str = Field(min_length=10, max_length=3000)
