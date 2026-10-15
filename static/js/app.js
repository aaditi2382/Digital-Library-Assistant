/**
 * Digital Library Assistant - Frontend Application
 * Third-Year Computer Engineering AI Course CI3 Project
 */

// Application State
const state = {
  currentView: 'chat', // 'chat', 'catalog', 'categories', 'recommendations', 'rules', 'admin', 'about'
  sessionId: localStorage.getItem('dla_session_id') || ('session_' + Math.random().toString(36).substring(2, 9)),
  messages: [],
  isTyping: false,
  currentUser: JSON.parse(localStorage.getItem('dla_user') || JSON.stringify({
    username: 'student',
    full_name: 'Aaditi Sharma',
    role: 'student'
  })),
  catalog: {
    books: [],
    total: 0,
    search: '',
    category: '',
    difficulty: '',
    availableOnly: false
  },
  categories: [],
  policies: [],
  adminStats: null,
  selectedBook: null,
  isRecording: false
};

// Initialize application on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  localStorage.setItem('dla_session_id', state.sessionId);
  initIcons();
  setupNavigation();
  setupChatHandlers();
  setupSpeechRecognition();
  loadInitialData();
  renderUserBadge();
});

function initIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// ----------------- Navigation & View Management ----------------- //

function setupNavigation() {
  const navItems = document.querySelectorAll('[data-view]');
  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const targetView = item.getAttribute('data-view');
      switchView(targetView);
    });
  });

  // Mobile menu toggle
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const sidebar = document.getElementById('sidebar');
  if (mobileMenuBtn && sidebar) {
    mobileMenuBtn.addEventListener('click', () => {
      sidebar.classList.toggle('-translate-x-full');
    });
  }

  // New Chat Button
  const newChatBtn = document.getElementById('newChatBtn');
  if (newChatBtn) {
    newChatBtn.addEventListener('click', () => {
      startNewChat();
    });
  }
}

function switchView(viewName) {
  state.currentView = viewName;

  // Update navigation highlight
  document.querySelectorAll('[data-view]').forEach(el => {
    if (el.getAttribute('data-view') === viewName) {
      el.classList.add('bg-indigo-600/20', 'text-indigo-400', 'border-l-2', 'border-indigo-500');
      el.classList.remove('text-slate-400', 'hover:bg-slate-800/60');
    } else {
      el.classList.remove('bg-indigo-600/20', 'text-indigo-400', 'border-l-2', 'border-indigo-500');
      el.classList.add('text-slate-400', 'hover:bg-slate-800/60');
    }
  });

  // Hide all view containers
  const views = ['chatView', 'catalogView', 'categoriesView', 'recommendationsView', 'rulesView', 'adminView', 'aboutView'];
  views.forEach(v => {
    const el = document.getElementById(v);
    if (el) el.classList.add('hidden');
  });

  // Show active container
  const activeContainer = document.getElementById(`${viewName}View`);
  if (activeContainer) {
    activeContainer.classList.remove('hidden');
  }

  // Close mobile sidebar if open
  const sidebar = document.getElementById('sidebar');
  if (sidebar && window.innerWidth < 1024) {
    sidebar.classList.add('-translate-x-full');
  }

  // Trigger view data loading
  if (viewName === 'catalog') loadCatalog();
  if (viewName === 'categories') loadCategories();
  if (viewName === 'rules') loadLibraryPolicies();
  if (viewName === 'admin') loadAdminDashboard();
  if (viewName === 'about') loadVivaDiagnostics();

  initIcons();
}

function renderUserBadge() {
  const badgeEl = document.getElementById('userBadgeContainer');
  if (!badgeEl) return;
  const isAdmin = state.currentUser.role === 'admin';
  badgeEl.innerHTML = `
    <div class="flex items-center justify-between p-3 rounded-xl bg-slate-800/60 border border-slate-700/60">
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 rounded-full ${isAdmin ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40' : 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/40'} flex items-center justify-center font-bold text-xs">
          ${state.currentUser.full_name.charAt(0)}
        </div>
        <div class="overflow-hidden">
          <p class="text-xs font-semibold text-slate-200 truncate">${state.currentUser.full_name}</p>
          <p class="text-[10px] uppercase font-bold tracking-wider ${isAdmin ? 'text-amber-400' : 'text-indigo-400'}">${state.currentUser.role}</p>
        </div>
      </div>
      <button onclick="toggleRoleModal()" class="text-xs text-slate-400 hover:text-slate-200 px-2 py-1 rounded bg-slate-700/50 hover:bg-slate-700 transition" title="Switch User Role">
        Switch
      </button>
    </div>
  `;
}

function toggleRoleModal() {
  const modal = document.getElementById('roleModal');
  if (modal) modal.classList.toggle('hidden');
}

async function handleRoleSwitch(role) {
  if (role === 'admin') {
    state.currentUser = {
      username: 'admin',
      full_name: 'Dr. Ramesh Patil (Chief Librarian)',
      role: 'admin'
    };
  } else {
    state.currentUser = {
      username: 'student',
      full_name: 'Aaditi Sharma',
      role: 'student'
    };
  }
  localStorage.setItem('dla_user', JSON.stringify(state.currentUser));
  renderUserBadge();
  toggleRoleModal();
  showToast(`Switched role to ${state.currentUser.role.toUpperCase()}`, 'success');
  if (state.currentView === 'admin') loadAdminDashboard();
  if (state.currentView === 'catalog') loadCatalog();
}

// ----------------- Chatbot Logic ----------------- //

function setupChatHandlers() {
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');

  if (chatForm && chatInput) {
    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = chatInput.value.trim();
      if (!text || state.isTyping) return;
      chatInput.value = '';
      sendChatMessage(text);
    });
  }

  // Quick suggestion chips on welcome screen or input
  document.querySelectorAll('[data-prompt]').forEach(chip => {
    chip.addEventListener('click', () => {
      const prompt = chip.getAttribute('data-prompt');
      if (prompt) {
        if (state.currentView !== 'chat') switchView('chat');
        sendChatMessage(prompt);
      }
    });
  });
}

function startNewChat() {
  state.sessionId = 'session_' + Math.random().toString(36).substring(2, 9);
  localStorage.setItem('dla_session_id', state.sessionId);
  state.messages = [];
  renderChatMessages();
  switchView('chat');
  showToast('Started a new conversation session.', 'info');
}

