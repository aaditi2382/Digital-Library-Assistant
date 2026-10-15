"""
Book Recommendation Engine for Digital Library Assistant.
Uses content-based scoring based on subject, difficulty, student academic year,
and availability status, generating grounded academic reasons for recommendation.
"""

from typing import List, Dict, Any, Optional
from app.database import query_all

RECOMMENDATION_REASONS = {
    "Artificial Intelligence: A Modern Approach": "Widely considered the gold standard textbook in AI, offering rigorous mathematical depth and comprehensive coverage of rational agents, search algorithms, and logic systems.",
    "Artificial Intelligence: Foundations of Computational Agents": "Outstanding conceptual focus on autonomous agent architecture and structured representation, ideal for advanced undergraduate projects.",
    "Natural Language Processing with Python": "Hands-on, accessible introduction combining linguistic theory with practical NLTK code examples in Python.",
    "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow": "The highest-rated practical machine learning book, taking you seamlessly from linear regression to deep neural architectures with production-ready code.",
    "Pattern Recognition and Machine Learning": "Exceptional mathematical rigour for students preparing for graduate-level AI or machine learning research.",
    "Introduction to Algorithms": "The world-famous 'CLRS' bible for algorithms, indispensable for university exams, competitive programming, and technical interviews.",
    "Grokking Algorithms: An Illustrated Guide for Programmers": "Best visual, conceptual introduction to algorithms; uses fun diagrams and simple analogies to demystify binary search and graph algorithms.",
    "Data Structures and Algorithms in Java": "Highly recommended for students who prefer Java, featuring step-by-step memory diagrams and self-test programming exercises.",
    "Database System Concepts": "The definitive university textbook for database systems (Korth & Silberschatz), perfect for university syllabus exams and relational theory.",
    "Operating System Concepts": "The famous 'Dinosaur Book' that clearly explains process scheduling, thread synchronization, semaphores, and memory management.",
    "Computer Networks": "Tanenbaum's classic text providing unmatched architectural clarity on the OSI and TCP/IP protocol stacks.",
    "Clean Code: A Handbook of Agile Software Craftsmanship": "Essential reading for every software engineer; teaches actionable principles to write maintainable, professional, readable code.",
    "Head First Design Patterns": "The most engaging, beginner-friendly guide to mastering the 23 Gang of Four object-oriented design patterns.",
    "Python Crash Course: A Hands-On, Project-Based Introduction": "The #1 recommended book for beginners in Python, featuring real-world arcade game and web app mini-projects.",
    "Automate the Boring Stuff with Python": "Super practical for students wanting to immediately apply Python to automate everyday tasks and web scraping.",
    "Head First Java": "Visual, interactive pedagogy that makes Java fundamentals, object inheritance, and memory management intuitive.",
    "The C Programming Language": "The immortal K&R classic; the cleanest, most concise guide to understanding low-level pointers and memory layout.",
    "Eloquent JavaScript: A Modern Introduction to Programming": "Deep, comprehensive exploration of modern JavaScript and web architectures.",
    "Architecting the Cloud: Design Decisions for Cloud Computing": "Crucial design patterns and trade-offs when transitioning monolithic software to cloud environments.",
    "CompTIA Security+ Get Certified Get Ahead: SY0-601": "The clearest foundational textbook covering network defense, cryptography basics, and threat modeling."
}

def generate_recommendation_reason(book: Dict[str, Any], requested_diff: Optional[str] = None) -> str:
    """Generates an academic pedagogical reason for why this book is recommended."""
    title = book.get("title", "")
    for known_title, reason in RECOMMENDATION_REASONS.items():
        if known_title.lower() in title.lower():
            return reason

    # Dynamic fallback reason based on metadata
    diff = book.get("difficulty", "Intermediate")
    copies = book.get("available_copies", 0)
    category = book.get("category", "Computer Science")

    if diff == "Beginner":
        base = f"Highly suited for beginners in {category} with clear foundational concepts and accessible examples."
    elif diff == "Advanced":
        base = f"Advanced, in-depth reference for {category} offering thorough technical rigor and real-world depth."
    else:
        base = f"Comprehensive standard reference textbook for {category} balancing theory and practical implementation."

    if copies > 0:
        return f"{base} Currently available on Shelf {book.get('shelf_number', 'General')} for immediate checkout."
    else:
        return f"{base} (Currently all copies are checked out, but you can place a reservation hold)."

class Recommender:
    """Intelligent Content-based Recommender for Library Resources."""

    def recommend(
        self,
        subject: Optional[str] = None,
        difficulty: Optional[str] = None,
        academic_year: Optional[str] = None,
        limit: int = 4,
        exclude_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommends books matching subject and difficulty constraints,
        scored by availability and relevance.
        """
        query = "SELECT * FROM books WHERE 1=1"
        params: List[Any] = []

        if subject:
            query += " AND (category LIKE ? OR subject LIKE ? OR title LIKE ?)"
            term = f"%{subject}%"
            params.extend([term, term, term])

        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)

        if exclude_ids:
            placeholders = ",".join(["?"] * len(exclude_ids))
            query += f" AND id NOT IN ({placeholders})"
            params.extend(exclude_ids)

        # Prioritize available copies and total popularity
        query += " ORDER BY (available_copies > 0) DESC, total_copies DESC, publication_year DESC LIMIT ?"
        params.append(limit)

        books = query_all(query, tuple(params))

        # If strict difficulty returned fewer than requested, relax difficulty constraint
        if len(books) < limit and difficulty:
            relaxed_query = "SELECT * FROM books WHERE (category LIKE ? OR subject LIKE ?)"
            term = f"%{subject}%" if subject else "%"
            r_params: List[Any] = [term, term]
            if exclude_ids:
                placeholders = ",".join(["?"] * len(exclude_ids))
                relaxed_query += f" AND id NOT IN ({placeholders})"
                r_params.extend(exclude_ids)
            already_ids = [b["id"] for b in books]
            if already_ids:
                p_in = ",".join(["?"] * len(already_ids))
                relaxed_query += f" AND id NOT IN ({p_in})"
                r_params.extend(already_ids)
            relaxed_query += " ORDER BY (available_copies > 0) DESC, total_copies DESC LIMIT ?"
            r_params.append(limit - len(books))
            additional = query_all(relaxed_query, tuple(r_params))
            books.extend(additional)

        # Enrich with personalized recommendation reasons
        enriched = []
        for b in books:
            b_dict = dict(b)
            b_dict["recommendation_reason"] = generate_recommendation_reason(b_dict, difficulty)
            enriched.append(b_dict)

        return enriched

# Singleton instance
recommender = Recommender()
