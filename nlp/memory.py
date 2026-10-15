"""
Conversation Memory and Context Management for Digital Library Assistant.
Maintains session state, tracks active entities, and resolves pronouns / follow-up queries.
"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from app.database import query_all, execute_write

class SessionContext:
    """Stores the active state for a user's conversation session."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.turn_count = 0
        self.last_intent: Optional[str] = None
        self.last_query: Optional[str] = None
        self.last_books: List[Dict[str, Any]] = [] # books returned in previous turn
        self.last_subject: Optional[str] = None
        self.last_difficulty: Optional[str] = None
        self.active_book: Optional[Dict[str, Any]] = None # current book in focus
        self.history: List[Dict[str, Any]] = []

    def update_turn(
        self,
        query: str,
        response_text: str,
        intent: str,
        books_returned: List[Dict[str, Any]],
        subject: Optional[str] = None,
        difficulty: Optional[str] = None,
        active_book: Optional[Dict[str, Any]] = None
    ):
        """Updates the conversation context after generating a response."""
        self.turn_count += 1
        self.last_query = query
        self.last_intent = intent
        
        if books_returned:
            self.last_books = books_returned
            if not active_book and len(books_returned) == 1:
                self.active_book = books_returned[0]
            elif active_book:
                self.active_book = active_book

        if subject:
            self.last_subject = subject
        if difficulty:
            self.last_difficulty = difficulty

        # Add to local history
        self.history.append({
            "turn": self.turn_count,
            "user": query,
            "assistant": response_text,
            "intent": intent,
            "timestamp": datetime.now().isoformat()
        })

        # Persist to database
        try:
            metadata = json.dumps({
                "intent": intent,
                "books_count": len(books_returned),
                "subject": self.last_subject,
                "difficulty": self.last_difficulty,
                "active_book_title": self.active_book.get("title") if self.active_book else None
            })
            execute_write(
                "INSERT INTO chat_history (session_id, role, message, intent, metadata_json) VALUES (?, ?, ?, ?, ?)",
                (self.session_id, "user", query, intent, metadata)
            )
            execute_write(
                "INSERT INTO chat_history (session_id, role, message, intent, metadata_json) VALUES (?, ?, ?, ?, ?)",
                (self.session_id, "assistant", response_text, intent, metadata)
            )
        except Exception as e:
            print(f"[MEMORY ERROR] Failed to persist chat history: {e}")

class ConversationMemoryManager:
    """Manages multi-user sessions in memory with SQLite synchronization."""

    def __init__(self):
        self._sessions: Dict[str, SessionContext] = {}

    def get_or_create(self, session_id: str) -> SessionContext:
        """Retrieves or instantiates a session context."""
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionContext(session_id)
        return self._sessions[session_id]

    def clear_session(self, session_id: str):
        """Clears memory for a given session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
        try:
            execute_write("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
        except Exception:
            pass

    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves persistent chat history for a session from the database."""
        rows = query_all(
            "SELECT role, message, intent, metadata_json, timestamp FROM chat_history WHERE session_id = ? ORDER BY id ASC LIMIT ?",
            (session_id, limit)
        )
        return rows

# Singleton instance
memory_manager = ConversationMemoryManager()