async function sendChatMessage(queryText) {
  // Add user message to UI
  const userMsg = {
    role: 'user',
    message: queryText,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };
  state.messages.push(userMsg);
  state.isTyping = true;
  renderChatMessages();

  try {
    const res = await API.sendMessage(queryText, state.sessionId);
    state.isTyping = false;
    const aiMsg = {
      role: 'assistant',
      message: res.message,
      intent: res.intent,
      confidence: res.confidence,
      entities: res.entities,
      books: res.books || [],
      suggestedQuestions: res.suggested_questions || [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    state.messages.push(aiMsg);
    renderChatMessages();
  } catch (err) {
    state.isTyping = false;
    state.messages.push({
      role: 'assistant',
      message: `⚠️ Sorry, an error occurred: ${err.message}`,
      intent: 'error',
      books: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });
    renderChatMessages();
  }
}

function renderChatMessages() {
  const container = document.getElementById('chatMessagesContainer');
  const welcomeHero = document.getElementById('welcomeHero');
  if (!container) return;

  if (state.messages.length === 0) {
    if (welcomeHero) welcomeHero.classList.remove('hidden');
    container.innerHTML = '';
    return;
  }

  if (welcomeHero) welcomeHero.classList.add('hidden');

  let html = '';
  state.messages.forEach((msg, idx) => {
    const isUser = msg.role === 'user';
    if (isUser) {
      html += `
        <div class="flex items-start justify-end space-x-3 mb-6 animate-message">
          <div class="max-w-[85%] md:max-w-[70%] bg-indigo-600 text-white px-4 py-3 rounded-2xl rounded-tr-sm shadow-md">
            <p class="text-sm leading-relaxed">${escapeHtml(msg.message)}</p>
            <span class="block text-[10px] text-indigo-200 mt-1 text-right">${msg.timestamp}</span>
          </div>
          <div class="w-8 h-8 rounded-full bg-indigo-500/30 border border-indigo-400/40 flex items-center justify-center text-indigo-300 font-bold text-xs flex-shrink-0">
            ${state.currentUser.full_name.charAt(0)}
          </div>
        </div>
      `;
    } else {
      html += `
        <div class="flex items-start space-x-3 mb-6 animate-message">
          <div class="w-8 h-8 rounded-full bg-slate-800 border border-indigo-500/40 flex items-center justify-center text-indigo-400 flex-shrink-0 shadow-lg">
            <i data-lucide="bot" class="w-4 h-4"></i>
          </div>
          <div class="max-w-[90%] md:max-w-[80%] space-y-3">
            <div class="bg-slate-800/90 border border-slate-700/70 px-4 py-3 rounded-2xl rounded-tl-sm text-slate-200 shadow-md">
              <!-- Intent Badge for Viva demonstration -->
              ${msg.intent ? `
                <div class="flex items-center space-x-2 mb-2 pb-1.5 border-b border-slate-700/50">
                  <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    Intent: ${msg.intent.replace('_', ' ')}
                  </span>
                  ${msg.confidence ? `<span class="text-[10px] text-slate-400">Confidence: ${(msg.confidence * 100).toFixed(0)}%</span>` : ''}
                </div>
              ` : ''}
              
              <!-- Formatted Message Body -->
              <div class="text-sm leading-relaxed prose prose-invert max-w-none">
                ${formatMarkdown(msg.message)}
              </div>

              <!-- Embedded Book Cards (if any) -->
              ${msg.books && msg.books.length > 0 ? renderInlineBookCards(msg.books) : ''}

              <span class="block text-[10px] text-slate-500 mt-2">${msg.timestamp}</span>
            </div>

            <!-- Follow-up Question Chips -->
            ${msg.suggestedQuestions && msg.suggestedQuestions.length > 0 ? `
              <div class="flex flex-wrap gap-1.5 pt-1">
                ${msg.suggestedQuestions.map(q => `
                  <button onclick="sendChatMessage('${escapeQuotes(q)}')" class="text-xs bg-slate-800/80 hover:bg-indigo-600/20 text-slate-300 hover:text-indigo-300 border border-slate-700 hover:border-indigo-500/40 px-3 py-1 rounded-full transition flex items-center space-x-1">
                    <span>${escapeHtml(q)}</span>
                    <i data-lucide="arrow-right" class="w-3 h-3 ml-1 text-slate-400"></i>
                  </button>
                `).join('')}
              </div>
            ` : ''}
          </div>
        </div>
      `;
    }
  });

  // Typing indicator
  if (state.isTyping) {
    html += `
      <div class="flex items-start space-x-3 mb-6 animate-message">
        <div class="w-8 h-8 rounded-full bg-slate-800 border border-indigo-500/40 flex items-center justify-center text-indigo-400 flex-shrink-0">
          <i data-lucide="bot" class="w-4 h-4"></i>
        </div>
        <div class="bg-slate-800/90 border border-slate-700/70 px-4 py-3 rounded-2xl rounded-tl-sm text-slate-400 flex items-center space-x-2">
          <span class="text-xs font-medium mr-1 text-slate-300">Consulting library knowledge base</span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </div>
      </div>
    `;
  }

  container.innerHTML = html;
  initIcons();

  // Scroll to bottom
  const scrollContainer = document.getElementById('chatScrollContainer');
  if (scrollContainer) {
    scrollContainer.scrollTop = scrollContainer.scrollHeight;
  }
}

function renderInlineBookCards(books) {
  return `
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3 pt-3 border-t border-slate-700/60">
      ${books.map(b => {
        const isAvailable = b.available_copies > 0;
        const diffBadge = getDifficultyBadgeClass(b.difficulty);
        return `
          <div class="p-3 rounded-xl bg-slate-900/80 border border-slate-700/80 flex flex-col justify-between hover:border-indigo-500/50 transition">
            <div>
              <div class="flex items-start justify-between gap-2 mb-1.5">
                <span class="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full ${diffBadge}">
                  ${b.difficulty || 'Intermediate'}
                </span>
                <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full ${isAvailable ? 'badge-available' : 'badge-unavailable'}">
                  ${isAvailable ? `${b.available_copies} / ${b.total_copies} Avail` : 'Issued Out'}
                </span>
              </div>
              <h4 class="text-xs font-bold text-slate-100 line-clamp-1 hover:text-indigo-400 cursor-pointer" onclick="showBookModal(${b.id})">
                ${escapeHtml(b.title)}
              </h4>
              <p class="text-[11px] text-slate-400 line-clamp-1 mt-0.5">by ${escapeHtml(b.author)}</p>
              <div class="flex items-center space-x-2 mt-2 text-[10px] text-slate-400">
                <span class="bg-slate-800 px-1.5 py-0.5 rounded border border-slate-700">📍 Shelf ${b.shelf_number}</span>
                <span class="truncate">${b.edition || ''}</span>
              </div>
              ${b.recommendation_reason ? `
                <p class="text-[10px] text-indigo-300/90 italic bg-indigo-950/40 p-1.5 rounded mt-2 border border-indigo-900/50">
                  "${escapeHtml(b.recommendation_reason)}"
                </p>
              ` : ''}
            </div>

            <div class="flex items-center space-x-1.5 mt-3 pt-2 border-t border-slate-800">
              <button onclick="sendChatMessage('Is ${escapeQuotes(b.title)} available?')" class="flex-1 text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 py-1 rounded text-center transition">
                Check Status
              </button>
              <button onclick="showBookModal(${b.id})" class="text-[11px] bg-indigo-600/30 hover:bg-indigo-600 text-indigo-300 hover:text-white px-2.5 py-1 rounded transition">
                Inspect
              </button>
            </div>
          </div>
        `;
      }).join('')}
    </div>
  `;
}

// ----------------- Speech Recognition ----------------- //

function setupSpeechRecognition() {
  const micBtn = document.getElementById('micBtn');
  if (!micBtn) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    micBtn.title = 'Speech Recognition is not supported by your browser.';
    micBtn.classList.add('opacity-50', 'cursor-not-allowed');
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-US';

  micBtn.addEventListener('click', () => {
    if (state.isRecording) {
      recognition.stop();
      return;
    }

    try {
      recognition.start();
      state.isRecording = true;
      micBtn.classList.add('recording-pulse');
      showToast('Listening... Speak your library query.', 'info');
    } catch (e) {
      console.error(e);
    }
  });

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    const chatInput = document.getElementById('chatInput');
    if (chatInput && transcript) {
      chatInput.value = transcript;
      showToast(`Heard: "${transcript}"`, 'success');
      // Auto send
      sendChatMessage(transcript);
    }
  };

  recognition.onend = () => {
    state.isRecording = false;
    micBtn.classList.remove('recording-pulse');
  };

  recognition.onerror = (e) => {
    state.isRecording = false;
    micBtn.classList.remove('recording-pulse');
    showToast(`Microphone error: ${e.error}`, 'error');
  };
}

// ----------------- Book Catalog View ----------------- //

async function loadCatalog() {
  const container = document.getElementById('catalogGrid');
  const countLabel = document.getElementById('catalogCountLabel');
  if (!container) return;

  container.innerHTML = `
    <div class="col-span-full py-12 text-center text-slate-400">
      <div class="typing-dot mr-1"></div><div class="typing-dot mr-1"></div><div class="typing-dot"></div>
      <p class="text-xs mt-2">Loading library catalog...</p>
    </div>
  `;

  try {
    const data = await API.getBooks({
      search: state.catalog.search,
      category: state.catalog.category,
      difficulty: state.catalog.difficulty,
      available_only: state.catalog.availableOnly,
      limit: 60
    });

    state.catalog.books = data.books;
    state.catalog.total = data.total;

    if (countLabel) {
      countLabel.textContent = `Showing ${data.books.length} of ${data.total} books`;
    }

    if (data.books.length === 0) {
      container.innerHTML = `
        <div class="col-span-full py-12 text-center text-slate-400 glass-card rounded-2xl p-8">
          <i data-lucide="book-x" class="w-12 h-12 mx-auto text-slate-500 mb-3"></i>
          <h3 class="text-base font-semibold text-slate-300">No books found</h3>
          <p class="text-xs text-slate-500 mt-1 max-w-md mx-auto">No books match your current filter criteria. Try adjusting the search term or category filter.</p>
          <button onclick="resetCatalogFilters()" class="mt-4 px-4 py-2 bg-indigo-600 text-xs font-medium text-white rounded-xl hover:bg-indigo-500 transition">
            Reset Filters
          </button>
        </div>
      `;
      initIcons();
      return;
    }

    const isAdmin = state.currentUser.role === 'admin';

    container.innerHTML = data.books.map(b => {
      const isAvailable = b.available_copies > 0;
      const diffBadge = getDifficultyBadgeClass(b.difficulty);
      return `
        <div class="glass-card rounded-2xl p-4 flex flex-col justify-between border border-slate-700/60 hover:border-indigo-500/40">
          <div>
            <div class="flex items-start justify-between gap-2 mb-2">
              <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${diffBadge}">
                ${b.difficulty}
              </span>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${isAvailable ? 'badge-available' : 'badge-unavailable'}">
                ${isAvailable ? `${b.available_copies}/${b.total_copies} Available` : 'All Issued'}
              </span>
            </div>

            <h3 class="text-sm font-bold text-slate-100 hover:text-indigo-400 cursor-pointer line-clamp-2" onclick="showBookModal(${b.id})">
              ${escapeHtml(b.title)}
            </h3>
            <p class="text-xs text-slate-400 mt-1 line-clamp-1">by ${escapeHtml(b.author)}</p>
            <p class="text-xs text-slate-500 mt-2 line-clamp-2">${escapeHtml(b.description || '')}</p>

            <div class="mt-3 pt-3 border-t border-slate-800 text-[11px] text-slate-400 space-y-1">
              <div class="flex justify-between">
                <span class="text-slate-500">Subject:</span>
                <span class="text-slate-300 font-medium">${escapeHtml(b.subject)}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-500">Shelf:</span>
                <span class="text-slate-300 font-mono font-semibold">${escapeHtml(b.shelf_number)}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-500">Publisher:</span>
                <span class="text-slate-400 truncate max-w-[150px]">${escapeHtml(b.publisher || 'N/A')} (${b.publication_year})</span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
            <button onclick="showBookModal(${b.id})" class="flex-1 py-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-xl transition">
              Details
            </button>
            <button onclick="askAssistantAboutBook('${escapeQuotes(b.title)}')" class="py-1.5 px-3 bg-indigo-600/30 hover:bg-indigo-600 text-indigo-300 hover:text-white text-xs font-medium rounded-xl transition flex items-center space-x-1" title="Ask Assistant in Chat">
              <i data-lucide="message-square" class="w-3.5 h-3.5"></i>
              <span>Ask AI</span>
            </button>

            ${isAdmin ? `
              <div class="flex items-center space-x-1 pl-1 border-l border-slate-800">
                <button onclick="openEditBookModal(${b.id})" class="p-1.5 text-slate-400 hover:text-amber-400 hover:bg-slate-800 rounded-lg transition" title="Edit Book">
                  <i data-lucide="edit-2" class="w-3.5 h-3.5"></i>
                </button>
                <button onclick="confirmDeleteBook(${b.id}, '${escapeQuotes(b.title)}')" class="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition" title="Delete Book">
                  <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                </button>
              </div>
            ` : ''}
          </div>
        </div>
      `;
    }).join('');

    initIcons();
  } catch (err) {
    container.innerHTML = `<div class="col-span-full text-center text-red-400 py-8">${err.message}</div>`;
  }
}

function setupCatalogFilters() {
  const searchInput = document.getElementById('catalogSearch');
  const catFilter = document.getElementById('catalogCategoryFilter');
  const diffFilter = document.getElementById('catalogDifficultyFilter');
  const availToggle = document.getElementById('catalogAvailableToggle');

  let debounceTimer;
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        state.catalog.search = e.target.value.trim();
        loadCatalog();
      }, 300);
    });
  }

  if (catFilter) {
    catFilter.addEventListener('change', (e) => {
      state.catalog.category = e.target.value;
      loadCatalog();
    });
  }

  if (diffFilter) {
    diffFilter.addEventListener('change', (e) => {
      state.catalog.difficulty = e.target.value;
      loadCatalog();
    });
  }

  if (availToggle) {
    availToggle.addEventListener('change', (e) => {
      state.catalog.availableOnly = e.target.checked;
      loadCatalog();
    });
  }
}

