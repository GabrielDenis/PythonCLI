from fastapi import APIRouter, HTTPException, Depends
import db
import schemas
from typing import List

router = APIRouter(prefix="/books", tags=["books"])

@APIRouter.get("/{topic_id}", response_model=List[schemas.Book]) # Wait, the original route was /topics/{topic_id}/books. Let's keep it RESTful.
# Actually, looking at previous API, GET books was nested: /topics/{topic_id}/books.
# But DELETE was flat: /books/{book_id}.
# Clean architecture suggests keeping resources together.
# Let's support both or move to a flatter structure. User asked for robustness.
# Let's keep /topics/{id}/books in topics router and /books/{id} here.

@router.delete("/{book_id}")
def delete_book(book_id: int):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Book deleted successfully"}

@router.patch("/{book_id}")
def update_book_status(book_id: int, book: schemas.BookUpdate):
    conn = db.get_connection()
    cur = conn.cursor()
    # Check if book exists
    cur.execute("SELECT id FROM books WHERE id = %s", (book_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")

    cur.execute("UPDATE books SET status = %s WHERE id = %s", (book.status, book_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Book status updated successfully"}
