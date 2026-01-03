import db
import psycopg

try:
    conn = db.get_connection()
    cur = conn.cursor()
    print("Checking 'topics' table columns:")
    cur.execute("SELECT * FROM topics LIMIT 0")
    print([desc[0] for desc in cur.description])
    
    print("\nChecking 'books' table columns:")
    cur.execute("SELECT * FROM books LIMIT 0")
    print([desc[0] for desc in cur.description])

    conn.close()
except Exception as e:
    print(f"Error checking columns: {e}")
