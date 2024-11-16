from typing import Optional, List, Annotated
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from infrastructure.database import engine, SessionLocal, database
from sqlalchemy.orm import Session
from repository.product_repository import ProductRepository
from domain.product import Base
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    description: Optional[str]
    categories: Optional[str]
    discount: Optional[int]

class UpdateProduct(BaseModel):
    price: Optional[int] = None
    color: Optional[str] = None
    size: Optional[str] = None
    remain_amount: Optional[int] = None
    description: Optional[str] = None
    categories: Optional[str]= None 
    discount: Optional[int] = None 

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



