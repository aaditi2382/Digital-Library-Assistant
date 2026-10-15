"""
Intent Classifier for Digital Library Assistant.
Uses a hybrid approach of regex pattern matching + TF-IDF Vector Cosine Similarity
over an exemplar corpus for 15 library-specific intents.
Suitable for Viva demonstration in a 3rd-year Computer Engineering AI course.
"""

import re
import math
from typing import Dict, Any, List, Tuple

INTENTS = {
    "book_search": "Search for books by topic, title, keywords, or programming language",
    "book_availability": "Check if a specific book is currently available and how many copies remain",
    "book_details": "Request full details, publisher, edition, or description of a book",
    "author_search": "Find books written by a specific author or query who authored a book",
    "category_search": "Explore categories or find books in a specific branch/domain",
    "book_recommendation": "Ask for suggestions or recommendations based on skill level or subject",
    "library_timings": "Inquire about library opening hours, closing hours, weekends, or holidays",
    "borrowing_rules": "Ask about borrowing limits, maximum books, or borrowing period",
    "renewal_info": "Inquire about how to renew borrowed books and renewal limits",
    "fine_info": "Ask about overdue fines, late return charges, or penalty rates",
    "library_rules": "Ask about reading room rules, mobile policy, food policy, conduct",
    "membership_info": "Ask how to get a library card, membership fees, or student eligibility",
    "location_shelf": "Ask where a book or department section is located physically",
    "general_library": "Ask general questions about the library, address, contact, email",
    "greeting": "Polite conversation greeting or farewell",
    "off_topic": "Questions completely unrelated to the library or academic topics",
    "unknown": "Query that could not be recognized"
}

# Exemplar training sentences for each intent
INTENT_EXEMPLARS: Dict[str, List[str]] = {
    "book_search": [
        "what books are available for python",
        "do you have python books",
        "show me books related to machine learning",
        "find books on dbms",
        "search books on operating systems",
        "what books are available for third year computer engineering students",
        "list books about computer networks",
        "show me java books",
        "find books about data structures",
        "any books on cloud computing",
        "do you have c++ programming books",
        "books for web development",
        "search for discrete mathematics",
        "i need books on cyber security"
    ],
    "book_availability": [
        "is clean code available",
        "is operating system concepts available",
        "how many copies of this book are available",
        "is artificial intelligence a modern approach in stock",
        "check availability of introduction to algorithms",
        "can i get fluent python right now",
        "are there any copies left of clrs",
        "is it available",
        "is this book available to borrow",
        "check if head first java is available"
    ],
    "book_details": [
        "tell me more about this book",
        "what is the isbn of clean code",
        "give me details of operating system concepts",
        "who published introduction to algorithms",
        "what edition is artificial intelligence a modern approach",
        "book details of modern operating systems",
        "describe head first java",
        "show book info for fluent python"
    ],
    "author_search": [
        "who is the author of this book",
        "who wrote clean code",
        "books by stuart russell",
        "do you have books by tanenbaum",
        "find books written by cormen",
        "books by robert c martin",
        "who wrote operating system concepts",
        "author of speech and language processing",
        "books by aurélien géron"
    ],
    "category_search": [
        "what categories of books do you have",
        "show all library categories",
        "list departments and categories",
        "what subjects are covered in the library",
        "show me the book categories"
    ],
    "book_recommendation": [
        "recommend some books for learning data structures",
        "i need beginner level java books",
        "what should i read to learn machine learning from scratch",
        "recommend good python books for a beginner",
        "suggest books for third year computer engineering",
        "which book is best for artificial intelligence",
        "give me book recommendations for deep learning",
        "i want to learn artificial intelligence from basics",
        "suggest good books for competitive programming"
    ],
    "library_timings": [
        "what are the library opening hours",
        "when does the library open",
        "what time does the library close",
        "is the library open on saturday",
        "what are the working days and holidays",
        "library timings",
        "when is the library closed",
        "are you open on sundays"
    ],
    "borrowing_rules": [
        "how can i issue a book",
        "how many books can i borrow",
        "what is the maximum number of books i can borrow",
        "how long can i keep a borrowed book",
        "what is the borrowing period for students",
        "how many days can i keep a book",
        "how do i check out a book",
        "borrowing limit for third year students"
    ],
    "renewal_info": [
        "how can i renew my borrowed book",
        "can i renew a book online",
        "what is the renewal policy",
        "how many times can i renew a book",
        "extend due date for book"
    ],
    "fine_info": [
        "what is the fine for returning a book late",
        "how much is the late return fee",
        "what is the penalty for overdue books",
        "fine rules per day",
        "what happens if i return a book after due date"
    ],
    "library_rules": [
        "what are the library rules",
        "can i bring food inside the library",
        "are mobile phones allowed in the library",
        "what is the lost book policy",
        "what if i damage or lose a book",
        "rules and regulations of the library",
        "is talking allowed in the reading hall"
    ],
    "membership_info": [
        "how do i get a library card",
        "how to apply for library membership",
        "is library membership free for students",
        "do i need a separate library card",
        "can external students join the library"
    ],
    "location_shelf": [
        "where can i find the database management systems books",
        "where is shelf cs-04",
        "where are python books kept",
        "location of artificial intelligence books",
        "where is the reading hall located",
        "what floor are computer science books on",
        "where can i find it"
    ],
    "general_library": [
        "what is the library contact email",
        "who is the chief librarian",
        "what is the library phone number",
        "how do i contact the library helpdesk",
        "where is the library situated on campus"
    ],
    "greeting": [
        "hi", "hello", "hey", "good morning", "good evening", "namaste", "how are you", "thanks", "thank you"
    ],
    "off_topic": [
        "what is the capital of france",
        "who won the world cup",
        "tell me a joke about dogs",
        "who is the president of the united states",
        "write a poem about love",
        "what is 45 plus 90",
        "what is the weather today",
        "can you book a flight for me"
    ]
}

