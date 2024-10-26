from fastapi import FastAPI
from internal.infrastructure.database import engine, SessionLocal, database
from entity.entity import Base
from contextlib import asynccontextmanager

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await database.connect()
        Base.metadata.create_all(bind=engine)
        print("Database connected successfully.")
    except Exception as e:
        print(f"Database connection error: {e}")

    yield

    await database.disconnect()
    print("Database disconnected successfully.")

app = FastAPI(lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()