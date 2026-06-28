from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, User as UserSchema

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/register", response_model=UserSchema)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # TODO: Implement user registration
    pass

@router.get("/{user_id}", response_model=UserSchema)
def get_user(user_id: int, db: Session = Depends(get_db)):
    # TODO: Implement get user
    pass

@router.post("/login")
def login_user(username: str, password: str, db: Session = Depends(get_db)):
    # TODO: Implement user login
    pass
