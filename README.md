# 📚 Digital Library Assistant (AI Course CI3 Project)

> **Third-Year Computer Engineering — Artificial Intelligence (CI3) Practical Project**  
> An intelligent conversational library assistant combining Natural Language Processing (NLP), Intent Recognition, Semantic Information Retrieval, and grounded Conversational AI.

---

## 🌟 Project Overview

The **Digital Library Assistant** is a full-stack, AI-powered virtual librarian application engineered specifically for engineering colleges. Students can interact naturally in English to search for course textbooks, check live copy availability, receive personalized study recommendations with pedagogical rationales, navigate physical shelf locations, and clarify library rules and overdue fine policies.

The system is strictly **hallucination-free** through a structured **Retrieval-Augmented Generation (RAG)** architecture: all factual queries are resolved against a real SQLite database as the single source of truth.

---

## 🎯 Key Features

1. **Conversational AI Chatbot**:
   - Understands natural language questions across 15 library-specific intents.
   - Detects user intent and extracts parameters (subject, proficiency level, title, author, shelf code, academic year).
   - Stateful conversation memory: Resolves follow-up queries and pronouns (*"Which of them are beginner friendly?"*, *"Is it available?"*, *"Who is the author?"*).
   - Out-of-domain guardrails: Gracefully handles off-topic inquiries and unknown subjects without fabricating books.

2. **Grounded Real-Time Knowledge Base**:
   - Pre-seeded with **50+ realistic computer engineering and allied textbooks** covering:
     - Artificial Intelligence & Machine Learning
     - Data Structures & Algorithms
     - Database Management Systems (DBMS)
     - Operating Systems
     - Computer Networks
     - Python, Java, C/C++ Programming
     - Web Development & Cloud Computing
     - Cyber Security & Cryptography
     - Software Engineering & Design Patterns
     - Discrete Mathematics & Linear Algebra
     - Computer Architecture & Engineering

3. **Accurate Availability Checking**:
   - Reports exact available vs total copies, physical shelf codes (e.g. `CS-04`), and library wings.
   - Accurately identifies when a book is issued out (e.g., *Architecting the Cloud*).

4. **AI Recommendation Engine**:
   - Content-based filtering matching requested subject, proficiency level (Beginner / Intermediate / Advanced), and real-time availability.
   - Provides academic explanations (*"Why this book is recommended"*).

5. **Student & Admin Portals**:
   - **Student View**: Chatbot assistant, searchable book catalog with live filters, categories browser, recommendations generator, timings & rules guide.
   - **Admin Dashboard**: Real-time statistics (total titles, volume, available vs issued copies, categories, authors), complete book CRUD (Add, Edit, Delete), one-click copy adjuster, and student query NLP audit logs.

6. **Interactive Viva Voce Guide**:
   - Built-in "About Project" section with a 6-stage AI architecture diagram, live classification matrix, and prepared technical Q&A for the examiner.

7. **Voice Input (Speech-to-Text)**:
   - Built-in microphone support using the Web Speech API for voice queries.

---

## 🧠 AI Architecture (6-Stage Pipeline)