function resetCatalogFilters() {
  state.catalog.search = '';
  state.catalog.category = '';
  state.catalog.difficulty = '';
  state.catalog.availableOnly = false;

  const searchInput = document.getElementById('catalogSearch');
  const catFilter = document.getElementById('catalogCategoryFilter');
  const diffFilter = document.getElementById('catalogDifficultyFilter');
  const availToggle = document.getElementById('catalogAvailableToggle');

  if (searchInput) searchInput.value = '';
  if (catFilter) catFilter.value = '';
  if (diffFilter) diffFilter.value = '';
  if (availToggle) availToggle.checked = false;

  loadCatalog();
}

function askAssistantAboutBook(title) {
  switchView('chat');
  sendChatMessage(`Tell me about "${title}" and check its availability.`);
}

// ----------------- Categories Explorer ----------------- //

async function loadCategories() {
  const container = document.getElementById('categoriesGrid');
  if (!container) return;

  try {
    const data = await API.getCategories();
    state.categories = data.categories;

    // Populate category dropdown in catalog filter as well
    const catFilter = document.getElementById('catalogCategoryFilter');
    if (catFilter && catFilter.options.length <= 1) {
      data.categories.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.name;
        opt.textContent = `${c.name} (${c.book_count})`;
        catFilter.appendChild(opt);
      });
    }

    container.innerHTML = data.categories.map(c => {
      return `
        <div class="glass-card rounded-2xl p-5 border border-slate-700/60 hover:border-indigo-500/40 flex flex-col justify-between">
          <div>
            <div class="w-10 h-10 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center mb-3 border border-indigo-500/30">
              <i data-lucide="${getCategoryIcon(c.icon)}" class="w-5 h-5"></i>
            </div>
            <h3 class="text-base font-bold text-slate-100">${escapeHtml(c.name)}</h3>
            <span class="inline-block text-[11px] font-semibold text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded-full mt-1 border border-indigo-500/20">
              ${c.book_count} Books
            </span>
            <p class="text-xs text-slate-400 mt-3 leading-relaxed">${escapeHtml(c.description || '')}</p>
          </div>

          <div class="mt-4 pt-3 border-t border-slate-800 flex items-center space-x-2">
            <button onclick="filterCatalogByCategory('${escapeQuotes(c.name)}')" class="flex-1 py-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-xl transition text-center">
              Browse Books
            </button>
            <button onclick="askAssistantAboutCategory('${escapeQuotes(c.name)}')" class="py-1.5 px-3 bg-indigo-600/30 hover:bg-indigo-600 text-indigo-300 hover:text-white text-xs font-medium rounded-xl transition" title="Ask Assistant in Chat">
              Ask AI
            </button>
          </div>
        </div>
      `;
    }).join('');

    initIcons();
  } catch (err) {
    container.innerHTML = `<div class="col-span-full text-center text-red-400 py-8">${err.message}</div>`;
  }
}

