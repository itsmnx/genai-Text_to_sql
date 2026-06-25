// static/js/script.js - Complete Updated Version
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');
    const chatMessages = document.getElementById('chatMessages');
    const queryInput = document.getElementById('queryInput');
    const sendBtn = document.getElementById('sendBtn');
    const clearBtn = document.getElementById('clearBtn');
    const profileBtn = document.getElementById('profileBtn');
    const dropdownMenu = document.getElementById('dropdownMenu');

    // Check if user is logged in
    const isLoggedIn = !!document.querySelector('.profile-dropdown');

    // Sidebar Toggle
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

    // Theme Management
    let isDarkMode = localStorage.getItem('theme') === 'dark';

    function setTheme(dark) {
        isDarkMode = dark;
        document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
        themeIcon.className = dark ? 'fas fa-sun' : 'fas fa-moon';
        themeText.textContent = dark ? 'Light Mode' : 'Dark Mode';
        localStorage.setItem('theme', dark ? 'dark' : 'light');
    }

    setTheme(isDarkMode);

    themeToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        setTheme(!isDarkMode);
    });

    // Close sidebar on outside click (mobile)
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        }
    });

    // Profile Dropdown
    if (profileBtn) {
        profileBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdownMenu.classList.toggle('show');
        });

        document.addEventListener('click', function() {
            if (dropdownMenu) {
                dropdownMenu.classList.remove('show');
            }
        });
    }

    // Agent click handlers
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
        });
    });

    // Page navigation
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
            
            if (!isLoggedIn && pageName !== 'dashboard') {
                addMessage('ai', `${pageMessages[pageName]} <br><br>💡 <strong>Tip:</strong> <a href="/register" style="color: var(--accent);">Create an account</a> to save your queries and access history!`);
            } else {
                addMessage('ai', pageMessages[pageName] || 'Welcome!');
            }
        });
    });

    // Auto-resize textarea
    queryInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });

    // Send message on Ctrl+Enter
    queryInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Send message on button click
    sendBtn.addEventListener('click', sendMessage);

    // Clear chat
    clearBtn.addEventListener('click', function() {
        if (confirm('Clear all messages?')) {
            chatMessages.innerHTML = '';
            addWelcomeMessage();
        }
    });

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
                    <li>Blocks destructive operations (DROP, TRUNCATE)</li>
                    <li>Validates user input</li>
                    <li>Sanitizes queries</li>
                </ul>
                <p>Your queries are always checked for safety! 🔒</p>
            `
        };
        return agentInfo[agentName] || `<h3>🤖 Agent</h3><p>This agent helps with your queries.</p>`;
    }

    function addWelcomeMessage() {
        const isGuest = !isLoggedIn;
        const guestHTML = isGuest ? `
            <div class="guest-note">
                <i class="fas fa-info-circle"></i>
                <span>You're using GenialQuery as a guest. <a href="/register">Sign up</a> to save your queries and access history!</span>
            </div>
        ` : '';

        const welcomeHTML = `
            <div class="message ai-message">
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="message-sender">GenialQuery AI</span>
                        <span class="message-time">Just now</span>
                    </div>
                    <div class="message-text">
                        <p>👋 Welcome to GenialQuery! I'm your AI assistant for query optimization.</p>
                        <p>Describe your data needs in natural language, and I'll generate optimized SQL queries with explanations.</p>
                        <p><strong>Example:</strong> "Show me all customers who made purchases over $100 in the last month"</p>
                        ${guestHTML}
                    </div>
                </div>
            </div>
        `;
        chatMessages.innerHTML = welcomeHTML;
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
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    query: text,
                    guest: !isLoggedIn
                })
            });

            removeTypingIndicator(typingId);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            addMessage('ai', data.response || data.query || 'No response generated.');

            if (data.sql) {
                addSQLMessage(data.sql, data.explanation);
            }

            if (!isLoggedIn && chatMessages.children.length > 4) {
                showGuestPrompt();
            }

        } catch (error) {
            removeTypingIndicator(typingId);
            console.error('Error:', error);
            addMessage('ai', '❌ Sorry, I encountered an error. Please try again.');
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
            const sqlCode = btn.closest('.message-content').querySelector('.sql-code code');
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

    // Add CSS for query results
    const style = document.createElement('style');
    style.textContent = `
        .query-results {
            margin-top: 12px;
            padding: 12px;
            background: var(--bg-primary);
            border-radius: 8px;
            border-left: 3px solid #10b981;
        }
        .query-results table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        .query-results th {
            background: var(--accent);
            color: white;
            padding: 6px 12px;
            text-align: left;
            border: 1px solid var(--border-color);
        }
        .query-results td {
            padding: 6px 12px;
            border: 1px solid var(--border-color);
        }
        .query-results tr:nth-child(even) {
            background: var(--bg-secondary);
        }
        .query-results tr:hover {
            background: var(--bg-message-ai);
        }
        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 4px 0;
        }
        .typing-indicator span {
            width: 8px;
            height: 8px;
            background: var(--text-secondary);
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
            30% { transform: translateY(-10px); opacity: 1; }
        }
        .copy-btn {
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            padding: 6px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            color: var(--text-primary);
            transition: all 0.3s ease;
        }
        .copy-btn:hover {
            background: var(--accent);
            color: white;
            border-color: var(--accent);
        }
        .run-btn {
            background: #10b981;
            color: white;
            border: none;
            padding: 6px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.3s ease;
        }
        .run-btn:hover {
            opacity: 0.8;
            transform: translateY(-1px);
        }
        .run-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .sql-keyword {
            color: #6C63FF;
            font-weight: 600;
        }
        .sql-code {
            background: var(--bg-primary);
            padding: 12px;
            border-radius: 6px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
            border-left: 3px solid var(--accent);
        }
        .guest-signup-prompt { max-width: 70%; margin: 0 auto; }
        .sidebar.collapsed { width: 60px; min-width: 60px; }
        .sidebar.collapsed .logo span,
        .sidebar.collapsed .nav-section h4,
        .sidebar.collapsed .nav-section ul li a span,
        .sidebar.collapsed .theme-toggle span,
        .sidebar.collapsed .guest-banner { display: none; }
        .sidebar.collapsed .nav-section ul li a { justify-content: center; padding: 12px; }
        .sidebar.collapsed .nav-section ul li a i { margin: 0; font-size: 18px; }
        .sidebar.collapsed .logo { justify-content: center; }
        .sidebar.collapsed .sidebar-toggle { display: none; }
        @media (max-width: 768px) {
            .guest-signup-prompt { max-width: 95%; }
            .sidebar.collapsed { width: 0; padding: 0; }
        }
    `;
    document.head.appendChild(style);

    addWelcomeMessage();
    console.log('💡 GenialQuery loaded! Press Ctrl+Enter to send messages.');
});