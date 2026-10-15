"""
Comprehensive realistic seed data for Digital Library Assistant.
Designed for Third-Year Computer Engineering AI Course CI3 Project.
"""

import hashlib
from app.database import get_db_connection, query_one

def hash_password(password: str) -> str:
    """Simple SHA-256 password hash for demonstration."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

SAMPLE_CATEGORIES = [
    {"name": "Artificial Intelligence", "description": "Core AI principles, intelligent agents, search algorithms, heuristic search, knowledge representation, and expert systems.", "icon": "bot"},
    {"name": "Machine Learning", "description": "Supervised, unsupervised, reinforcement learning, neural networks, deep learning, and statistical pattern recognition.", "icon": "brain"},
    {"name": "Data Structures", "description": "Arrays, linked lists, stacks, queues, trees, graphs, hashing, heaps, and advanced data organization structures.", "icon": "network"},
    {"name": "Algorithms", "description": "Algorithm design techniques, asymptotic analysis, dynamic programming, greedy algorithms, divide-and-conquer, and NP-completeness.", "icon": "git-branch"},
    {"name": "Database Management Systems", "description": "Relational models, SQL, normalization, transaction processing, concurrency control, indexing, and NoSQL databases.", "icon": "database"},
    {"name": "Operating Systems", "description": "Process management, CPU scheduling, synchronization, deadlocks, memory virtualization, file systems, and distributed OS.", "icon": "cpu"},
    {"name": "Computer Networks", "description": "OSI and TCP/IP protocol stacks, routing algorithms, socket programming, transport layer flow control, and wireless networks.", "icon": "globe"},
    {"name": "Web Development", "description": "Frontend and backend web architectures, HTML5, CSS3, JavaScript, modern frameworks, RESTful APIs, and full-stack development.", "icon": "layout"},
    {"name": "Python", "description": "Python programming language, syntax, data structures, scientific computing libraries, scripting, and OOP concepts.", "icon": "terminal"},
    {"name": "Java", "description": "Object-oriented programming with Java, JVM internals, multithreading, collections framework, and enterprise architectures.", "icon": "coffee"},
    {"name": "C/C++", "description": "Procedural and object-oriented low-level systems programming, pointer mechanics, memory management, and modern C++ STL.", "icon": "code-2"},
    {"name": "Cloud Computing", "description": "Virtualization, cloud service models (IaaS, PaaS, SaaS), AWS, Azure, microservices, containerization, and distributed scalability.", "icon": "cloud"},
    {"name": "Cyber Security", "description": "Network security, cryptography, ethical hacking, vulnerability assessment, authentication protocols, and information defense.", "icon": "shield-check"},
    {"name": "Software Engineering", "description": "Agile methodologies, SDLC, design patterns, software testing, refactoring, Clean Code principles, and software architecture.", "icon": "layers"},
    {"name": "Mathematics", "description": "Discrete mathematics, graph theory, linear algebra, probability, calculus, and mathematical logic for computer engineers.", "icon": "calculator"},
    {"name": "Engineering", "description": "Computer architecture, digital logic design, microprocessor interfacing, theory of computation, and systems engineering.", "icon": "binary"}
]

SAMPLE_BOOKS = [
    # 1. Artificial Intelligence
    {
        "isbn": "978-0134610993",
        "title": "Artificial Intelligence: A Modern Approach",
        "author": "Stuart Russell, Peter Norvig",
        "category": "Artificial Intelligence",
        "subject": "Artificial Intelligence",
        "description": "The definitive comprehensive introduction to the theory and practice of artificial intelligence, covering rational agents, problem solving, knowledge representation, reasoning, planning, and machine learning.",
        "publisher": "Pearson Education",
        "publication_year": 2020,
        "edition": "4th Edition",
        "total_copies": 5,
        "available_copies": 3,
        "shelf_number": "CS-01",
        "location": "Central Library - 2nd Floor, AI & Data Science Wing",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-1119501404",
        "title": "Artificial Intelligence: Foundations of Computational Agents",
        "author": "David L. Poole, Alan K. Mackworth",
        "category": "Artificial Intelligence",
        "subject": "Artificial Intelligence",
        "description": "A structured computational approach to understanding natural and artificial intelligence through autonomous decision-making agents and structured representation.",
        "publisher": "Cambridge University Press",
        "publication_year": 2017,
        "edition": "2nd Edition",
        "total_copies": 3,
        "available_copies": 2,
        "shelf_number": "CS-01",
        "location": "Central Library - 2nd Floor, AI & Data Science Wing",
        "language": "English",
        "difficulty": "Advanced"
    },
    {
        "isbn": "978-0596516499",
        "title": "Natural Language Processing with Python",
        "author": "Steven Bird, Ewan Klein, Edward Loper",
        "category": "Artificial Intelligence",
        "subject": "Natural Language Processing",
        "description": "Practical guide to NLP using Python and the Natural Language Toolkit (NLTK), covering tokenization, tagging, parsing, and semantic extraction.",
        "publisher": "O'Reilly Media",
        "publication_year": 2009,
        "edition": "1st Edition",
        "total_copies": 4,
        "available_copies": 4,
        "shelf_number": "CS-02",
        "location": "Central Library - 2nd Floor, AI & Data Science Wing",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-0131873216",
        "title": "Speech and Language Processing",
        "author": "Daniel Jurafsky, James H. Martin",
        "category": "Artificial Intelligence",
        "subject": "Natural Language Processing",
        "description": "The authoritative textbook on computational linguistics, speech recognition, speech synthesis, statistical machine translation, and language modeling.",
        "publisher": "Pearson Prentice Hall",
        "publication_year": 2021,
        "edition": "3rd Draft Edition",
        "total_copies": 3,
        "available_copies": 1,
        "shelf_number": "CS-02",
        "location": "Central Library - 2nd Floor, AI & Data Science Wing",
        "language": "English",
        "difficulty": "Advanced"
    },

    # 2. Machine Learning
    {
        "isbn": "978-1492032649",
        "title": "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow",
        "author": "Aurélien Géron",
        "category": "Machine Learning",
        "subject": "Machine Learning",
        "description": "A hands-on, practical guide demonstrating how to build end-to-end machine learning and deep neural network solutions using modern Python ecosystems.",
        "publisher": "O'Reilly Media",
        "publication_year": 2019,
        "edition": "2nd Edition",
        "total_copies": 6,
        "available_copies": 4,
        "shelf_number": "CS-02",
        "location": "Central Library - 2nd Floor, AI & Data Science Wing",
        "language": "English",
        "difficulty": "Beginner"
    },
    {
        "isbn": "978-0387310732",
        "title": "Pattern Recognition and Machine Learning",
        "author": "Christopher M. Bishop",
        "category": "Machine Learning",
        "subject": "Machine Learning",
        "description": "A comprehensive mathematical and statistical foundation for pattern recognition and Bayesian machine learning algorithms.",
        "publisher": "Springer",
        "publication_year": 2006,
        "edition": "1st Edition",
        "total_copies": 4,
        "available_copies": 2,
        "shelf_number": "CS-02",
        "location": "Central Library - 2nd Floor, AI & Data Science Wing",
        "language": "English",
        "difficulty": "Advanced"
    },
    {
        "isbn": "978-0262035613",
        "title": "Deep Learning",
        "author": "Ian Goodfellow, Yoshua Bengio, Aaron Courville",
        "category": "Machine Learning",
        "subject": "Deep Learning",
        "description": "The quintessential text introducing deep neural networks, mathematical fundamentals, convolutional networks, sequence modeling, and generative models.",
        "publisher": "MIT Press",
        "publication_year": 2016,
        "edition": "1st Edition",
        "total_copies": 4,
        "available_copies": 3,
        "shelf_number": "CS-02",
        "location": "Central Library - 2nd Floor, AI & Data Science Wing",
        "language": "English",
        "difficulty": "Advanced"
    },
    {
        "isbn": "978-1466583283",
        "title": "Machine Learning: An Algorithmic Perspective",
        "author": "Stephen Marsland",
        "category": "Machine Learning",
        "subject": "Machine Learning",
        "description": "Step-by-step introduction to machine learning algorithms accompanied by clear, executable Python code for students.",
        "publisher": "Chapman and Hall/CRC",
        "publication_year": 2015,
        "edition": "2nd Edition",
        "total_copies": 3,
        "available_copies": 3,
        "shelf_number": "CS-02",
        "location": "Central Library - 2nd Floor, AI & Data Science Wing",
        "language": "English",
        "difficulty": "Beginner"
    },

    # 3. Data Structures & Algorithms
    {
        "isbn": "978-0262033848",
        "title": "Introduction to Algorithms",
        "author": "Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein",
        "category": "Algorithms",
        "subject": "Algorithms",
        "description": "Globally renowned reference and textbook (CLRS) on data structures and algorithms, covering sorting, trees, dynamic programming, graph algorithms, and NP-completeness.",
        "publisher": "MIT Press",
        "publication_year": 2009,
        "edition": "3rd Edition",
        "total_copies": 8,
        "available_copies": 5,
        "shelf_number": "CS-03",
        "location": "Central Library - 1st Floor, Core Computing Stacks",
        "language": "English",
        "difficulty": "Advanced"
    },
    {
        "isbn": "978-0132847377",
        "title": "Data Structures and Algorithm Analysis in C++",
        "author": "Mark Allen Weiss",
        "category": "Data Structures",
        "subject": "Data Structures",
        "description": "Rigorous treatment of fundamental data structures and algorithm analysis using standard modern C++ templates.",
        "publisher": "Pearson",
        "publication_year": 2013,
        "edition": "4th Edition",
        "total_copies": 5,
        "available_copies": 4,
        "shelf_number": "CS-03",
        "location": "Central Library - 1st Floor, Core Computing Stacks",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-0672324536",
        "title": "Data Structures and Algorithms in Java",
        "author": "Robert Lafore",
        "category": "Data Structures",
        "subject": "Data Structures",
        "description": "Visual, student-friendly introductory text explaining arrays, linked lists, binary trees, heaps, and graph algorithms with Java code and diagrams.",
        "publisher": "Sams Publishing",
        "publication_year": 2002,
        "edition": "2nd Edition",
        "total_copies": 4,
        "available_copies": 4,
        "shelf_number": "CS-03",
        "location": "Central Library - 1st Floor, Core Computing Stacks",
        "language": "English",
        "difficulty": "Beginner"
    },
    {
        "isbn": "978-1617292231",
        "title": "Grokking Algorithms: An Illustrated Guide for Programmers",
        "author": "Aditya Bhargava",
        "category": "Algorithms",
        "subject": "Algorithms",
        "description": "A delightfully illustrated, beginner-friendly guide that teaches common algorithms such as binary search, quicksort, graph breadth-first search, and Dijkstra's algorithm.",
        "publisher": "Manning Publications",
        "publication_year": 2016,
        "edition": "1st Edition",
        "total_copies": 6,
        "available_copies": 5,
        "shelf_number": "CS-03",
        "location": "Central Library - 1st Floor, Core Computing Stacks",
        "language": "English",
        "difficulty": "Beginner"
    },

    # 4. Database Management Systems
    {
        "isbn": "978-0073523323",
        "title": "Database System Concepts",
        "author": "Abraham Silberschatz, Henry F. Korth, S. Sudarshan",
        "category": "Database Management Systems",
        "subject": "Database Management Systems",
        "description": "The standard university textbook covering relational database theory, SQL syntax, schema design, normalization forms, transaction ACID properties, concurrency control, and recovery.",
        "publisher": "McGraw-Hill Education",
        "publication_year": 2019,
        "edition": "7th Edition",
        "total_copies": 7,
        "available_copies": 4,
        "shelf_number": "CS-04",
        "location": "Central Library - 1st Floor, Core Computing Stacks",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-0133970777",
        "title": "Fundamentals of Database Systems",
        "author": "Ramez Elmasri, Shamkant B. Navathe",
        "category": "Database Management Systems",
        "subject": "Database Management Systems",
        "description": "Comprehensive guide to conceptual database modeling using ER diagrams, relational calculus, query optimization techniques, and modern object-relational stores.",
        "publisher": "Pearson",
        "publication_year": 2015,
        "edition": "7th Edition",
        "total_copies": 5,
        "available_copies": 3,
        "shelf_number": "CS-04",
        "location": "Central Library - 1st Floor, Core Computing Stacks",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-0123814791",
        "title": "Data Mining: Concepts and Techniques",
        "author": "Jiawei Han, Micheline Kamber, Jian Pei",
        "category": "Database Management Systems",
        "subject": "Data Mining",
        "description": "Advanced exploration of warehouse architectures, association rule mining, Apriori algorithms, cluster analysis, and outlier detection.",
        "publisher": "Morgan Kaufmann",
        "publication_year": 2011,
        "edition": "3rd Edition",
        "total_copies": 3,
        "available_copies": 1,
        "shelf_number": "CS-04",
        "location": "Central Library - 1st Floor, Core Computing Stacks",
        "language": "English",
        "difficulty": "Advanced"
    },
    {
        "isbn": "978-1449373320",
        "title": "Designing Data-Intensive Applications",
        "author": "Martin Kleppmann",
        "category": "Database Management Systems",
        "subject": "Distributed Databases",
        "description": "The big ideas behind reliable, scalable, and maintainable systems: replication, partitioning, transactions, consensus, and batch/stream processing.",
        "publisher": "O'Reilly Media",
        "publication_year": 2017,
        "edition": "1st Edition",
        "total_copies": 5,
        "available_copies": 2,
        "shelf_number": "CS-04",
        "location": "Central Library - 1st Floor, Core Computing Stacks",
        "language": "English",
        "difficulty": "Advanced"
    },

    # 5. Operating Systems
    {
        "isbn": "978-1118063330",
        "title": "Operating System Concepts",
        "author": "Abraham Silberschatz, Peter B. Galvin, Greg Gagne",
        "category": "Operating Systems",
        "subject": "Operating Systems",
        "description": "Known as the classic 'Dinosaur Book', this text teaches process synchronization, semaphores, virtual memory paging, disk scheduling, and security architectures.",
        "publisher": "Wiley",
        "publication_year": 2018,
        "edition": "10th Edition",
        "total_copies": 6,
        "available_copies": 2,
        "shelf_number": "CS-05",
        "location": "Central Library - 1st Floor, Core Computing Stacks",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-0133591620",
        "title": "Modern Operating Systems",
        "author": "Andrew S. Tanenbaum, Herbert Bos",
        "category": "Operating Systems",
        "subject": "Operating Systems",
        "description": "Thorough, authoritative examination of contemporary operating system design, thread models, deadlock prevention, Linux and Windows case studies.",
        "publisher": "Pearson",
        "publication_year": 2014,
        "edition": "4th Edition",
        "total_copies": 4,
        "available_copies": 3,
        "shelf_number": "CS-05",
        "location": "Central Library - 1st Floor, Core Computing Stacks",
        "language": "English",
        "difficulty": "Advanced"
    },
    {
        "isbn": "978-1985086593",
        "title": "Operating Systems: Three Easy Pieces",
        "author": "Remzi H. Arpaci-Dusseau, Andrea C. Arpaci-Dusseau",
        "category": "Operating Systems",
        "subject": "Operating Systems",
        "description": "A wonderfully intuitive textbook organized around three core pillars: Virtualization, Concurrency, and Persistence.",
        "publisher": "CreateSpace Independent Publishing",
        "publication_year": 2018,
        "edition": "1.00 Edition",
        "total_copies": 5,
        "available_copies": 4,
        "shelf_number": "CS-05",
        "location": "Central Library - 1st Floor, Core Computing Stacks",
        "language": "English",
        "difficulty": "Beginner"
    },

    # 6. Computer Networks
    {
        "isbn": "978-0132126953",
        "title": "Computer Networks",
        "author": "Andrew S. Tanenbaum, David J. Wetherall",
        "category": "Computer Networks",
        "subject": "Computer Networks",
        "description": "Classic textbook covering network layers from physical transmission media to application layer protocols, wireless networking, and network security.",
        "publisher": "Pearson",
        "publication_year": 2011,
        "edition": "5th Edition",
        "total_copies": 6,
        "available_copies": 1,
        "shelf_number": "CS-06",
        "location": "Central Library - 1st Floor, Core Computing Stacks",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-0133594140",
        "title": "Computer Networking: A Top-Down Approach",
        "author": "James F. Kurose, Keith W. Ross",
        "category": "Computer Networks",
        "subject": "Computer Networks",
        "description": "Motivates networking concepts by starting at the application layer (HTTP, DNS, CDN) down to physical layers with hands-on Wireshark lab assignments.",
        "publisher": "Pearson",
        "publication_year": 2020,
        "edition": "8th Edition",
        "total_copies": 6,
        "available_copies": 4,
        "shelf_number": "CS-06",
        "location": "Central Library - 1st Floor, Core Computing Stacks",
        "language": "English",
        "difficulty": "Beginner"
    },
    {
        "isbn": "978-0073376226",
        "title": "Data Communications and Networking",
        "author": "Behrouz A. Forouzan",
        "category": "Computer Networks",
        "subject": "Computer Networks",
        "description": "Clear presentation of signal processing, data encoding, multiplexing, error detection CRC, data link controls, and routing protocols.",
        "publisher": "McGraw-Hill",
        "publication_year": 2012,
        "edition": "5th Edition",
        "total_copies": 5,
        "available_copies": 3,
        "shelf_number": "CS-06",
        "location": "Central Library - 1st Floor, Core Computing Stacks",
        "language": "English",
        "difficulty": "Intermediate"
    },

    # 7. Software Engineering & Clean Code
    {
        "isbn": "978-0132350884",
        "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
        "author": "Robert C. Martin",
        "category": "Software Engineering",
        "subject": "Software Engineering",
        "description": "Must-read guide on writing clean, readable, modular code. Covers naming conventions, small functions, unit testing, error handling, and code smells.",
        "publisher": "Prentice Hall",
        "publication_year": 2008,
        "edition": "1st Edition",
        "total_copies": 5,
        "available_copies": 1,
        "shelf_number": "CS-07",
        "location": "Central Library - 2nd Floor, Software Systems Wing",
        "language": "English",
        "difficulty": "Beginner"
    },
    {
        "isbn": "978-0201633610",
        "title": "Design Patterns: Elements of Reusable Object-Oriented Software",
        "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
        "category": "Software Engineering",
        "subject": "Software Engineering",
        "description": "The seminal 'Gang of Four' work establishing 23 classic Creational, Structural, and Behavioral object-oriented software design patterns.",
        "publisher": "Addison-Wesley Professional",
        "publication_year": 1994,
        "edition": "1st Edition",
        "total_copies": 4,
        "available_copies": 2,
        "shelf_number": "CS-07",
        "location": "Central Library - 2nd Floor, Software Systems Wing",
        "language": "English",
        "difficulty": "Advanced"
    },
    {
        "isbn": "978-0596007126",
        "title": "Head First Design Patterns",
        "author": "Eric Freeman, Elisabeth Robson",
        "category": "Software Engineering",
        "subject": "Software Engineering",
        "description": "Visually stimulating, engaging introduction to OOP design patterns: Strategy, Observer, Decorator, Factory, Singleton, Command, and Adapter.",
        "publisher": "O'Reilly Media",
        "publication_year": 2004,
        "edition": "1st Edition",
        "total_copies": 5,
        "available_copies": 4,
        "shelf_number": "CS-07",
        "location": "Central Library - 2nd Floor, Software Systems Wing",
        "language": "English",
        "difficulty": "Beginner"
    },
    {
        "isbn": "978-0134494166",
        "title": "Clean Architecture: A Craftsman's Guide to Software Structure and Design",
        "author": "Robert C. Martin",
        "category": "Software Engineering",
        "subject": "Software Engineering",
        "description": "Core universal rules of software architecture: SOLID principles, component cohesion, boundaries, dependency inversion, and decoupling.",
        "publisher": "Prentice Hall",
        "publication_year": 2017,
        "edition": "1st Edition",
        "total_copies": 4,
        "available_copies": 3,
        "shelf_number": "CS-07",
        "location": "Central Library - 2nd Floor, Software Systems Wing",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-0135957059",
        "title": "The Pragmatic Programmer: Your Journey to Mastery",
        "author": "David Thomas, Andrew Hunt",
        "category": "Software Engineering",
        "subject": "Software Engineering",
        "description": "Timeless practical wisdom on software craftsmanship, career growth, testing strategies, orthogonality, and pragmatic team dynamics.",
        "publisher": "Addison-Wesley Professional",
        "publication_year": 2019,
        "edition": "20th Anniversary Edition",
        "total_copies": 4,
        "available_copies": 3,
        "shelf_number": "CS-07",
        "location": "Central Library - 2nd Floor, Software Systems Wing",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-0134757599",
        "title": "Refactoring: Improving the Design of Existing Code",
        "author": "Martin Fowler",
        "category": "Software Engineering",
        "subject": "Software Engineering",
        "description": "Principles and specific catalog of code refactorings that make code easier to understand and cheaper to modify, featuring JavaScript examples.",
        "publisher": "Addison-Wesley Professional",
        "publication_year": 2018,
        "edition": "2nd Edition",
        "total_copies": 3,
        "available_copies": 2,
        "shelf_number": "CS-07",
        "location": "Central Library - 2nd Floor, Software Systems Wing",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-0078022128",
        "title": "Software Engineering: A Practitioner's Approach",
        "author": "Roger S. Pressman, Bruce R. Maxim",
        "category": "Software Engineering",
        "subject": "Software Engineering",
        "description": "Comprehensive engineering guide to Agile methods, requirements engineering, architectural modeling, quality metrics, and risk management.",
        "publisher": "McGraw-Hill",
        "publication_year": 2014,
        "edition": "8th Edition",
        "total_copies": 5,
        "available_copies": 4,
        "shelf_number": "CS-14",
        "location": "Central Library - 2nd Floor, Software Systems Wing",
        "language": "English",
        "difficulty": "Intermediate"
    },

    # 8. Python Programming
    {
        "isbn": "978-1593279288",
        "title": "Python Crash Course: A Hands-On, Project-Based Introduction",
        "author": "Eric Matthes",
        "category": "Python",
        "subject": "Python",
        "description": "The world's bestselling guide to Python. Teaches foundational syntax, functions, classes, followed by projects in 2D Space Invaders arcade, data visualization, and web apps.",
        "publisher": "No Starch Press",
        "publication_year": 2019,
        "edition": "2nd Edition",
        "total_copies": 6,
        "available_copies": 6,
        "shelf_number": "CS-08",
        "location": "Central Library - 1st Floor, Programming Languages Stacks",
        "language": "English",
        "difficulty": "Beginner"
    },
    {
        "isbn": "978-1491946008",
        "title": "Fluent Python: Clear, Concise, and Effective Programming",
        "author": "Luciano Ramalho",
        "category": "Python",
        "subject": "Python",
        "description": "Takes Python programmers beyond basic syntax to write idiomatic, expressive code using generators, coroutines, descriptors, and metaprogramming.",
        "publisher": "O'Reilly Media",
        "publication_year": 2022,
        "edition": "2nd Edition",
        "total_copies": 4,
        "available_copies": 2,
        "shelf_number": "CS-08",
        "location": "Central Library - 1st Floor, Programming Languages Stacks",
        "language": "English",
        "difficulty": "Advanced"
    },
    {
        "isbn": "978-1593279929",
        "title": "Automate the Boring Stuff with Python",
        "author": "Al Sweigart",
        "category": "Python",
        "subject": "Python",
        "description": "Practical beginner guide teaching how to automate everyday tasks: web scraping, manipulating PDFs and Excel sheets, automating mouse/keyboard actions, and sending emails.",
        "publisher": "No Starch Press",
        "publication_year": 2019,
        "edition": "2nd Edition",
        "total_copies": 5,
        "available_copies": 5,
        "shelf_number": "CS-08",
        "location": "Central Library - 1st Floor, Programming Languages Stacks",
        "language": "English",
        "difficulty": "Beginner"
    },
    {
        "isbn": "978-1491957660",
        "title": "Python for Data Analysis",
        "author": "Wes McKinney",
        "category": "Python",
        "subject": "Data Science",
        "description": "Written by the creator of Python pandas library. Complete guide to manipulating, processing, cleaning, and crunching datasets in Python.",
        "publisher": "O'Reilly Media",
        "publication_year": 2022,
        "edition": "3rd Edition",
        "total_copies": 4,
        "available_copies": 3,
        "shelf_number": "CS-08",
        "location": "Central Library - 1st Floor, Programming Languages Stacks",
        "language": "English",
        "difficulty": "Intermediate"
    },

    # 9. Java Programming
    {
        "isbn": "978-0596009205",
        "title": "Head First Java",
        "author": "Kathy Sierra, Bert Bates",
        "category": "Java",
        "subject": "Java",
        "description": "A brain-friendly, visual learning experience for Java fundamentals, object design, encapsulation, inheritance, GUI programming with Swing, and networking.",
        "publisher": "O'Reilly Media",
        "publication_year": 2022,
        "edition": "3rd Edition",
        "total_copies": 6,
        "available_copies": 5,
        "shelf_number": "CS-09",
        "location": "Central Library - 1st Floor, Programming Languages Stacks",
        "language": "English",
        "difficulty": "Beginner"
    },
    {
        "isbn": "978-0134685991",
        "title": "Effective Java",
        "author": "Joshua Bloch",
        "category": "Java",
        "subject": "Java",
        "description": "The definitive best-practices guide for professional Java developers, covering generics, lambdas, streams, concurrency, and serialization.",
        "publisher": "Addison-Wesley Professional",
        "publication_year": 2017,
        "edition": "3rd Edition",
        "total_copies": 4,
        "available_copies": 2,
        "shelf_number": "CS-09",
        "location": "Central Library - 1st Floor, Programming Languages Stacks",
        "language": "English",
        "difficulty": "Advanced"
    },
    {
        "isbn": "978-0135166307",
        "title": "Core Java Volume I – Fundamentals",
        "author": "Cay S. Horstmann",
        "category": "Java",
        "subject": "Java",
        "description": "In-depth guide to Java language basics, OOP concepts, reflection, exception handling, and standard library collections framework.",
        "publisher": "Prentice Hall",
        "publication_year": 2018,
        "edition": "11th Edition",
        "total_copies": 4,
        "available_copies": 4,
        "shelf_number": "CS-09",
        "location": "Central Library - 1st Floor, Programming Languages Stacks",
        "language": "English",
        "difficulty": "Intermediate"
    },

    # 10. C / C++ Programming
    {
        "isbn": "978-0131103627",
        "title": "The C Programming Language",
        "author": "Brian W. Kernighan, Dennis M. Ritchie",
        "category": "C/C++",
        "subject": "C Programming",
        "description": "Known as K&R C, this concise masterpiece written by the language designers teaches pointers, memory structures, I/O functions, and Unix system interfaces.",
        "publisher": "Prentice Hall",
        "publication_year": 1988,
        "edition": "2nd Edition",
        "total_copies": 5,
        "available_copies": 3,
        "shelf_number": "CS-10",
        "location": "Central Library - 1st Floor, Programming Languages Stacks",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-0321563842",
        "title": "The C++ Programming Language",
        "author": "Bjarne Stroustrup",
        "category": "C/C++",
        "subject": "C++ Programming",
        "description": "The definitive reference by the inventor of C++, covering modern C++11, abstraction mechanisms, standard template library (STL), and concurrency models.",
        "publisher": "Addison-Wesley Professional",
        "publication_year": 2013,
        "edition": "4th Edition",
        "total_copies": 3,
        "available_copies": 1,
        "shelf_number": "CS-10",
        "location": "Central Library - 1st Floor, Programming Languages Stacks",
        "language": "English",
        "difficulty": "Advanced"
    },
    {
        "isbn": "978-0321714114",
        "title": "C++ Primer",
        "author": "Stanley B. Lippman, Josée Lajoie, Barbara E. Moo",
        "category": "C/C++",
        "subject": "C++ Programming",
        "description": "Comprehensive tutorial introducing C++ from fundamentals through standard library idioms, dynamic memory smart pointers, and generic templates.",
        "publisher": "Addison-Wesley Professional",
        "publication_year": 2012,
        "edition": "5th Edition",
        "total_copies": 5,
        "available_copies": 5,
        "shelf_number": "CS-10",
        "location": "Central Library - 1st Floor, Programming Languages Stacks",
        "language": "English",
        "difficulty": "Beginner"
    },

    # 11. Web Development
    {
        "isbn": "978-1593279509",
        "title": "Eloquent JavaScript: A Modern Introduction to Programming",
        "author": "Marijn Haverbeke",
        "category": "Web Development",
        "subject": "Web Development",
        "description": "Deep immersion into JavaScript, DOM manipulation, asynchronous programming with async/await, Canvas graphics, and Node.js backend development.",
        "publisher": "No Starch Press",
        "publication_year": 2018,
        "edition": "3rd Edition",
        "total_copies": 6,
        "available_copies": 4,
        "shelf_number": "CS-11",
        "location": "Central Library - 2nd Floor, Web & Cloud Wing",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-1492051725",
        "title": "Learning React: Modern Patterns for Developing React Apps",
        "author": "Alex Banks, Eve Porcello",
        "category": "Web Development",
        "subject": "Web Development",
        "description": "Teaches functional programming concepts, React hooks, state management, component composition, and asynchronous server data fetching.",
        "publisher": "O'Reilly Media",
        "publication_year": 2020,
        "edition": "2nd Edition",
        "total_copies": 4,
        "available_copies": 3,
        "shelf_number": "CS-11",
        "location": "Central Library - 2nd Floor, Web & Cloud Wing",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-1449331818",
        "title": "Learning JavaScript Design Patterns",
        "author": "Addy Osmani",
        "category": "Web Development",
        "subject": "Web Development",
        "description": "Essential architectural and design patterns for modern JavaScript web applications, modular patterns, observer, publish/subscribe, and MVC.",
        "publisher": "O'Reilly Media",
        "publication_year": 2012,
        "edition": "1st Edition",
        "total_copies": 3,
        "available_copies": 3,
        "shelf_number": "CS-11",
        "location": "Central Library - 2nd Floor, Web & Cloud Wing",
        "language": "English",
        "difficulty": "Beginner"
    },

    # 12. Cloud Computing
    {
        "isbn": "978-0133387520",
        "title": "Cloud Computing: Concepts, Technology & Architecture",
        "author": "Thomas Erl, Ricardo Puttini, Zaigham Mahmood",
        "category": "Cloud Computing",
        "subject": "Cloud Computing",
        "description": "Vendor-neutral breakdown of cloud computing models, SaaS, PaaS, IaaS, multi-tenancy, elasticity, hypervisors, and cloud security architectures.",
        "publisher": "Prentice Hall",
        "publication_year": 2013,
        "edition": "1st Edition",
        "total_copies": 4,
        "available_copies": 2,
        "shelf_number": "CS-12",
        "location": "Central Library - 2nd Floor, Web & Cloud Wing",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-1118617618",
        "title": "Architecting the Cloud: Design Decisions for Cloud Computing",
        "author": "Michael J. Kavis",
        "category": "Cloud Computing",
        "subject": "Cloud Computing",
        "description": "Strategic guidance on selecting cloud service models, disaster recovery, vendor lock-in mitigation, and designing resilient enterprise cloud systems.",
        "publisher": "Wiley",
        "publication_year": 2014,
        "edition": "1st Edition",
        "total_copies": 2,
        "available_copies": 0,  # INTENTIONALLY 0 TO DEMONSTRATE UNAVAILABILITY!
        "shelf_number": "CS-12",
        "location": "Central Library - 2nd Floor, Web & Cloud Wing",
        "language": "English",
        "difficulty": "Advanced"
    },
    {
        "isbn": "978-1491929124",
        "title": "Site Reliability Engineering: How Google Runs Production Systems",
        "author": "Betsy Beyer, Chris Jones, Jennifer Petoff, Niall Richard Murphy",
        "category": "Cloud Computing",
        "subject": "DevOps & Cloud Systems",
        "description": "Google's internal engineers share principles and practices of building, deploying, monitoring, and maintaining massive distributed systems.",
        "publisher": "O'Reilly Media",
        "publication_year": 2016,
        "edition": "1st Edition",
        "total_copies": 4,
        "available_copies": 1,
        "shelf_number": "CS-12",
        "location": "Central Library - 2nd Floor, Web & Cloud Wing",
        "language": "English",
        "difficulty": "Advanced"
    },

    # 13. Cyber Security
    {
        "isbn": "978-1939136053",
        "title": "CompTIA Security+ Get Certified Get Ahead: SY0-601",
        "author": "Darril Gibson",
        "category": "Cyber Security",
        "subject": "Cyber Security",
        "description": "Covers essential baseline cybersecurity concepts: threats, attacks, vulnerabilities, identity management, cryptography basics, and risk mitigation.",
        "publisher": "Y Cerr Press",
        "publication_year": 2021,
        "edition": "1st Edition",
        "total_copies": 5,
        "available_copies": 4,
        "shelf_number": "CS-13",
        "location": "Central Library - 2nd Floor, Security & Systems Wing",
        "language": "English",
        "difficulty": "Beginner"
    },
    {
        "isbn": "978-1118026472",
        "title": "The Web Application Hacker's Handbook",
        "author": "Dafydd Stuttard, Marcus Pinto",
        "category": "Cyber Security",
        "subject": "Web Security",
        "description": "Practical handbook exploring web security vulnerabilities: SQL injection, cross-site scripting (XSS), CSRF, authentication bypass, and session flaws.",
        "publisher": "Wiley",
        "publication_year": 2011,
        "edition": "2nd Edition",
        "total_copies": 3,
        "available_copies": 1,
        "shelf_number": "CS-13",
        "location": "Central Library - 2nd Floor, Security & Systems Wing",
        "language": "English",
        "difficulty": "Advanced"
    },
    {
        "isbn": "978-0134444284",
        "title": "Cryptography and Network Security: Principles and Practice",
        "author": "William Stallings",
        "category": "Cyber Security",
        "subject": "Cryptography",
        "description": "Mathematical principles of symmetric encryption (AES, DES), public key cryptography (RSA, ECC), digital signatures, hashes, and IPsec.",
        "publisher": "Pearson",
        "publication_year": 2016,
        "edition": "7th Edition",
        "total_copies": 5,
        "available_copies": 3,
        "shelf_number": "CS-13",
        "location": "Central Library - 2nd Floor, Security & Systems Wing",
        "language": "English",
        "difficulty": "Intermediate"
    },

    # 14. Mathematics for Computer Science
    {
        "isbn": "978-0073383095",
        "title": "Discrete Mathematics and Its Applications",
        "author": "Kenneth H. Rosen",
        "category": "Mathematics",
        "subject": "Discrete Mathematics",
        "description": "Standard college textbook for CS engineering math: propositional logic, set theory, induction, recurrence relations, graph theory, and Boolean algebra.",
        "publisher": "McGraw-Hill Education",
        "publication_year": 2018,
        "edition": "8th Edition",
        "total_copies": 8,
        "available_copies": 6,
        "shelf_number": "ENG-01",
        "location": "Central Library - 1st Floor, Engineering Mathematics Wing",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-0980232776",
        "title": "Linear Algebra and Its Applications",
        "author": "Gilbert Strang",
        "category": "Mathematics",
        "subject": "Linear Algebra",
        "description": "Essential mathematical foundations for AI and computer vision: vector spaces, matrix transformations, eigenvalues, eigenvectors, and singular value decomposition.",
        "publisher": "Wellesley-Cambridge Press",
        "publication_year": 2016,
        "edition": "5th Edition",
        "total_copies": 5,
        "available_copies": 4,
        "shelf_number": "ENG-01",
        "location": "Central Library - 1st Floor, Engineering Mathematics Wing",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-8174091955",
        "title": "Higher Engineering Mathematics",
        "author": "B.S. Grewal",
        "category": "Mathematics",
        "subject": "Engineering Mathematics",
        "description": "Standard engineering reference covering differential calculus, integral calculus, differential equations, complex numbers, numerical methods, and Fourier transforms.",
        "publisher": "Khanna Publishers",
        "publication_year": 2017,
        "edition": "44th Edition",
        "total_copies": 9,
        "available_copies": 6,
        "shelf_number": "ENG-02",
        "location": "Central Library - 1st Floor, Engineering Mathematics Wing",
        "language": "English",
        "difficulty": "Intermediate"
    },

    # 15. Engineering & Computer Architecture
    {
        "isbn": "978-0134797076",
        "title": "Computer Organization and Architecture",
        "author": "William Stallings",
        "category": "Engineering",
        "subject": "Computer Architecture",
        "description": "Instruction set architectures (RISC/CISC), CPU pipelining, cache memory hierarchy, superscalar execution, and parallel multiprocessors.",
        "publisher": "Pearson",
        "publication_year": 2018,
        "edition": "11th Edition",
        "total_copies": 5,
        "available_copies": 3,
        "shelf_number": "CS-15",
        "location": "Central Library - 1st Floor, Hardware Systems Stacks",
        "language": "English",
        "difficulty": "Intermediate"
    },
    {
        "isbn": "978-0134092669",
        "title": "Computer Systems: A Programmer's Perspective",
        "author": "Randal E. Bryant, David R. O'Hallaron",
        "category": "Engineering",
        "subject": "Computer Systems",
        "description": "Bridging software programming with hardware execution: binary representation, machine code assembly, memory caches, virtual memory, and concurrent network servers.",
        "publisher": "Pearson",
        "publication_year": 2015,
        "edition": "3rd Edition",
        "total_copies": 4,
        "available_copies": 2,
        "shelf_number": "CS-15",
        "location": "Central Library - 1st Floor, Hardware Systems Stacks",
        "language": "English",
        "difficulty": "Advanced"
    },
    {
        "isbn": "978-1133187790",
        "title": "Introduction to the Theory of Computation",
        "author": "Michael Sipser",
        "category": "Engineering",
        "subject": "Theory of Computation",
        "description": "Automata theory, regular expressions, context-free grammars, Turing machines, decidability, computational complexity, and P vs NP problems.",
        "publisher": "Cengage Learning",
        "publication_year": 2012,
        "edition": "3rd Edition",
        "total_copies": 5,
        "available_copies": 3,
        "shelf_number": "CS-16",
        "location": "Central Library - 1st Floor, Theoretical Computing Stacks",
        "language": "English",
        "difficulty": "Advanced"
    }
]

SAMPLE_LIBRARY_INFO = [
    {
        "key": "library_name",
        "title": "Library Name",
        "value": "Central Academic Library & Information Resource Center (College of Engineering)",
        "category": "general"
    },
    {
        "key": "timings_weekday",
        "title": "Weekday Hours",
        "value": "Monday to Friday: 8:00 AM – 8:00 PM. Book issue/return counter operates 8:30 AM – 6:30 PM.",
        "category": "timings"
    },
    {
        "key": "timings_saturday",
        "title": "Saturday Hours",
        "value": "Saturday: 9:00 AM – 5:00 PM. Digital Library and Reading Hall remain open.",
        "category": "timings"
    },
    {
        "key": "timings_sunday_holidays",
        "title": "Sundays and Holidays",
        "value": "Closed on Sundays and Gazetted National Holidays. During semester examination weeks, the Ground Floor Reading Hall remains open on Sundays from 10:00 AM to 4:00 PM.",
        "category": "timings"
    },
    {
        "key": "location",
        "title": "Physical Location",
        "value": "Floor 1 & Floor 2, Dr. APJ Abdul Kalam Learning Resource Complex, North Academic Quadrangle.",
        "category": "general"
    },
    {
        "key": "contact_info",
        "title": "Contact Information",
        "value": "Email: library-helpdesk@engineering.edu | Chief Librarian: chief.librarian@engineering.edu | Phone: +91 (020) 2456-7890 (Ext: 3401 / 3402).",
        "category": "general"
    },
    {
        "key": "borrowing_limit_student",
        "title": "Student Borrowing Limit",
        "value": "Undergraduate engineering students can borrow up to 4 books at a time. Third-year (TE) and Final-year (BE) students working on sanctioned capstone projects can request 1 additional reference book with HOD recommendation.",
        "category": "borrowing"
    },
    {
        "key": "borrowing_limit_faculty",
        "title": "Faculty Borrowing Limit",
        "value": "Full-time faculty and research scholars may borrow up to 8 books at a time for up to 60 days.",
        "category": "borrowing"
    },
    {
        "key": "borrowing_duration",
        "title": "Borrowing Duration",
        "value": "Standard borrowing duration is 14 days (2 weeks) for undergraduate students. Books must be returned or renewed on or before the stamped due date.",
        "category": "borrowing"
    },
    {
        "key": "issue_process",
        "title": "How to Issue a Book",
        "value": "1. Search for the book title in the catalog and note the Shelf Number (e.g., CS-04). 2. Retrieve the book from the designated shelf. 3. Present your Institute RFID Student Identity Card and the book at the Ground Floor Circulation Desk or use the Self-Service RFID Kiosk. 4. Collect the printed receipt and note the 14-day due date.",
        "category": "borrowing"
    },
    {
        "key": "renewal_policy",
        "title": "Book Renewal Policy",
        "value": "Books can be renewed up to 2 consecutive times (14 days each renewal) through the online portal or at the circulation counter, provided no other student has placed an active hold/reservation on that copy.",
        "category": "borrowing"
    },
    {
        "key": "fine_policy",
        "title": "Overdue Fines",
        "value": "A late return fine of ₹5 per day per overdue book is levied for the first 7 days past the due date. Thereafter, the fine increases to ₹10 per day. All pending fines must be cleared before semester exam hall tickets can be verified.",
        "category": "fines"
    },
    {
        "key": "lost_damaged_policy",
        "title": "Lost or Damaged Book Policy",
        "value": "If a borrowed book is lost or physically damaged, the student must notify the library desk immediately. The borrower must replace the copy with an identical brand-new copy of the same or newer edition, OR pay 150% of the current market price of the book plus a flat ₹100 processing surcharge.",
        "category": "rules"
    },
    {
        "key": "membership_rules",
        "title": "Library Membership",
        "value": "All officially enrolled engineering students, faculty, and research fellows automatically receive library membership upon admission. Your Institute Smart RFID ID Card functions as your library barcode card. No separate registration fee is required.",
        "category": "general"
    },
    {
        "key": "general_conduct",
        "title": "General Library Rules & Conduct",
        "value": "1. Absolute silence must be maintained in all Reading Halls. 2. Cellular phones must be kept on silent/vibrate mode; calls are strictly prohibited inside stacks. 3. Food, open beverages, and snacks are not allowed inside (sealed water bottles permitted). 4. Reference section books with red labels are strictly for in-library reading and cannot be taken home. 5. Discussion rooms on the 2nd Floor may be booked for group projects.",
        "category": "rules"
    }
]

SAMPLE_USERS = [
    {
        "username": "student",
        "password_hash": hash_password("student123"),
        "full_name": "Aaditi Sharma",
        "role": "student",
        "email": "aaditi.ce@engineering.edu"
    },
    {
        "username": "admin",
        "password_hash": hash_password("admin123"),
        "full_name": "Dr. Ramesh Patil (Chief Librarian)",
        "role": "admin",
        "email": "chief.librarian@engineering.edu"
    }
]

def seed_database_if_empty():
    """Seeds the database with categories, books, library info, and users if not already populated."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if books already exist
    cursor.execute("SELECT COUNT(*) AS count FROM books")
    book_count = cursor.fetchone()["count"]

    if book_count == 0:
        print("[SEED] Seeding categories...")
        for cat in SAMPLE_CATEGORIES:
            cursor.execute(
                "INSERT INTO categories (name, description, icon) VALUES (?, ?, ?)",
                (cat["name"], cat["description"], cat["icon"])
            )

        print(f"[SEED] Seeding {len(SAMPLE_BOOKS)} books...")
        for b in SAMPLE_BOOKS:
            cursor.execute("""
                INSERT INTO books (
                    isbn, title, author, category, subject, description,
                    publisher, publication_year, edition, total_copies,
                    available_copies, shelf_number, location, language, difficulty
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                b["isbn"], b["title"], b["author"], b["category"], b["subject"],
                b["description"], b["publisher"], b["publication_year"], b["edition"],
                b["total_copies"], b["available_copies"], b["shelf_number"],
                b["location"], b["language"], b["difficulty"]
            ))

        print("[SEED] Seeding library policies and info...")
        for info in SAMPLE_LIBRARY_INFO:
            cursor.execute("""
                INSERT INTO library_info (key, title, value, category)
                VALUES (?, ?, ?, ?)
            """, (info["key"], info["title"], info["value"], info["category"]))

        print("[SEED] Seeding demo user credentials...")
        for u in SAMPLE_USERS:
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, role, email)
                VALUES (?, ?, ?, ?, ?)
            """, (u["username"], u["password_hash"], u["full_name"], u["role"], u["email"]))

        conn.commit()
        print("[SEED] Database seeding complete!")
    else:
        print(f"[SEED] Database already has {book_count} books. Skipping initial seed.")

    conn.close()

if __name__ == "__main__":
    from app.database import init_db
    init_db()
    seed_database_if_empty()