function filterCatalogByCategory(catName) {
  state.catalog.category = catName;
  const catFilter = document.getElementById('catalogCategoryFilter');
  if (catFilter) catFilter.value = catName;
  switchView('catalog');
}

function askAssistantAboutCategory(catName) {
  switchView('chat');
  sendChatMessage(`What books are available for ${catName}?`);
}

// ----------------- Recommendations Tab ----------------- //

async function generateRecommendations() {
  const subjInput = document.getElementById('recSubjectInput');
  const diffSelect = document.getElementById('recDifficultySelect');
  const resultsContainer = document.getElementById('recResultsContainer');

  if (!resultsContainer) return;

  const subject = subjInput ? subjInput.value.trim() : '';
  const diff = diffSelect ? diffSelect.value : '';

  resultsContainer.innerHTML = `
    <div class="py-12 text-center text-slate-400">
      <div class="typing-dot mr-1"></div><div class="typing-dot mr-1"></div><div class="typing-dot"></div>
      <p class="text-xs mt-2">Generating personalized recommendations...</p>
    </div>
  `;

  try {
    const data = await API.getRecommendations(subject, diff, 6);
    if (!data.recommendations || data.recommendations.length === 0) {
      resultsContainer.innerHTML = `
        <div class="text-center py-8 text-slate-400">
          <p class="text-sm">No recommendations found matching your criteria. Try another subject!</p>
        </div>
      `;
      return;
    }

    resultsContainer.innerHTML = `
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        ${data.recommendations.map(b => {
          const isAvail = b.available_copies > 0;
          return `
            <div class="glass-card rounded-2xl p-4 border border-slate-700/70 flex flex-col justify-between">
              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${getDifficultyBadgeClass(b.difficulty)}">
                    ${b.difficulty}
                  </span>
                  <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${isAvail ? 'badge-available' : 'badge-unavailable'}">
                    ${isAvail ? `${b.available_copies} Copies Available` : 'Issued'}
                  </span>
                </div>
                <h4 class="text-sm font-bold text-slate-100 hover:text-indigo-400 cursor-pointer" onclick="showBookModal(${b.id})">
                  ${escapeHtml(b.title)}
                </h4>
                <p class="text-xs text-slate-400 mt-1">by ${escapeHtml(b.author)}</p>

                <div class="mt-3 bg-indigo-950/40 p-2.5 rounded-xl border border-indigo-900/60">
                  <p class="text-[11px] text-indigo-300 font-medium">💡 Rationale:</p>
                  <p class="text-[11px] text-slate-300 mt-0.5 leading-relaxed">${escapeHtml(b.recommendation_reason || '')}</p>
                </div>
              </div>

              <div class="mt-4 pt-3 border-t border-slate-800 flex items-center space-x-2">
                <button onclick="showBookModal(${b.id})" class="flex-1 py-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-xl transition text-center">
                  Book Details
                </button>
                <button onclick="askAssistantAboutBook('${escapeQuotes(b.title)}')" class="py-1.5 px-3 bg-indigo-600/30 hover:bg-indigo-600 text-indigo-300 hover:text-white text-xs font-medium rounded-xl transition">
                  Ask AI
                </button>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;

    initIcons();
  } catch (err) {
    resultsContainer.innerHTML = `<div class="text-center text-red-400 py-6">${err.message}</div>`;
  }
}

// ----------------- Library Rules & Timings ----------------- //