def _tokenize(text: str) -> List[str]:
    """Simple alphanumeric tokenizer with lowercase normalization."""
    return re.findall(r"\b[a-z0-9+#]+\b", text.lower())

def _build_tfidf_vectorizer():
    """Builds an in-memory TF-IDF dictionary for fast cosine similarity without heavy ML dependencies."""
    doc_freq: Dict[str, int] = {}
    doc_count = 0
    all_exemplars: List[Tuple[str, List[str]]] = []

    for intent, examples in INTENT_EXEMPLARS.items():
        for ex in examples:
            tokens = _tokenize(ex)
            all_exemplars.append((intent, tokens))
            unique_tokens = set(tokens)
            for t in unique_tokens:
                doc_freq[t] = doc_freq.get(t, 0) + 1
            doc_count += 1

    idf: Dict[str, float] = {}
    for term, freq in doc_freq.items():
        idf[term] = math.log((1.0 + doc_count) / (1.0 + freq)) + 1.0

    return all_exemplars, idf

ALL_EXEMPLARS, IDF_DICT = _build_tfidf_vectorizer()

def _compute_vector(tokens: List[str]) -> Dict[str, float]:
    """Computes TF-IDF vector for given tokens."""
    tf: Dict[str, int] = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    
    vec: Dict[str, float] = {}
    total_len = len(tokens) or 1
    for t, count in tf.items():
        weight = (count / total_len) * IDF_DICT.get(t, 1.0)
        vec[t] = weight
    return vec

