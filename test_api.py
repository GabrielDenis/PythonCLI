from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_create_topic():
    response = client.post(
        "topics",
        json={"name": "Test Topic"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Topic created successfully"}

    response = client.get("topics")
    assert response.status_code == 200

    topics = response.json()
    found = any(t["name"] == "Test Topic" for t in topics)
    assert found

def test_login_failure():
    response = client.post(
        "login",
        json={"username": "fakeuser", "password": "wrongpassword"}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "User not found"}

def test_book_lifecycle():
    # 1. Create a Topic
    topic_res = client.post("topics", json={"name": "Book Test Topic"})
    assert topic_res.status_code == 200
    
    # Get Topic ID
    topics = client.get("topics").json()
    topic = next(t for t in topics if t["name"] == "Book Test Topic")
    topic_id = topic["id"]

    # 2. Add a Book to the Topic
    book_res = client.post(f"topics/{topic_id}/books", json={"title": "Test Book", "author": "Tester"})
    assert book_res.status_code == 200
    
    # Get Book ID
    topics_updated = client.get("topics").json()
    our_topic = next(t for t in topics_updated if t["id"] == topic_id)
    book = our_topic["books"][0]
    book_id = book["id"]
    
    assert book["title"] == "Test Book"
    assert book["status"] == "unread"  # Default status

    # 3. Update Status to 'read'
    print(f"Patching book: books/{book_id}")
    patch_res = client.patch(f"books/{book_id}", json={"status": "read"})
    print(f"Patch Status: {patch_res.status_code}")
    assert patch_res.status_code == 200
    
    # Verify Status Update
    topics_final = client.get("topics").json()
    final_book = next(t for t in topics_final if t["id"] == topic_id)["books"][0]
    assert final_book["status"] == "read"

    # 4. Delete Book
    print(f"Deleting book: books/{book_id}")
    del_res = client.delete(f"books/{book_id}")
    print(f"Delete Status: {del_res.status_code}")
    assert del_res.status_code == 200
    
    # Verify Deletion
    topics_after_del = client.get("topics").json()
    books_remaining = next(t for t in topics_after_del if t["id"] == topic_id)["books"]
    assert len(books_remaining) == 0