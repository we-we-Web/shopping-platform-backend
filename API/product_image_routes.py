from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Response
from typing import Annotated
import filetype
from loguru import logger
import boto3
from uuid import uuid4
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import select
from infrastructure.database import SessionLocal
from domain.product import Product
from infrastructure.database import database

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

async def s3_upload(contents: bytes, key: str):
    logger.info(f"Uploading file to S3 with key: {key}")
    bucket.put_object(Key=key, Body=contents)

async def s3_download(key: str):
    return s3.Object(bucket_name=AWS_BUCKET_NAME, key=key).get()['Body'].read()

# 建立 Router
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/upload_image")
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
    await s3_upload(contents=contents, key=file_name)

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
    try:
        query = select(Product).where(Product.id == product_id)
        result = db.execute(query)
        product = result.scalar_one_or_none()
        contents = await s3_download(key=product.image_url)
        
    except:
        raise HTTPException(status_code=404, detail="Product not found or image not found")

    return Response(
        content=contents,
        headers={
            'Contents-Disposition': f'inline;filename={product.image_url}',
            'Content-Type': 'application/octet-stream',
        }
    )
