from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from databases import Database

URL_DATABASE = 'mysql+pymysql://root:aa22610000@localhost:3306/shoppingplatform'

engine = create_engine(URL_DATABASE)

database = Database(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()