from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Response, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from loguru import logger
import filetype
import boto3
from uuid import uuid4
import os
from dotenv import load_dotenv
from infrastructure.database import SessionLocal, database
from domain.product import Product
from repository.product_repository import ProductRepository
from API.dto.ProductModel import ProductModel
from API.dto.UpdateProduct import UpdateProduct
from API.dto.CheckRemain import CheckRemain

load_dotenv()


KB = 1024
MB = 1024 * KB
SUPPORTED_FILE_TYPES = {
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'jpg': 'image/jpg'
}
AWS_BUCKET_NAME = 'dongyishoppingplatform'

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
    region_name='ap-southeast-2'
)

import logging

logger = logging.getLogger(__name__)

async def s3_upload(contents: bytes, key: str, content_type: str, acl: str = 'private', server_side_encryption='AES256'):
    logger.info(f"Uploading file to S3 with key: {key} and ACL: {acl}")
    try:
        s3.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=key,
            Body=contents,
            ContentType=content_type,
            ACL=acl,
            ServerSideEncryption=server_side_encryption
        )
        logger.info(f"File successfully uploaded to S3 with key: {key}")
    except Exception as e:
        logger.error(f"Failed to upload file to S3: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file to S3")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


router = APIRouter()


@router.patch("/upload_image")
async def create_product_image(product_id: int, db: db_dependency, file: UploadFile | None = None):
    if not file:
        return {"message": "No file uploaded"}

    contents = await file.read()
    size = len(contents)

    if not 0 < size <= 5 * MB:
        return {"message": "File size must be between 0 and 5MB"}

    kind = filetype.guess(contents)

    if kind is None or kind.extension not in SUPPORTED_FILE_TYPES:
        return {"message": "File type not supported"}

    file_name = f'{uuid4()}.{kind.extension}'
    await s3_upload(contents=contents, key=file_name, content_type=file.content_type, acl='public-read')

    query = select(Product).where(Product.id == product_id)
    result = db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        return {"message": "Product not found"}

    if product.image_url is None:
        product.image_url = []

    product.image_url = product.image_url + [file_name]
    db.add(product)
    db.commit()
    db.refresh(product)

    return {"message": "Image uploaded successfully", "image_url": product.image_url}

@router.get("/get_image")
async def get_product_images(product_id: int, db: db_dependency):
    query = select(Product).where(Product.id == product_id)
    result = db.execute(query)
    product = result.scalar_one_or_none()

    if not product or not product.image_url:
        raise HTTPException(status_code=404, detail="Product not found or images not found")

    image_urls = product.image_url  # 假設這是一個包含多個圖片 URL 的列表

    # 構建圖片的完整 URL
    full_image_urls = [f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{url}" for url in image_urls]

    return JSONResponse(content={"image_urls": full_image_urls})

@router.post("/", response_model=int)
async def create_product(product: ProductModel):
    product_data = product.model_dump()
    product_id = await ProductRepository.create_product(product_data)
    return product_id

@router.delete("/{product_id}", response_model=bool)
async def delete_product(product_id: int):
    return await ProductRepository.delete_product(product_id)

@router.patch("/{product_id}", response_model=bool)
async def update_product(product_id: int, update_data: UpdateProduct, db: db_dependency):
    return await ProductRepository.update_product(product_id, update_data.model_dump(exclude_unset=True), db)

@router.get("/{product_id}", response_model=ProductModel)
async def get_product_by_id(product_id: int):
    return await ProductRepository.get_product_by_id(product_id)

@router.get("/", response_model=List[ProductModel])
async def get_all_products():
    return await ProductRepository.get_all_products()

@router.get("/categories/{category}", response_model=List[ProductModel])
async def get_products_by_category(category: str):
    return await ProductRepository.get_products_by_category(category)

@router.get("/name/{name}", response_model=List[ProductModel])
async def get_product_by_name(name: str):
    return await ProductRepository.get_products_by_name(name)

@router.put("/stock_upd", response_model=bool)
async def update_stock(update_data: List[CheckRemain], db: db_dependency):
    return await ProductRepository.update_stock(update_data, db)