def _cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    """Calculates cosine similarity between two sparse term vectors."""
    common_keys = set(vec1.keys()) & set(vec2.keys())
    if not common_keys:
        return 0.0
    dot = sum(vec1[k] * vec2[k] for k in common_keys)
    norm1 = math.sqrt(sum(v * v for v in vec1.values()))
    norm2 = math.sqrt(sum(v * v for v in vec2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

class IntentClassifier:
    """Fast, explainable hybrid intent classifier."""

    def __init__(self):
        self.exemplars = ALL_EXEMPLARS
        self.idf = IDF_DICT

    def predict(self, query: str) -> Dict[str, Any]:
        """
        Predicts intent and confidence score for a user query.
        Returns:
            {
                "intent": str,
                "confidence": float,
                "is_off_topic": bool,
                "is_greeting": bool,
                "matched_pattern": Optional[str]
            }
        """
        clean_text = query.strip().lower()
        if not clean_text:
            return {"intent": "unknown", "confidence": 0.0, "is_off_topic": False, "is_greeting": False}

        # 1. Direct Regex / Keyword Rules for High Precision
        rule_intent = self._rule_based_check(clean_text)
        if rule_intent:
            return {
                "intent": rule_intent["intent"],
                "confidence": 0.95,
                "is_off_topic": rule_intent["intent"] == "off_topic",
                "is_greeting": rule_intent["intent"] == "greeting",
                "matched_pattern": rule_intent.get("pattern")
            }

        # 2. TF-IDF Cosine Similarity against exemplar corpus
        query_tokens = _tokenize(clean_text)
        if not query_tokens:
            return {"intent": "unknown", "confidence": 0.0, "is_off_topic": False, "is_greeting": False}

        q_vec = _compute_vector(query_tokens)

        best_intent = "unknown"
        best_score = 0.0

        for intent, ex_tokens in self.exemplars:
            ex_vec = _compute_vector(ex_tokens)
            score = _cosine_similarity(q_vec, ex_vec)
            if score > best_score:
                best_score = score
                best_intent = intent

        # Thresholds
        if best_score < 0.25:
            # Check if query contains any book/technical keywords
            tech_keywords = ["python", "java", "book", "read", "ai", "ml", "dbms", "os", "network", "cloud", "security", "author", "copies"]
            if any(k in clean_text for k in tech_keywords):
                best_intent = "book_search"
                best_score = 0.50
            else:
                best_intent = "unknown"

        return {
            "intent": best_intent,
            "confidence": round(best_score, 3),
            "is_off_topic": best_intent == "off_topic",
            "is_greeting": best_intent == "greeting",
            "matched_pattern": "tfidf_cosine_match"
        }

    def _rule_based_check(self, text: str) -> Dict[str, str]:
        """Explicit regex rules for unambiguous queries."""
        # Greetings
        if re.search(r"^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening)|namaste)\b", text):
            return {"intent": "greeting", "pattern": "greeting_rule"}
        
        # Thanks
        if re.search(r"^(thanks|thank\s+you|thx|great thanks|appreciate it)\b", text):
            return {"intent": "greeting", "pattern": "thanks_rule"}

        # Off-topic checks (e.g. capital of france, weather, politics)
        if re.search(r"(capital of|who won the|prime minister|president of|weather today|tell me a joke|write a poem|sing a song|book a flight)", text):
            return {"intent": "off_topic", "pattern": "off_topic_rule"}

        # Timings / Hours
        if re.search(r"(opening hour|closing hour|library timing|timings|when does the library open|when does the library close|open on (saturday|sunday)|working day|working hours)", text):
            return {"intent": "library_timings", "pattern": "timing_rule"}

        # Fine rules
        if re.search(r"(fine|penalty|late fee|overdue charge|return.*late.*fine|fine for returning|late return)", text):
            return {"intent": "fine_info", "pattern": "fine_rule"}

        # Renewal rules
        if re.search(r"(renew|renewal|extend.*due date|can i renew)", text):
            return {"intent": "renewal_info", "pattern": "renewal_rule"}

        # Borrowing rules / limits
        if re.search(r"(how many books.*borrow|maximum.*books.*borrow|borrowing limit|how long.*keep|borrowing duration|how can i issue|issue a book|borrow a book)", text):
            return {"intent": "borrowing_rules", "pattern": "borrow_rule"}

        # Membership
        if re.search(r"(library card|membership|join the library|membership fee|register for library)", text):
            return {"intent": "membership_info", "pattern": "membership_rule"}

        # General Library Rules / Conduct / Lost book
        if re.search(r"(lost.*book|damage.*book|food.*allowed|mobile.*allowed|silence|library rule|rules and regulation)", text):
            return {"intent": "library_rules", "pattern": "rules_rule"}

        # Recommendations
        if re.search(r"(recommend|suggest|what should i read|best book for|beginner friendly|beginner-friendly|from basics|from scratch)", text):
            return {"intent": "book_recommendation", "pattern": "recommend_rule"}

        # Availability
        if re.search(r"(is .* available|availability of|how many copies|in stock|copies left|can i get .* right now)", text):
            return {"intent": "book_availability", "pattern": "availability_rule"}

        # Location / Shelf
        if re.search(r"(where can i find|where is shelf|shelf number|where are .* books kept|where is the .* section|which floor)", text):
            return {"intent": "location_shelf", "pattern": "location_rule"}

        # Author query
        if re.search(r"(who is the author|who wrote|author of|books by )", text):
            return {"intent": "author_search", "pattern": "author_rule"}

        # Categories list
        if re.search(r"(what categories|list categories|all categories|show categories|what subjects)", text):
            return {"intent": "category_search", "pattern": "category_rule"}

        # Book details
        if re.search(r"(details of|isbn of|who published|edition of|tell me more about)", text):
            return {"intent": "book_details", "pattern": "details_rule"}

        return None

# Singleton instance
classifier = IntentClassifier()
