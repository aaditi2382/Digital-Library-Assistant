/**
 * API Client for Digital Library Assistant
 * Handles all REST communication with FastAPI backend
 */

const API = {
  // Chat endpoints
  async sendMessage(query, sessionId) {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: sessionId })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to process message.');
    }
    return res.json();
  },

  async getChatHistory(sessionId) {
    const res = await fetch(`/api/chat/history/${encodeURIComponent(sessionId)}`);
    if (!res.ok) return { messages: [] };
    return res.json();
  },

  async clearChat(sessionId) {
    const res = await fetch(`/api/chat/clear/${encodeURIComponent(sessionId)}`, {
      method: 'POST'
    });
    return res.json();
  },

  // Books endpoints
  async getBooks(params = {}) {
    const query = new URLSearchParams();
    if (params.search) query.append('search', params.search);
    if (params.category) query.append('category', params.category);
    if (params.difficulty) query.append('difficulty', params.difficulty);
    if (params.available_only) query.append('available_only', 'true');
    if (params.limit) query.append('limit', params.limit);
    if (params.offset) query.append('offset', params.offset);

    const res = await fetch(`/api/books?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch books.');
    return res.json();
  },

  async getBookById(id) {
    const res = await fetch(`/api/books/${id}`);
    if (!res.ok) throw new Error('Book not found.');
    return res.json();
  },

  async getRecommendations(subject, difficulty, limit = 4) {
    const query = new URLSearchParams();
    if (subject) query.append('subject', subject);
    if (difficulty) query.append('difficulty', difficulty);
    if (limit) query.append('limit', limit);

    const res = await fetch(`/api/books/recommendations?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch recommendations.');
    return res.json();
  },

  // Library Info endpoints
  async getLibraryInfo() {
    const res = await fetch('/api/info');
    if (!res.ok) throw new Error('Failed to fetch library information.');
    return res.json();
  },

  async getCategories() {
    const res = await fetch('/api/info/categories');
    if (!res.ok) throw new Error('Failed to fetch categories.');
    return res.json();
  },

  // Admin & Auth endpoints
  async login(username, password) {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Invalid username or password.');
    }
    return res.json();
  },

  async getAdminStats() {
    const res = await fetch('/api/admin/stats');
    if (!res.ok) throw new Error('Failed to fetch library stats.');
    return res.json();
  },

  async addBook(bookData) {
    const res = await fetch('/api/admin/books', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(bookData)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to add book.');
    }
    return res.json();
  },

  async updateBook(id, bookData) {
    const res = await fetch(`/api/admin/books/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(bookData)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to update book.');
    }
    return res.json();
  },

  async deleteBook(id) {
    const res = await fetch(`/api/admin/books/${id}`, {
      method: 'DELETE'
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to delete book.');
    }
    return res.json();
  },

  async updateBookCopies(id, availableCopies) {
    const res = await fetch(`/api/admin/books/${id}/copies`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ available_copies: availableCopies })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to update copies.');
    }
    return res.json();
  },

  async updatePolicy(key, value) {
    const res = await fetch(`/api/admin/info/${encodeURIComponent(key)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to update policy.');
    }
    return res.json();
  },

  // AI Diagnostics for Viva
  async getDiagnostics() {
    const res = await fetch('/api/ai/diagnostics');
    if (!res.ok) throw new Error('Failed to fetch AI diagnostics.');
    return res.json();
  }
};
