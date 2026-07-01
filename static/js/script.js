// static/js/script.js - Complete Auth Management
document.addEventListener('DOMContentLoaded', function() {
    // ============================================
    // AUTH STATE
    // ============================================
    let isAuthenticated = false;
    let currentUser = null;
    let accessToken = localStorage.getItem('access_token');

    // ============================================
    // DOM Elements
    // ============================================
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');
    const chatMessages = document.getElementById('chatMessages');
    const queryInput = document.getElementById('queryInput');
    const sendBtn = document.getElementById('sendBtn');
    const clearBtn = document.getElementById('clearBtn');
    const authSection = document.getElementById('authSection');
    const sidebarProfile = document.getElementById('sidebarProfile');
    const welcomeMessage = document.getElementById('welcomeMessage');
    const guestBadge = document.getElementById('guestBadge');
    const guestNote = document.getElementById('guestNote');

    // ============================================
    // AUTH FUNCTIONS
    // ============================================

    function checkAuth() {
        const token = localStorage.getItem('access_token');
        const username = localStorage.getItem('username');
        
        if (token && username) {
            // Verify token with /api/me
            fetch('/api/me', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    isAuthenticated = true;
                    currentUser = data.user;
                    updateUIForAuthenticatedUser();
                } else {
                    // Token invalid
                    logoutUser();
                }
            })
            .catch(() => {
                logoutUser();
            });
        } else {
            isAuthenticated = false;
            currentUser = null;
            updateUIForGuest();
        }
    }

    function logoutUser() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('username');
        localStorage.removeItem('user_email');
        isAuthenticated = false;
        currentUser = null;
        updateUIForGuest();
        // Optionally redirect to login
        // window.location.href = '/login';
    }

    function updateUIForAuthenticatedUser() {
        const username = currentUser?.username || 'User';
        const email = currentUser?.email || '';
        
        // Update header
        if (authSection) {
            authSection.innerHTML = `
                <div class="profile-dropdown">
                    <button class="profile-btn" id="profileBtn">
                        <img src="https://ui-avatars.com/api/?name=${username}&background=6C63FF&color=fff&size=32" alt="Profile">
                        <span class="profile-name">${username}</span>
                        <i class="fas fa-chevron-down"></i>
                    </button>
                    <div class="dropdown-menu" id="dropdownMenu">
                        <a href="#" onclick="openProfileModal()"><i class="fas fa-user"></i> Profile</a>
                        <a href="#"><i class="fas fa-cog"></i> Settings</a>
                        <a href="#"><i class="fas fa-key"></i> API Keys</a>
                        <hr>
                        <a href="#" onclick="logoutUser()" class="logout-btn">
                            <i class="fas fa-sign-out-alt"></i> Logout
                        </a>
                    </div>
                </div>
            `;
            
            // Add profile dropdown event
            const profileBtn = document.getElementById('profileBtn');
            const dropdownMenu = document.getElementById('dropdownMenu');
            if (profileBtn && dropdownMenu) {
                profileBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    dropdownMenu.classList.toggle('show');
                });
                document.addEventListener('click', function() {
                    dropdownMenu.classList.remove('show');
                });
            }
        }
        
        // Update sidebar
        if (sidebarProfile) {
            sidebarProfile.innerHTML = `
                <div class="user-profile-sidebar">
                    <div class="profile-card">
                        <img src="https://ui-avatars.com/api/?name=${username}&background=6C63FF&color=fff&size=40" alt="Profile">
                        <div class="profile-info">
                            <strong>${username}</strong>
                            <small>${email || 'user@example.com'}</small>
                        </div>
                        <button class="profile-edit-btn" onclick="openProfileModal()" title="Edit Profile">
                            <i class="fas fa-edit"></i>
                        </button>
                    </div>
                </div>
            `;
        }
        
        // Update welcome message
        if (welcomeMessage) {
            welcomeMessage.innerHTML = `
                <p>👋 Welcome back, <strong>${username}</strong>! I'm your AI assistant for query optimization.</p>
                <p>Describe your data needs in natural language, and I'll generate optimized SQL queries with explanations.</p>
                <p><strong>Example:</strong> "Show me all customers who made purchases over $100 in the last month"</p>
            `;
        }
        
        // Hide guest elements
        if (guestBadge) guestBadge.style.display = 'none';
        if (guestNote) guestNote.style.display = 'none';
    }

    function updateUIForGuest() {
        // Update header with login/signup buttons
        if (authSection) {
            authSection.innerHTML = `
                <div class="auth-buttons">
                    <a href="/login" class="btn-outline">Login</a>
                    <a href="/register" class="btn-primary">Sign Up Free</a>
                </div>
            `;
        }
        
        // Update sidebar with guest banner
        if (sidebarProfile) {
            sidebarProfile.innerHTML = `
                <div class="guest-banner">
                    <i class="fas fa-user-astronaut"></i>
                    <span>Guest Mode</span>
                    <small>Sign up to save queries</small>
                    <div style="margin-top: 8px; display: flex; gap: 6px; flex-wrap: wrap;">
                        <a href="/login" class="guest-btn guest-btn-outline">Login</a>
                        <a href="/register" class="guest-btn guest-btn-primary">Sign Up</a>
                    </div>
                </div>
            `;
        }
        
        // Update welcome message
        if (welcomeMessage) {
            welcomeMessage.innerHTML = `
                <p>👋 Welcome to GenialQuery! I'm your AI assistant for query optimization.</p>
                <p>Describe your data needs in natural language, and I'll generate optimized SQL queries with explanations.</p>
                <p><strong>Example:</strong> "Show me all customers who made purchases over $100 in the last month"</p>
                <div class="guest-note">
                    <i class="fas fa-info-circle"></i>
                    <span>You're using GenialQuery as a guest. <a href="/register">Sign up</a> to save your queries and access history!</span>
                </div>
            `;
        }
        
        // Show guest badge
        if (guestBadge) guestBadge.style.display = 'inline';
        if (guestNote) guestNote.style.display = 'block';
    }

    // ============================================
    // PROFILE MODAL FUNCTIONS
    // ============================================

    window.openProfileModal = function() {
        const modal = document.getElementById('profileModal');
        if (currentUser) {
            document.getElementById('modalUsername').value = currentUser.username || '';
            document.getElementById('modalEmail').value = currentUser.email || '';
        }
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    };

    window.closeProfileModal = function() {
        const modal = document.getElementById('profileModal');
        modal.classList.remove('active');
        document.body.style.overflow = '';
    };

    // Profile form submission
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Profile updated successfully!');
            closeProfileModal();
        });
    }

    // Close modal on overlay click
    document.addEventListener('click', function(e) {
        const modal = document.getElementById('profileModal');
        if (modal && e.target === modal) {
            closeProfileModal();
        }
    });

    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeProfileModal();
        }
    });

    // ============================================
    // SIDEBAR TOGGLE
    // ============================================

    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            sidebar.classList.toggle('open');
            const icon = this.querySelector('i');
            if (sidebar.classList.contains('open')) {
                icon.className = 'fas fa-times';
            } else {
                icon.className = 'fas fa-bars';
            }
        });
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            sidebar.classList.toggle('collapsed');
            const icon = this.querySelector('i');
            if (sidebar.classList.contains('collapsed')) {
                icon.className = 'fas fa-chevron-right';
            } else {
                icon.className = 'fas fa-bars';
            }
        });
    }

    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            const isClickOnSidebar = sidebar.contains(e.target);
            const isClickOnHamburger = hamburgerBtn && hamburgerBtn.contains(e.target);
            
            if (!isClickOnSidebar && !isClickOnHamburger) {
                sidebar.classList.remove('open');
                if (hamburgerBtn) {
                    const icon = hamburgerBtn.querySelector('i');
                    if (icon) icon.className = 'fas fa-bars';
                }
            }
        }
    });

    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('open');
            if (hamburgerBtn) {
                const icon = hamburgerBtn.querySelector('i');
                if (icon) icon.className = 'fas fa-bars';
            }
        }
    });

    // ============================================
    // THEME MANAGEMENT
    // ============================================
    
    let isDarkMode = localStorage.getItem('theme') === 'dark';

    function setTheme(dark) {
        isDarkMode = dark;
        document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
        if (themeIcon) themeIcon.className = dark ? 'fas fa-sun' : 'fas fa-moon';
        if (themeText) themeText.textContent = dark ? 'Light Mode' : 'Dark Mode';
        localStorage.setItem('theme', dark ? 'dark' : 'light');
    }

    setTheme(isDarkMode);

    if (themeToggle) {
        themeToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            setTheme(!isDarkMode);
        });
    }

    // ============================================
    // AGENT & PAGE NAVIGATION
    // ============================================

    document.querySelectorAll('[data-agent]').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const agentName = this.dataset.agent;
            const agentDisplayName = {
                'query': 'Query Agent',
                'explanation': 'Explanation Agent',
                'impact': 'Impact Agent',
                'optimizer': 'Optimizer Agent',
                'schema': 'Schema Agent',
                'security': 'Security Agent'
            };
            
            const agentInfo = getAgentInfo(agentName);
            addMessage('ai', agentInfo);
            document.getElementById('pageTitle').textContent = agentDisplayName[agentName] || 'Dashboard';
            
            document.querySelectorAll('[data-agent]').forEach(el => {
                el.closest('li').classList.remove('active');
            });
            this.closest('li').classList.add('active');
            
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('open');
                if (hamburgerBtn) {
                    const icon = hamburgerBtn.querySelector('i');
                    if (icon) icon.className = 'fas fa-bars';
                }
            }
        });
    });

    document.querySelectorAll('[data-page]').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const pageName = this.dataset.page;
            const pageDisplayName = {
                'dashboard': 'Dashboard',
                'history': 'History',
                'saved': 'Saved Queries',
                'optimize': 'Optimize'
            };
            
            document.getElementById('pageTitle').textContent = pageDisplayName[pageName] || 'Dashboard';
            
            document.querySelectorAll('[data-page]').forEach(el => {
                el.closest('li').classList.remove('active');
            });
            this.closest('li').classList.add('active');
            
            const pageMessages = {
                'dashboard': '📊 Welcome back to your dashboard! How can I help you today?',
                'history': '📜 Your query history will appear here. Sign up to save your queries!',
                'saved': '⭐ Your saved queries will appear here. Bookmark important queries!',
                'optimize': '🚀 Need to optimize a query? Paste it here and I\'ll help you optimize it!'
            };
            
            if (!isAuthenticated && pageName !== 'dashboard') {
                addMessage('ai', `${pageMessages[pageName]} <br><br>💡 <strong>Tip:</strong> <a href="/register" style="color: var(--accent);">Create an account</a> to save your queries and access history!`);
            } else {
                addMessage('ai', pageMessages[pageName] || 'Welcome!');
            }
            
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('open');
                if (hamburgerBtn) {
                    const icon = hamburgerBtn.querySelector('i');
                    if (icon) icon.className = 'fas fa-bars';
                }
            }
        });
    });

    // ============================================
    // CHAT FUNCTIONALITY
    // ============================================

    if (queryInput) {
        queryInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });

        queryInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            if (confirm('Clear all messages?')) {
                chatMessages.innerHTML = '';
                // Re-add welcome message
                if (isAuthenticated && currentUser) {
                    welcomeMessage.innerHTML = `
                        <p>👋 Welcome back, <strong>${currentUser.username}</strong>! I'm your AI assistant for query optimization.</p>
                        <p>Describe your data needs in natural language, and I'll generate optimized SQL queries with explanations.</p>
                        <p><strong>Example:</strong> "Show me all customers who made purchases over $100 in the last month"</p>
                    `;
                }
            }
        });
    }

    // ============================================
    // HELPER FUNCTIONS
    // ============================================

    function getAgentInfo(agentName) {
        const agentInfo = {
            'query': `
                <h3>🔍 Query Agent</h3>
                <p>The Query Agent converts natural language into SQL queries.</p>
                <p><strong>What it does:</strong></p>
                <ul>
                    <li>Understands your data needs from text</li>
                    <li>Generates optimized SQL queries</li>
                    <li>Supports SELECT, INSERT, UPDATE, DELETE</li>
                    <li>Handles JOINs and aggregations</li>
                </ul>
                <p>Try asking: <em>"Show me all customers"</em></p>
            `,
            'explanation': `
                <h3>💡 Explanation Agent</h3>
                <p>The Explanation Agent helps you understand what a query does.</p>
                <p><strong>What it does:</strong></p>
                <ul>
                    <li>Explains query purpose in plain English</li>
                    <li>Breaks down complex SQL into understandable parts</li>
                    <li>Identifies query type (SELECT, JOIN, AGGREGATE)</li>
                </ul>
                <p>Every query you run automatically gets an explanation!</p>
            `,
            'impact': `
                <h3>📊 Impact Agent</h3>
                <p>The Impact Agent analyzes query performance.</p>
                <p><strong>What it does:</strong></p>
                <ul>
                    <li>Estimates execution time</li>
                    <li>Identifies performance bottlenecks</li>
                    <li>Suggests optimizations</li>
                    <li>Rates query impact (Low/Medium/High)</li>
                </ul>
                <p>Try asking: <em>"Analyze the performance of my last query"</em></p>
            `,
            'optimizer': `
                <h3>🚀 Optimizer Agent</h3>
                <p>The Optimizer Agent improves your SQL queries.</p>
                <p><strong>What it does:</strong></p>
                <ul>
                    <li>Converts SELECT * to specific columns</li>
                    <li>Adds LIMIT for performance</li>
                    <li>Optimizes JOIN conditions</li>
                    <li>Suggests indexes</li>
                </ul>
                <p>All queries are automatically optimized!</p>
            `,
            'schema': `
                <h3>📐 Schema Agent</h3>
                <p>The Schema Agent knows your database structure.</p>
                <p><strong>Current Tables:</strong></p>
                <ul>
                    <li>📊 train (context, question, answer)</li>
                    <li>📊 test (context, question, answer)</li>
                    <li>📊 validation (context, question, answer)</li>
                    <li>📊 train_split (context, question, answer)</li>
                    <li>📊 query_history (natural_query, sql_query)</li>
                </ul>
                <p>Ask about any table to get its structure!</p>
            `,
            'security': `
                <h3>🛡️ Security Agent</h3>
                <p>The Security Agent protects against malicious queries.</p>
                <p><strong>What it does:</strong></p>
                <ul>
                    <li>Detects SQL injection attempts</li>
                    <li>Blocks destructive operations (DROP, DELETE, TRUNCATE)</li>
                    <li>Validates user input</li>
                    <li>Sanitizes queries</li>
                </ul>
                <p>Your queries are always checked for safety! 🔒</p>
            `
        };
        return agentInfo[agentName] || `<h3>🤖 Agent</h3><p>This agent helps with your queries.</p>`;
    }

    function addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type === 'user' ? 'user-message' : 'ai-message'}`;

        const avatar = type === 'user' ? '👤' : '🤖';
        const sender = type === 'user' ? 'You' : 'GenialQuery AI';
        const time = new Date().toLocaleTimeString();

        messageDiv.innerHTML = `
            <div class="message-avatar">
                ${avatar}
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-sender">${sender}</span>
                    <span class="message-time">${time}</span>
                </div>
                <div class="message-text">
                    ${content}
                </div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    function addSQLMessage(sql, explanation) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai-message';

        const formattedSQL = formatSQL(sql);

        messageDiv.innerHTML = `
            <div class="message-avatar">
                🤖
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-sender">GenialQuery AI</span>
                    <span class="message-time">${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="message-text">
                    <p><strong>📝 Optimized SQL Query:</strong></p>
                    <pre class="sql-code"><code>${formattedSQL}</code></pre>
                    ${explanation ? `<p><strong>💡 Explanation:</strong><br>${escapeHtml(explanation)}</p>` : ''}
                    <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                        <button class="copy-btn" onclick="copyToClipboard()">
                            <i class="fas fa-copy"></i> Copy SQL
                        </button>
                        <button class="run-btn" onclick="simulateRun()">
                            <i class="fas fa-play"></i> Run Query (Demo)
                        </button>
                    </div>
                </div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    function formatSQL(sql) {
        const keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'ON', 'LIMIT', 'ORDER BY', 'GROUP BY', 'HAVING', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'TABLE', 'INTO', 'VALUES', 'SET', 'AND', 'OR', 'NOT', 'AS', 'SUM', 'COUNT', 'AVG', 'MAX', 'MIN', 'DISTINCT'];
        let formatted = escapeHtml(sql);
        keywords.forEach(keyword => {
            const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
            formatted = formatted.replace(regex, `<span class="sql-keyword">${keyword}</span>`);
        });
        return formatted;
    }

    async function sendMessage() {
        const text = queryInput.value.trim();
        if (!text) return;

        addMessage('user', text);
        queryInput.value = '';
        queryInput.style.height = 'auto';
        sendBtn.disabled = true;

        const typingId = addTypingIndicator();

        try {
            const token = localStorage.getItem('access_token');
            const headers = {
                'Content-Type': 'application/json'
            };
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch('/api/query', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ 
                    query: text,
                    guest: !isAuthenticated
                })
            });

            removeTypingIndicator(typingId);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success === false) {
                addMessage('ai', `❌ ${data.error || data.message || 'An error occurred'}`);
                return;
            }

            addMessage('ai', data.response || data.query || 'No response generated.');

            if (data.sql) {
                addSQLMessage(data.sql, data.explanation);
            }

            if (!isAuthenticated && chatMessages.children.length > 4) {
                showGuestPrompt();
            }

        } catch (error) {
            removeTypingIndicator(typingId);
            console.error('Error:', error);
            addMessage('ai', `❌ Sorry, I encountered an error: ${error.message}`);
        } finally {
            sendBtn.disabled = false;
            queryInput.focus();
        }
    }

    function addTypingIndicator() {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'message ai-message';
        div.innerHTML = `
            <div class="message-avatar">
                🤖
            </div>
            <div class="message-content">
                <div class="message-text">
                    <div class="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        `;
        chatMessages.appendChild(div);
        scrollToBottom();
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function showGuestPrompt() {
        if (document.querySelector('.guest-signup-prompt')) return;

        const promptDiv = document.createElement('div');
        promptDiv.className = 'message ai-message guest-signup-prompt';
        promptDiv.innerHTML = `
            <div class="message-avatar">
                💡
            </div>
            <div class="message-content" style="background: linear-gradient(135deg, #6C63FF, #5a52d5); color: white;">
                <div class="message-text" style="text-align: center; padding: 8px 0;">
                    <p style="font-size: 16px; font-weight: 600;">🌟 Enjoying GenialQuery?</p>
                    <p style="font-size: 14px; opacity: 0.9;">Create a free account to save your queries and access history!</p>
                    <div style="margin-top: 12px; display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;">
                        <a href="/register" style="background: white; color: #6C63FF; padding: 8px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s ease;">Sign Up Free</a>
                        <button onclick="this.parentElement.parentElement.parentElement.parentElement.remove()" style="background: rgba(255,255,255,0.2); color: white; padding: 8px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.3); cursor: pointer; transition: all 0.3s ease;">Dismiss</button>
                    </div>
                </div>
            </div>
        `;
        chatMessages.appendChild(promptDiv);
        scrollToBottom();
    }

    // ============================================
    // GLOBAL FUNCTIONS (accessible from HTML)
    // ============================================

    window.copyToClipboard = function(text) {
        if (!text) {
            const btn = event.target.closest('.copy-btn');
            const sqlCode = btn ? btn.closest('.message-content').querySelector('.sql-code code') : null;
            if (sqlCode) {
                text = sqlCode.textContent;
            }
        }
        
        if (!text) {
            alert('No SQL to copy!');
            return;
        }
        
        text = text.replace(/```sql/g, '').replace(/```/g, '').trim();
        
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(() => {
                showCopySuccess(event.target.closest('.copy-btn'));
            }).catch(err => {
                console.error('Failed to copy:', err);
                fallbackCopy(text);
            });
        } else {
            fallbackCopy(text);
        }
    };

    function showCopySuccess(btn) {
        if (!btn) return;
        const original = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        btn.style.background = '#10b981';
        btn.style.color = 'white';
        setTimeout(() => {
            btn.innerHTML = original;
            btn.style.background = '';
            btn.style.color = '';
        }, 2000);
    }

    function fallbackCopy(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        textarea.style.left = '-9999px';
        document.body.appendChild(textarea);
        textarea.select();
        
        try {
            document.execCommand('copy');
            showCopySuccess(document.querySelector('.copy-btn:hover') || document.querySelector('.copy-btn'));
        } catch (err) {
            console.error('Failed to copy:', err);
            alert('Could not copy to clipboard. Please copy the text manually.');
        }
        
        document.body.removeChild(textarea);
    }

    window.simulateRun = function() {
        const btn = event.target.closest('.run-btn');
        const original = btn.innerHTML;
        const messageContent = btn.closest('.message-content');
        const sqlCode = messageContent.querySelector('.sql-code code');
        const sql = sqlCode ? sqlCode.textContent : '';
        
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running query...';
        btn.disabled = true;
        
        setTimeout(() => {
            const results = generateSampleResults(sql);
            
            const resultDiv = document.createElement('div');
            resultDiv.className = 'query-results';
            resultDiv.innerHTML = `
                <div style="margin-top: 12px; padding: 12px; background: var(--bg-primary); border-radius: 8px; border-left: 3px solid #10b981;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <strong style="color: var(--text-primary);">📊 Query Results</strong>
                        <span style="font-size: 12px; color: var(--text-secondary);">${results.rowCount} rows returned</span>
                    </div>
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                            <thead>
                                <tr style="background: var(--accent); color: white;">
                                    ${results.columns.map(col => `<th style="padding: 6px 12px; text-align: left; border: 1px solid var(--border-color);">${col}</th>`).join('')}
                                </tr>
                            </thead>
                            <tbody>
                                ${results.data.map(row => `
                                    <tr style="border-bottom: 1px solid var(--border-color);">
                                        ${results.columns.map(col => `<td style="padding: 6px 12px; border: 1px solid var(--border-color);">${row[col] || '-'}</td>`).join('')}
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                    <div style="margin-top: 8px; font-size: 12px; color: var(--text-secondary);">
                        ⚡ Execution time: ${(Math.random() * 0.5 + 0.1).toFixed(2)}s
                    </div>
                </div>
            `;
            
            const sqlContainer = messageContent.querySelector('.message-text');
            const existingResults = sqlContainer.querySelector('.query-results');
            if (existingResults) {
                existingResults.remove();
            }
            sqlContainer.appendChild(resultDiv);
            
            btn.innerHTML = '<i class="fas fa-check"></i> Done!';
            setTimeout(() => {
                btn.innerHTML = original;
                btn.disabled = false;
            }, 1500);
        }, 1500);
    };

    function generateSampleResults(sql) {
        if (!sql) {
            return { columns: ['message'], data: [{'message': 'No results to display'}], rowCount: 1 };
        }
        
        const sqlLower = sql.toLowerCase();
        let columns = ['id', 'name', 'email'];
        let data = [];
        
        if (sqlLower.includes('employee')) {
            columns = ['id', 'name', 'email', 'department', 'position', 'hire_date', 'salary'];
            data = [
                {'id': 1, 'name': 'John Doe', 'email': 'john.doe@company.com', 'department': 'Engineering', 'position': 'Senior Developer', 'hire_date': '2026-05-15', 'salary': 85000},
                {'id': 2, 'name': 'Jane Smith', 'email': 'jane.smith@company.com', 'department': 'Sales', 'position': 'Sales Manager', 'hire_date': '2026-05-20', 'salary': 78000},
                {'id': 3, 'name': 'Bob Johnson', 'email': 'bob.johnson@company.com', 'department': 'Marketing', 'position': 'Marketing Lead', 'hire_date': '2026-06-01', 'salary': 72000}
            ];
        } else if (sqlLower.includes('customer')) {
            columns = ['id', 'name', 'email', 'city', 'total_spent'];
            data = [
                {'id': 1, 'name': 'Acme Corp', 'email': 'info@acme.com', 'city': 'New York', 'total_spent': 25000},
                {'id': 2, 'name': 'TechStart Inc', 'email': 'contact@techstart.com', 'city': 'San Francisco', 'total_spent': 18000}
            ];
        } else if (sqlLower.includes('train') || sqlLower.includes('test') || sqlLower.includes('validation')) {
            columns = ['id', 'context', 'question', 'answer'];
            data = [
                {'id': 1, 'context': 'Machine learning is a subset of AI.', 'question': 'What is machine learning?', 'answer': 'A subset of AI'},
                {'id': 2, 'context': 'Python is a popular programming language.', 'question': 'Which language is popular?', 'answer': 'Python'},
                {'id': 3, 'context': 'Data science combines statistics and computing.', 'question': 'What does data science combine?', 'answer': 'Statistics and computing'}
            ];
        } else if (sqlLower.includes('count') || sqlLower.includes('sum') || sqlLower.includes('avg')) {
            columns = ['metric', 'value'];
            data = [
                {'metric': 'Total Records', 'value': 1247},
                {'metric': 'Average', 'value': 453.72},
                {'metric': 'Sum', 'value': 462387.50}
            ];
        } else {
            columns = ['id', 'name', 'created_at'];
            data = [
                {'id': 1, 'name': 'Record 1', 'created_at': '2026-06-20'},
                {'id': 2, 'name': 'Record 2', 'created_at': '2026-06-21'},
                {'id': 3, 'name': 'Record 3', 'created_at': '2026-06-22'}
            ];
        }
        
        data = data.slice(0, 5);
        return { columns: columns, data: data, rowCount: data.length };
    }

    // ============================================
    // INITIALIZE
    // ============================================

    // Check authentication on load
    checkAuth();

    // Expose logoutUser globally
    window.logoutUser = logoutUser;

    console.log('💡 GenialQuery loaded! Press Ctrl+Enter to send messages.');
});