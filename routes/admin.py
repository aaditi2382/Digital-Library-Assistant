"""
Admin and Authentication routes for Digital Library Assistant.
Handles library statistics, full CRUD for books, policy edits, and auth verification.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import hashlib
from app.database import query_all, query_one, execute_write
from app.nlp.entity_extractor import extractor

router = APIRouter(prefix="/api/admin", tags=["Admin"])
auth_router = APIRouter(prefix="/api/auth", tags=["Auth"])

# Pydantic Schemas for Admin Operations
class BookCreate(BaseModel):
    isbn: str = Field(..., min_length=5)
    title: str = Field(..., min_length=2)
    author: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    subject: str = Field(..., min_length=2)
    description: Optional[str] = ""
    publisher: Optional[str] = ""
    publication_year: int = Field(2024, ge=1900, le=2030)
    edition: Optional[str] = "1st Edition"
    total_copies: int = Field(1, ge=1)
    available_copies: int = Field(1, ge=0)
    shelf_number: str = Field(..., min_length=2)
    location: str = Field(..., min_length=2)
    language: Optional[str] = "English"
    difficulty: Optional[str] = "Intermediate"

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    edition: Optional[str] = None
    total_copies: Optional[int] = None
    available_copies: Optional[int] = None
    shelf_number: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = None
    difficulty: Optional[str] = None

class CopiesUpdate(BaseModel):
    available_copies: int = Field(..., ge=0)

class PolicyUpdate(BaseModel):
    value: str = Field(..., min_length=1)

class LoginRequest(BaseModel):
    username: str
    password: str

@auth_router.post("/login")
async def login(payload: LoginRequest):
    """Simple authentication for student and admin roles."""
    pwd_hash = hashlib.sha256(payload.password.encode("utf-8")).hexdigest()
    user = query_one(
        "SELECT id, username, full_name, role, email FROM users WHERE username = ? AND password_hash = ?",
        (payload.username.strip(), pwd_hash)
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    return {
        "status": "success",
        "user": user,
        "token": f"mock-token-{user['id']}-{user['role']}"
    }

@router.get("/stats")
async def get_library_statistics():
    """
    Computes real-time statistics for the Admin Dashboard:
    Total titles, total copies, available copies, issued copies, categories, unique authors.
    """
    # Total titles and copies
    total_titles_row = query_one("SELECT COUNT(*) AS count, SUM(total_copies) AS total_vol, SUM(available_copies) AS avail_vol FROM books")
    total_titles = total_titles_row["count"] if total_titles_row else 0
    total_volume = total_titles_row["total_vol"] or 0
    avail_volume = total_titles_row["avail_vol"] or 0
    issued_volume = max(0, total_volume - avail_volume)

    # Categories count
    cat_row = query_one("SELECT COUNT(*) AS count FROM categories")
    total_cats = cat_row["count"] if cat_row else 0

    # Authors count
    authors_data = query_all("SELECT DISTINCT author FROM books")
    total_authors = len(authors_data)

    # Category distribution for charts
    cat_dist = query_all("""
        SELECT category, COUNT(*) as count, SUM(total_copies) as total_copies, SUM(available_copies) as available_copies
        FROM books
        GROUP BY category
        ORDER BY count DESC
    """)

    # Difficulty distribution
    diff_dist = query_all("""
        SELECT difficulty, COUNT(*) as count
        FROM books
        GROUP BY difficulty
    """)

    # Recent chat activity
    recent_chats = query_all("""
        SELECT session_id, message, intent, timestamp
        FROM chat_history
        WHERE role = 'user'
        ORDER BY id DESC LIMIT 10
    """)

    return {
        "summary": {
            "total_titles": total_titles,
            "total_volume": total_volume,
            "available_copies": avail_volume,
            "issued_copies": issued_volume,
            "total_categories": total_cats,
            "total_authors": total_authors
        },
        "category_distribution": cat_dist,
        "difficulty_distribution": diff_dist,
        "recent_queries": recent_chats
    }

@router.post("/books")
async def add_book(payload: BookCreate):
    """Adds a new book record into the library knowledge base."""
    # Check ISBN uniqueness
    existing = query_one("SELECT id FROM books WHERE isbn = ?", (payload.isbn.strip(),))
    if existing:
        raise HTTPException(status_code=400, detail="A book with this ISBN already exists.")

    new_id = execute_write("""
        INSERT INTO books (
            isbn, title, author, category, subject, description, publisher,
            publication_year, edition, total_copies, available_copies,
            shelf_number, location, language, difficulty
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload.isbn.strip(), payload.title.strip(), payload.author.strip(),
        payload.category.strip(), payload.subject.strip(), payload.description.strip(),
        payload.publisher.strip(), payload.publication_year, payload.edition.strip(),
        payload.total_copies, payload.available_copies, payload.shelf_number.strip().upper(),
        payload.location.strip(), payload.language.strip(), payload.difficulty.strip()
    ))

    # Reload NLP cache
    extractor._load_catalog_cache()

    return {"status": "success", "message": f"Book '{payload.title}' added successfully.", "id": new_id}

@router.put("/books/{book_id}")
async def update_book(book_id: int, payload: BookUpdate):
    """Updates an existing book record."""
    book = query_one("SELECT * FROM books WHERE id = ?", (book_id,))
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")

    update_fields = []
    params = []
    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = ?")
            params.append(value)

    if not update_fields:
        return {"status": "unchanged", "message": "No fields provided to update."}

    params.append(book_id)
    execute_write(f"UPDATE books SET {', '.join(update_fields)} WHERE id = ?", tuple(params))

    # Reload NLP cache
    extractor._load_catalog_cache()

    return {"status": "success", "message": "Book updated successfully."}

@router.delete("/books/{book_id}")
async def delete_book(book_id: int):
    """Deletes a book record from the catalog."""
    book = query_one("SELECT id, title FROM books WHERE id = ?", (book_id,))
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")

    execute_write("DELETE FROM books WHERE id = ?", (book_id,))
    extractor._load_catalog_cache()
    return {"status": "success", "message": f"Book '{book['title']}' deleted successfully."}

@router.patch("/books/{book_id}/copies")
async def update_book_copies(book_id: int, payload: CopiesUpdate):
    """Quickly updates the number of available copies for issue/return."""
    book = query_one("SELECT id, title, total_copies FROM books WHERE id = ?", (book_id,))
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")

    if payload.available_copies > book["total_copies"]:
        raise HTTPException(status_code=400, detail=f"Available copies cannot exceed total copies ({book['total_copies']}).")

    execute_write("UPDATE books SET available_copies = ? WHERE id = ?", (payload.available_copies, book_id))
    return {"status": "success", "message": f"Available copies updated to {payload.available_copies}."}

@router.put("/info/{key}")
async def update_policy(key: str, payload: PolicyUpdate):
    """Updates the value of a library rule or policy."""
    policy = query_one("SELECT key, title FROM library_info WHERE key = ?", (key,))
    if not policy:
        raise HTTPException(status_code=404, detail="Policy key not found.")

    execute_write("UPDATE library_info SET value = ? WHERE key = ?", (payload.value.strip(), key))
    return {"status": "success", "message": f"Policy '{policy['title']}' updated successfully."}
