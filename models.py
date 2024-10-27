from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base
from databases import Database
from typing import Optional, List
from sqlalchemy.sql import insert, delete, select, update
from fastapi import FastAPI, HTTPException
from database import database

Base = declarative_base()


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64))
    price = Column(Integer)
    color = Column(String(32))
    size = Column(String(32))
    remain_amount = Column(Integer)


class ProductDAO:
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
    async def update_product(product_id: int, update_data: dict):
        query = update(Product).where(Product.id == product_id).values(**update_data)
        result = await database.execute(query)
        if result == 0:
            raise HTTPException(status_code=404, detail="Product not found")
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
