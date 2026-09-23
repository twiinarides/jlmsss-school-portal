/**
 * HELPDESK CHAT WIDGET — Complete JavaScript
 * Floating chat button, session management, message polling
 */

(function () {
  'use strict';

  const POLL_INTERVAL = 5000; // 5 seconds
  const STORAGE_KEY   = 'jlmsss_help_session';

  /* ── Helpers ── */
  const CSRF = () => document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
  const $ = sel => document.querySelector(sel);
  const $$ = sel => document.querySelectorAll(sel);
  const fmt = date => new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  async function post(url, data) {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': CSRF(),
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify(data),
    });
    return res.json();
  }

  async function get(url) {
    const res = await fetch(url, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    });
    return res.json();
  }

  /* ══════════════════════════════════════════════════
     SESSION MANAGEMENT
  ══════════════════════════════════════════════════ */
  function saveSession(data) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); } catch (e) {}
  }
  function loadSession() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || null; } catch (e) { return null; }
  }
  function clearSession() {
    try { localStorage.removeItem(STORAGE_KEY); } catch (e) {}
  }

  /* ══════════════════════════════════════════════════
     WIDGET CORE
  ══════════════════════════════════════════════════ */
  class HelpWidget {
    constructor() {
      this.fab        = $('#hd-fab');
      this.window     = $('#hd-window');
      this.badge      = $('#hd-fab-badge');
      this.introPanel = $('#hd-intro');
      this.chatPanel  = $('#hd-chat');
      this.messagesEl = $('#hd-messages');
      this.inputEl    = $('#hd-msg-input');
      this.sendBtn    = $('#hd-send-btn');
      this.startBtn   = $('#hd-start-btn');

      this.session    = loadSession();
      this.lastMsgId  = 0;
      this.pollTimer  = null;
      this.isOpen     = false;
      this.unreadCount = 0;

      if (!this.fab) return; // Widget not in DOM

      this._init();
    }

    _init() {
      // FAB open/close
      this.fab.addEventListener('click', () => this.toggle());

      // Close via header X
      $$('[data-hd-close]').forEach(btn => btn.addEventListener('click', () => this.close()));

      // Start session form
      this.startBtn?.addEventListener('click', () => this._startSession());

      // Send message
      this.sendBtn?.addEventListener('click', () => this._sendMessage());
      this.inputEl?.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this._sendMessage();
        }
      });

      // Auto-resize textarea
      this.inputEl?.addEventListener('input', () => {
        this.inputEl.style.height = 'auto';
        this.inputEl.style.height = Math.min(this.inputEl.scrollHeight, 100) + 'px';
      });

      // If existing session, show chat
      if (this.session) {
        this._showChat();
        this._loadHistory();
      }

      // Visitor End Chat Button click listener
      const visitorEndBtn = $('#hd-visitor-end-btn');
      if (visitorEndBtn) {
        visitorEndBtn.addEventListener('click', async () => {
          if (!this.session) return;
          if (!confirm('Are you sure you want to end this conversation?')) return;
          
          visitorEndBtn.disabled = true;
          const oldText = visitorEndBtn.innerHTML;
          visitorEndBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Ending...';
          
          try {
            await post('/help/close/', { session_key: this.session.key });
          } catch (e) {}
          
          visitorEndBtn.disabled = false;
          visitorEndBtn.innerHTML = oldText;
          this._resetToIntro();
        });
      }
    }

    _resetToIntro() {
      this._stopPolling();
      this.session = null;
      localStorage.removeItem('hd_session');
      this.lastMsgId = 0;
      this.unreadCount = 0;
      this._updateBadge();
      
      // Empty chat messages
      if (this.messagesEl) this.messagesEl.innerHTML = '';
      
      // Show intro panel
      if (this.introPanel) this.introPanel.style.display = 'block';
      if (this.chatPanel) this.chatPanel.style.display = 'none';
      
      // Hide end button
      const endBtn = $('#hd-visitor-end-btn');
      if (endBtn) endBtn.style.display = 'none';
      
      // Clear form inputs
      const visName = $('#hd-vis-name');
      const visEmail = $('#hd-vis-email');
      const visPhone = $('#hd-vis-phone');
      const visSubject = $('#hd-vis-subject');
      if (visName) visName.value = '';
      if (visEmail) visEmail.value = '';
      if (visPhone) visPhone.value = '';
      if (visSubject) visSubject.value = '';
      
      const err = $('#hd-intro-error');
      if (err) err.style.display = 'none';
    }

    toggle() {
      this.isOpen ? this.close() : this.open();
    }

    open() {
      this.isOpen = true;
      this.fab.classList.add('open');
      this.window.classList.add('open');
      this.window.setAttribute('aria-hidden', 'false');
      // Clear unread badge
      this.unreadCount = 0;
      this._updateBadge();
      // Start polling if session active
      if (this.session) this._startPolling();
      // Focus input
      setTimeout(() => this.inputEl?.focus(), 350);
    }

    close() {
      this.isOpen = false;
      this.fab.classList.remove('open');
      this.window.classList.remove('open');
      this.window.setAttribute('aria-hidden', 'true');
      this._stopPolling();
    }

    async _startSession() {
      const name    = $('#hd-vis-name')?.value.trim();
      const email   = $('#hd-vis-email')?.value.trim();
      const phone   = $('#hd-vis-phone')?.value.trim();
      const subject = $('#hd-vis-subject')?.value.trim();

      if (!name || !email) {
        this._showIntroError('Please enter your name and email.');
        return;
      }
      if (!this._validateEmail(email)) {
        this._showIntroError('Please enter a valid email address.');
        return;
      }

      this.startBtn.disabled = true;
      this.startBtn.textContent = 'Starting…';

      const sessionKey = this._generateKey();
      try {
        const res = await post('/help/start/', { session_key: sessionKey, name, email, phone, subject });
        if (res.success) {
          this.session = { key: sessionKey, name, email, session_id: res.session_id };
          saveSession(this.session);
          this._showChat();
          this._startPolling();
          this._appendWelcome(name);
        } else {
          this._showIntroError('Could not start session. Please try again.');
        }
      } catch (e) {
        this._showIntroError('Connection error. Please check your internet and try again.');
      } finally {
        if (this.startBtn) {
          this.startBtn.disabled = false;
          this.startBtn.textContent = 'Start Chat';
        }
      }
    }

    async _sendMessage() {
      const text = this.inputEl?.value.trim();
      if (!text || !this.session) return;

      this.inputEl.value = '';
      this.inputEl.style.height = 'auto';
      this.sendBtn.disabled = true;

      try {
        const res = await post('/help/send/', {
          session_key: this.session.key,
          message: text,
          sender_type: 'visitor',
          sender_name: this.session.name,
        });
        if (res.success) {
          await this._poll();
        } else {
          this._appendSystemMsg('Message failed to send. Please try again.');
        }
      } catch (e) {
        this._appendSystemMsg('Message failed to send. Please try again.');
      } finally {
        this.sendBtn.disabled = false;
        this.inputEl?.focus();
      }
    }

    async _loadHistory() {
      if (!this.session) return;
      try {
        const data = await get(`/help/messages/${this.session.key}/`);
        if (data.messages?.length) {
          data.messages.forEach(m => this._appendMessage(m, false));
          this.lastMsgId = data.messages[data.messages.length - 1].id;
          this._scrollToBottom();
        }
      } catch (e) {}
    }

    _startPolling() {
      this._stopPolling();
      this.pollTimer = setInterval(() => this._poll(), POLL_INTERVAL);
    }

    _stopPolling() {
      if (this.pollTimer) { clearInterval(this.pollTimer); this.pollTimer = null; }
    }

    async _poll() {
      if (!this.session) return;
      try {
        const data = await get(`/help/messages/${this.session.key}/?last_id=${this.lastMsgId}`);
        if (data.messages?.length) {
          data.messages.forEach(m => {
            this._appendMessage(m, true);
            if (m.sender_type === 'admin' && !this.isOpen) {
              this.unreadCount++;
              this._updateBadge();
            }
          });
          this.lastMsgId = data.messages[data.messages.length - 1].id;
          // Update session status in storage
          if (data.session_status) {
            this.session.status = data.session_status;
            saveSession(this.session);
          }
        }
      } catch (e) {}
    }

    _appendMessage(msg, animate = true) {
      if (!this.messagesEl) return;

      // Duplicate prevention
      if (msg.id && this.messagesEl.querySelector(`[data-msg-id="${msg.id}"]`)) {
        return;
      }

      const div = document.createElement('div');
      div.className = `hd-msg ${msg.sender_type}`;
      if (msg.id) div.setAttribute('data-msg-id', msg.id);
      if (animate) div.style.animation = 'msg-appear .25s ease';

      const name = msg.sender_type === 'admin'
        ? (msg.sender_name || 'Support Team')
        : (this.session?.name || 'You');

      div.innerHTML = `
        <div class="hd-msg__bubble">${this._escHtml(msg.message)}</div>
        <div class="hd-msg__meta">${name} · ${fmt(msg.sent_at)}</div>
      `;

      this.messagesEl.appendChild(div);
      if (animate || this.isOpen) this._scrollToBottom();
    }

    _appendWelcome(name) {
      if (!this.messagesEl) return;
      const div = document.createElement('div');
      div.className = 'hd-msg admin';
      div.innerHTML = `
        <div class="hd-msg__bubble">Hello ${this._escHtml(name)}! 👋 Welcome to Janan Luwum Memorial SSS Support. How can we help you today? We'll reply as soon as possible.</div>
        <div class="hd-msg__meta">Support Team · ${fmt(new Date())}</div>
      `;
      this.messagesEl.appendChild(div);
      this._scrollToBottom();
    }

    _appendSystemMsg(text) {
      if (!this.messagesEl) return;
      const div = document.createElement('div');
      div.style.cssText = 'text-align:center;font-size:.75rem;color:#aaa;padding:.25rem';
      div.textContent = text;
      this.messagesEl.appendChild(div);
      this._scrollToBottom();
    }

    _showChat() {
      this.introPanel && (this.introPanel.style.display = 'none');
      this.chatPanel  && (this.chatPanel.style.display = 'flex');
      const endBtn = $('#hd-visitor-end-btn');
      if (endBtn) endBtn.style.display = 'inline-flex';
    }

    _showIntroError(msg) {
      const err = $('#hd-intro-error');
      if (err) { err.textContent = msg; err.style.display = 'block'; }
    }

    _scrollToBottom() {
      if (this.messagesEl) {
        this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
      }
    }

    _updateBadge() {
      if (!this.badge) return;
      this.badge.textContent = this.unreadCount;
      this.badge.classList.toggle('visible', this.unreadCount > 0);
    }

    _validateEmail(email) {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    _generateKey() {
      return 'hd_' + Math.random().toString(36).slice(2) + Date.now().toString(36);
    }

    _escHtml(str) {
      return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/\n/g,'<br>');
    }
  }

  /* ══════════════════════════════════════════════════
     ADMIN DESK (for help/admin-desk/ pages)
  ══════════════════════════════════════════════════ */
  class AdminHelpDesk {
    constructor() {
      this.chatWindow = $('#hd-admin-messages');
      this.replyForm  = $('#hd-admin-reply-form');
      this.replyInput = $('#hd-admin-reply-input');
      this.sessionId  = this.chatWindow?.dataset.sessionId;
      this.pollTimer  = null;
      this.lastId     = 0;

      if (!this.chatWindow) return;
      this._init();
    }

    _init() {
      // Auto-scroll to bottom
      this.chatWindow.scrollTop = this.chatWindow.scrollHeight;

      // Calculate last message id from existing messages
      const msgs = this.chatWindow.querySelectorAll('[data-msg-id]');
      if (msgs.length) {
        this.lastId = parseInt(msgs[msgs.length - 1].dataset.msgId || '0');
      }

      // Reply form
      this.replyForm?.addEventListener('submit', e => {
        e.preventDefault();
        this._sendReply();
      });
      this.replyInput?.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this._sendReply();
        }
      });

      // Start polling for new visitor messages
      this._startPolling();

      // Session item clicks in sidebar
      $$('.hd-session-item[data-session-url]').forEach(item => {
        item.addEventListener('click', () => {
          window.location.href = item.dataset.sessionUrl;
        });
      });
    }

    _startPolling() {
      this.pollTimer = setInterval(() => this._poll(), POLL_INTERVAL);
    }

    async _poll() {
      if (!this.sessionId) return;
      try {
        const sessionKey = this.chatWindow?.dataset.sessionKey;
        if (!sessionKey) return;
        const data = await get(`/help/messages/${sessionKey}/?last_id=${this.lastId}&admin=1`);
        if (data.messages?.length) {
          data.messages.forEach(m => this._appendMessage(m));
          this.lastId = data.messages[data.messages.length - 1].id;
        }
      } catch (e) {}
    }

    async _sendReply() {
      const text = this.replyInput?.value.trim();
      if (!text) return;

      const btn = this.replyForm?.querySelector('button[type="submit"]');
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }

      try {
        this.replyForm.submit();
      } catch (e) {
        if (btn) { btn.disabled = false; btn.textContent = 'Send Reply'; }
      }
    }

    _appendMessage(msg) {
      if (!this.chatWindow) return;
      const div = document.createElement('div');
      div.className = `hd-msg ${msg.sender_type}`;
      div.dataset.msgId = msg.id;
      div.innerHTML = `
        <div class="hd-msg__bubble">${msg.message.replace(/\n/g,'<br>')}</div>
        <div class="hd-msg__meta">${msg.sender_name || msg.sender_type} · ${fmt(msg.sent_at)}</div>
      `;
      this.chatWindow.appendChild(div);
      this.chatWindow.scrollTop = this.chatWindow.scrollHeight;
    }
  }

  /* ── INIT ── */
  document.addEventListener('DOMContentLoaded', () => {
    new HelpWidget();
    new AdminHelpDesk();
  });

})();
