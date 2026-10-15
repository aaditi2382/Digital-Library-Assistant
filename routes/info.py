"""
Library Information and Category routes for Digital Library Assistant.
"""

from fastapi import APIRouter
from app.database import query_all

router = APIRouter(prefix="/api/info", tags=["Library Information"])

@router.get("")
async def get_all_library_info():
    """Retrieves all general library rules, timings, and policies."""
    records = query_all("SELECT key, title, value, category FROM library_info ORDER BY category, title")
    grouped = {}
    for r in records:
        cat = r["category"]
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(r)
    return {"policies": records, "grouped": grouped}

@router.get("/categories")
async def get_all_categories():
    """Retrieves all library academic categories with book counts."""
    sql = """
        SELECT c.id, c.name, c.description, c.icon, COUNT(b.id) AS book_count
        FROM categories c
        LEFT JOIN books b ON b.category = c.name
        GROUP BY c.id, c.name, c.description, c.icon
        ORDER BY c.name ASC
    """
    categories = query_all(sql)
    return {"categories": categories}
