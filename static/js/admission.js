/**
 * ADMISSION PORTAL — Complete JavaScript
 * Handles: multi-step form navigation, conditional fields,
 * AJAX auto-save, file uploads, form validation, language toggle
 */

(function () {
  'use strict';

  /* ── Constants ── */
  const CSRF = () => document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
  const SAVE_INTERVAL = 30000; // 30 seconds auto-save

  /* ── Toast notifications ── */
  function showToast(msg, type = 'info', duration = 3500) {
    let toast = document.getElementById('adm-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'adm-toast';
      toast.className = 'adm-toast';
      document.body.appendChild(toast);
    }
    const icons = { success: 'check-circle', error: 'exclamation-circle', info: 'info-circle', warning: 'exclamation-triangle' };
    toast.innerHTML = `<i class="fas fa-${icons[type] || 'info-circle'}"></i>${msg}`;
    toast.className = `adm-toast show ${type}`;
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.remove('show'), duration);
  }

  /* ── CSRF fetch helper ── */
  async function apiFetch(url, data, method = 'POST') {
    const opts = {
      method,
      headers: {
        'X-CSRFToken': CSRF(),
        'X-Requested-With': 'XMLHttpRequest',
      },
    };
    if (data instanceof FormData) {
      opts.body = data;
    } else {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(data);
    }
    const res = await fetch(url, opts);
    return res.json();
  }

  /* ══════════════════════════════════════════════════
     MULTI-STEP FORM ENGINE
  ══════════════════════════════════════════════════ */
  class AdmissionForm {
    constructor(container) {
      this.container = container;
      this.container._formInstance = this; // Store reference
      this.appNumber = container.dataset.appNumber;
      this.saveUrl = container.dataset.saveUrl;
      this.submitUrl = container.dataset.submitUrl;
      this.uploadUrl = container.dataset.uploadUrl;
      this.lang = document.documentElement.dataset.admLang || 'en';

      this.sections = Array.from(container.querySelectorAll('.adm-section-panel'));
      this.stepItems = Array.from(container.querySelectorAll('.adm-step-item'));
      this.currentIndex = 0;
      this.savedData = {};

      this._init();
    }

    _init() {
      this._loadSavedData();
      this._bindStepClicks();
      this._bindNavButtons();
      this._bindConditionalFields();
      this._bindFileUploads();
      this._bindAutoSave();
      this._bindInputTracking();
      this._showSection(0);
      this._updateProgress();
    }

    _loadSavedData() {
      try {
        const stored = localStorage.getItem(`adm_draft_${this.appNumber}`);
        if (stored) this.savedData = JSON.parse(stored);
      } catch (e) {}
    }

    _bindStepClicks() {
      this.stepItems.forEach((item, idx) => {
        item.addEventListener('click', () => {
          if (idx < this.currentIndex || item.classList.contains('completed')) {
            this._navigateTo(idx);
          }
        });
      });
    }

    _bindNavButtons() {
      this.container.querySelectorAll('[data-adm-next]').forEach(btn => {
        btn.addEventListener('click', () => this._next());
      });
      this.container.querySelectorAll('[data-adm-prev]').forEach(btn => {
        btn.addEventListener('click', () => this._prev());
      });
    }

    _bindConditionalFields() {
      // Fields with data-condition-field attribute are conditionally shown
      this.container.querySelectorAll('[data-condition-field]').forEach(field => {
        const targetKey = field.dataset.conditionField;
        const operator = field.dataset.conditionOperator || 'eq';
        const condValue = field.dataset.conditionValue || '';

        const evaluate = () => {
          const sourceEl = this.container.querySelector(`[name="${targetKey}"], [data-field-key="${targetKey}"]`);
          if (!sourceEl) return;
          let currentVal = '';
          if (sourceEl.type === 'checkbox') {
            currentVal = sourceEl.checked ? sourceEl.value : '';
          } else {
            currentVal = sourceEl.value || '';
          }

          let show = false;
          if (operator === 'eq')       show = currentVal === condValue;
          else if (operator === 'neq') show = currentVal !== condValue;
          else if (operator === 'contains') show = currentVal.toLowerCase().includes(condValue.toLowerCase());

          field.classList.toggle('hidden', !show);
          // Update required attribute
          const inputs = field.querySelectorAll('input, select, textarea');
          inputs.forEach(inp => {
            if (!show) inp.removeAttribute('required');
            else if (inp.dataset.originalRequired) inp.setAttribute('required', '');
          });
        };

        // Bind to all matching source fields
        const sourceEl = this.container.querySelector(`[name="${targetKey}"], [data-field-key="${targetKey}"]`);
        if (sourceEl) {
          sourceEl.addEventListener('change', evaluate);
          sourceEl.addEventListener('input', evaluate);
          evaluate(); // initial
        }
      });

      // Transfer section toggle
      const transferCheckbox = this.container.querySelector('[name="is_transfer"]');
      const transferSection = this.container.querySelector('[data-transfer-section]');
      if (transferCheckbox && transferSection) {
        const toggle = () => {
          transferSection.classList.toggle('hidden', !transferCheckbox.checked);
        };
        transferCheckbox.addEventListener('change', toggle);
        toggle();
      }
    }

    _bindFileUploads() {
      this.container.querySelectorAll('.adm-file-drop').forEach(drop => {
        const input = drop.querySelector('input[type="file"]');
        const fieldKey = drop.dataset.fieldKey;
        const preview = drop.closest('.adm-field').querySelector('.adm-file-preview');

        // Drag events
        drop.addEventListener('dragover', e => { e.preventDefault(); drop.classList.add('drag-over'); });
        drop.addEventListener('dragleave', () => drop.classList.remove('drag-over'));
        drop.addEventListener('drop', e => {
          e.preventDefault();
          drop.classList.remove('drag-over');
          if (e.dataTransfer.files[0]) this._uploadFile(fieldKey, e.dataTransfer.files[0], drop, preview);
        });

        // Click/select
        input?.addEventListener('change', () => {
          if (input.files[0]) this._uploadFile(fieldKey, input.files[0], drop, preview);
        });

        // Delete existing file
        preview?.querySelector('.delete-file')?.addEventListener('click', async () => {
          const res = await apiFetch(`/apply/form/${this.appNumber}/delete-file/${fieldKey}/`, {});
          if (res.success) {
            preview.style.display = 'none';
            drop.style.display = '';
            showToast('File removed.', 'info');
          }
        });
      });
    }

    async _uploadFile(fieldKey, file, dropEl, previewEl) {
      const maxMb = parseInt(dropEl.dataset.maxSizeMb || '5');
      if (file.size > maxMb * 1024 * 1024) {
        showToast(`File is too large. Maximum size is ${maxMb}MB.`, 'error');
        return;
      }

      // Show uploading state
      dropEl.innerHTML = `<span class="adm-file-uploading"><i class="fas fa-spinner fa-spin me-2"></i>Uploading...</span>`;

      const fd = new FormData();
      fd.append('field_key', fieldKey);
      fd.append('file', file);

      try {
        const res = await fetch(this.uploadUrl, {
          method: 'POST',
          headers: { 'X-CSRFToken': CSRF(), 'X-Requested-With': 'XMLHttpRequest' },
          body: fd,
        });
        const data = await res.json();
        if (data.success) {
          dropEl.style.display = 'none';
          if (previewEl) {
            previewEl.style.display = 'flex';
            previewEl.querySelector('.file-name').textContent = data.name;
            previewEl.querySelector('.file-size').textContent = `${Math.round(file.size / 1024)} KB`;
          }
          showToast('File uploaded successfully!', 'success');
          this.stepItems[this.currentIndex]?.classList.add('has-file');
        } else {
          showToast(data.error || 'Upload failed.', 'error');
          // Restore drop zone
          this._restoreDropZone(dropEl);
        }
      } catch (err) {
        showToast('Upload failed. Please try again.', 'error');
        this._restoreDropZone(dropEl);
      }
    }

    _restoreDropZone(dropEl) {
      dropEl.innerHTML = `
        <i class="fas fa-cloud-upload-alt"></i>
        <p>Drag & drop file here or <span>browse</span></p>
        <input type="file">`;
    }

    _bindInputTracking() {
      this.container.querySelectorAll('input, select, textarea').forEach(el => {
        // Store original required status
        if (el.required) el.dataset.originalRequired = '1';

        el.addEventListener('change', () => {
          const key = el.name || el.dataset.fieldKey;
          if (key) this.savedData[key] = el.type === 'checkbox' ? el.checked : el.value;
          this._markDirty();
        });
        el.addEventListener('blur', () => this._validateField(el));
      });
    }

    _validateField(el) {
      const field = el.closest('.adm-field');
      if (!field) return true;
      if (el.required && !el.value.trim()) {
        field.classList.add('has-error');
        return false;
      }
      field.classList.remove('has-error');
      return true;
    }

    _validateSection(index) {
      const section = this.sections[index];
      if (!section) return true;
      let valid = true;
      section.querySelectorAll('input[required], select[required], textarea[required]').forEach(el => {
        const field = el.closest('.adm-field');
        if (field && (field.classList.contains('hidden') || field.closest('.hidden'))) return; // skip hidden fields!
        if (!this._validateField(el)) valid = false;
      });

      // Validate required file uploads
      section.querySelectorAll('.adm-file-drop[data-required="1"]').forEach(dropEl => {
        const field = dropEl.closest('.adm-field');
        if (field) {
          // Skip if hidden
          if (field.classList.contains('hidden') || field.closest('.hidden')) return;

          const previewEl = field.querySelector('.adm-file-preview');
          if (dropEl.style.display !== 'none' && (!previewEl || previewEl.style.display === 'none')) {
            field.classList.add('has-error');
            const errText = field.querySelector('.adm-error-text');
            if (errText) {
              errText.textContent = 'Uploading this document is required.';
              errText.style.display = 'block';
            }
            valid = false;
          } else {
            field.classList.remove('has-error');
          }
        }
      });

      return valid;
    }

    _markDirty() {
      try {
        localStorage.setItem(`adm_draft_${this.appNumber}`, JSON.stringify(this.savedData));
      } catch (e) {}
      this._updateSaveIndicator('saving');
    }

    _bindAutoSave() {
      setInterval(() => this.saveDraft(), SAVE_INTERVAL);
    }

    async saveDraft() {
      this._updateSaveIndicator('saving');
      const formData = this._collectFormData();
      try {
        const res = await apiFetch(this.saveUrl, formData);
        if (res.success) {
          this._updateSaveIndicator('saved');
        } else {
          this._updateSaveIndicator('error');
        }
      } catch (e) {
        this._updateSaveIndicator('error');
      }
    }

    _collectFormData() {
      const data = {};
      this.container.querySelectorAll('input:not([type="file"]), select, textarea').forEach(el => {
        const key = el.name || el.dataset.fieldKey;
        if (!key) return;
        if (el.type === 'checkbox') {
          if (!data[key]) data[key] = [];
          if (el.checked) data[key].push(el.value);
        } else if (el.type === 'radio') {
          if (el.checked) data[key] = el.value;
        } else {
          data[key] = el.value;
        }
      });
      return data;
    }

    _updateSaveIndicator(state) {
      const ind = document.querySelector('.adm-autosave-indicator');
      if (!ind) return;
      ind.className = `adm-autosave-indicator ${state}`;
      const texts = { saved: 'Draft saved', saving: 'Saving…', error: 'Save failed' };
      const span = ind.querySelector('span');
      if (span) span.textContent = texts[state] || '';
    }

    _navigateTo(index) {
      this._showSection(index);
    }

    async _next() {
      if (!this._validateSection(this.currentIndex)) {
        showToast('Please fill all required fields before continuing.', 'warning');
        return;
      }
      await this.saveDraft();
      if (this.currentIndex < this.sections.length - 1) {
        this.stepItems[this.currentIndex]?.classList.add('completed');
        this._showSection(this.currentIndex + 1);
      }
    }

    _prev() {
      if (this.currentIndex > 0) {
        this._showSection(this.currentIndex - 1);
      }
    }

    _showSection(index) {
      this.sections.forEach((s, i) => s.classList.toggle('active', i === index));
      this.stepItems.forEach((s, i) => {
        s.classList.toggle('active', i === index);
        if (i < index) s.classList.add('completed');
      });
      this.currentIndex = index;
      this._updateProgress();
      this._updateNavButtons();
      // Scroll to top of form panel
      this.container.querySelector('.adm-form-panel')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    _updateProgress() {
      const total = this.sections.length;
      const current = this.currentIndex + 1;
      const pct = Math.round((current / total) * 100);
      const bar = document.querySelector('.adm-mobile-progress__fill');
      const text = document.querySelector('.adm-mobile-progress__text');
      if (bar) bar.style.width = `${pct}%`;
      if (text) text.textContent = `Step ${current} of ${total}`;
    }

    _updateNavButtons() {
      const prevBtns = this.container.querySelectorAll('[data-adm-prev]');
      const nextBtns = this.container.querySelectorAll('[data-adm-next]');
      const submitBtns = this.container.querySelectorAll('[data-adm-submit]');
      const isLast = this.currentIndex === this.sections.length - 1;

      prevBtns.forEach(b => { b.style.visibility = this.currentIndex === 0 ? 'hidden' : 'visible'; });
      nextBtns.forEach(b => { b.style.display = isLast ? 'none' : ''; });
      submitBtns.forEach(b => { b.style.display = isLast ? '' : 'none'; });
    }
  }

  /* ══════════════════════════════════════════════════
     SUBMIT FORM
  ══════════════════════════════════════════════════ */
  function initSubmitButton() {
    const submitBtn = document.querySelector('[data-adm-submit]');
    const form = document.getElementById('adm-main-form');
    if (!submitBtn || !form) return;

    submitBtn.addEventListener('click', async (e) => {
      e.preventDefault();

      // Full validation check of all steps before final submission
      const panels = Array.from(document.querySelectorAll('.adm-section-panel'));
      let allValid = true;
      let firstInvalidIndex = -1;

      // Helper function to validate a single field
      const validateField = (el) => {
        const field = el.closest('.adm-field');
        if (!field) return true;
        
        // Skip validation if field is hidden
        if (field.classList.contains('hidden') || field.closest('.hidden')) return true;

        if (el.required && !el.value.trim()) {
          field.classList.add('has-error');
          return false;
        }
        field.classList.remove('has-error');
        return true;
      };

      panels.forEach((section, index) => {
        // Validate text/select inputs
        section.querySelectorAll('input[required], select[required], textarea[required]').forEach(el => {
          if (!validateField(el)) {
            allValid = false;
            if (firstInvalidIndex === -1) firstInvalidIndex = index;
          }
        });

        // Validate required file uploads
        section.querySelectorAll('.adm-file-drop[data-required="1"]').forEach(dropEl => {
          const field = dropEl.closest('.adm-field');
          if (field) {
            // Skip if hidden
            if (field.classList.contains('hidden') || field.closest('.hidden')) return;

            const previewEl = field.querySelector('.adm-file-preview');
            if (dropEl.style.display !== 'none' && (!previewEl || previewEl.style.display === 'none')) {
              field.classList.add('has-error');
              const errText = field.querySelector('.adm-error-text');
              if (errText) {
                errText.textContent = 'Uploading this document is required.';
                errText.style.display = 'block';
              }
              allValid = false;
              if (firstInvalidIndex === -1) firstInvalidIndex = index;
            } else {
              field.classList.remove('has-error');
            }
          }
        });
      });

      if (!allValid) {
        showToast('Your application is incomplete. Please upload all required documents and fill out all fields.', 'error');
        const formContainer = document.getElementById('adm-form-container');
        if (formContainer && formContainer._formInstance) {
          formContainer._formInstance._navigateTo(firstInvalidIndex);
        }
        return;
      }

      if (!confirm('Are you sure you want to submit your application? You will not be able to make changes after submission.')) return;

      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting…';

      form.submit();
    });
  }

  /* ══════════════════════════════════════════════════
     CLASS SELECTOR (window detail page)
  ══════════════════════════════════════════════════ */
  function initClassSelector() {
    const cards = document.querySelectorAll('[data-class-card]');
    const startBtn = document.getElementById('adm-start-btn');
    const classInput = document.getElementById('adm-selected-class');
    const transferInput = document.getElementById('adm-is-transfer');

    if (!cards.length) return;

    cards.forEach(card => {
      card.addEventListener('click', () => {
        cards.forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        if (classInput) classInput.value = card.dataset.classCode;
        if (startBtn) {
          startBtn.disabled = false;
          startBtn.innerHTML = `<i class="fas fa-arrow-right me-2"></i>Apply for ${card.querySelector('.class-name')?.textContent}`;
        }
      });
    });

    // Transfer toggle
    const transferToggle = document.querySelector('[data-transfer-toggle]');
    if (transferToggle && transferInput) {
      transferToggle.addEventListener('change', () => {
        transferInput.value = transferToggle.checked ? '1' : '0';
      });
    }
  }

  /* ══════════════════════════════════════════════════
     STATUS TRACKER
  ══════════════════════════════════════════════════ */
  function initStatusTracker() {
    const form = document.getElementById('status-check-form');
    if (!form) return;

    form.addEventListener('submit', e => {
      const appNum = form.querySelector('[name="app_number"]')?.value.trim();
      const email = form.querySelector('[name="email"]')?.value.trim();

      if (!appNum || !email) {
        e.preventDefault();
        showToast('Please enter both your application number and email.', 'warning');
      }
    });
  }

  /* ══════════════════════════════════════════════════
     OPTION CARDS (radio/checkbox styled)
  ══════════════════════════════════════════════════ */
  function initOptionCards() {
    document.querySelectorAll('.adm-option-item').forEach(item => {
      const input = item.querySelector('input[type="radio"], input[type="checkbox"]');
      if (!input) return;

      const updateState = () => {
        if (input.type === 'radio') {
          // Unselect siblings
          const name = input.name;
          document.querySelectorAll(`input[type="radio"][name="${name}"]`).forEach(r => {
            r.closest('.adm-option-item')?.classList.remove('selected');
          });
        }
        item.classList.toggle('selected', input.checked);
      };

      item.addEventListener('click', () => {
        if (input.type === 'radio') input.checked = true;
        else input.checked = !input.checked;
        updateState();
        input.dispatchEvent(new Event('change', { bubbles: true }));
      });

      if (input.checked) updateState();
    });
  }

  /* ══════════════════════════════════════════════════
     LANGUAGE TOGGLE (smooth switching)
  ══════════════════════════════════════════════════ */
  function initLanguageToggle() {
    document.querySelectorAll('.lang-btn[data-lang]').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const lang = btn.dataset.lang;
        if (!lang) return;

        // Immediately update localStorage + HTML attribute for next page
        localStorage.setItem('adm_lang', lang);
        document.documentElement.dataset.admLang = lang;

        // Update active class
        document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll(`.lang-btn[data-lang="${lang}"]`).forEach(b => b.classList.add('active'));

        // If this is a link (not a button), let it navigate
        if (btn.tagName === 'A') return;

        // For form pages: navigate via fetch
        try {
          await fetch(btn.dataset.langUrl || `/apply/lang/${lang}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': CSRF() },
          });
          window.location.reload();
        } catch (e) {
          window.location.reload();
        }
      });
    });
  }

  /* ══════════════════════════════════════════════════
     PRINT CONFIRMATION
  ══════════════════════════════════════════════════ */
  function initPrintButton() {
    document.querySelectorAll('[data-print]').forEach(btn => {
      btn.addEventListener('click', () => window.print());
    });
  }

  /* ══════════════════════════════════════════════════
     PHONE NUMBER FORMATTING
  ══════════════════════════════════════════════════ */
  function initPhoneFields() {
    document.querySelectorAll('input[type="tel"], input[name="phone"]').forEach(input => {
      input.addEventListener('input', () => {
        // Allow only digits, spaces, +, -
        input.value = input.value.replace(/[^0-9+\-\s]/g, '');
      });
    });
  }

  /* ══════════════════════════════════════════════════
     SPOTS BAR ANIMATION
  ══════════════════════════════════════════════════ */
  function initSpotsBars() {
    document.querySelectorAll('.adm-spots-bar__fill').forEach(bar => {
      const pct = parseInt(bar.dataset.pct || '0');
      setTimeout(() => { bar.style.width = `${pct}%`; }, 100);
      if (pct >= 90) bar.classList.add('danger');
      else if (pct >= 70) bar.classList.add('warning');
    });
  }

  /* ── INIT ── */
  document.addEventListener('DOMContentLoaded', () => {
    const formContainer = document.getElementById('adm-form-container');
    if (formContainer) new AdmissionForm(formContainer);

    initSubmitButton();
    initClassSelector();
    initStatusTracker();
    initOptionCards();
    initLanguageToggle();
    initPrintButton();
    initPhoneFields();
    initSpotsBars();
  });

})();
