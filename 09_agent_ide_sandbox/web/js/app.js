/**
 * app.js
 * ======
 * Frontend controller for Agent-IDE Sandbox & LOGOS Ultra Interface.
 * Coordinates chat interactions, live sandbox feedback, and dynamic API switching.
 */

(function () {
  'use strict';

  // Application State
  const state = {
    provider: 'mock',
    model: 'mock-developer-v1',
    enableLogos: true,
    customEndpoint: '',
    apiKey: '',
    retries: 3,
    isProcessing: false,
    modelsCatalog: {},
    conversationCount: 0,
  };

  // DOM Elements
  const DOM = {
    sidebar: document.getElementById('sidebar'),
    btnSidebarToggle: document.getElementById('btn-sidebar-toggle'),
    btnNewChat: document.getElementById('btn-new-chat'),
    btnClearChat: document.getElementById('btn-clear-chat'),
    btnModelPill: document.getElementById('btn-model-pill'),
    topModelDisplay: document.getElementById('top-model-display'),
    sidebarProviderName: document.getElementById('sidebar-provider-name'),
    sidebarModelName: document.getElementById('sidebar-model-name'),
    sidebarTopology: document.getElementById('sidebar-topology'),
    inputModelTag: document.getElementById('input-model-tag'),
    logosIndicator: document.getElementById('logos-indicator'),
    btnToggleLogos: document.getElementById('btn-toggle-logos'),
    holoTracesCount: document.getElementById('holo-traces-count'),
    holoCompressionRatio: document.getElementById('holo-compression-ratio'),
    chatFeed: document.getElementById('chat-feed'),
    welcomeContainer: document.getElementById('welcome-container'),
    chatInput: document.getElementById('chat-input'),
    btnSend: document.getElementById('btn-send'),
    // Modal
    modalBackdrop: document.getElementById('modal-backdrop'),
    btnOpenSettings: document.getElementById('btn-open-settings'),
    btnQuickSettings: document.getElementById('btn-quick-settings'),
    btnCloseModal: document.getElementById('btn-close-modal'),
    btnCancelSettings: document.getElementById('btn-cancel-settings'),
    btnSaveSettings: document.getElementById('btn-save-settings'),
    providerSelect: document.getElementById('provider-select'),
    modelInput: document.getElementById('model-input'),
    endpointInput: document.getElementById('endpoint-input'),
    apiKeyInput: document.getElementById('api-key-input'),
    presetPills: document.getElementById('preset-pills'),
    logosCheckbox: document.getElementById('logos-checkbox'),
    retriesInput: document.getElementById('retries-input'),
    retriesVal: document.getElementById('retries-val'),
  };

  // --------------------------------------------------------------------------
  // Initialization & System Sync
  // --------------------------------------------------------------------------

  async function initApp() {
    setupEventListeners();
    await fetchSystemStatus();
    await fetchModelsCatalog();
  }

  async function fetchSystemStatus() {
    try {
      const res = await fetch('/api/status');
      if (!res.ok) return;
      const data = await res.json();

      state.provider = data.active_provider;
      state.model = data.active_model;
      state.enableLogos = data.enable_logos;

      updateUIHeaderAndSidebar(data);
    } catch (err) {
      console.warn('Could not sync system status:', err);
    }
  }

  async function fetchModelsCatalog() {
    try {
      const res = await fetch('/api/models');
      if (!res.ok) return;
      state.modelsCatalog = await res.json();
      renderModelPresets();
    } catch (err) {
      console.warn('Could not fetch models catalog:', err);
    }
  }

  function updateUIHeaderAndSidebar(statusData) {
    const provName = state.provider.toUpperCase();
    DOM.sidebarProviderName.textContent = provName;
    DOM.sidebarModelName.textContent = state.model;
    DOM.topModelDisplay.textContent = `${provName}: ${state.model}`;
    DOM.inputModelTag.textContent = `Model: ${provName}`;

    // Holographic telemetry
    if (statusData && statusData.holographic_memory) {
      const hm = statusData.holographic_memory;
      DOM.holoTracesCount.textContent = hm.total_records || 0;
      DOM.holoCompressionRatio.textContent = `${hm.compression_ratio || 1.0}x`;
    }

    // LOGOS Indicator
    if (state.enableLogos) {
      DOM.logosIndicator.style.display = 'flex';
    } else {
      DOM.logosIndicator.style.display = 'none';
    }
  }

  // --------------------------------------------------------------------------
  // Event Listeners
  // --------------------------------------------------------------------------

  function setupEventListeners() {
    // Sidebar toggle
    DOM.btnSidebarToggle.addEventListener('click', () => {
      DOM.sidebar.classList.toggle('collapsed');
    });

    // Auto-resize textarea
    DOM.chatInput.addEventListener('input', () => {
      DOM.chatInput.style.height = 'auto';
      DOM.chatInput.style.height = Math.min(DOM.chatInput.scrollHeight, 180) + 'px';
    });

    // Keydown in input
    DOM.chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submitMessage();
      }
    });

    // Send button
    DOM.btnSend.addEventListener('click', submitMessage);

    // New chat / Clear chat
    DOM.btnNewChat.addEventListener('click', clearChatSession);
    DOM.btnClearChat.addEventListener('click', clearChatSession);

    // Quick Task Chips
    document.querySelectorAll('.task-chip').forEach((chip) => {
      chip.addEventListener('click', () => {
        const taskText = chip.getAttribute('data-task');
        DOM.chatInput.value = taskText;
        DOM.chatInput.focus();
        submitMessage();
      });
    });

    // Toggle LOGOS button in input bar
    DOM.btnToggleLogos.addEventListener('click', () => {
      state.enableLogos = !state.enableLogos;
      DOM.logosCheckbox.checked = state.enableLogos;
      saveCurrentSettings();
    });

    // Settings Modal triggers
    DOM.btnOpenSettings.addEventListener('click', openSettingsModal);
    DOM.btnQuickSettings.addEventListener('click', openSettingsModal);
    DOM.btnModelPill.addEventListener('click', openSettingsModal);
    DOM.btnCloseModal.addEventListener('click', closeSettingsModal);
    DOM.btnCancelSettings.addEventListener('click', closeSettingsModal);
    DOM.modalBackdrop.addEventListener('click', (e) => {
      if (e.target === DOM.modalBackdrop) closeSettingsModal();
    });

    // Provider select change -> update presets
    DOM.providerSelect.addEventListener('change', () => {
      renderModelPresets();
    });

    // Retries slider input
    DOM.retriesInput.addEventListener('input', () => {
      DOM.retriesVal.textContent = DOM.retriesInput.value;
    });

    // Save settings button
    DOM.btnSaveSettings.addEventListener('click', async () => {
      await saveCurrentSettings();
      closeSettingsModal();
    });
  }

  // --------------------------------------------------------------------------
  // Settings & Presets
  // --------------------------------------------------------------------------

  function openSettingsModal() {
    DOM.providerSelect.value = state.provider;
    DOM.modelInput.value = state.model;
    DOM.endpointInput.value = state.customEndpoint;
    DOM.logosCheckbox.checked = state.enableLogos;
    DOM.retriesInput.value = state.retries;
    DOM.retriesVal.textContent = state.retries;
    renderModelPresets();
    DOM.modalBackdrop.classList.add('open');
  }

  function closeSettingsModal() {
    DOM.modalBackdrop.classList.remove('open');
  }

  function renderModelPresets() {
    DOM.presetPills.innerHTML = '';
    const selectedProvider = DOM.providerSelect.value;
    const presets = (state.modelsCatalog.presets && state.modelsCatalog.presets[selectedProvider]) || [];

    presets.forEach((modelName) => {
      const pill = document.createElement('span');
      pill.className = 'preset-pill';
      pill.textContent = modelName;
      pill.addEventListener('click', () => {
        DOM.modelInput.value = modelName;
      });
      DOM.presetPills.appendChild(pill);
    });

    // Auto-fill default model if input is empty
    if (!DOM.modelInput.value && presets.length > 0) {
      DOM.modelInput.value = presets[0];
    }
  }

  async function saveCurrentSettings() {
    const payload = {
      provider: DOM.providerSelect.value,
      model: DOM.modelInput.value,
      custom_endpoint: DOM.endpointInput.value || null,
      api_key: DOM.apiKeyInput.value || null,
      enable_logos: DOM.logosCheckbox.checked,
      max_retries: parseInt(DOM.retriesInput.value, 10) || 3,
    };

    try {
      const res = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const data = await res.json();
        state.provider = data.active_provider;
        state.model = data.active_model;
        state.enableLogos = data.enable_logos;
        state.retries = payload.max_retries;
        state.customEndpoint = payload.custom_endpoint || '';
        updateUIHeaderAndSidebar(data);
      }
    } catch (err) {
      console.error('Failed to save settings:', err);
    }
  }

  // --------------------------------------------------------------------------
  // Chat Actions & Message Rendering
  // --------------------------------------------------------------------------

  async function submitMessage() {
    const text = DOM.chatInput.value.trim();
    if (!text || state.isProcessing) return;

    // Hide welcome greeting if present
    if (DOM.welcomeContainer) {
      DOM.welcomeContainer.style.display = 'none';
    }

    // Render user message bubble
    appendUserMessage(text);
    DOM.chatInput.value = '';
    DOM.chatInput.style.height = 'auto';

    // Render loading indicator
    state.isProcessing = true;
    DOM.btnSend.disabled = true;
    const loadingNode = appendLoadingIndicator();
    scrollToBottom();

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: text }),
      });

      loadingNode.remove();

      if (!res.ok) {
        const errData = await res.json();
        appendErrorMessage(errData.error || 'Request failed.');
      } else {
        const responseData = await res.json();
        appendAssistantMessage(responseData);
        // Refresh telemetry
        fetchSystemStatus();
      }
    } catch (err) {
      loadingNode.remove();
      appendErrorMessage(`Network error: ${err.message}`);
    } finally {
      state.isProcessing = false;
      DOM.btnSend.disabled = false;
      scrollToBottom();
    }
  }

  function appendUserMessage(text) {
    const row = document.createElement('div');
    row.className = 'message-row user';
    row.innerHTML = `
      <div class="message-bubble">${escapeHtml(text)}</div>
      <div class="avatar user-avatar">👤</div>
    `;
    DOM.chatFeed.appendChild(row);
  }

  function appendLoadingIndicator() {
    const row = document.createElement('div');
    row.className = 'message-row bot';
    row.innerHTML = `
      <div class="avatar bot-avatar">⚡</div>
      <div class="message-bubble">
        <div class="typing-indicator">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </div>
      </div>
    `;
    DOM.chatFeed.appendChild(row);
    return row;
  }

  function appendErrorMessage(msg) {
    const row = document.createElement('div');
    row.className = 'message-row bot';
    row.innerHTML = `
      <div class="avatar bot-avatar">⚠️</div>
      <div class="message-bubble" style="color: var(--accent-rose);">
        <strong>Execution Error:</strong> ${escapeHtml(msg)}
      </div>
    `;
    DOM.chatFeed.appendChild(row);
  }

  function appendAssistantMessage(data) {
    const row = document.createElement('div');
    row.className = 'message-row bot';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    // 1. Thinking / Pondering Accordion (if available)
    if (data.thinking) {
      const thinkingEl = createThinkingAccordion(data.thinking);
      bubble.appendChild(thinkingEl);
    }

    // 2. Main Response Text
    const textEl = document.createElement('div');
    textEl.className = 'message-text';
    textEl.innerHTML = renderSimpleMarkdown(data.content || '');
    bubble.appendChild(textEl);

    // 3. Sandbox Code Execution Card (if code is present)
    if (data.type === 'code_execution' && data.code) {
      const sandboxCard = createSandboxCard(data);
      bubble.appendChild(sandboxCard);
    }

    row.innerHTML = `<div class="avatar bot-avatar">⚡</div>`;
    row.appendChild(bubble);
    DOM.chatFeed.appendChild(row);
  }

  // --------------------------------------------------------------------------
  // LOGOS Thinking Accordion Component
  // --------------------------------------------------------------------------

  function createThinkingAccordion(thinking) {
    const container = document.createElement('div');
    container.className = 'thinking-accordion';

    const header = document.createElement('div');
    header.className = 'thinking-header';
    header.innerHTML = `
      <div class="thinking-title">
        <span>🧠</span>
        <span>LOGOS Cognitive Reasoning & Pondering</span>
        <span class="badge logos-badge">${thinking.topology || 'adaptive'}</span>
      </div>
      <svg class="thinking-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="6 9 12 15 18 9"></polyline>
      </svg>
    `;

    const content = document.createElement('div');
    content.className = 'thinking-content';

    // Summary block
    let summaryHtml = `<div class="thinking-block"><div class="thinking-block-title">Synthesis Summary</div><div>${escapeHtml(thinking.summary || '')}</div></div>`;

    // Invariants table
    let propsHtml = '';
    if (thinking.qualified_properties && thinking.qualified_properties.length > 0) {
      propsHtml += `
        <div class="thinking-block">
          <div class="thinking-block-title">Verified Invariants (Confidence &ge; 95%)</div>
          <table class="invariants-table">
            <thead>
              <tr><th>Angle / Dimension</th><th>Confidence</th><th>Invariant Property</th></tr>
            </thead>
            <tbody>
      `;
      thinking.qualified_properties.forEach((p) => {
        propsHtml += `
          <tr>
            <td><strong>${escapeHtml(p.name)}</strong></td>
            <td><span class="confidence-pill passed">${(p.confidence * 100).toFixed(1)}%</span></td>
            <td>${escapeHtml(p.hypothesis)}</td>
          </tr>
        `;
      });
      if (thinking.rejected_hypotheses) {
        thinking.rejected_hypotheses.forEach((r) => {
          propsHtml += `
            <tr>
              <td><strong>${escapeHtml(r.name)}</strong></td>
              <td><span class="confidence-pill rejected">${(r.confidence * 100).toFixed(1)}% (REJECTED)</span></td>
              <td style="text-decoration: line-through; opacity: 0.6;">${escapeHtml(r.hypothesis)}</td>
            </tr>
          `;
        });
      }
      propsHtml += `</tbody></table></div>`;
    }

    content.innerHTML = summaryHtml + propsHtml;

    header.addEventListener('click', () => {
      container.classList.toggle('open');
    });

    container.appendChild(header);
    container.appendChild(content);
    return container;
  }

  // --------------------------------------------------------------------------
  // Sandbox Card Component (Tabs: Code / Terminal / Audit)
  // --------------------------------------------------------------------------

  function createSandboxCard(data) {
    const card = document.createElement('div');
    card.className = 'sandbox-card';

    const cardId = 'sb-' + Math.random().toString(36).substr(2, 9);

    card.innerHTML = `
      <div class="sandbox-tabs">
        <button class="sandbox-tab active" data-target="${cardId}-code">Synthesized Code</button>
        <button class="sandbox-tab" data-target="${cardId}-term">Sandbox Terminal</button>
        <button class="sandbox-tab" data-target="${cardId}-audit">Reviewer Audit</button>
        <div class="sandbox-tab-actions">
          <button class="btn-copy-code" data-code="${encodeURIComponent(data.code)}">Copy</button>
        </div>
      </div>

      <div class="sandbox-panel active code-view" id="${cardId}-code">
        <pre><code>${escapeHtml(data.code)}</code></pre>
      </div>

      <div class="sandbox-panel terminal-view" id="${cardId}-term">
        <pre>${escapeHtml(data.test_logs || 'No execution logs recorded.')}</pre>
      </div>

      <div class="sandbox-panel review-view" id="${cardId}-audit">
        <div class="audit-metrics-grid">
          <div class="audit-metric-box">
            <span class="audit-metric-label">Execution Status</span>
            <span class="audit-metric-val" style="color: ${data.status === 'success' ? 'var(--accent-emerald)' : 'var(--accent-rose)'};">
              ${data.status ? data.status.toUpperCase() : 'UNKNOWN'}
            </span>
          </div>
          <div class="audit-metric-box">
            <span class="audit-metric-label">Security Audit</span>
            <span class="audit-metric-val" style="color: var(--accent-emerald);">
              ${(data.review && data.review.security_check) || 'passed'}
            </span>
          </div>
          <div class="audit-metric-box">
            <span class="audit-metric-label">Style & Contract Score</span>
            <span class="audit-metric-val" style="color: var(--accent-purple);">
              ${(data.review && data.review.style_score) || 9.0} / 10.0
            </span>
          </div>
        </div>
      </div>
    `;

    // Tab switching handlers
    const tabs = card.querySelectorAll('.sandbox-tab');
    tabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        tabs.forEach((t) => t.classList.remove('active'));
        card.querySelectorAll('.sandbox-panel').forEach((p) => p.classList.remove('active'));

        tab.classList.add('active');
        const targetId = tab.getAttribute('data-target');
        const targetPanel = card.querySelector('#' + targetId);
        if (targetPanel) targetPanel.classList.add('active');
      });
    });

    // Copy code handler
    const copyBtn = card.querySelector('.btn-copy-code');
    copyBtn.addEventListener('click', () => {
      const rawCode = decodeURIComponent(copyBtn.getAttribute('data-code'));
      navigator.clipboard.writeText(rawCode).then(() => {
        copyBtn.textContent = 'Copied!';
        setTimeout(() => (copyBtn.textContent = 'Copy'), 2000);
      });
    });

    return card;
  }

  // --------------------------------------------------------------------------
  // Helpers & Markdown Rendering
  // --------------------------------------------------------------------------

  async function clearChatSession() {
    try {
      await fetch('/api/clear', { method: 'POST' });
    } catch (e) {}

    DOM.chatFeed.innerHTML = '';
    if (DOM.welcomeContainer) {
      DOM.welcomeContainer.style.display = 'flex';
      DOM.chatFeed.appendChild(DOM.welcomeContainer);
    }
    fetchSystemStatus();
  }

  function scrollToBottom() {
    DOM.chatFeed.scrollTop = DOM.chatFeed.scrollHeight;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function renderSimpleMarkdown(text) {
    if (!text) return '';
    let out = escapeHtml(text);
    // Bold
    out = out.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Inline code
    out = out.replace(/`(.*?)`/g, '<code style="background: rgba(255,255,255,0.08); padding: 2px 5px; border-radius: 4px; font-family: var(--font-mono); font-size: 12px;">$1</code>');
    // Bullet lists
    out = out.replace(/^\s*-\s+(.*)$/gm, '<li style="margin-left: 18px;">$1</li>');
    // Paragraphs
    out = out.replace(/\n\n/g, '<br><br>');
    return out;
  }

  // Start app
  document.addEventListener('DOMContentLoaded', initApp);
})();
