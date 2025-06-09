from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import config
from time import sleep

# Define typed base
class Base(DeclarativeBase):
    pass

# even though the backend container depens on the database container as 
# and we even use depends_on: - mariadb in the docker-compose 
# we need to sleep here - since mariadb just is not fast enough 
# we the fast python script to listen to port 3306
# thats why we need to sleep here so mariadb has enough time to listen to the port
# please dont ask me how i found out... this was the longest 3h of my life 
sleep(5) 
# Session factory (read env vars from config.py)
engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=True)
SessionLocal = sessionmaker(bind=engine)
