from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from databases import Database
# from dotenv import load_dotenv
import os

# load_dotenv()

URL_DATABASE = "mysql+pymysql://root:wb9TJ10NuKiW2OvfoG4Dmdn7y85hA6Q3@hnd1.clusters.zeabur.com:31197/shopping_platform_DB"

engine = create_engine(URL_DATABASE)

database = Database(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()