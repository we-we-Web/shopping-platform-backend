from fastapi import APIRouter, Depends, UploadFile, File
import magic
from loguru import logger
import boto3
from uuid import uuid4
import os
from dotenv import load_dotenv

load_dotenv()

KB = 1024
MB = 1024 * KB

SUPPORTED_FILE_TYPES = {
    'image/jpeg' : 'jpeg',
    'image/png' : 'png'
}

AWS_BUCKET_NAME = 'dongyishoppingplatform'

s3 = boto3.resource(
    's3',
    aws_access_key_id= os.getenv("aws_access_key_id"),
    aws_secret_access_key= os.getenv("aws_secret_access_key")
)
bucket = s3.Bucket(AWS_BUCKET_NAME)

async def s3_upload(contents: bytes, key: str):
    logger.info(f"Uploading file to S3 with key: {key}")
    bucket.put_object(Key=key, Body=contents)

# 建立 Router
router = APIRouter()

@router.post("/")
async def create_product_image(file: UploadFile | None = None):
    if not file:
        return {"message": "No file uploaded"}
    
    contents = await file.read()
    size = len(contents)

    if not 0 < size <= 5 * MB:
        return {"message": "File size must be between 0 and 5MB"}
    
    file_type = magic.from_buffer(buffer=contents, mime=True)

    if file_type not in SUPPORTED_FILE_TYPES:
        return {"message": "File type not supported"}
    
    await s3_upload(contents = contents, key = f'{uuid4()}.{SUPPORTED_FILE_TYPES[file_type]}')