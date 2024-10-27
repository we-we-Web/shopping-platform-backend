from typing import Optional
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    price: int
    color: str
    size: str
    remain_amount: int

class UpdateProduct(BaseModel):
    price: Optional[int] = None
    color: Optional[str] = None
    size: Optional[str] = None
    remain_amount: Optional[int] = None