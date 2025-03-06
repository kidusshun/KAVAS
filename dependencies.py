from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db

def get_db_dependency():
    """
    Create a dependency that will be used across the application
    """
    def _get_db():
        db = next(get_db())
        try:
            yield db
        finally:
            db.close()
    
    return _get_db