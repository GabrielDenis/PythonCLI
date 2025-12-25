from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv
import db
import cache
import json
import httpx
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

class Book(BaseModel):
    title: str
    author: str

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
    try:
        cached_topics = cache.get_cache("all_topics")
        if cached_topics:
            print("Cache Hit")
            return json.loads(cached_topics)
    except Exception as e:
        print(f"Redis not ready: {e}")
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

    try:
        cache.set_cache("all_topics", topics_data)
    except:
        pass

    return topics_data

@app.post("/topics")
def create_topic(topic: Topic):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO topics (name, status) VALUES (%s, %s)", (topic.name, "todo"))
    conn.commit()
    cur.close()
    conn.close()

    try:
        cache.r.delete("all_topics")
    except:
        pass

    return {"message": "Topic created successfully"}

@app.put("/topics/{topic_name}/done")
def mark_done(topic_name: str):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE topics SET status = 'done' WHERE name = %s", (topic_name,))
    conn.commit()
    cur.close()
    conn.close()

    try:
        cache.r.delete("all_topics")
    except:
        pass

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

@app.post("/topics/{topic_id}/enrich")
async def enrich_topics(topic_id: int):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM topics WHERE id = %s", (topic_id,))
    topic = cur.fetchone()

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    topic_name = topic[0]

    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://openlibrary.org/search.json?q={topic_name}")
        data = response.json()

    saved_books = []

    for doc in data['docs'][:3]:
        title = doc.get('title', 'Unknown')
        author = doc.get('author_name', ['Unknown'])[0]

        cur.execute("INSERT INTO books (title, author, topic_id) VALUES (%s, %s, %s)", (title, author, topic_id))
        saved_books.append({"title": title, "author": author})

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Books Found!", "books": saved_books}

@app.get("/topics/{topic_id}/books")
def read_books(topic_id: int):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books WHERE topic_id = %s", (topic_id,))
    books = cur.fetchall()
    cur.close()
    conn.close()
    
    return [{"id": b[0], "title": b[1], "author": b[2]} for b in books]
            