from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv
from os import getenv
import db
import schemas

load_dotenv()
router = APIRouter(tags=["auth"])

SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register")
def register(user: schemas.UserCreate):
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (user.username, get_password_hash(user.password)))
        conn.commit()
    except Exception as e:
        conn.rollback() # Important for unique constraint usually
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Username already registered")
        
    cur.close()
    conn.close()
    return {"message": "User registered successfully"}

@router.post("/login")
def login(user: schemas.UserCreate):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (user.username,))
    db_user = cur.fetchone()
    cur.close()
    conn.close()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    if not verify_password(user.password, db_user[2]):
        raise HTTPException(status_code=400, detail="Incorrect password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
