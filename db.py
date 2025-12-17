import psycopg

def get_connection():
    return psycopg.connect(
        dbname="learning_tracker",
        user="postgres",
        password="1234", 
        host="localhost"
    )

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS topics (id SERIAL PRIMARY KEY,name VARCHAR(255) NOT NULL, status VARCHAR(255) NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY,username VARCHAR(50) UNIQUE NOT NULL,password_hash VARCHAR(255) NOT NULL)")
    conn.commit()
    cursor.close()
    conn.close()

    print("Table 'topics' created successfully!")

if __name__ == "__main__":
    try:
        create_table()
    except Exception as e:
        print(f"Error: {e}")