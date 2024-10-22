from typing import Optional, Union, List, Annotated
from sqlalchemy import select
import uvicorn
from fastapi import FastAPI, Body, Cookie, Header, HTTPException, Depends, status
from pydantic import BaseModel, Field
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class PostBase(BaseModel):
    title: str
    content: str
    user_id: int

class StudentBase(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get('/student', response_model=List[StudentBase])
async def get_student(db: db_dependency):
    query = select(models.Student)
    return db.execute(query).scalars().all()

@app.post('/users', status_code=status.HTTP_201_CREATED)
async def create_user(user: StudentBase, db: db_dependency):
    db_user = models.Student(**user.dict())
    db.add(db_user)
    db.commit()

