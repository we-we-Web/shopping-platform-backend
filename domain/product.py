from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64))
    price = Column(Integer)
    size = Column(JSON, nullable=True, default=dict)
    description = Column(String(256))  
    categories = Column(String(256))  
    discount = Column(Integer)
    image_url = Column(String(256))