```
Student Query (Natural Language)
               │
               ▼
[ Stage 1: Input Preprocessing & Tokenization ]
  • Normalization, alphanumeric token extraction, punctuation removal
               │
               ▼
[ Stage 2: Hybrid Intent Classification ]
  • Rule-based Pattern Matching + TF-IDF Vector Cosine Similarity
  • 15 Intents (book_search, availability, details, recommendation, timings, etc.)
               │
               ▼
[ Stage 3: Entity & Slot Extraction ]
  • Extracts Subject, Difficulty, Title, Author, Shelf Code, Academic Year
               │
               ▼
[ Stage 4: Conversation Memory & Context Resolution ]
  • SessionContext tracks active books and resolves anaphora ("it", "them", "which one")
               │
               ▼
[ Stage 5: Grounded Database Retrieval (RAG) ]
  • Queries SQLite catalog and library_info policies (zero hallucinations)
               │
               ▼
[ Stage 6: Response Generation & Structured Cards ]
  • Generates grounded answer with interactive book cards and follow-up prompts
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Web browser (Chrome, Edge, Firefox)

### 1. Installation
In the project directory:
```bash
# Install lightweight Python dependencies
py -m pip install -r requirements.txt
```

### 2. Run the Application
Launch the server with the one-click runner:
```bash
py run.py
```
Or directly using Uvicorn:
```bash
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Open in Browser
- **Web Application**: [`http://127.0.0.1:8000`](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)
- **AI Diagnostics**: [`http://127.0.0.1:8000/api/ai/diagnostics`](http://127.0.0.1:8000/api/ai/diagnostics)

---

## 🔑 Demo User Credentials

| Role | Username | Password | Access Capabilities |
|---|---|---|---|
| **Student** | `student` | `student123` | Search books, Chatbot, Availability, Recommendations, Policies |
| **Admin** | `admin` | `admin123` | Full Book CRUD, Modify Copies, Edit Policies, View Statistics |

*Note: You can also use the one-click "Switch" button in the bottom-left sidebar of the UI to toggle between Student and Admin personas instantly!*

---

## 🧪 Demo Scenarios & Test Queries

Try these sample queries to demonstrate each requirement:

### 1. Natural Language Book Search
- *"What books are available for Python?"*
- *"Show me books related to machine learning."*
- *"Find books on DBMS"*

### 2. Specific Availability Checking
- *"Is Clean Code available?"* (Returns available copies, shelf `CS-07`, 2nd floor)
- *"Is Architecting the Cloud available?"* (Demonstrates unavailable handling: 0 copies available)

### 3. Conversational Memory & Follow-up Questions
1. User: *"Find books on Python."*
2. User: *"Which of them are beginner friendly?"* (Filters previous turn results to return *Python Crash Course*)
3. User: *"Is it available?"* (Checks availability for the active book)

### 4. Pedagogical Recommendations
- *"I am a beginner in machine learning. What should I read?"*
- *"Recommend some books for learning data structures."*
- *"What books are available for third-year computer engineering students?"*

### 5. Library Policies & Information
- *"What are the library opening hours?"*
- *"How many books can I borrow?"*
- *"What is the fine for returning a book late?"*
- *"How can I issue a book?"*
- *"Where can I find the Database Management Systems books?"*

### 6. AI Safety & Off-Topic Handling
- *"What is the capital of France?"* (Politely redirects back to library assistance)
- *"Do you have quantum computing books?"* (Politely states book is not in database and suggests related topics)

---

## 🎓 Viva Voce Reference Questions & Answers

### Q1. Why is this project relevant to AI and NLP?
**Answer**: It applies practical Natural Language Processing to convert unstructured student queries into structured intent classifications and entity slots. It demonstrates a complete end-to-end RAG architecture with stateful conversation context management.

### Q2. How is Intent Classification implemented?
**Answer**: We implement a hybrid classifier combining deterministic regex rules with TF-IDF vectorization and Cosine Similarity against an exemplar dataset of 15 library intents. This ensures deterministic accuracy for common questions and high semantic generalization without requiring heavy GPU models.

### Q3. How does the system prevent hallucinations?
**Answer**: By enforcing strict grounding. Rather than relying on an LLM's ungrounded memory, the system uses the SQLite database as the single source of truth. Copy availability is dynamically computed from `available_copies`. If a book doesn't exist, the system informs the user and suggests existing topics.

### Q4. How is multi-turn conversation memory maintained?
**Answer**: Each user session is managed by a `SessionContext` object in memory that tracks `last_books`, `last_subject`, `last_difficulty`, and the active book. When anaphoric expressions (*"them"*, *"it"*, *"which one"*) are detected, the system resolves constraints against the previous turn rather than initiating a cold search.

---

## 📁 Project Structure

```
Virtual_library/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application & router mounting
│   ├── database.py              # SQLite connection, schema, and queries
│   ├── seed_data.py             # 50+ books, 16 categories, policies, demo users
│   ├── nlp/
│   │   ├── __init__.py
│   │   ├── intent_classifier.py # Hybrid regex + TF-IDF Cosine Similarity
│   │   ├── entity_extractor.py  # Subject, difficulty, title, author, shelf extraction
│   │   ├── recommender.py       # Content-based recommendation scoring & rationales
│   │   ├── memory.py            # Stateful SessionContext conversation manager
│   │   └── rag_engine.py        # Central grounded dialogue orchestrator
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py              # Chat processing, history, clear endpoints
│   │   ├── books.py             # Catalog search, filter, single book details
│   │   ├── admin.py             # Dashboard statistics, book CRUD, copy adjuster
│   │   ├── info.py              # Library timings, policies, category list
│   │   └── diagnostics.py       # AI pipeline metrics & viva questions
│   └── static/
│       ├── index.html           # Modern single-page web interface
│       ├── css/
│       │   └── style.css        # Glassmorphic UI styles, badges, animations
│       └── js/
│           ├── api.js           # REST API client
│           └── app.js           # Reactive view controller & speech recognition
├── library.db                   # SQLite database (auto-generated)
├── requirements.txt             # Python dependencies
├── run.py                       # One-click launch runner
└── README.md                    # Project documentation & viva guide
```

---

## 👩‍💻 Developed For
- **Course**: Third-Year Computer Engineering — Artificial Intelligence (CI3 Project)
- **Academic Year**: 2026
