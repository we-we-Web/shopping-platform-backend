from typing import Annotated, List
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from internal.infrastructure.router import get_db, app

db_dependency = Annotated[Session, Depends(get_db)]

from internal.model.model import Product, UpdateProduct
from internal.repository.repository import ProductRepository

#新增產品
@app.post("/products", response_model=int)
async def create_product(product: Product):
    product_data = product.model_dump()
    product_id = await ProductRepository.create_product(product_data)
    return product_id

# 刪除產品
@app.delete("/products/{product_id}", response_model=bool)
async def delete_product(product_id: int):
    return await ProductRepository.delete_product(product_id)

# 更新產品
@app.put("/products/{product_id}", response_model=bool)
async def update_product(product_id: int, update_data: UpdateProduct):
    return await ProductRepository.update_product(product_id, update_data.model_dump(exclude_unset=True))

# 獲取產品
@app.get("/products/{product_id}", response_model=Product)
async def get_product_by_id(product_id: int):
    return await ProductRepository.get_product_by_id(product_id)

# 獲取所有產品
@app.get("/products", response_model=List[Product])
async def get_all_products():
    return await ProductRepository.get_all_products()