async function loadLibraryPolicies() {
  const container = document.getElementById('policiesAccordion');
  if (!container) return;

  try {
    const data = await API.getLibraryInfo();
    state.policies = data.policies;

    const categories = {
      'timings': { title: '🕒 Opening Hours & Timings', icon: 'clock' },
      'borrowing': { title: '📚 Borrowing & Issue Rules', icon: 'book-open' },
      'fines': { title: '💰 Overdue Fines & Late Return', icon: 'coins' },
      'rules': { title: '⚠️ Code of Conduct & Lost Books', icon: 'shield-alert' },
      'general': { title: '🏛️ General Information & Membership', icon: 'info' }
    };

    let html = '';
    for (const [catKey, meta] of Object.entries(categories)) {
      const items = data.grouped[catKey] || [];
      if (items.length === 0) continue;

      html += `
        <div class="glass-card rounded-2xl p-5 border border-slate-700/60 mb-4">
          <h3 class="text-base font-bold text-slate-100 flex items-center space-x-2 mb-4 pb-2 border-b border-slate-800">
            <span>${meta.title}</span>
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            ${items.map(p => `
              <div class="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
                <h4 class="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-1">${escapeHtml(p.title)}</h4>
                <p class="text-xs text-slate-300 leading-relaxed">${escapeHtml(p.value)}</p>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    container.innerHTML = html;
    initIcons();
  } catch (err) {
    container.innerHTML = `<div class="text-center text-red-400 py-8">${err.message}</div>`;
  }
}

// ----------------- Admin Dashboard ----------------- //

async function loadAdminDashboard() {
  if (state.currentUser.role !== 'admin') {
    const adminContainer = document.getElementById('adminView');
    if (adminContainer) {
      adminContainer.innerHTML = `
        <div class="max-w-md mx-auto text-center py-16 px-6 glass-card rounded-3xl border border-slate-700/60">
          <div class="w-14 h-14 rounded-2xl bg-amber-500/20 text-amber-400 flex items-center justify-center mx-auto mb-4 border border-amber-500/30">
            <i data-lucide="lock" class="w-7 h-7"></i>
          </div>
          <h2 class="text-xl font-bold text-slate-100 mb-2">Administrator Access Required</h2>
          <p class="text-xs text-slate-400 mb-6 leading-relaxed">
            You are currently browsing as a Student. Switch to the Administrator account to manage book catalog records, adjust copy counts, update library rules, and view usage statistics.
          </p>
          <button onclick="handleRoleSwitch('admin')" class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl transition shadow-lg shadow-indigo-600/20">
            Switch to Admin (Dr. Ramesh Patil)
          </button>
        </div>
      `;
      initIcons();
    }
    return;
  }

  try {
    const stats = await API.getAdminStats();
    state.adminStats = stats;
    renderAdminDashboard(stats);
  } catch (err) {
    console.error(err);
  }
}

function renderAdminDashboard(stats) {
  const container = document.getElementById('adminContentArea');
  if (!container) return;

  const s = stats.summary;

  container.innerHTML = `
    <!-- Top Summary Stat Cards -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
      <div class="glass-card p-4 rounded-2xl border border-slate-700/60">
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Titles</p>
        <h3 class="text-2xl font-extrabold text-slate-100 mt-1">${s.total_titles}</h3>
        <p class="text-[10px] text-indigo-400 mt-1">Unique textbook editions</p>
      </div>
      <div class="glass-card p-4 rounded-2xl border border-slate-700/60">
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Copies</p>
        <h3 class="text-2xl font-extrabold text-slate-100 mt-1">${s.total_volume}</h3>
        <p class="text-[10px] text-slate-400 mt-1">Physical book volumes</p>
      </div>
      <div class="glass-card p-4 rounded-2xl border border-slate-700/60">
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Available</p>
        <h3 class="text-2xl font-extrabold text-emerald-400 mt-1">${s.available_copies}</h3>
        <p class="text-[10px] text-emerald-500/80 mt-1">Ready on shelves</p>
      </div>
      <div class="glass-card p-4 rounded-2xl border border-slate-700/60">
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Issued Out</p>
        <h3 class="text-2xl font-extrabold text-amber-400 mt-1">${s.issued_copies}</h3>
        <p class="text-[10px] text-amber-500/80 mt-1">With students / faculty</p>
      </div>
      <div class="glass-card p-4 rounded-2xl border border-slate-700/60">
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Categories</p>
        <h3 class="text-2xl font-extrabold text-indigo-400 mt-1">${s.total_categories}</h3>
        <p class="text-[10px] text-indigo-400/80 mt-1">Core branches</p>
      </div>
      <div class="glass-card p-4 rounded-2xl border border-slate-700/60">
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Authors</p>
        <h3 class="text-2xl font-extrabold text-purple-400 mt-1">${s.total_authors}</h3>
        <p class="text-[10px] text-purple-400/80 mt-1">Acclaimed textbook writers</p>
      </div>
    </div>

    <!-- Management Controls Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-4">
      <div>
        <h3 class="text-base font-bold text-slate-100">Library Catalog Management</h3>
        <p class="text-xs text-slate-400">Add, modify metadata, adjust copy counts, or remove catalog records</p>
      </div>
      <button onclick="openAddBookModal()" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl transition flex items-center space-x-1.5 shadow-lg shadow-indigo-600/20">
        <i data-lucide="plus" class="w-4 h-4"></i>
        <span>Add New Book</span>
      </button>
    </div>

    <!-- Books Management Table -->
    <div class="glass-card rounded-2xl border border-slate-700/60 overflow-hidden mb-6">
      <div class="p-3 bg-slate-900/60 border-b border-slate-800 flex items-center justify-between gap-3">
        <input type="text" id="adminTableSearch" placeholder="Search title, ISBN, author, shelf..." class="bg-slate-800/80 text-xs text-slate-200 px-3 py-1.5 rounded-xl border border-slate-700 focus:outline-none focus:border-indigo-500 w-64" oninput="filterAdminBooksTable(this.value)">
        <span class="text-[11px] text-slate-400" id="adminTableCount">Displaying catalog books</span>
      </div>
      <div class="overflow-x-auto max-h-96">
        <table class="w-full text-left text-xs text-slate-300">
          <thead class="bg-slate-900/90 text-[10px] uppercase font-bold text-slate-400 tracking-wider sticky top-0 z-10 border-b border-slate-800">
            <tr>
              <th class="p-3">Title & Author</th>
              <th class="p-3">Category</th>
              <th class="p-3">Difficulty</th>
              <th class="p-3 text-center">Copies (Avail/Total)</th>
              <th class="p-3">Shelf</th>
              <th class="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody id="adminBooksTableBody" class="divide-y divide-slate-800/60">
            <!-- Rendered by renderAdminTableRows -->
          </tbody>
        </table>
      </div>
    </div>

    <!-- Category & Query Activity Breakdown -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- Category Distribution Breakdown -->
      <div class="glass-card rounded-2xl p-5 border border-slate-700/60">
        <h4 class="text-sm font-bold text-slate-100 mb-3 flex items-center justify-between">
          <span>Category Distribution</span>
          <span class="text-xs text-indigo-400 font-normal">Books per Domain</span>
        </h4>
        <div class="space-y-2.5 max-h-64 overflow-y-auto pr-2">
          ${stats.category_distribution.map(c => {
            const pct = Math.round((c.count / s.total_titles) * 100);
            return `
              <div>
                <div class="flex justify-between text-xs mb-1">
                  <span class="text-slate-300 font-medium">${c.category}</span>
                  <span class="text-slate-400">${c.count} titles (${c.available_copies}/${c.total_copies} copies)</span>
                </div>
                <div class="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div class="h-full bg-indigo-500 rounded-full" style="width: ${pct}%"></div>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>

      <!-- Recent Chat Queries Log -->
      <div class="glass-card rounded-2xl p-5 border border-slate-700/60">
        <h4 class="text-sm font-bold text-slate-100 mb-3 flex items-center justify-between">
          <span>Recent Student Inquiries</span>
          <span class="text-xs text-indigo-400 font-normal">NLP Log</span>
        </h4>
        <div class="space-y-2 max-h-64 overflow-y-auto pr-1">
          ${stats.recent_queries && stats.recent_queries.length > 0 ? stats.recent_queries.map(q => `
            <div class="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80 text-xs">
              <div class="flex items-center justify-between text-[10px] text-slate-500 mb-1">
                <span class="font-bold text-indigo-400 uppercase tracking-wider">Intent: ${escapeHtml(q.intent || 'unknown')}</span>
                <span>${q.timestamp ? q.timestamp.split('T')[0] : ''}</span>
              </div>
              <p class="text-slate-200">"${escapeHtml(q.message)}"</p>
            </div>
          `).join('') : '<p class="text-xs text-slate-500">No chat logs recorded yet.</p>'}
        </div>
      </div>
    </div>
  `;

  initIcons();
  loadAdminBooksTableData();
}

let adminAllBooks = [];

async function loadAdminBooksTableData() {
  try {
    const data = await API.getBooks({ limit: 100 });
    adminAllBooks = data.books;
    renderAdminTableRows(adminAllBooks);
  } catch (e) {
    console.error(e);
  }
}

function renderAdminTableRows(books) {
  const tbody = document.getElementById('adminBooksTableBody');
  const countEl = document.getElementById('adminTableCount');
  if (!tbody) return;

  if (countEl) countEl.textContent = `Showing ${books.length} books`;

  tbody.innerHTML = books.map(b => {
    return `
      <tr class="hover:bg-slate-800/40 transition">
        <td class="p-3">
          <p class="font-bold text-slate-200">${escapeHtml(b.title)}</p>
          <p class="text-[11px] text-slate-400">by ${escapeHtml(b.author)} • <span class="font-mono">${b.isbn}</span></p>
        </td>
        <td class="p-3 text-slate-300">${escapeHtml(b.category)}</td>
        <td class="p-3">
          <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${getDifficultyBadgeClass(b.difficulty)}">
            ${b.difficulty}
          </span>
        </td>
        <td class="p-3 text-center">
          <div class="inline-flex items-center space-x-1.5 bg-slate-900 px-2 py-1 rounded-lg border border-slate-700/60">
            <button onclick="adjustBookCopies(${b.id}, ${b.available_copies - 1})" class="w-5 h-5 flex items-center justify-center rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold ${b.available_copies <= 0 ? 'opacity-30 cursor-not-allowed' : ''}" ${b.available_copies <= 0 ? 'disabled' : ''}>-</button>
            <span class="font-bold font-mono px-1 ${b.available_copies > 0 ? 'text-emerald-400' : 'text-red-400'}">${b.available_copies}</span>
            <span class="text-slate-500">/</span>
            <span class="font-bold font-mono text-slate-400">${b.total_copies}</span>
            <button onclick="adjustBookCopies(${b.id}, ${b.available_copies + 1})" class="w-5 h-5 flex items-center justify-center rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold ${b.available_copies >= b.total_copies ? 'opacity-30 cursor-not-allowed' : ''}" ${b.available_copies >= b.total_copies ? 'disabled' : ''}>+</button>
          </div>
        </td>
        <td class="p-3 font-mono font-semibold text-slate-300">${b.shelf_number}</td>
        <td class="p-3 text-right">
          <div class="inline-flex items-center space-x-1">
            <button onclick="openEditBookModal(${b.id})" class="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-amber-400 transition" title="Edit Metadata">
              <i data-lucide="edit-2" class="w-3.5 h-3.5"></i>
            </button>
            <button onclick="confirmDeleteBook(${b.id}, '${escapeQuotes(b.title)}')" class="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-red-400 transition" title="Delete">
              <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');

  initIcons();
}

function filterAdminBooksTable(keyword) {
  const q = keyword.toLowerCase().trim();
  if (!q) {
    renderAdminTableRows(adminAllBooks);
    return;
  }
  const filtered = adminAllBooks.filter(b => 
    b.title.toLowerCase().includes(q) ||
    b.author.toLowerCase().includes(q) ||
    b.isbn.toLowerCase().includes(q) ||
    b.shelf_number.toLowerCase().includes(q) ||
    b.category.toLowerCase().includes(q)
  );
  renderAdminTableRows(filtered);
}

async function adjustBookCopies(bookId, newCopies) {
  if (newCopies < 0) return;
  try {
    await API.updateBookCopies(bookId, newCopies);
    showToast('Available copies updated.', 'success');
    loadAdminDashboard();
  } catch (e) {
    showToast(e.message, 'error');
  }
}

async function confirmDeleteBook(bookId, title) {
  if (confirm(`Are you sure you want to delete "${title}" from the library catalog?`)) {
    try {
      await API.deleteBook(bookId);
      showToast(`Book "${title}" deleted successfully.`, 'success');
      loadAdminDashboard();
    } catch (e) {
      showToast(e.message, 'error');
    }
  }
}

// ----------------- About Project & Viva Diagnostics ----------------- //

async function loadVivaDiagnostics() {
  const container = document.getElementById('vivaDiagnosticsArea');
  if (!container) return;

  try {
    const data = await API.getDiagnostics();

    container.innerHTML = `
      <!-- Project Metadata Header -->
      <div class="glass-card rounded-3xl p-6 border border-slate-700/60 mb-6 bg-gradient-to-r from-indigo-950/40 to-slate-900/60">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-2">
              <i data-lucide="graduation-cap" class="w-4 h-4"></i>
              <span>Third-Year Computer Engineering AI Course CI3 Project</span>
            </div>
            <h2 class="text-2xl font-extrabold text-slate-100">Digital Library Assistant</h2>
            <p class="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              An intelligent conversational assistant combining Natural Language Processing, Intent Classification,
              Entity Extraction, and Retrieval-Augmented Generation (RAG) over a structured SQLite knowledge base.
            </p>
          </div>
          <div class="text-right">
            <span class="text-[11px] uppercase tracking-wider font-bold text-slate-500 block">System Reliability</span>
            <span class="text-emerald-400 font-extrabold text-lg flex items-center justify-end space-x-1">
              <i data-lucide="shield-check" class="w-5 h-5 mr-1"></i>
              <span>100% Grounded (Zero Hallucination)</span>
            </span>
          </div>
        </div>

        <!-- AI Concepts Badges -->
        <div class="mt-6 pt-4 border-t border-slate-800 flex flex-wrap gap-2">
          ${['Natural Language Processing (NLP)', 'Intent Classification', 'Conversational AI & Memory', 'Information Retrieval', 'Semantic Search & TF-IDF', 'Recommendation Systems', 'Retrieval-Augmented Generation (RAG)', 'Database Grounding'].map(c => `
            <span class="text-xs font-medium px-3 py-1 rounded-xl bg-slate-800 text-slate-300 border border-slate-700/80">
              ✓ ${c}
            </span>
          `).join('')}
        </div>
      </div>

      <!-- End-to-End AI Architecture Pipeline -->
      <div class="glass-card rounded-3xl p-6 border border-slate-700/60 mb-6">
        <h3 class="text-base font-bold text-slate-100 mb-1 flex items-center space-x-2">
          <i data-lucide="git-merge" class="w-5 h-5 text-indigo-400"></i>
          <span>AI Architecture & Request Flow</span>
        </h3>
        <p class="text-xs text-slate-400 mb-6">The 6-stage explainable pipeline executed for each user inquiry:</p>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          ${data.architecture_pipeline.map(step => `
            <div class="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 flex flex-col justify-between">
              <div>
                <span class="w-6 h-6 rounded-lg bg-indigo-600/30 text-indigo-400 border border-indigo-500/40 text-xs font-bold flex items-center justify-center mb-2">
                  ${step.stage}
                </span>
                <h4 class="text-xs font-bold text-slate-200">${step.name}</h4>
                <p class="text-[11px] text-slate-400 mt-1 leading-relaxed">${step.desc}</p>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Live Diagnostics Test Matrix -->
      <div class="glass-card rounded-3xl p-6 border border-slate-700/60 mb-6">
        <h3 class="text-base font-bold text-slate-100 mb-1 flex items-center space-x-2">
          <i data-lucide="activity" class="w-5 h-5 text-indigo-400"></i>
          <span>Live Intent & Entity Classification Matrix</span>
        </h3>
        <p class="text-xs text-slate-400 mb-4">Sample test cases demonstrating classification confidence and extracted entities:</p>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-900/80 text-[10px] uppercase font-bold text-slate-400 tracking-wider">
              <tr>
                <th class="p-3">Sample Student Query</th>
                <th class="p-3">Predicted Intent</th>
                <th class="p-3">Confidence</th>
                <th class="p-3">Extracted Subject</th>
                <th class="p-3">Extracted Title</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60">
              ${data.live_intent_tests.map(t => `
                <tr class="hover:bg-slate-800/30">
                  <td class="p-3 font-medium text-slate-200">"${escapeHtml(t.query)}"</td>
                  <td class="p-3">
                    <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      ${t.detected_intent}
                    </span>
                  </td>
                  <td class="p-3 font-mono font-bold text-emerald-400">${(t.confidence * 100).toFixed(0)}%</td>
                  <td class="p-3 text-slate-400">${t.extracted_subject || '—'}</td>
                  <td class="p-3 text-slate-400 italic">${t.extracted_title ? escapeHtml(t.extracted_title) : '—'}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Viva Q&A Cheat Sheet Accordion -->
      <div class="glass-card rounded-3xl p-6 border border-slate-700/60">
        <h3 class="text-base font-bold text-slate-100 mb-1 flex items-center space-x-2">
          <i data-lucide="help-circle" class="w-5 h-5 text-indigo-400"></i>
          <span>Viva Voce Reference Questions & Answers</span>
        </h3>
        <p class="text-xs text-slate-400 mb-6">Prepared answers for viva examiners evaluating AI concepts:</p>

        <div class="space-y-3">
          ${data.viva_questions.map((vq, idx) => `
            <div class="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-4">
              <h4 class="text-xs font-bold text-indigo-400 flex items-start space-x-2">
                <span class="text-slate-500">Q${idx + 1}.</span>
                <span>${escapeHtml(vq.q)}</span>
              </h4>
              <p class="text-xs text-slate-300 mt-2 pl-5 leading-relaxed border-l-2 border-indigo-500/40">
                ${escapeHtml(vq.a)}
              </p>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    initIcons();
  } catch (err) {
    container.innerHTML = `<div class="text-center text-red-400 py-8">${err.message}</div>`;
  }
}

// ----------------- Book Inspector Modal ----------------- //

async function showBookModal(bookId) {
  const modal = document.getElementById('bookDetailModal');
  const body = document.getElementById('bookModalBody');
  if (!modal || !body) return;

  body.innerHTML = `
    <div class="py-12 text-center text-slate-400">
      <div class="typing-dot mr-1"></div><div class="typing-dot mr-1"></div><div class="typing-dot"></div>
      <p class="text-xs mt-2">Loading book details...</p>
    </div>
  `;
  modal.classList.remove('hidden');

  try {
    const book = await API.getBookById(bookId);
    state.selectedBook = book;
    const isAvail = book.available_copies > 0;

    body.innerHTML = `
      <div class="space-y-4">
        <div class="flex items-start justify-between gap-3">
          <div>
            <div class="flex items-center space-x-2 mb-2">
              <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${getDifficultyBadgeClass(book.difficulty)}">
                ${book.difficulty}
              </span>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${isAvail ? 'badge-available' : 'badge-unavailable'}">
                ${isAvail ? `${book.available_copies} of ${book.total_copies} Copies Available` : 'Currently Issued Out'}
              </span>
            </div>
            <h3 class="text-lg font-bold text-slate-100">${escapeHtml(book.title)}</h3>
            <p class="text-xs text-slate-400 mt-0.5">by <span class="text-slate-200 font-semibold">${escapeHtml(book.author)}</span></p>
          </div>
        </div>

        <p class="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
          ${escapeHtml(book.description || 'No description available.')}
        </p>

        <div class="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
          <div class="p-3 rounded-xl bg-slate-900/40 border border-slate-800/80">
            <span class="text-[10px] text-slate-500 uppercase font-bold block">Shelf Number</span>
            <span class="font-mono font-bold text-indigo-400 text-sm mt-0.5 block">${escapeHtml(book.shelf_number)}</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900/40 border border-slate-800/80">
            <span class="text-[10px] text-slate-500 uppercase font-bold block">Physical Location</span>
            <span class="text-slate-200 font-medium text-xs mt-0.5 block truncate" title="${escapeHtml(book.location)}">${escapeHtml(book.location)}</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900/40 border border-slate-800/80">
            <span class="text-[10px] text-slate-500 uppercase font-bold block">ISBN</span>
            <span class="font-mono text-slate-300 text-xs mt-0.5 block">${escapeHtml(book.isbn)}</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900/40 border border-slate-800/80">
            <span class="text-[10px] text-slate-500 uppercase font-bold block">Publisher & Year</span>
            <span class="text-slate-300 text-xs mt-0.5 block">${escapeHtml(book.publisher || 'N/A')} (${book.publication_year})</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900/40 border border-slate-800/80">
            <span class="text-[10px] text-slate-500 uppercase font-bold block">Edition</span>
            <span class="text-slate-300 text-xs mt-0.5 block">${escapeHtml(book.edition || '1st')}</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900/40 border border-slate-800/80">
            <span class="text-[10px] text-slate-500 uppercase font-bold block">Category</span>
            <span class="text-slate-300 text-xs mt-0.5 block">${escapeHtml(book.category)}</span>
          </div>
        </div>

        <div class="flex items-center space-x-2 pt-3 border-t border-slate-800">
          <button onclick="askAssistantAboutBook('${escapeQuotes(book.title)}'); closeBookModal();" class="flex-1 py-2 px-4 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl transition flex items-center justify-center space-x-1.5 shadow-lg shadow-indigo-600/20">
            <i data-lucide="message-square" class="w-4 h-4"></i>
            <span>Ask Chatbot About This Book</span>
          </button>
          <button onclick="closeBookModal()" class="py-2 px-4 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-xl transition">
            Close
          </button>
        </div>
      </div>
    `;

    initIcons();
  } catch (err) {
    body.innerHTML = `<div class="text-center text-red-400 py-6">${err.message}</div>`;
  }
}

function closeBookModal() {
  const modal = document.getElementById('bookDetailModal');
  if (modal) modal.classList.add('hidden');
}

// ----------------- Add / Edit Book Modal ----------------- //

function openAddBookModal() {
  const modal = document.getElementById('bookFormModal');
  const title = document.getElementById('bookFormTitle');
  const form = document.getElementById('bookForm');
  if (!modal || !form) return;

  if (title) title.textContent = 'Add New Book to Knowledge Base';
  form.reset();
  form.setAttribute('data-mode', 'add');
  form.removeAttribute('data-book-id');

  // Pre-fill categories
  populateCategorySelect('formCategory');

  modal.classList.remove('hidden');
  initIcons();
}

async function openEditBookModal(bookId) {
  const modal = document.getElementById('bookFormModal');
  const title = document.getElementById('bookFormTitle');
  const form = document.getElementById('bookForm');
  if (!modal || !form) return;

  try {
    const book = await API.getBookById(bookId);
    if (title) title.textContent = `Edit Book: ${book.title}`;
    form.setAttribute('data-mode', 'edit');
    form.setAttribute('data-book-id', bookId);

    populateCategorySelect('formCategory', book.category);

    document.getElementById('formIsbn').value = book.isbn;
    document.getElementById('formTitle').value = book.title;
    document.getElementById('formAuthor').value = book.author;
    document.getElementById('formSubject').value = book.subject;
    document.getElementById('formDifficulty').value = book.difficulty;
    document.getElementById('formPublisher').value = book.publisher || '';
    document.getElementById('formYear').value = book.publication_year;
    document.getElementById('formEdition').value = book.edition || '';
    document.getElementById('formTotalCopies').value = book.total_copies;
    document.getElementById('formAvailableCopies').value = book.available_copies;
    document.getElementById('formShelf').value = book.shelf_number;
    document.getElementById('formLocation').value = book.location;
    document.getElementById('formDescription').value = book.description || '';

    modal.classList.remove('hidden');
    initIcons();
  } catch (e) {
    showToast(e.message, 'error');
  }
}

function closeBookFormModal() {
  const modal = document.getElementById('bookFormModal');
  if (modal) modal.classList.add('hidden');
}

function populateCategorySelect(selectId, selectedVal) {
  const select = document.getElementById(selectId);
  if (!select) return;
  select.innerHTML = '';
  state.categories.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.name;
    opt.textContent = c.name;
    if (selectedVal && selectedVal === c.name) opt.selected = true;
    select.appendChild(opt);
  });
}

async function handleBookFormSubmit(e) {
  e.preventDefault();
  const form = document.getElementById('bookForm');
  if (!form) return;

  const mode = form.getAttribute('data-mode');
  const bookId = form.getAttribute('data-book-id');

  const bookData = {
    isbn: document.getElementById('formIsbn').value.trim(),
    title: document.getElementById('formTitle').value.trim(),
    author: document.getElementById('formAuthor').value.trim(),
    category: document.getElementById('formCategory').value,
    subject: document.getElementById('formSubject').value.trim(),
    difficulty: document.getElementById('formDifficulty').value,
    publisher: document.getElementById('formPublisher').value.trim(),
    publication_year: parseInt(document.getElementById('formYear').value),
    edition: document.getElementById('formEdition').value.trim(),
    total_copies: parseInt(document.getElementById('formTotalCopies').value),
    available_copies: parseInt(document.getElementById('formAvailableCopies').value),
    shelf_number: document.getElementById('formShelf').value.trim().toUpperCase(),
    location: document.getElementById('formLocation').value.trim(),
    description: document.getElementById('formDescription').value.trim(),
    language: 'English'
  };

  try {
    if (mode === 'add') {
      await API.addBook(bookData);
      showToast(`Book "${bookData.title}" added to library!`, 'success');
    } else {
      await API.updateBook(bookId, bookData);
      showToast(`Book "${bookData.title}" updated successfully!`, 'success');
    }
    closeBookFormModal();
    if (state.currentView === 'admin') loadAdminDashboard();
    if (state.currentView === 'catalog') loadCatalog();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ----------------- Initial Data Loader ----------------- //

async function loadInitialData() {
  try {
    const catData = await API.getCategories();
    state.categories = catData.categories;
    setupCatalogFilters();
  } catch (err) {
    console.error('Failed to preload categories:', err);
  }
}

// ----------------- Utility Helpers ----------------- //

function formatMarkdown(text) {
  if (!text) return '';
  let out = escapeHtml(text);
  // Bold: **text**
  out = out.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Italic: *text*
  out = out.replace(/\*(.*?)\*/g, '<em>$1</em>');
  // Lists: • or -
  out = out.replace(/^\s*[•\-]\s+(.*)$/gm, '<li class="ml-4 list-disc">$1</li>');
  // Paragraphs / newlines
  out = out.replace(/\n\n/g, '<br/><br/>');
  out = out.replace(/\n/g, '<br/>');
  return out;
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function escapeQuotes(str) {
  if (!str) return '';
  return String(str).replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function getDifficultyBadgeClass(diff) {
  const d = (diff || '').toLowerCase();
  if (d === 'beginner') return 'badge-beginner';
  if (d === 'advanced') return 'badge-advanced';
  return 'badge-intermediate';
}

function getCategoryIcon(iconName) {
  const valid = ['bot', 'brain', 'network', 'git-branch', 'database', 'cpu', 'globe', 'layout', 'terminal', 'coffee', 'code-2', 'cloud', 'shield-check', 'layers', 'calculator', 'binary', 'book'];
  return valid.includes(iconName) ? iconName : 'book';
}

function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  const colors = {
    success: 'bg-emerald-600 text-white',
    error: 'bg-red-600 text-white',
    info: 'bg-slate-800 text-slate-100 border border-slate-700'
  };
  toast.className = `fixed bottom-5 right-5 z-50 px-4 py-2.5 rounded-xl text-xs font-semibold shadow-xl transition-all duration-300 transform translate-y-3 opacity-0 ${colors[type] || colors.info}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-3', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('translate-y-3', 'opacity-0');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
