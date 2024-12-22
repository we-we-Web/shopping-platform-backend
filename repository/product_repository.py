from sqlalchemy.sql import insert, delete, select, update
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, update
from fastapi import FastAPI, HTTPException
from infrastructure.database import database
from domain.product import Product

class ProductRepository:
    @staticmethod
    async def create_product(product_data: dict):
        query = select(Product).where(Product.id == product_data["id"])
        product = await database.fetch_one(query)
        if(product):
            raise HTTPException(status_code=409, detail="Product already exist")
        else:
            query = insert(Product).values(**product_data)
            product_id = await database.execute(query)
            return product_id

    @staticmethod
    async def delete_product(product_id: int):
        query = delete(Product).where(Product.id == product_id)
        result = await database.execute(query)
        if result == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return True

    @staticmethod
    async def update_product(product_id: int, update_data: dict, db: Session):
        query = select(Product).where(Product.id == product_id)
        result = db.execute(query)
        product = result.scalar_one_or_none()
        if result == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        
        for field, value in update_data.items():
            setattr(product, field, value)

        db.add(product)
        db.commit()
        db.refresh(product)

        return True

    @staticmethod
    async def get_product_by_id(product_id: int):
        query = select(Product).where(Product.id == product_id)
        product = await database.fetch_one(query)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    
    @staticmethod
    async def get_all_products():
        query = select(Product)
        products = await database.fetch_all(query)
        if not products:
            raise HTTPException(status_code=404, detail="There isn't any product")
        return products
    
    @staticmethod
    async def get_products_by_category(category: str):
        query = select(Product).filter(Product.categories.like(f"%{category}%"))
        products = await database.fetch_all(query)
        if not products:
            raise HTTPException(status_code=404, detail="There isn't any product in this category")
        return products
    
    @staticmethod
    async def get_products_by_name(name: str):
        query = select(Product).filter(or_(
                func.locate(name, Product.name) > 0,
                func.locate(Product.name, name) > 0
            ))
        products = await database.fetch_all(query)
        if not products:
            raise HTTPException(status_code=404, detail="There isn't any product with this name")
        return products

    
    @staticmethod
    async def update_stock(update_data: list, db: Session):
        for data in update_data:
            order_data = data.dict()
            query = select(Product).where(Product.id == order_data["id"])
            result = db.execute(query)
            product = result.scalar_one_or_none()

            if not product:
                raise HTTPException(status_code=404, detail=f"Product with ID {order_data['id']} not found")

            for field, value in order_data["spec"].items():
                if product.size.get(field, 0) < value:
                    raise HTTPException(status_code=400, detail=f"Stock of {field} is not enough")

                # 減少庫存
                product.size[field] -= value

            # 使用 SQLAlchemy 的 `update` 方法將變更提交到資料庫
            stmt = (
                update(Product)
                .where(Product.id == order_data["id"])
                .values(size=product.size)
            )
            db.execute(stmt)
            db.commit()


        return True


