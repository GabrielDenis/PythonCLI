from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv
import db
from os import getenv

load_dotenv()
app = FastAPI()

SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Topic(BaseModel):
    name: str

class UserCreate(BaseModel):
    username: str
    password: str

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

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/topics")
def read_topics():
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM topics")
    topics = cur.fetchall()
    cur.close()
    conn.close()
    
    topics_data = []

    for row in topics:
        topics_data.append({
            "id": row[0],
            "name": row[1],
            "status": row[2]
        })

    return topics_data

@app.post("/topics")
def create_topic(topic: Topic):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO topics (name, status) VALUES (%s, %s)", (topic.name, "todo"))
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Topic created successfully"}

@app.put("/topics/{topic_name}/done")
def mark_done(topic_name: str):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE topics SET status = 'done' WHERE name = %s", (topic_name,))
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Topic marked as done successfully"}

@app.post("/register")
def register(user: UserCreate):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (user.username, get_password_hash(user.password)))
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserCreate):
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