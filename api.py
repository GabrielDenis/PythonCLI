from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import db
from routers import topics, books, auth

load_dotenv()
app = FastAPI()

# Database Migration on Startup
@app.on_event("startup")
def startup_event():
    try:
        db.run_migrations()
        print("Database migrations run successfully!")
    except Exception as e:
        print(f"Error running migrations: {e}")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost",
        "https://gabrieldenis.com",
        "https://www.gabrieldenis.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(topics.router)
app.include_router(books.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}