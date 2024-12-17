from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Response
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

load_dotenv()


KB = 1024
MB = 1024 * KB
SUPPORTED_FILE_TYPES = {
    'jpeg': 'jpeg',
    'png': 'png',
    'jpg': 'jpg'
}
AWS_BUCKET_NAME = 'dongyishoppingplatform'

s3 = boto3.resource(
    's3',
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key")
)
bucket = s3.Bucket(AWS_BUCKET_NAME)


async def s3_upload(contents: bytes, key: str, content_type: str):
    logger.info(f"Uploading file to S3 with key: {key}")
    bucket.put_object(Key=key, Body=contents, ContentType=content_type)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


router = APIRouter()


class ProductModel(BaseModel):
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
    
    file_name = f'{uuid4()}.{SUPPORTED_FILE_TYPES[kind.extension]}'
    await s3_upload(contents=contents, key=file_name, content_type=file.content_type)

    query = select(Product).where(Product.id == product_id)
    result = db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        return {"message": "Product not found"}

    product.image_url = file_name
    db.add(product)
    db.commit()
    db.refresh(product)

    return {"message": "Image uploaded successfully", "image_url": product.image_url}

@router.get("/get_image")
async def get_product_image(product_id: int, db: db_dependency):
    query = select(Product).where(Product.id == product_id)
    result = db.execute(query)
    product = result.scalar_one_or_none()

    if not product or not product.image_url:
        raise HTTPException(status_code=404, detail="Product not found or image not found")

    try:
        obj = s3.Object(bucket_name=AWS_BUCKET_NAME, key=product.image_url)
        file_obj = obj.get()
        contents = file_obj['Body'].read()
        content_type = file_obj['ContentType']
    except Exception as e:
        logger.error(f"Error fetching image: {e}")
        raise HTTPException(status_code=404, detail="Image not found")

    return Response(
        content=contents,
        headers={
            'Content-Disposition': f'inline;filename={product.image_url}',
            'Content-Type': content_type,
        }
    )

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
