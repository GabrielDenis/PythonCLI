from fastapi import APIRouter, HTTPException
import db
import cache
import json
import httpx
import schemas
from typing import List

router = APIRouter(prefix="/topics", tags=["topics"])

@router.get("/", response_model=List[dict]) # The original didn't use response_model effectively for the complex logic but let's try to match behavior
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
    
    topics_data = []

    # We need to fetch books for each topic too if we want to show count
    # The original implementation fetched topics and then... wait, the original didn't fetch books in /topics 
    # Ah, the original /topics endpoint in TopicList.tsx showed "Books: {topic.books ? topic.books.length : 0}"
    # So the /topics endpoint MUST return books data too?
    # Let's check the original code in api.py step 1135:
    # It returned: {"id": row[0], "name": row[1], "status": row[2]} 
    # It DID NOT return books array. 
    # Wait, the Frontend TopicList.tsx: <p>Books: {topic.books ? topic.books.length : 0}</p>
    # If the API doesn't return books, then topic.books is undefined, length is 0. 
    # So the "visible" books feature was fake or just prepared? 
    # The frontend code in 1154: topics.map... topic.books.length.
    # The API code in 1135: read_topics just returns id, name, status.
    # So the original app WAS NOT returning books count correctly? Or did I miss something?
    # Re-reading api.py: YES, it only returned id, name, status.
    # So the "Books: 0" was always 0.
    # 
    # FOR THE NEW FEATURE to work (Book Board), we NEED to return books.
    # I should update this endpoint to fetch books associated with the topic.
    
    # Let's do a JOIN or a second query. A separate query for each topic is N+1 problem.
    # A generic JOIN is better.
    
    # Fetch topics first
    for row in topics:
        t_id = row[0]
        # Fetch books for this topic
        cur.execute("SELECT id, title, author, status FROM books WHERE topic_id = %s", (t_id,))
        books_rows = cur.fetchall()
        books_list = [{"id": b[0], "title": b[1], "author": b[2], "status": b[3]} for b in books_rows]
        
        topics_data.append({
            "id": row[0],
            "name": row[1],
            "status": row[2],
            "books": books_list # Now we return the books!
        })

    cur.close()
    conn.close()

    try:
        cache.set_cache("all_topics", topics_data)
    except:
        pass

    return topics_data

@router.post("/")
def create_topic(topic: schemas.Topic):
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

@router.put("/{topic_name}/done")
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

@router.delete("/{topic_id}")
def delete_topic(topic_id: int):
    conn = db.get_connection()
    cur = conn.cursor()
    
    # Check if topic exists
    cur.execute("SELECT id FROM topics WHERE id = %s", (topic_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Topic not found")

    # Delete topic (Books will be deleted automatically due to CASCADE)
    cur.execute("DELETE FROM topics WHERE id = %s", (topic_id,))
    conn.commit()
    cur.close()
    conn.close()

    try:
        cache.r.delete("all_topics")
    except:
        pass

    return {"message": "Topic deleted successfully"}

@router.post("/{topic_id}/enrich")
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

        # Use new generic structure? No, stick to raw sql for now
        cur.execute("INSERT INTO books (title, author, topic_id, status) VALUES (%s, %s, %s, 'unread')", (title, author, topic_id))
        saved_books.append({"title": title, "author": author, "status": "unread"})

    conn.commit()
    cur.close()
    conn.close()
    
    try:
        cache.r.delete("all_topics") # Invalidate cache so list updates
    except:
        pass

    return {"message": "Books Found!", "books": saved_books}

@router.get("/{topic_id}/books", response_model=List[schemas.Book])
def read_books(topic_id: int):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, author FROM books WHERE topic_id = %s", (topic_id,))
    books = cur.fetchall()
    cur.close()
    conn.close()
    
    return [{"title": b[1], "author": b[2]} for b in books]

@router.post("/{topic_id}/books")
def create_book(topic_id: int, book: schemas.Book):
    conn = db.get_connection()
    cur = conn.cursor()
    # Verify topic exists
    cur.execute("SELECT id FROM topics WHERE id = %s", (topic_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Topic not found")
        
    cur.execute("INSERT INTO books (title, author, topic_id, status) VALUES (%s, %s, %s, 'unread')", (book.title, book.author, topic_id))
    conn.commit()
    cur.close()
    conn.close()
    
    try:
        cache.r.delete("all_topics")
    except:
        pass

    return {"message": "Book added successfully"}
