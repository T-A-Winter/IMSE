from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from SQL_backend import config

# Define typed base
class Base(DeclarativeBase):
    pass

# Session factory (read env vars from config.py)
engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=True)
SessionLocal = sessionmaker(bind=engine)
