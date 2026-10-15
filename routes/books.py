"""
Books and Catalog routes for Digital Library Assistant.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from app.database import query_all, query_one
from app.nlp.recommender import recommender

router = APIRouter(prefix="/api/books", tags=["Books"])

@router.get("")
async def list_books(
    search: Optional[str] = Query(None, description="Search keyword in title, author, subject, or description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (Beginner, Intermediate, Advanced)"),
    available_only: Optional[bool] = Query(False, description="Filter only books with available copies > 0"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Retrieves paginated and filtered list of books from the catalog."""
    sql = "SELECT * FROM books WHERE 1=1"
    params: List[Any] = []

    if search:
        s = f"%{search.strip()}%"
        sql += " AND (title LIKE ? OR author LIKE ? OR subject LIKE ? OR description LIKE ? OR isbn LIKE ? OR shelf_number LIKE ?)"
        params.extend([s, s, s, s, s, s])

    if category:
        sql += " AND category = ?"
        params.append(category)

    if difficulty:
        sql += " AND difficulty = ?"
        params.append(difficulty)

    if available_only:
        sql += " AND available_copies > 0"

    # Count total matching
    count_sql = f"SELECT COUNT(*) AS total FROM ({sql})"
    total_row = query_one(count_sql, tuple(params))
    total_count = total_row["total"] if total_row else 0

    sql += " ORDER BY title ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    books = query_all(sql, tuple(params))
    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "books": books
    }

@router.get("/recommendations")
async def get_recommendations(
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 4
):
    """Retrieves AI-recommended books based on subject and difficulty."""
    recs = recommender.recommend(subject=subject, difficulty=difficulty, limit=limit)
    return {"recommendations": recs}

@router.get("/{book_id}")
async def get_book_by_id(book_id: int):
    """Retrieves full details for a specific book by ID."""
    book = query_one("SELECT * FROM books WHERE id = ?", (book_id,))
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")
    return book

@router.get("/by-isbn/{isbn}")
async def get_book_by_isbn(isbn: str):
    """Retrieves book details by ISBN."""
    book = query_one("SELECT * FROM books WHERE isbn = ?", (isbn,))
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")
    return book
