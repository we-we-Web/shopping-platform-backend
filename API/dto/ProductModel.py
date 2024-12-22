from pydantic import BaseModel
from typing import Optional

class ProductModel(BaseModel):
    id: int
    name: str
    price: int
    size: dict
    description: Optional[str]
    categories: Optional[str]
    discount: Optional[int]