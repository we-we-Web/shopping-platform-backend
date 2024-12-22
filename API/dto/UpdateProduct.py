from pydantic import BaseModel
from typing import Optional

class UpdateProduct(BaseModel):
    price: Optional[int] = None
    size: Optional[dict] = None
    description: Optional[str] = None
    categories: Optional[str] = None
    discount: Optional[int] = None