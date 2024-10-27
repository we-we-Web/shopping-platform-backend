from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64))
    price = Column(Integer)
    color = Column(String(32))
    size = Column(String(32))
    remain_amount = Column(Integer)
