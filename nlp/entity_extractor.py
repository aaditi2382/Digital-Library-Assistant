"""
Entity and Slot Extractor for Digital Library Assistant.
Extracts structured parameters from student queries:
- Subject / Category
- Difficulty Level (Beginner / Intermediate / Advanced)
- Book Title candidate
- Author candidate
- Shelf Number / ISBN
- Academic Target Year (e.g., Third-Year Computer Engineering)
- Anaphoric references ('it', 'them', 'which one', 'this book')
"""

import re
import difflib
from typing import Dict, Any, List, Optional
from app.database import query_all

KNOWN_SUBJECTS = {
    "python": "Python",
    "java": "Java",
    "c++": "C/C++",
    "cpp": "C/C++",
    "c programming": "C/C++",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Machine Learning",
    "nlp": "Artificial Intelligence",
    "natural language processing": "Artificial Intelligence",
    "data structure": "Data Structures",
    "data structures": "Data Structures",
    "ds": "Data Structures",
    "algorithm": "Algorithms",
    "algorithms": "Algorithms",
    "clrs": "Algorithms",
    "dbms": "Database Management Systems",
    "database": "Database Management Systems",
    "databases": "Database Management Systems",
    "sql": "Database Management Systems",
    "data mining": "Database Management Systems",
    "operating system": "Operating Systems",
    "operating systems": "Operating Systems",
    "os": "Operating Systems",
    "network": "Computer Networks",
    "networks": "Computer Networks",
    "networking": "Computer Networks",
    "computer networks": "Computer Networks",
    "web": "Web Development",
    "web development": "Web Development",
    "javascript": "Web Development",
    "react": "Web Development",
    "html": "Web Development",
    "cloud": "Cloud Computing",
    "cloud computing": "Cloud Computing",
    "aws": "Cloud Computing",
    "devops": "Cloud Computing",
    "security": "Cyber Security",
    "cyber security": "Cyber Security",
    "cryptography": "Cyber Security",
    "hacking": "Cyber Security",
    "software engineering": "Software Engineering",
    "clean code": "Software Engineering",
    "design patterns": "Software Engineering",
    "math": "Mathematics",
    "mathematics": "Mathematics",
    "discrete mathematics": "Mathematics",
    "linear algebra": "Mathematics",
    "engineering": "Engineering",
    "computer architecture": "Engineering",
    "theory of computation": "Engineering",
    "automata": "Engineering"
}

DIFFICULTY_PATTERNS = {
    "Beginner": [
        r"\bbeginner\b", r"\bbeginners\b", r"\bbasics?\b", r"\bfrom scratch\b",
        r"\bintroductory\b", r"\bintroduction\b", r"\bfundamentals?\b", r"\beasy\b",
        r"\bstarting out\b", r"\bnovice\b"
    ],
    "Advanced": [
        r"\badvanced\b", r"\bexpert\b", r"\bdeep\b", r"\bin-depth\b",
        r"\bmastery\b", r"\bcomplex\b", r"\bresearch\b"
    ],
    "Intermediate": [
        r"\bintermediate\b", r"\bpractitioner\b", r"\bmedium\b"
    ]
}

YEAR_PATTERNS = [
    r"\bthird[- ]year\b", r"\b3rd[- ]year\b", r"\bte\b", r"\bthird year\b",
    r"\bfinal[- ]year\b", r"\b4th[- ]year\b", r"\bbe\b", r"\bsecond[- ]year\b",
    r"\b2nd[- ]year\b", r"\bse\b", r"\bfirst[- ]year\b", r"\b1st[- ]year\b", r"\bfe\b"
]

