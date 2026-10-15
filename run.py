"""
One-click launch script for Digital Library Assistant.
Third-Year Computer Engineering AI Course CI3 Project.
Run using: py run.py
"""

import sys
import os

# Safe UTF-8 reconfiguration for Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import uvicorn

BANNER = """
========================================================================
   [DLA] DIGITAL LIBRARY ASSISTANT - AI CI3 PROJECT
   Developed for Third-Year Computer Engineering AI Course
========================================================================
   Web Application:       http://127.0.0.1:8000
   Interactive API Docs:  http://127.0.0.1:8000/docs
   AI Diagnostics:        http://127.0.0.1:8000/api/ai/diagnostics

   Demo Credentials:
      * Student User:     username: student   / password: student123
      * Administrator:    username: admin     / password: admin123

   Press Ctrl+C to stop the server.
========================================================================
"""

def main():
    print(BANNER)
    # Ensure current directory is in sys.path
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    if curr_dir not in sys.path:
        sys.path.insert(0, curr_dir)

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
