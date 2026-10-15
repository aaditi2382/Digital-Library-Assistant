"""
RAG (Retrieval-Augmented Generation) & Conversational Engine for Digital Library Assistant.
Coordinates:
1. Intent Classification
2. Entity Extraction & Slot Filling
3. Context & Anaphora Resolution
4. Knowledge Base Retrieval (Books, Policies, Categories)
5. Grounded Response Generation (Built-in NLG + Optional LLM Enhancement)
6. Suggested Follow-up Questions
"""

import os
import json
import re
import requests
from typing import Dict, Any, List, Optional
from app.database import query_all, query_one
from app.nlp.intent_classifier import classifier
from app.nlp.entity_extractor import extractor
from app.nlp.memory import memory_manager
from app.nlp.recommender import recommender

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

class RAGEngine:
    """End-to-end RAG orchestrator for grounded library dialogues."""

    def __init__(self):
        self.classifier = classifier
        self.extractor = extractor
        self.memory = memory_manager
        self.recommender = recommender

    def process_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Processes a student query and returns a grounded response with structured book cards.
        """
        clean_text = query.strip()
        session = self.memory.get_or_create(session_id)

        # Step 1: Intent Classification
        intent_result = self.classifier.predict(clean_text)
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]

        # Step 2: Entity & Slot Extraction
        entities = self.extractor.extract(clean_text)

        # Step 3: Handle Off-Topic & Greetings immediately
        if intent_result["is_off_topic"]:
            response_text = (
                "I am your **Digital Library Assistant** for the College of Engineering. "
                "I can assist you with book searches, availability checks, personalized recommendations, "
                "shelf locations, borrowing rules, and library timings.\n\n"
                "Please feel free to ask a library-related question!"
            )
            session.update_turn(clean_text, response_text, "off_topic", [])
            return {
                "message": response_text,
                "intent": "off_topic",
                "confidence": confidence,
                "entities": entities,
                "books": [],
                "suggested_questions": [
                    "What books are available for Python?",
                    "Check library opening hours",
                    "Recommend beginner books for AI"
                ],
                "session_id": session_id
            }

        if intent_result["is_greeting"]:
            greeting_text = (
                "Hello! Welcome to the **Digital Library Assistant**. 📚\n\n"
                "How can I help you today? You can search for engineering textbooks, check real-time availability, "
                "get personalized recommendations, or ask about library rules and timings."
            )
            session.update_turn(clean_text, greeting_text, "greeting", [])
            return {
                "message": greeting_text,
                "intent": "greeting",
                "confidence": confidence,
                "entities": entities,
                "books": [],
                "suggested_questions": [
                    "Find books about machine learning",
                    "Is Clean Code available?",
                    "How many books can I borrow?",
                    "Recommend books for Data Structures"
                ],
                "session_id": session_id
            }

        # Step 4: Anaphora / Context Resolution
        # Only treat as follow-up if query references previous context (e.g. "which of them", "is it available", "who wrote it")
        # and does not name a specific new book title or explicit new subject
        has_referent = entities["has_anaphora"] or any(w in clean_text.lower() for w in ["which of them", "which one", "among them"])
        has_new_explicit_target = bool(entities.get("book_title") or (entities.get("subject") and not any(w in clean_text.lower() for w in ["them", "these", "which"])))
        
        if session.last_books and has_referent and not has_new_explicit_target:
            followup_resp = self._handle_followup(clean_text, intent, entities, session)
            if followup_resp:
                return followup_resp

        # Step 5: Intent-Specific Retrieval & Handling
        if intent == "library_timings":
            return self._handle_timings(session, clean_text, intent, confidence, entities)

        elif intent in ["borrowing_rules", "renewal_info", "fine_info", "library_rules", "membership_info", "general_library"]:
            return self._handle_library_policy(session, clean_text, intent, confidence, entities)

        elif intent == "category_search":
            return self._handle_categories(session, clean_text, intent, confidence, entities)

        elif intent == "book_availability":
            return self._handle_availability(session, clean_text, intent, confidence, entities)

        elif intent == "book_details":
            return self._handle_details(session, clean_text, intent, confidence, entities)

        elif intent == "author_search":
            return self._handle_author(session, clean_text, intent, confidence, entities)

        elif intent == "location_shelf":
            return self._handle_location(session, clean_text, intent, confidence, entities)

        elif intent == "book_recommendation":
            return self._handle_recommendations(session, clean_text, intent, confidence, entities)

        else: # book_search or default
            return self._handle_book_search(session, clean_text, intent, confidence, entities)

    # ------------------ Intent Handlers ------------------ #

    def _handle_followup(
        self,
        query: str,
        intent: str,
        entities: Dict[str, Any],
        session: Any
    ) -> Optional[Dict[str, Any]]:
        """Handles conversational context and pronoun resolution."""
        lower_q = query.lower()

        # Case 1: "Which of them are beginner friendly?" or "Which one is beginner?"
        if ("which of them" in lower_q or "which one" in lower_q or "among them" in lower_q or "beginner" in lower_q) and session.last_books:
            req_diff = entities.get("difficulty") or ("Beginner" if "beginner" in lower_q else None)
            if req_diff:
                filtered = [b for b in session.last_books if b.get("difficulty", "").lower() == req_diff.lower()]
                if filtered:
                    best = filtered[0]
                    msg = (
                        f"Among the previously mentioned books, **{best['title']}** by {best['author']} "
                        f"is specifically tailored for **{req_diff}s**.\n\n"
                        f"📖 **Overview:** {best['description']}\n"
                        f"📍 **Location:** Shelf {best['shelf_number']} ({best['location']})\n"
                        f"🟢 **Availability:** {best['available_copies']} of {best['total_copies']} copies available."
                    )
                    session.update_turn(query, msg, "book_recommendation", filtered, active_book=best)
                    return {
                        "message": msg,
                        "intent": "book_recommendation",
                        "confidence": 0.95,
                        "entities": entities,
                        "books": filtered,
                        "suggested_questions": [
                            f"Is {best['title']} available to borrow?",
                            f"Who published {best['title']}?",
                            "Recommend more advanced books on this topic"
                        ],
                        "session_id": session.session_id
                    }
                else:
                    msg = f"None of the {len(session.last_books)} books from our previous search were categorized strictly as '{req_diff}'. Would you like me to search the entire library for {req_diff} books in {session.last_subject or 'this topic'}?"
                    return {
                        "message": msg,
                        "intent": "book_search",
                        "confidence": 0.90,
                        "entities": entities,
                        "books": session.last_books,
                        "suggested_questions": [
                            f"Find beginner books on {session.last_subject or 'computer engineering'}",
                            "Show all available books"
                        ],
                        "session_id": session.session_id
                    }

        # Case 2: "Is it available?" or "Is this book available?"
        if ("is it available" in lower_q or "available?" in lower_q or "copies left" in lower_q) and (session.active_book or session.last_books):
            target = session.active_book or session.last_books[0]
            # Refresh from DB
            curr = query_one("SELECT * FROM books WHERE id = ?", (target["id"],)) or target
            avail = curr["available_copies"]
            total = curr["total_copies"]
            if avail > 0:
                msg = (
                    f"Yes, **{curr['title']}** by {curr['author']} is currently **Available**.\n\n"
                    f"• **Available Copies:** {avail} of {total}\n"
                    f"• **Shelf:** {curr['shelf_number']}\n"
                    f"• **Location:** {curr['location']}\n\n"
                    f"You can issue this book at the circulation desk or self-service RFID kiosk."
                )
            else:
                msg = (
                    f"Currently, all {total} copies of **{curr['title']}** by {curr['author']} are checked out (0 available).\n\n"
                    f"• **Shelf:** {curr['shelf_number']}\n"
                    f"You can place a reservation hold on this book at the library circulation desk."
                )
            session.update_turn(query, msg, "book_availability", [curr], active_book=curr)
            return {
                "message": msg,
                "intent": "book_availability",
                "confidence": 0.95,
                "entities": entities,
                "books": [curr],
                "suggested_questions": [
                    f"Where can I find shelf {curr['shelf_number']}?",
                    f"Who published {curr['title']}?",
                    f"Recommend books similar to {curr['title']}"
                ],
                "session_id": session.session_id
            }

        # Case 3: "Who is the author of this book?" or "Who wrote it?"
        if ("who is the author" in lower_q or "who wrote" in lower_q or "author" in lower_q) and (session.active_book or session.last_books):
            target = session.active_book or session.last_books[0]
            msg = f"The author of **{target['title']}** is **{target['author']}**. It is published by {target.get('publisher', 'the publisher')} ({target.get('edition', '')})."
            session.update_turn(query, msg, "author_search", [target], active_book=target)
            return {
                "message": msg,
                "intent": "author_search",
                "confidence": 0.95,
                "entities": entities,
                "books": [target],
                "suggested_questions": [
                    f"Is {target['title']} available?",
                    f"What shelf is {target['title']} on?",
                    f"More books by {target['author']}"
                ],
                "session_id": session.session_id
            }

        # Case 4: "Where can I find it?" / "Where is it located?"
        if ("where can i find it" in lower_q or "where is it" in lower_q or "which shelf" in lower_q) and (session.active_book or session.last_books):
            target = session.active_book or session.last_books[0]
            msg = (
                f"**{target['title']}** is located in:\n\n"
                f"📍 **Shelf:** {target['shelf_number']}\n"
                f"🏢 **Wing/Floor:** {target['location']}\n"
                f"🟢 **Available Copies:** {target['available_copies']} of {target['total_copies']}"
            )
            session.update_turn(query, msg, "location_shelf", [target], active_book=target)
            return {
                "message": msg,
                "intent": "location_shelf",
                "confidence": 0.95,
                "entities": entities,
                "books": [target],
                "suggested_questions": [
                    f"How can I issue {target['title']}?",
                    f"What are the borrowing rules?",
                    "Check library opening hours"
                ],
                "session_id": session.session_id
            }

        return None

    def _handle_timings(self, session, query, intent, confidence, entities) -> Dict[str, Any]:
        """Provides accurate, grounded library timings."""
        records = query_all("SELECT key, title, value FROM library_info WHERE category = 'timings'")
        info_map = {r["key"]: r["value"] for r in records}

        msg = (
            "🕒 **Central Academic Library Timings & Working Hours:**\n\n"
            f"• **Monday to Friday:** {info_map.get('timings_weekday', '8:00 AM – 8:00 PM')}\n"
            f"• **Saturdays:** {info_map.get('timings_saturday', '9:00 AM – 5:00 PM')}\n"
            f"• **Sundays & Holidays:** {info_map.get('timings_sunday_holidays', 'Closed on Sundays and Gazette Holidays.')}\n\n"
            "💡 *Tip: During semester exam weeks, the Ground Floor Reading Hall remains accessible on Sundays from 10:00 AM to 4:00 PM.*"
        )
        session.update_turn(query, msg, intent, [])
        return {
            "message": msg,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "books": [],
            "suggested_questions": [
                "What is the maximum number of books I can borrow?",
                "What is the fine for returning a book late?",
                "How do I issue a book?"
            ],
            "session_id": session.session_id
        }

    def _handle_library_policy(self, session, query, intent, confidence, entities) -> Dict[str, Any]:
        """Grounds responses in the official library policies table."""
        lower_q = query.lower()

        if intent == "fine_info" or "fine" in lower_q or "penalty" in lower_q:
            rule = query_one("SELECT value FROM library_info WHERE key = 'fine_policy'")
            msg = (
                "💰 **Overdue Fine & Late Return Policy:**\n\n"
                f"{rule['value'] if rule else 'Late return fine is ₹5 per day per overdue book.'}\n\n"
                "⚠️ *Please return or renew your books on or before the 14-day due date to prevent fines and library hold blocks.*"
            )
            suggested = ["How can I renew my borrowed book?", "What is the borrowing period?", "Check library opening hours"]

        elif intent == "renewal_info" or "renew" in lower_q:
            rule = query_one("SELECT value FROM library_info WHERE key = 'renewal_policy'")
            msg = (
                "🔄 **Book Renewal Policy:**\n\n"
                f"{rule['value'] if rule else 'Books can be renewed up to 2 times for 14 days each.'}\n\n"
                "📌 *Note: If another student has placed an active reservation hold on the title, online renewal will not be permitted.*"
            )
            suggested = ["What is the fine for returning a book late?", "How many books can I borrow?", "Check library opening hours"]

        elif intent == "borrowing_rules" or "how many books" in lower_q or "borrow" in lower_q or "duration" in lower_q or "issue" in lower_q:
            student_lim = query_one("SELECT value FROM library_info WHERE key = 'borrowing_limit_student'")
            duration = query_one("SELECT value FROM library_info WHERE key = 'borrowing_duration'")
            process = query_one("SELECT value FROM library_info WHERE key = 'issue_process'")
            
            msg = (
                "📚 **Library Borrowing Rules & Issue Guidelines:**\n\n"
                f"• **Student Borrowing Limit:** {student_lim['value'] if student_lim else 'Up to 4 books.'}\n"
                f"• **Borrowing Duration:** {duration['value'] if duration else '14 days (2 weeks).'}\n"
                f"• **How to Issue:** {process['value'] if process else 'Present your student RFID ID card at the circulation desk.'}"
            )
            suggested = ["How can I renew my borrowed book?", "What is the fine for returning a book late?", "Find books on Python"]

        elif intent == "membership_info" or "membership" in lower_q or "library card" in lower_q:
            rule = query_one("SELECT value FROM library_info WHERE key = 'membership_rules'")
            msg = (
                "🪪 **Library Membership Information:**\n\n"
                f"{rule['value'] if rule else 'Enrolled students are automatically registered using their Institute RFID Card.'}"
            )
            suggested = ["What are the library opening hours?", "How many books can I borrow?", "Show all book categories"]

        elif "lost" in lower_q or "damage" in lower_q:
            rule = query_one("SELECT value FROM library_info WHERE key = 'lost_damaged_policy'")
            msg = (
                "⚠️ **Lost or Damaged Book Policy:**\n\n"
                f"{rule['value'] if rule else 'Lost books must be replaced with the same edition or compensated at 150% market value.'}"
            )
            suggested = ["What is the fine for returning a book late?", "What are the general library rules?", "Library helpdesk contact"]

        else: # General rules / conduct
            rule = query_one("SELECT value FROM library_info WHERE key = 'general_conduct'")
            msg = (
                "📖 **General Library Rules & Code of Conduct:**\n\n"
                f"{rule['value'] if rule else 'Please maintain silence and follow library rules.'}"
            )
            suggested = ["What are the library opening hours?", "How many books can I borrow?", "Find books on Data Structures"]

        session.update_turn(query, msg, intent, [])
        return {
            "message": msg,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "books": [],
            "suggested_questions": suggested,
            "session_id": session.session_id
        }

    def _handle_categories(self, session, query, intent, confidence, entities) -> Dict[str, Any]:
        """Lists available book categories and their coverage."""
        cats = query_all("SELECT name, description, icon FROM categories ORDER BY name ASC")
        cat_lines = [f"• **{c['name']}**: {c['description']}" for c in cats]
        msg = (
            f"🏛️ We have **{len(cats)} Academic Categories** available in the library knowledge base:\n\n"
            + "\n".join(cat_lines)
            + "\n\n💡 *You can ask me to find books in any of these categories (e.g., 'Find books on Artificial Intelligence' or 'Show Operating Systems books')!*"
        )
        session.update_turn(query, msg, intent, [])
        return {
            "message": msg,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "books": [],
            "suggested_questions": [
                "Find books on Artificial Intelligence",
                "Show books for Database Management Systems",
                "Recommend beginner books for Python"
            ],
            "session_id": session.session_id
        }

    def _handle_availability(self, session, query, intent, confidence, entities) -> Dict[str, Any]:
        """Checks real-time availability for a named book or author."""
        title_cand = entities.get("book_title")
        author_cand = entities.get("author")

        matched_book = None
        if title_cand:
            matched_book = query_one(
                "SELECT * FROM books WHERE title LIKE ? ORDER BY CASE WHEN title = ? THEN 1 ELSE 2 END LIMIT 1",
                (f"%{title_cand}%", title_cand)
            )

        # Fallback to fuzzy keyword search if direct match was not found
        if not matched_book:
            raw_tokens = re.findall(r"\b[a-zA-Z]{4,}\b", query.lower())
            for t in raw_tokens:
                if t not in ["available", "stock", "check", "copies", "book", "right", "there"]:
                    cand = query_one("SELECT * FROM books WHERE title LIKE ? LIMIT 1", (f"%{t}%",))
                    if cand:
                        matched_book = cand
                        break

        if not matched_book:
            msg = (
                f"I could not find a book matching **'{title_cand or query}'** in our library database.\n\n"
                "Please verify the title spelling, or ask me to browse books by category (e.g., 'Show Python books' or 'Show books on Operating Systems')."
            )
            session.update_turn(query, msg, intent, [])
            return {
                "message": msg,
                "intent": intent,
                "confidence": confidence,
                "entities": entities,
                "books": [],
                "suggested_questions": [
                    "What books are available for Python?",
                    "Is Clean Code available?",
                    "Show all book categories"
                ],
                "session_id": session.session_id
            }

        avail = matched_book["available_copies"]
        total = matched_book["total_copies"]
        shelf = matched_book["shelf_number"]
        loc = matched_book["location"]

        if avail > 0:
            msg = (
                f"Yes! **{matched_book['title']}** by {matched_book['author']} is currently **Available**.\n\n"
                f"• **Available copies:** {avail}\n"
                f"• **Total copies:** {total}\n"
                f"• **Shelf:** {shelf}\n"
                f"• **Location:** {loc}\n"
                f"• **Edition:** {matched_book['edition']} ({matched_book['publication_year']})\n\n"
                f"You can find it on Shelf **{shelf}** in the {loc}."
            )
        else:
            msg = (
                f"⚠️ **{matched_book['title']}** by {matched_book['author']} is in our catalog, but **currently unavailable** (all {total} copies are issued).\n\n"
                f"• **Total copies:** {total}\n"
                f"• **Available copies:** 0\n"
                f"• **Shelf:** {shelf}\n"
                f"• **Location:** {loc}\n\n"
                f"You can visit the circulation desk to place an active reservation hold."
            )

        session.update_turn(query, msg, intent, [matched_book], active_book=matched_book)
        return {
            "message": msg,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "books": [matched_book],
            "suggested_questions": [
                f"Who is the author of {matched_book['title']}?",
                f"Recommend books similar to {matched_book['title']}",
                "How many days can I keep a borrowed book?"
            ],
            "session_id": session.session_id
        }

    def _handle_details(self, session, query, intent, confidence, entities) -> Dict[str, Any]:
        """Provides full catalog metadata for a book."""
        title_cand = entities.get("book_title")
        matched = None
        if title_cand:
            matched = query_one("SELECT * FROM books WHERE title LIKE ? LIMIT 1", (f"%{title_cand}%",))

        if not matched and session.active_book:
            matched = session.active_book

        if not matched and session.last_books:
            matched = session.last_books[0]

        if not matched:
            return self._handle_book_search(session, query, intent, confidence, entities)

        msg = (
            f"📖 **Book Information: {matched['title']}**\n\n"
            f"• **Author(s):** {matched['author']}\n"
            f"• **ISBN:** {matched['isbn']}\n"
            f"• **Category:** {matched['category']} | **Subject:** {matched['subject']}\n"
            f"• **Edition:** {matched['edition']} ({matched['publication_year']})\n"
            f"• **Publisher:** {matched['publisher']}\n"
            f"• **Difficulty:** {matched['difficulty']}\n"
            f"• **Availability:** {matched['available_copies']} of {matched['total_copies']} copies available\n"
            f"• **Shelf:** {matched['shelf_number']} ({matched['location']})\n\n"
            f"**Description:**\n{matched['description']}"
        )
        session.update_turn(query, msg, intent, [matched], active_book=matched)
        return {
            "message": msg,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "books": [matched],
            "suggested_questions": [
                f"Is {matched['title']} available to borrow?",
                f"Where can I find shelf {matched['shelf_number']}?",
                f"Recommend books for {matched['category']}"
            ],
            "session_id": session.session_id
        }

    def _handle_author(self, session, query, intent, confidence, entities) -> Dict[str, Any]:
        """Handles author searches and author-specific listings."""
        author = entities.get("author")
        title = entities.get("book_title")

        # If user asks: "who is the author of Clean Code?"
        if title:
            b = query_one("SELECT * FROM books WHERE title LIKE ? LIMIT 1", (f"%{title}%",))
            if b:
                msg = f"The author of **{b['title']}** is **{b['author']}**. It was published by {b['publisher']} in {b['publication_year']} ({b['edition']})."
                session.update_turn(query, msg, intent, [b], active_book=b)
                return {
                    "message": msg,
                    "intent": intent,
                    "confidence": confidence,
                    "entities": entities,
                    "books": [b],
                    "suggested_questions": [
                        f"Is {b['title']} available?",
                        f"More books by {b['author']}",
                        f"Where is shelf {b['shelf_number']}?"
                    ],
                    "session_id": session.session_id
                }

        # If user asks: "books by Stuart Russell" or "books written by Cormen"
        if author:
            books = query_all("SELECT * FROM books WHERE author LIKE ? ORDER BY publication_year DESC", (f"%{author}%",))
            if books:
                msg = f"I found **{len(books)} book(s)** authored by **{author}** in our library:"
                session.update_turn(query, msg, intent, books)
                return {
                    "message": msg,
                    "intent": intent,
                    "confidence": confidence,
                    "entities": entities,
                    "books": books,
                    "suggested_questions": [
                        f"Is {books[0]['title']} available?",
                        "What is the borrowing period?",
                        "Check library timings"
                    ],
                    "session_id": session.session_id
                }

        return self._handle_book_search(session, query, intent, confidence, entities)

    def _handle_location(self, session, query, intent, confidence, entities) -> Dict[str, Any]:
        """Provides physical shelf location and room guidance."""
        shelf = entities.get("shelf")
        subj = entities.get("subject")
        title = entities.get("book_title")

        if title:
            b = query_one("SELECT * FROM books WHERE title LIKE ? LIMIT 1", (f"%{title}%",))
            if b:
                msg = (
                    f"**{b['title']}** by {b['author']} is placed on:\n\n"
                    f"📍 **Shelf:** {b['shelf_number']}\n"
                    f"🏢 **Location:** {b['location']}\n"
                    f"🟢 **Available Copies:** {b['available_copies']} of {b['total_copies']}"
                )
                session.update_turn(query, msg, intent, [b], active_book=b)
                return {
                    "message": msg,
                    "intent": intent,
                    "confidence": confidence,
                    "entities": entities,
                    "books": [b],
                    "suggested_questions": [
                        f"Is {b['title']} available to borrow?",
                        "How do I issue a book?",
                        "What are the library opening hours?"
                    ],
                    "session_id": session.session_id
                }

        if shelf:
            books_on_shelf = query_all("SELECT * FROM books WHERE shelf_number = ? LIMIT 5", (shelf,))
            if books_on_shelf:
                loc = books_on_shelf[0]["location"]
                msg = f"Shelf **{shelf}** is situated in **{loc}**.\nIt holds books on {books_on_shelf[0]['category']}. Here are some books on this shelf:"
                session.update_turn(query, msg, intent, books_on_shelf)
                return {
                    "message": msg,
                    "intent": intent,
                    "confidence": confidence,
                    "entities": entities,
                    "books": books_on_shelf,
                    "suggested_questions": [
                        "Check library timings",
                        "How many books can I borrow?",
                        "Show all categories"
                    ],
                    "session_id": session.session_id
                }

        if subj:
            books_subj = query_all("SELECT * FROM books WHERE category LIKE ? OR subject LIKE ? LIMIT 4", (f"%{subj}%", f"%{subj}%"))
            if books_subj:
                shelves = list(set(b["shelf_number"] for b in books_subj))
                locs = list(set(b["location"] for b in books_subj))
                msg = (
                    f"Books for **{subj}** are located in:\n"
                    f"📍 **Shelves:** {', '.join(shelves)}\n"
                    f"🏢 **Section:** {locs[0]}\n\n"
                    f"Here are the books available in this section:"
                )
                session.update_turn(query, msg, intent, books_subj, subject=subj)
                return {
                    "message": msg,
                    "intent": intent,
                    "confidence": confidence,
                    "entities": entities,
                    "books": books_subj,
                    "suggested_questions": [
                        f"Which of them are beginner friendly?",
                        f"Recommend the best book for {subj}",
                        "Check library opening hours"
                    ],
                    "session_id": session.session_id
                }

        return self._handle_book_search(session, query, intent, confidence, entities)

    def _handle_recommendations(self, session, query, intent, confidence, entities) -> Dict[str, Any]:
        """Provides pedagogically justified recommendations based on criteria."""
        subj = entities.get("subject")
        diff = entities.get("difficulty")
        year = entities.get("academic_year")

        # Academic Year context: Third-Year Computer Engineering
        if year and not subj:
            # For 3rd year CE, recommend core subjects: AI, DBMS, OS, Computer Networks, Software Engineering
            books = query_all("""
                SELECT * FROM books
                WHERE category IN ('Artificial Intelligence', 'Operating Systems', 'Database Management Systems', 'Computer Networks', 'Software Engineering')
                ORDER BY (available_copies > 0) DESC, total_copies DESC LIMIT 5
            """)
            msg = (
                f"🎓 Here are recommended foundational textbooks for **{year}** students, "
                f"covering your Semester 5 & 6 core curriculum (Artificial Intelligence, Operating Systems, DBMS, and Networks):"
            )
            # Add reasons
            enriched = []
            for b in books:
                b_dict = dict(b)
                b_dict["recommendation_reason"] = f"Core reference book for {b['category']} prescribed in the third-year computer engineering syllabus."
                enriched.append(b_dict)

            session.update_turn(query, msg, intent, enriched, subject="Third-Year CE")
            return {
                "message": msg,
                "intent": intent,
                "confidence": confidence,
                "entities": entities,
                "books": enriched,
                "suggested_questions": [
                    "Which of them are beginner friendly?",
                    "Is Artificial Intelligence by Stuart Russell available?",
                    "How many books can I borrow?"
                ],
                "session_id": session.session_id
            }

        recs = self.recommender.recommend(subject=subj, difficulty=diff, limit=4)

        diff_str = f" for **{diff}** level" if diff else ""
        subj_str = f" in **{subj}**" if subj else ""
        msg = f"💡 Here are top recommended textbooks{subj_str}{diff_str} currently in our library:"

        session.update_turn(query, msg, intent, recs, subject=subj, difficulty=diff)
        return {
            "message": msg,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "books": recs,
            "suggested_questions": [
                f"Is {recs[0]['title']} available?",
                "Which one is best for beginners?" if not diff else "Show all books in this category",
                "What is the borrowing duration?"
            ],
            "session_id": session.session_id
        }

    def _handle_book_search(self, session, query, intent, confidence, entities) -> Dict[str, Any]:
        """Performs search by title, subject, category, difficulty, or keywords."""
        subj = entities.get("subject")
        diff = entities.get("difficulty")
        title = entities.get("book_title")
        author = entities.get("author")
        shelf = entities.get("shelf")

        sql = "SELECT * FROM books WHERE 1=1"
        params: List[Any] = []

        if title:
            sql += " AND title LIKE ?"
            params.append(f"%{title}%")
        elif author:
            sql += " AND author LIKE ?"
            params.append(f"%{author}%")
        elif shelf:
            sql += " AND shelf_number = ?"
            params.append(shelf)
        elif subj:
            sql += " AND (category LIKE ? OR subject LIKE ? OR title LIKE ?)"
            term = f"%{subj}%"
            params.extend([term, term, term])
        else:
            # Keyword search across title, author, subject, description
            STOP_WORDS = {
                "what", "books", "book", "available", "show", "find", "have", "some",
                "read", "need", "give", "list", "you", "for", "with", "the", "and",
                "are", "any", "all", "can", "get", "there", "about", "related", "does",
                "please", "search", "like", "want", "would", "know", "check"
            }
            clean_tokens = [t for t in re.findall(r"\b[a-zA-Z0-9+#]{3,}\b", query.lower())
                            if t not in STOP_WORDS]
            if clean_tokens:
                sub_clauses = []
                for t in clean_tokens:
                    sub_clauses.append("(title LIKE ? OR author LIKE ? OR subject LIKE ? OR description LIKE ? OR category LIKE ?)")
                    p = f"%{t}%"
                    params.extend([p, p, p, p, p])
                # Require all distinct search keywords to match (AND logic)
                sql += f" AND ({' AND '.join(sub_clauses)})"
            else:
                sql += " AND 1=1"

        if diff:
            sql += " AND difficulty = ?"
            params.append(diff)

        # Ordering: available first, then total copies
        sql += " ORDER BY (available_copies > 0) DESC, total_copies DESC LIMIT 6"

        books = query_all(sql, tuple(params))

        # Check if no matching books found
        if not books:
            search_term = title or subj or (" ".join(clean_tokens) if 'clean_tokens' in locals() and clean_tokens else "")
            term_mention = f" for **'{search_term}'**" if search_term else ""
            msg = (
                f"I couldn't find any books{term_mention} in the current library database.\n\n"
                f"You can try searching for related topics such as **Artificial Intelligence**, "
                f"**Data Structures**, **Computer Architecture**, **Operating Systems**, or **Advanced Computing**."
            )
            session.update_turn(query, msg, intent, [])
            return {
                "message": msg,
                "intent": intent,
                "confidence": confidence,
                "entities": entities,
                "books": [],
                "suggested_questions": [
                    "What books are available for Python?",
                    "Show books related to machine learning",
                    "List all categories"
                ],
                "session_id": session.session_id
            }

        # Build helpful introductory message
        if subj and diff:
            intro = f"I found **{len(books)} {diff}-level book(s)** for **{subj}**:"
        elif subj:
            intro = f"Yes! I found **{len(books)} book(s)** related to **{subj}**:"
        elif title:
            intro = f"I found the following matching book in our catalog:"
        else:
            intro = f"I found **{len(books)} relevant book(s)** in the library catalog:"

        session.update_turn(query, intro, intent, books, subject=subj, difficulty=diff)
        return {
            "message": intro,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "books": books,
            "suggested_questions": [
                "Which of them are beginner friendly?" if not diff else "Is the first book available to borrow?",
                "How many books can I borrow?",
                "Where can I find these books?"
            ],
            "session_id": session.session_id
        }

# Singleton instance
rag_engine = RAGEngine()
