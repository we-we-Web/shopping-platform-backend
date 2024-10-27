from typing import Optional, Union, List, Annotated
from sqlalchemy import select
import uvicorn
from fastapi import FastAPI, Body, Cookie, Header, HTTPException, Depends, status
from pydantic import BaseModel, Field
from database import engine, SessionLocal, database
from databases import Database
from sqlalchemy.orm import Session
from models import ProductDAO, Base

app = FastAPI()

@app.on_event("startup")
async def startup():
    try:
        await database.connect()
        Base.metadata.create_all(bind=engine)
        print("Database connected successfully.")
    except Exception as e:
        print(f"Database connection error: {e}")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("Database disconnected successfully.")


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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#新增產品
@app.post("/products", response_model=int)
async def create_product(product: Product):
    product_data = product.model_dump()
    product_id = await ProductDAO.create_product(product_data)
    return product_id

# 刪除產品
@app.delete("/products/{product_id}", response_model=bool)
async def delete_product(product_id: int):
    return await ProductDAO.delete_product(product_id)

# 更新產品
@app.put("/products/{product_id}", response_model=bool)
async def update_product(product_id: int, update_data: UpdateProduct):
    return await ProductDAO.update_product(product_id, update_data.model_dump(exclude_unset=True))

# 獲取產品
@app.get("/products/{product_id}", response_model=Product)
async def get_product_by_id(product_id: int):
    return await ProductDAO.get_product_by_id(product_id)