class EntityExtractor:
    """Extracts entities and slots from natural language queries."""

    def __init__(self):
        self._cached_titles: List[str] = []
        self._cached_authors: List[str] = []
        self._load_catalog_cache()

    def _load_catalog_cache(self):
        """Loads known titles and authors for fuzzy matching."""
        try:
            books = query_all("SELECT title, author FROM books")
            self._cached_titles = [b["title"] for b in books]
            
            # Split authors into individual names
            authors = set()
            for b in books:
                raw = b["author"]
                for a in re.split(r",|\sand\s|&", raw):
                    a_clean = a.strip()
                    if len(a_clean) > 3:
                        authors.add(a_clean)
            self._cached_authors = list(authors)
        except Exception:
            self._cached_titles = []
            self._cached_authors = []

    def extract(self, query: str) -> Dict[str, Any]:
        """Extracts all entities and detected parameters from a query string."""
        text = query.strip()
        lower_text = text.lower()

        # 1. Subject / Category
        matched_subject = None
        # Sort keys by length descending to match longest phrase first (e.g., 'machine learning' before 'learning')
        sorted_subj_keys = sorted(KNOWN_SUBJECTS.keys(), key=len, reverse=True)
        for key in sorted_subj_keys:
            pattern = r"\b" + re.escape(key) + r"\b"
            if re.search(pattern, lower_text):
                matched_subject = KNOWN_SUBJECTS[key]
                break

        # 2. Difficulty
        matched_difficulty = None
        for diff_level, patterns in DIFFICULTY_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, lower_text):
                    matched_difficulty = diff_level
                    break
            if matched_difficulty:
                break

        # 3. Target Academic Year
        matched_year = None
        for y_pat in YEAR_PATTERNS:
            if re.search(y_pat, lower_text):
                if "third" in lower_text or "3rd" in lower_text or "te" in lower_text:
                    matched_year = "Third Year (TE) Computer Engineering"
                elif "final" in lower_text or "4th" in lower_text or "be" in lower_text:
                    matched_year = "Final Year (BE) Computer Engineering"
                elif "second" in lower_text or "2nd" in lower_text or "se" in lower_text:
                    matched_year = "Second Year (SE) Computer Engineering"
                break

        # 4. Shelf code (e.g. CS-04, ENG-01)
        shelf_match = re.search(r"\b([A-Z]{2,3}-\d{2})\b", text, re.IGNORECASE)
        matched_shelf = shelf_match.group(1).upper() if shelf_match else None

        # 5. ISBN code
        isbn_match = re.search(r"\b(978[-\d]{10,14})\b", text)
        matched_isbn = isbn_match.group(1) if isbn_match else None

        # 6. Book Title candidate (Fuzzy match + Quoted string + Regex extract)
        matched_title = self._extract_title(text, lower_text)

        # 7. Author candidate
        matched_author = self._extract_author(text, lower_text)

        # 8. Anaphora / Follow-up Reference Detection
        has_anaphora = bool(re.search(
            r"\b(them|it|this book|that book|these books|which one|which of them|available\?)\b",
            lower_text
        ))

        return {
            "subject": matched_subject,
            "difficulty": matched_difficulty,
            "academic_year": matched_year,
            "shelf": matched_shelf,
            "isbn": matched_isbn,
            "book_title": matched_title,
            "author": matched_author,
            "has_anaphora": has_anaphora,
            "raw_query": text
        }

    def _extract_title(self, text: str, lower_text: str) -> Optional[str]:
        """Extracts book title using quotes, common patterns, or fuzzy matching against catalog."""
        # Check quoted strings first: e.g., "Clean Code"
        quote_match = re.search(r'["\']([^"\']{3,50})["\']', text)
        if quote_match:
            candidate = quote_match.group(1)
            # Find closest match in catalog
            close = difflib.get_close_matches(candidate, self._cached_titles, n=1, cutoff=0.5)
            return close[0] if close else candidate

        # Check pattern: "is <Title> available", "details of <Title>", "book <Title>"
        avail_patterns = [
            r"is\s+([a-zA-Z0-9\s:,\-]{3,40}?)\s+(?:available|in stock)",
            r"availability of\s+([a-zA-Z0-9\s:,\-]{3,40})",
            r"details of\s+([a-zA-Z0-9\s:,\-]{3,40})",
            r"tell me about\s+([a-zA-Z0-9\s:,\-]{3,40})",
            r"book\s+([a-zA-Z0-9\s:,\-]{4,40})"
        ]
        for pat in avail_patterns:
            m = re.search(pat, lower_text)
            if m:
                extracted = m.group(1).strip()
                # filter out non-titles like "python", "any books"
                if extracted not in ["python", "any books", "there", "it", "this"]:
                    close = difflib.get_close_matches(extracted, [t.lower() for t in self._cached_titles], n=1, cutoff=0.55)
                    if close:
                        # return original title casing
                        idx = [t.lower() for t in self._cached_titles].index(close[0])
                        return self._cached_titles[idx]

        # Scan for known titles directly inside query text
        # Ignore titles that just match broad subjects if the query is a general topic query
        subject_names = [s.lower() for s in KNOWN_SUBJECTS.keys()]
        for title in self._cached_titles:
            t_clean = re.sub(r":.*$", "", title).strip() # before colon
            if len(t_clean) > 4:
                # If t_clean is just a generic subject name (e.g. "Deep Learning", "Machine Learning")
                # and user query says "learn machine learning", "books on machine learning", don't extract as title
                if t_clean.lower() in subject_names:
                    pattern = r"(?:book|title|called|named|read)\s+['\"]?" + re.escape(t_clean.lower()) + r"['\"]?"
                    if re.search(pattern, lower_text):
                        return title
                    continue

                if t_clean.lower() in lower_text:
                    return title

        return None

    def _extract_author(self, text: str, lower_text: str) -> Optional[str]:
        """Extracts author name from query."""
        # e.g., "books by stuart russell", "written by cormen", "by tanenbaum"
        author_match = re.search(r"(?:by|written by|author\s+is|author\s+of\s+([a-zA-Z\s]+)\s+is)\s+([a-zA-Z\s\.]+)", lower_text)
        if author_match:
            candidate = author_match.group(2).strip()
            # check against known authors
            for auth in self._cached_authors:
                if auth.lower() in candidate or candidate in auth.lower():
                    return auth
                # check surname
                surname = auth.split()[-1].lower()
                if len(surname) > 3 and surname in candidate:
                    return auth

        # Direct scan of cached authors
        for auth in self._cached_authors:
            if auth.lower() in lower_text:
                return auth
            surname = auth.split()[-1].lower()
            if len(surname) > 3 and f" {surname} " in f" {lower_text} ":
                return auth

        return None

# Singleton instance
extractor = EntityExtractor()
