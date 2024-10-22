from sqlalchemy import Boolean, Column, Integer, String
from database import Base

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64))
    userid = Column(Integer, unique=True, nullable=True)
    password = Column(String(32))
    usergroup = Column(String(32))

class Group(Base):
    __tablename__ = 'studentgroups'

    id = Column(Integer, primary_key=True, index=True)
    groupname = Column(String(32), unique=True)
    members = Column(String(64))
