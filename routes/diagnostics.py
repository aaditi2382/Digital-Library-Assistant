"""
AI Architecture and Viva Diagnostics endpoint for Digital Library Assistant.
Designed for 3rd-year Computer Engineering AI CI3 Viva presentation.
"""

from fastapi import APIRouter
from app.nlp.intent_classifier import INTENTS, classifier
from app.nlp.entity_extractor import extractor

router = APIRouter(prefix="/api/ai", tags=["AI Diagnostics"])

VIVA_QUESTIONS = [
    {
        "q": "What is the role of Natural Language Processing (NLP) in this Digital Library Assistant?",
        "a": "NLP bridges the gap between student natural-language queries (e.g., 'Do you have beginner Python books?') and structured database queries. It extracts user intent, entities (subject, difficulty level, book title, author), and maintains conversational context."
    },
    {
        "q": "How does the Intent Detection mechanism work in your system?",
        "a": "The system employs a hybrid two-tier approach: First, deterministic regex rules check for unambiguous patterns (such as 'opening hours' or 'fine for returning late'). Second, a TF-IDF vectorizer and Cosine Similarity calculate distance against an exemplar corpus of 15 library intents, providing robust classification and confidence scoring without heavy GPU requirements."
    },
    {
        "q": "How does this application implement Retrieval-Augmented Generation (RAG)?",
        "a": "Instead of letting an AI model hallucinate non-existent books or incorrect copy counts, user questions trigger grounded information retrieval from our SQLite database. The retrieved facts (actual titles, available copies, shelf codes, library rules) form the authoritative ground truth context used to construct the answer."
    },
    {
        "q": "How does the chatbot handle conversation memory and follow-up questions?",
        "a": "A SessionContext manager tracks the current state per user (last_books, active_book, last_subject, last_difficulty). When an anaphoric referent is detected (like 'Which of them are beginner friendly?' or 'Is it available?'), the engine resolves the pronoun against the previously retrieved records rather than searching from scratch."
    },
    {
        "q": "How do you guarantee AI safety and zero hallucinations?",
        "a": "The system applies strict grounding verification: availability is reported strictly from the 'available_copies' field in the database. If a book doesn't exist, the system explicitly reports that no records match and suggests related domains rather than inventing titles."
    },
    {
        "q": "How does the book recommendation algorithm work?",
        "a": "It utilizes content-based filtering factoring in domain category, requested proficiency/difficulty (Beginner/Intermediate/Advanced), circulation popularity, and real-time availability bonus. Each recommended book is returned with an academic pedagogical rationale explaining why it suits the student's level."
    }
]

SAMPLE_DIAGNOSTIC_QUERIES = [
    "What books are available for Python?",
    "Is Clean Code available?",
    "Recommend some books for learning data structures.",
    "What is the fine for returning a book late?",
    "What are the library opening hours?",
    "Where can I find the Database Management Systems books?"
]

@router.get("/diagnostics")
async def get_ai_diagnostics():
    """Returns AI architecture diagnostics and viva reference questions."""
    tests = []
    for q in SAMPLE_DIAGNOSTIC_QUERIES:
        intent_res = classifier.predict(q)
        entities = extractor.extract(q)
        tests.append({
            "query": q,
            "detected_intent": intent_res["intent"],
            "confidence": intent_res["confidence"],
            "extracted_subject": entities["subject"],
            "extracted_difficulty": entities["difficulty"],
            "extracted_title": entities["book_title"]
        })

    return {
        "project_name": "Digital Library Assistant",
        "academic_course": "Third-Year Computer Engineering AI Course CI3 Project",
        "architecture_pipeline": [
            {"stage": 1, "name": "Input Preprocessing & Tokenization", "desc": "Cleans text, normalizes tokens, and isolates alphanumeric terms."},
            {"stage": 2, "name": "Hybrid Intent Detection", "desc": "Applies deterministic rule matching and TF-IDF Cosine Similarity across 15 library intents."},
            {"stage": 3, "name": "Entity & Slot Extraction", "desc": "Extracts book titles, author names, shelf codes, subjects, and difficulty levels."},
            {"stage": 4, "name": "Context & Pronoun Resolution", "desc": "SessionContext manager resolves 'them', 'it', and follow-up constraints against prior turn results."},
            {"stage": 5, "name": "Grounded Database Retrieval (RAG)", "desc": "Queries SQLite knowledge base as single source of truth to avoid hallucinations."},
            {"stage": 6, "name": "Structured NLG & UI Response", "desc": "Formats natural language response with interactive book cards, availability badges, and suggested prompts."}
        ],
        "intents": INTENTS,
        "live_intent_tests": tests,
        "viva_questions": VIVA_QUESTIONS
    }
