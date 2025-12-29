import psycopg
import os

def get_connection():
    # Production (Render)
    if os.getenv("DATABASE_URL"):
        return psycopg.connect(os.getenv("DATABASE_URL"))
    
    # Local Development
    return psycopg.connect(
        dbname="learning_tracker",
        user="postgres",
        password="1234", 
        host=os.getenv("DB_HOST", "localhost")
    )

def run_migrations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS topics (id SERIAL PRIMARY KEY,name VARCHAR(255) NOT NULL, status VARCHAR(255) NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY,username VARCHAR(50) UNIQUE NOT NULL,password_hash VARCHAR(255) NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS books (id SERIAL PRIMARY KEY, title VARCHAR(255) NOT NULL, author VARCHAR(255), topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE)")
    
    # ---------------------------------------------------------
    # MIGRATION: Add 'status' column to books if it doesn't exist
    # ---------------------------------------------------------
    try:
        cursor.execute("ALTER TABLE books ADD COLUMN status VARCHAR(50) DEFAULT 'unread'")
    except Exception as e:
        # If column already exists, ignore the error
        conn.rollback()
        pass

    conn.commit()
    cursor.close()
    conn.close()

    print("Migrations run successfully!")

if __name__ == "__main__":
    try:
        run_migrations()
    except Exception as e:
        print(f"Error: {e}")