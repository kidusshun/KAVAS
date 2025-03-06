import time

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from config import Settings

engine = create_engine(
    url = Settings.DATABASE_URL,
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_database_connection(max_retries=5, retry_interval=1):
    """Check if the database is accessible, with retries."""
    retries = 0
    
    while retries < max_retries:
        try:
            # Create a new connection and test it with a simple query
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except OperationalError as e:
            retries += 1
            if retries == max_retries:
                raise Exception(f"Database connection failed after {max_retries} attempts: {str(e)}")
            time.sleep(retry_interval)
    
    return False