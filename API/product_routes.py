from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from repository.product_repository import ProductRepository
from infrastructure.database import SessionLocal

# 建立 Router
router = APIRouter()

# Pydantic Models
class Product(BaseModel):
    id: int
    name: str
    price: int
    color: str
    size: str
    remain_amount: int
    description: Optional[str]
    categories: Optional[str]
    discount: Optional[int]
    image_url: Optional[str]

class UpdateProduct(BaseModel):
    price: Optional[int] = None
    color: Optional[str] = None
    size: Optional[str] = None
    remain_amount: Optional[int] = None
    description: Optional[str] = None
    categories: Optional[str] = None
    discount: Optional[int] = None

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# 新增產品
@router.post("/", response_model=int)
async def create_product(product: Product):
    product_data = product.model_dump()
    product_id = await ProductRepository.create_product(product_data)
    return product_id

# 刪除產品
@router.delete("/{product_id}", response_model=bool)
async def delete_product(product_id: int):
    return await ProductRepository.delete_product(product_id)

# 更新產品
@router.put("/{product_id}", response_model=bool)
async def update_product(product_id: int, update_data: UpdateProduct):
    return await ProductRepository.update_product(product_id, update_data.model_dump(exclude_unset=True))

# 獲取產品
@router.get("/{product_id}", response_model=Product)
async def get_product_by_id(product_id: int):
    return await ProductRepository.get_product_by_id(product_id)

# 獲取所有產品
@router.get("/", response_model=List[Product])
async def get_all_products():
    return await ProductRepository.get_all_products()

# 獲取特定類別的產品
@router.get("categories/{category}", response_model=List[Product])
async def get_products_by_category(category: str):
    return await ProductRepository.get_products_by_category(category)

#獲取特定名稱的產品
@router.get("name/{name}", response_model=List[Product])
async def get_product_by_name(name: str):
    return await ProductRepository.get_products_by_name(name)
