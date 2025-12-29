from pydantic import BaseModel
from typing import Optional

class Topic(BaseModel):
    name: str

class UserCreate(BaseModel):
    username: str
    password: str

class Book(BaseModel):
    title: str
    author: str

class BookUpdate(BaseModel):
    status: str
