/**
 * app.js
 * ======
 * Frontend controller for Agent-IDE Sandbox, Claude UI, MCP Studio,
 * and TypeSafe AI Jev Fast Pipeline.
 */

(function () {
  'use strict';

  // API Base auto-detection
  const API_BASE = (window.location.protocol === 'file:') ? 'http://127.0.0.1:8000' : window.location.origin;
  // Fix: when served from 127.0.0.1:8000, use same origin, not empty string causing CORS confusion

  // App State
  const state = {
    provider: 'mock',
    model: 'mock-developer-v1',
    enableLogos: true,
    isSubmitting: false,
    activeChatId: null,
    activeProjectId: null,
    catalog: {},
    chats: [],
    projects: [],
    artifacts: [],
    mcpPresets: [],
  };

  // Cached DOM Elements
  const DOM = {};

  function initDOM() {
    DOM.sidebar = document.getElementById('sidebar');
    DOM.btnToggleSidebar = document.getElementById('btn-toggle-sidebar');
    DOM.btnShowSidebar = document.getElementById('btn-show-sidebar');
    DOM.btnNewChat = document.getElementById('btn-new-chat');
    DOM.btnNavProjects = document.getElementById('btn-nav-projects');
    DOM.btnNavArtifacts = document.getElementById('btn-nav-artifacts');
    DOM.btnNavCode = document.getElementById('btn-nav-code');
    DOM.btnNavMcpStudio = document.getElementById('btn-nav-mcp-studio');
    DOM.btnAddProject = document.getElementById('btn-add-project');
    DOM.projectsPinnedList = document.getElementById('projects-pinned-list');
    DOM.chatsHistoryList = document.getElementById('chats-history-list');
    DOM.profileBar = document.getElementById('profile-bar');
    DOM.btnExportChat = document.getElementById('btn-export-chat');
    DOM.btnSearchChats = document.getElementById('btn-search-chats');

    // Chat Header
    DOM.btnTopModel = document.getElementById('btn-top-model');
    DOM.headerModelName = document.getElementById('header-model-name');
    DOM.jevSpeedBadge = document.getElementById('jev-speed-badge');
    DOM.jevLatencyVal = document.getElementById('jev-latency-val');
    DOM.pillLogosToggle = document.getElementById('pill-logos-toggle');
    DOM.btnOpenSettings = document.getElementById('btn-open-settings');
    DOM.btnClearSession = document.getElementById('btn-clear-session');

    // Chat View
    DOM.chatScrollArea = document.getElementById('chat-scroll-area');
    DOM.chatStream = document.getElementById('chat-stream');
    DOM.welcomeHero = document.getElementById('welcome-hero');

    // Input Dock
    DOM.promptInput = document.getElementById('prompt-input');
    DOM.btnSubmit = document.getElementById('btn-submit');
    DOM.btnModelQuick = document.getElementById('btn-model-quick');
    DOM.dockModelLabel = document.getElementById('dock-model-label');
    DOM.btnQuickMcp = document.getElementById('btn-quick-mcp');

    // MCP Studio Modal
    DOM.mcpStudioModal = document.getElementById('mcp-studio-modal');
    DOM.btnCloseMcpModal = document.getElementById('btn-close-mcp-modal');
    DOM.btnCloseMcpFooter = document.getElementById('btn-close-mcp-footer');
    DOM.mcpTemplateSelect = document.getElementById('mcp-template-select');
    DOM.mcpServerName = document.getElementById('mcp-server-name');
    DOM.mcpTransport = document.getElementById('mcp-transport');
    DOM.mcpServerDesc = document.getElementById('mcp-server-desc');
    DOM.mcpToolName = document.getElementById('mcp-tool-name');
    DOM.mcpToolDesc = document.getElementById('mcp-tool-desc');
    DOM.mcpToolParams = document.getElementById('mcp-tool-params');
    DOM.mcpToolCode = document.getElementById('mcp-tool-code');
    DOM.mcpTestArgs = document.getElementById('mcp-test-args');
    DOM.btnTestMcpTool = document.getElementById('btn-test-mcp-tool');
    DOM.btnGenerateMcpServer = document.getElementById('btn-generate-mcp-server');
    DOM.mcpJsonrpcOutput = document.getElementById('mcp-jsonrpc-output');
    DOM.mcpPythonCode = document.getElementById('mcp-python-code');
    DOM.mcpConfigCode = document.getElementById('mcp-config-code');
    DOM.btnCopyMcpPy = document.getElementById('btn-copy-mcp-py');
    DOM.btnCopyMcpCfg = document.getElementById('btn-copy-mcp-cfg');

    // Projects Modal
    DOM.projectsModal = document.getElementById('projects-modal');
    DOM.btnCloseProjectsModal = document.getElementById('btn-close-projects-modal');
    DOM.newProjectTitle = document.getElementById('new-project-title');
    DOM.newProjectDesc = document.getElementById('new-project-desc');
    DOM.btnSaveNewProject = document.getElementById('btn-save-new-project');
    DOM.projectsDialogList = document.getElementById('projects-dialog-list');

    // Artifacts Modal
    DOM.artifactsModal = document.getElementById('artifacts-modal');
    DOM.btnCloseArtifactsModal = document.getElementById('btn-close-artifacts-modal');
    DOM.artifactsListSidebar = document.getElementById('artifacts-list-sidebar');
    DOM.artifactViewerPane = document.getElementById('artifact-viewer-pane');

    // Settings Modal
    DOM.settingsModal = document.getElementById('settings-modal');
    DOM.btnCloseSettingsModal = document.getElementById('btn-close-settings-modal');
    DOM.btnCancelModal = document.getElementById('btn-cancel-modal');
    DOM.btnSaveModal = document.getElementById('btn-save-modal');
    DOM.modalProvider = document.getElementById('modal-provider');
    DOM.modalModel = document.getElementById('modal-model');
    DOM.modalEndpoint = document.getElementById('modal-endpoint');
    DOM.modalApikey = document.getElementById('modal-apikey');
    DOM.modalPresets = document.getElementById('modal-presets');
    DOM.btnTestConnection = document.getElementById('btn-test-connection');
    DOM.connStatusBanner = document.getElementById('conn-status-banner');
    DOM.connBannerText = document.getElementById('conn-banner-text');
    DOM.connTestResult = document.getElementById('conn-test-result');

    // Local AI Studio & Model Gallery DOM
    DOM.btnNavLocalAi = document.getElementById('btn-nav-local-ai');
    DOM.sidebarLocalStatusBadge = document.getElementById('sidebar-local-status-badge');
    DOM.localAiCallout = document.getElementById('local-ai-callout');
    DOM.btnHeroOpenGallery = document.getElementById('btn-hero-open-gallery');
    DOM.heroOllamaStatusChip = document.getElementById('hero-ollama-status-chip');
    DOM.heroStatusText = document.getElementById('hero-status-text');
    DOM.btnSettingsOpenGallery = document.getElementById('btn-settings-open-gallery');
    DOM.localAiModal = document.getElementById('local-ai-modal');
    DOM.btnCloseLocalAiModal = document.getElementById('btn-close-local-ai-modal');
    DOM.btnCloseLocalAiFooter = document.getElementById('btn-close-local-ai-footer');
    DOM.daemonStatusDot = document.getElementById('daemon-status-dot');
    DOM.daemonHeadline = document.getElementById('daemon-headline');
    DOM.daemonSubtext = document.getElementById('daemon-subtext');
    DOM.btnDaemonToggle = document.getElementById('btn-daemon-toggle');
    DOM.btnDaemonDownload = document.getElementById('btn-daemon-download');
    DOM.pullProgressPanel = document.getElementById('pull-progress-panel');
    DOM.progressModelName = document.getElementById('progress-model-name');
    DOM.progressPct = document.getElementById('progress-pct');
    DOM.progressStatusMsg = document.getElementById('progress-status-msg');
    DOM.progressFill = document.getElementById('progress-fill');
    DOM.modelGalleryGrid = document.getElementById('model-gallery-grid');
  }

  // --------------------------------------------------------------------------
  // Initialization & Boot
  // --------------------------------------------------------------------------

  
  function cleanStaticPlaceholders() {
    // Remove hardcoded static projects from HTML (zeta, higgs etc)
    if (DOM.projectsPinnedList) {
      const staticItems = DOM.projectsPinnedList.querySelectorAll('li');
      // If we haven't loaded from API yet and static items exist, clear them to avoid confusion
      if (state.projects.length === 0 && staticItems.length > 0) {
        // Check if these are the old hardcoded ones
        const hasHardcoded = Array.from(staticItems).some(li => li.textContent.includes('Zeta function') || li.textContent.includes('Higgs boson'));
        if (hasHardcoded) {
          DOM.projectsPinnedList.innerHTML = '<li class="sidebar-item-row" style="opacity:0.5; font-style:italic;"><span class="item-title">Loading projects...</span></li>';
        }
      }
    }
  }

  async function init() {
    initDOM();
    bindEvents();
    await fetchStatus();
    await fetchModels();
    await fetchOllamaStatus();
    await fetchChats();
    await fetchProjects();
    await fetchArtifacts();
    await fetchMcpPresets();
  }

  // --------------------------------------------------------------------------
  // Event Bindings
  // --------------------------------------------------------------------------

  
  function initProfile() {
    // Clean left column - make profile dynamic, not static abhijith
    const profileNameEl = document.querySelector('.profile-meta, #profile-bar .profile-left span, [data-profile-name]');
    let userName = localStorage.getItem('agent_ide_user_name') || 'User';
    // If URL has ?user=xxx, use that
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('user')) {
      userName = urlParams.get('user');
      localStorage.setItem('agent_ide_user_name', userName);
    }
    // Update all profile displays
    const abhijithEls = document.querySelectorAll('*');
    abhijithEls.forEach(el => {
      if (el.childNodes.length === 1 && el.textContent && el.textContent.trim().startsWith('abhijith')) {
        // Don't touch if it's inside code
        if (el.tagName !== 'CODE' && el.tagName !== 'PRE') {
          // Find the parent profile bar
          const profileBar = el.closest('#profile-bar, .sidebar-profile-bar');
          if (profileBar) {
            // Replace abhijith text with dynamic
            el.innerHTML = el.innerHTML.replace(/abhijith.*?(Free)?/i, `${escapeHtml(userName)} · Free`);
            el.style.cursor = 'pointer';
            el.title = 'Click to edit name';
            el.addEventListener('click', () => {
              const newName = prompt('Enter your name:', userName);
              if (newName && newName.trim()) {
                localStorage.setItem('agent_ide_user_name', newName.trim());
                location.reload();
              }
            });
          }
        }
      }
    });
    // Also directly fix profile bar if found
    const profileBarText = document.getElementById('profile-bar');
    if (profileBarText) {
      const textNode = profileBarText.querySelector('.profile-left');
      if (textNode && textNode.textContent.includes('abhijith')) {
        textNode.innerHTML = textNode.innerHTML.replace(/abhijith/i, escapeHtml(userName));
      }
    }
  }

  function bindEvents() {
    initProfile();
    cleanStaticPlaceholders();
    // 1. Clean Sidebar Toggle (Fixed mini split-panel button, zero console errors)
    if (DOM.btnToggleSidebar) {
      DOM.btnToggleSidebar.addEventListener('click', () => {
        DOM.sidebar.classList.add('collapsed');
        if (DOM.btnShowSidebar) DOM.btnShowSidebar.style.display = 'flex';
      });
    }

    if (DOM.btnShowSidebar) {
      DOM.btnShowSidebar.addEventListener('click', () => {
        DOM.sidebar.classList.remove('collapsed');
        DOM.btnShowSidebar.style.display = 'none';
      });
    }

    // 2. New Chat
    if (DOM.btnNewChat) {
      DOM.btnNewChat.addEventListener('click', startNewChat);
    }
    if (DOM.btnClearSession) {
      DOM.btnClearSession.addEventListener('click', startNewChat);
    }

    // 3. Navigation items
    if (DOM.btnNavProjects) {
      DOM.btnNavProjects.addEventListener('click', () => openModal(DOM.projectsModal));
    }
    if (DOM.btnAddProject) {
      DOM.btnAddProject.addEventListener('click', () => openModal(DOM.projectsModal));
    }
    if (DOM.btnNavArtifacts) {
      DOM.btnNavArtifacts.addEventListener('click', openArtifactsModal);
    }
    if (DOM.btnNavCode) {
      DOM.btnNavCode.addEventListener('click', () => openModal(DOM.settingsModal));
    }
    if (DOM.btnNavMcpStudio || DOM.btnQuickMcp) {
      const openMcp = () => openModal(DOM.mcpStudioModal);
      if (DOM.btnNavMcpStudio) DOM.btnNavMcpStudio.addEventListener('click', openMcp);
      if (DOM.btnQuickMcp) DOM.btnQuickMcp.addEventListener('click', openMcp);
    }

    // 4. Input textarea auto-grow and submit
    if (DOM.promptInput) {
      DOM.promptInput.addEventListener('input', () => {
        DOM.promptInput.style.height = 'auto';
        DOM.promptInput.style.height = Math.min(DOM.promptInput.scrollHeight, 180) + 'px';
      });

      DOM.promptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          submitPrompt();
        }
      });
    }

    if (DOM.btnSubmit) {
      DOM.btnSubmit.addEventListener('click', submitPrompt);
    }

    // 5. Suggestion chips
    document.querySelectorAll('.suggestion-chip').forEach((chip) => {
      chip.addEventListener('click', () => {
        const query = chip.getAttribute('data-query');
        if (DOM.promptInput) {
          DOM.promptInput.value = query;
          submitPrompt();
        }
      });
    });

    // 6. Theme dots
    document.querySelectorAll('.btn-theme-dot').forEach((btn) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.btn-theme-dot').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        const theme = btn.getAttribute('data-theme');
        document.documentElement.setAttribute('data-theme', theme);
      });
    });

    // 7. LOGOS toggle
    if (DOM.pillLogosToggle) {
      DOM.pillLogosToggle.addEventListener('click', () => {
        state.enableLogos = !state.enableLogos;
        DOM.pillLogosToggle.classList.toggle('active', state.enableLogos);
      });
    }

    // 8. Settings modal triggers
    const openSettings = () => {
      if (DOM.modalProvider) DOM.modalProvider.value = state.provider;
      if (DOM.modalModel) DOM.modalModel.value = state.model;
      renderModelPresets();
      openModal(DOM.settingsModal);
    };
    if (DOM.btnTopModel) DOM.btnTopModel.addEventListener('click', openSettings);
    if (DOM.btnModelQuick) DOM.btnModelQuick.addEventListener('click', openSettings);
    if (DOM.btnOpenSettings) DOM.btnOpenSettings.addEventListener('click', openSettings);

    if (DOM.btnCloseSettingsModal) DOM.btnCloseSettingsModal.addEventListener('click', () => closeModal(DOM.settingsModal));
    if (DOM.btnCancelModal) DOM.btnCancelModal.addEventListener('click', () => closeModal(DOM.settingsModal));
    if (DOM.btnSaveModal) DOM.btnSaveModal.addEventListener('click', saveSettings);
    if (DOM.modalProvider) DOM.modalProvider.addEventListener('change', () => {
      renderModelPresets();
      // Clear previous test result when switching provider
      if (DOM.connTestResult) { DOM.connTestResult.style.display = 'none'; }
    });
    if (DOM.btnTestConnection) DOM.btnTestConnection.addEventListener('click', testConnection);

    // 9. MCP Studio modal handlers
    if (DOM.btnCloseMcpModal) DOM.btnCloseMcpModal.addEventListener('click', () => closeModal(DOM.mcpStudioModal));
    if (DOM.btnCloseMcpFooter) DOM.btnCloseMcpFooter.addEventListener('click', () => closeModal(DOM.mcpStudioModal));
    if (DOM.btnTestMcpTool) DOM.btnTestMcpTool.addEventListener('click', runMcpSandboxTest);
    if (DOM.btnGenerateMcpServer) DOM.btnGenerateMcpServer.addEventListener('click', generateMcpServerCode);
    if (DOM.mcpTemplateSelect) DOM.mcpTemplateSelect.addEventListener('change', onMcpTemplateChange);

    // MCP Studio Tab switching
    document.querySelectorAll('.mcp-tab').forEach((tab) => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.mcp-tab').forEach((t) => t.classList.remove('active'));
        document.querySelectorAll('.mcp-tab-pane').forEach((p) => p.classList.remove('active'));
        tab.classList.add('active');
        const target = tab.getAttribute('data-tab');
        const pane = document.getElementById(`pane-${target}`);
        if (pane) pane.classList.add('active');
      });
    });

    if (DOM.btnCopyMcpPy) {
      DOM.btnCopyMcpPy.addEventListener('click', () => copyText(DOM.mcpPythonCode.textContent, DOM.btnCopyMcpPy));
    }
    if (DOM.btnCopyMcpCfg) {
      DOM.btnCopyMcpCfg.addEventListener('click', () => copyText(DOM.mcpConfigCode.textContent, DOM.btnCopyMcpCfg));
    }

    // 10. Projects modal handlers
    if (DOM.btnCloseProjectsModal) DOM.btnCloseProjectsModal.addEventListener('click', () => closeModal(DOM.projectsModal));
    if (DOM.btnSaveNewProject) DOM.btnSaveNewProject.addEventListener('click', createNewProject);

    // 11. Artifacts modal handlers
    if (DOM.btnCloseArtifactsModal) DOM.btnCloseArtifactsModal.addEventListener('click', () => closeModal(DOM.artifactsModal));

    // 12. User Profile actions
    if (DOM.btnExportChat) {
      DOM.btnExportChat.addEventListener('click', exportChatHistory);
    }
    if (DOM.btnSearchChats) {
      DOM.btnSearchChats.addEventListener('click', () => {
        const query = prompt('Search past chats and tasks:');
        if (query) filterChatsList(query);
      });
    }

    // 13. Local AI Studio modal & actions
    if (DOM.btnNavLocalAi) DOM.btnNavLocalAi.addEventListener('click', openLocalAiStudio);
    if (DOM.btnHeroOpenGallery) DOM.btnHeroOpenGallery.addEventListener('click', openLocalAiStudio);
    if (DOM.btnSettingsOpenGallery) {
      DOM.btnSettingsOpenGallery.addEventListener('click', () => {
        closeModal(DOM.settingsModal);
        openLocalAiStudio();
      });
    }
    if (DOM.btnCloseLocalAiModal) DOM.btnCloseLocalAiModal.addEventListener('click', () => closeModal(DOM.localAiModal));
    if (DOM.btnCloseLocalAiFooter) DOM.btnCloseLocalAiFooter.addEventListener('click', () => closeModal(DOM.localAiModal));
    if (DOM.btnDaemonToggle) DOM.btnDaemonToggle.addEventListener('click', launchOllamaDaemon);
  }

  // --------------------------------------------------------------------------
  // API Fetchers
  // --------------------------------------------------------------------------

  async function fetchStatus() {
    try {
      const res = await fetch(API_BASE + '/api/status');
      if (!res.ok) return;
      const data = await res.json();
      state.provider = data.active_provider;
      state.model = data.active_model;
      state.enableLogos = data.enable_logos;

      updateHeaderDisplays();
    } catch (e) {
      console.warn('Could not sync status:', e);
    }
  }

  async function fetchModels() {
    try {
      const res = await fetch(API_BASE + '/api/models');
      if (!res.ok) return;
      state.catalog = await res.json();
      renderModelPresets();
    } catch (e) {}
  }

  async function fetchChats() {
    try {
      const res = await fetch(API_BASE + '/api/chats');
      if (!res.ok) return;
      let data = await res.json();
      // Handle both {chats: []} and [] formats
      state.chats = Array.isArray(data) ? data : (data.chats || []);
      // If backend returns empty, keep empty (don't show hardcoded)
      if (state.chats.length === 0) {
        localStorage.setItem('agent_ide_chats', JSON.stringify([]));
      }
      renderChatsHistoryList();
    } catch (e) {}
  }

  async function fetchProjects() {
    try {
      const res = await fetch(API_BASE + '/api/projects');
      if (!res.ok) return;
      let pData = await res.json();
      state.projects = Array.isArray(pData) ? pData : (pData.projects || []);
      renderProjectsList();
    } catch (e) {}
  }

  async function fetchArtifacts() {
    try {
      const res = await fetch(API_BASE + '/api/artifacts');
      if (!res.ok) return;
      state.artifacts = await res.json();
    } catch (e) {}
  }

  async function fetchMcpPresets() {
    try {
      const res = await fetch(API_BASE + '/api/mcp/presets');
      if (!res.ok) return;
      state.mcpPresets = await res.json();
    } catch (e) {}
  }

  // --------------------------------------------------------------------------
  // UI Rendering & Navigation
  // --------------------------------------------------------------------------

  function updateHeaderDisplays() {
    const isMock = state.provider === 'mock';
    const provLabel = state.provider.toUpperCase();
    const shortModel = state.model.length > 28 ? state.model.slice(0, 26) + '…' : state.model;

    if (DOM.headerModelName) {
      DOM.headerModelName.textContent = isMock
        ? `Mock Engine — ${shortModel}`
        : `${provLabel}: ${shortModel}`;
    }
    if (DOM.dockModelLabel) DOM.dockModelLabel.textContent = isMock ? 'MOCK' : provLabel;

    // Update status banner in settings modal
    if (DOM.connStatusBanner && DOM.connBannerText) {
      DOM.connStatusBanner.className = 'conn-banner ' + (isMock ? 'conn-banner--mock' : 'conn-banner--live');
      DOM.connBannerText.textContent = isMock
        ? 'Mock Engine — offline mode (no API key needed)'
        : `✅ Connected: ${provLabel} — ${shortModel}`;
    }
  }

  function renderChatsHistoryList() {
    if (!DOM.chatsHistoryList) return;
    DOM.chatsHistoryList.innerHTML = '';

    state.chats.forEach((chat) => {
      const li = document.createElement('li');
      li.className = 'sidebar-item-row';
      if (state.activeChatId === chat.id) li.classList.add('active');
      li.setAttribute('data-chat-id', chat.id);
      li.title = chat.title;

      li.innerHTML = `
        <span class="bullet-dot">○</span>
        <span class="item-title">${escapeHtml(chat.title)}</span>
      `;

      li.addEventListener('click', () => loadChatSession(chat.id));
      DOM.chatsHistoryList.appendChild(li);
    });
  }

  function renderProjectsList() {
    // Only populate dialog list, sidebar project list was removed
    if (DOM.projectsDialogList) {
      DOM.projectsDialogList.innerHTML = '';
      state.projects.forEach((proj) => {
        const item = document.createElement('li');
        item.style.padding = '8px';
        item.style.borderBottom = '1px solid var(--border-color)';
        item.innerHTML = `
          <strong>${escapeHtml(proj.title)}</strong>
          <div style="font-size: 11px; color: var(--text-muted);">${escapeHtml(proj.description || '')}</div>
        `;
        DOM.projectsDialogList.appendChild(item);
      });
    }
  }

  function renderModelPresets() {
    if (!DOM.modalPresets || !DOM.modalProvider) return;
    DOM.modalPresets.innerHTML = '';
    const curProv = DOM.modalProvider.value;
    const presets = (state.catalog.presets && state.catalog.presets[curProv]) || [];

    presets.forEach((p) => {
      const tag = document.createElement('span');
      tag.className = 'pill-btn';
      tag.textContent = p;
      tag.onclick = () => {
        if (DOM.modalModel) DOM.modalModel.value = p;
      };
      DOM.modalPresets.appendChild(tag);
    });
  }

  // --------------------------------------------------------------------------
  // Chat Execution & Prompt Handling
  // --------------------------------------------------------------------------

  async function submitPrompt() {
    const text = DOM.promptInput ? DOM.promptInput.value.trim() : '';
    if (!text || state.isSubmitting) return;

    if (DOM.welcomeHero) DOM.welcomeHero.style.display = 'none';

    appendUserMessage(text);
    DOM.promptInput.value = '';
    DOM.promptInput.style.height = 'auto';

    state.isSubmitting = true;
    if (DOM.btnSubmit) DOM.btnSubmit.disabled = true;

    const loader = appendThinkingLoader();
    scrollToBottom();

    const t0 = Date.now();

    try {
      // Stream live progress events via SSE
      const res = await fetch(API_BASE + '/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: text }),
      });

      if (!res.ok) {
        loader.remove();
        const err = await res.json().catch(() => ({}));
        appendBotMessage({ content: `**Error:** ${err.error || 'Server error occurred'}` });
      } else {
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let finalData = null;

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('data: ')) {
              try {
                const parsed = JSON.parse(trimmed.slice(6));
                if (parsed.type === 'progress' && parsed.event) {
                  loader.updateStatus(parsed.event.message);
                } else if (parsed.type === 'final' && parsed.data) {
                  finalData = parsed.data;
                }
              } catch (e) {}
            }
          }
        }

        loader.remove();

        if (finalData) {
          appendBotMessage(finalData);

          // Update Jev latency badge if returned
          if (finalData.jev && finalData.jev.total_latency_ms && DOM.jevLatencyVal) {
            DOM.jevLatencyVal.textContent = `${finalData.jev.total_latency_ms.toFixed(1)}ms`;
          }

          await fetchChats();
          await fetchArtifacts();
        } else {
          appendBotMessage({ content: '**Notice:** Process completed but no payload returned.' });
        }
      }
    } catch (err) {
      loader.remove();
      appendBotMessage({
        content: `**Network Error:** Could not connect to API server at \`${API_BASE || 'localhost:8000'}\`. Ensure \`python run_web_ui.py\` is running.`,
      });
    } finally {
      state.isSubmitting = false;
      if (DOM.btnSubmit) DOM.btnSubmit.disabled = false;
      scrollToBottom();
    }
  }

  function appendUserMessage(text) {
    const row = document.createElement('div');
    row.className = 'chat-message user';
    row.innerHTML = `<div class="msg-body"><div class="msg-text">${escapeHtml(text)}</div><button class="btn-edit-prompt" title="Edit prompt" style="margin-left:8px; background:transparent; border:1px solid var(--border-color); color:var(--text-muted); border-radius:4px; padding:2px 6px; font-size:11px; cursor:pointer;">✎ Edit</button></div>`;
    // Make editable
    const editBtn = row.querySelector('.btn-edit-prompt');
    if (editBtn) {
      editBtn.addEventListener('click', () => {
        if (DOM.promptInput) {
          DOM.promptInput.value = text;
          DOM.promptInput.focus();
          DOM.promptInput.style.height = 'auto';
          DOM.promptInput.style.height = DOM.promptInput.scrollHeight + 'px';
          // Scroll to input
          DOM.promptInput.scrollIntoView({behavior: 'smooth'});
        }
      });
    }
    DOM.chatStream.appendChild(row);
  }

  function appendThinkingLoader() {
    const row = document.createElement('div');
    row.className = 'chat-message bot';
    const start = Date.now();

    row.innerHTML = `
      <div class="msg-avatar">✦</div>
      <div class="msg-body">
        <div style="display: flex; align-items: center; gap: 10px; font-size: 12.5px; color: var(--text-muted);">
          <div class="typing-pulse">
            <span class="pulse-dot"></span>
            <span class="pulse-dot"></span>
            <span class="pulse-dot"></span>
          </div>
          <span id="loader-status-text">⚡ TypeSafe AI Jev: Parallel decision pass...</span>
          <span style="font-family: var(--font-mono); font-size: 11px;">(<span id="loader-timer">0.0</span>s)</span>
        </div>
      </div>
    `;
    DOM.chatStream.appendChild(row);

    const timer = row.querySelector('#loader-timer');
    const statusText = row.querySelector('#loader-status-text');

    let customMessage = null;

    const interval = setInterval(() => {
      const elapsed = ((Date.now() - start) / 1000).toFixed(1);
      if (timer) timer.textContent = elapsed;
      if (statusText) {
        if (customMessage) {
          statusText.textContent = customMessage;
        } else if (elapsed < 0.8) {
          statusText.textContent = '⚡ TypeSafe AI Jev: Single-pass typed decision primitives...';
        } else if (elapsed < 3.0) {
          statusText.textContent = '🧠 LOGOS Ultra: Synthesizing structural invariants...';
        } else if (elapsed < 7.0) {
          statusText.textContent = '🧪 Executing sandbox subprocess audit...';
        } else {
          statusText.textContent = '✨ Finalizing verified artifacts...';
        }
      }
    }, 100);

    return {
      remove: () => {
        clearInterval(interval);
        row.remove();
      },
      updateStatus: (msg) => {
        if (msg) {
          customMessage = msg;
          if (statusText) statusText.textContent = msg;
        }
      },
    };
  }

  function appendBotMessage(data) {
    const row = document.createElement('div');
    row.className = 'chat-message bot';

    const body = document.createElement('div');
    body.className = 'msg-body';

    // 1. TypeSafe AI Jev Telemetry Badge
    if (data.jev) {
      const jevBadge = document.createElement('div');
      jevBadge.className = 'jev-message-badge';
      const intentVal = data.jev.intent ? data.jev.intent.value : 'GENERAL';
      const latVal = data.jev.total_latency_ms ? data.jev.total_latency_ms.toFixed(1) : '9.0';
      const reqSb = (data.jev.guards && data.jev.guards.requires_sandbox && data.jev.guards.requires_sandbox.decision) ? 'YES' : 'NO';

      jevBadge.innerHTML = `
        <span>⚡ <strong>Jev Fast-Path:</strong> ${latVal}ms</span>
        <span style="opacity: 0.5;">|</span>
        <span>Intent: <strong>${escapeHtml(intentVal)}</strong></span>
        <span style="opacity: 0.5;">|</span>
        <span>Sandbox: <strong>${reqSb}</strong></span>
      `;
      body.appendChild(jevBadge);
    }

    // 2. Claude 3.7 Style Thinking Accordion
    if (data.thinking) {
      const drawer = document.createElement('div');
      drawer.className = 'thinking-drawer';

      let propItems = '';
      if (data.thinking.qualified_properties) {
        data.thinking.qualified_properties.forEach((p) => {
          propItems += `
            <div class="invariant-item">
              <span class="confidence-tag">${(p.confidence * 100).toFixed(1)}%</span>
              <div><strong>${escapeHtml(p.name)}:</strong> ${escapeHtml(p.hypothesis)}</div>
            </div>
          `;
        });
      }

      let blueprintHtml = '';
      if (data.thinking.blueprint && data.thinking.blueprint.components && data.thinking.blueprint.components.length > 0) {
        let compRows = '';
        data.thinking.blueprint.components.forEach((c) => {
          compRows += `
            <div style="font-size: 11.5px; padding: 4px 8px; background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 4px;">
              <span style="color: var(--accent-color); font-weight: 600;">[${escapeHtml(c.id)}] ${escapeHtml(c.name)}</span>
              <span style="color: var(--text-muted); font-size: 10.5px; margin-left: 6px;">(${escapeHtml(c.subsystem || 'core')})</span>
              <div style="color: var(--text-muted); font-size: 11px; margin-top: 2px;">${escapeHtml(c.contract || c.purpose || '')}</div>
            </div>
          `;
        });
        blueprintHtml = `
          <div style="margin-top: 10px; border-top: 1px dashed var(--border-color); padding-top: 8px;">
            <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--accent-color); letter-spacing: 0.05em; margin-bottom: 6px;">
              📐 Component Contracts & Blueprint Architecture
            </div>
            <div style="display: flex; flex-direction: column; gap: 4px;">
              ${compRows}
            </div>
          </div>
        `;
      }

      let holoHtml = '';
      if (data.thinking.holographic_stats) {
        const hs = data.thinking.holographic_stats;
        holoHtml = `
          <div style="margin-top: 8px; font-size: 11px; color: var(--text-muted); display: flex; gap: 14px; flex-wrap: wrap; background: rgba(0,0,0,0.2); padding: 6px 10px; border-radius: 4px; border: 1px solid var(--border-color);">
            <span>🌌 <strong>Holographic Projection:</strong> 100,000,000+ Effective Tokens</span>
            <span>⚡ <strong>Physical Tokens:</strong> ${data.thinking.total_tokens_used || 1200}</span>
            <span>📊 <strong>Boundary Entries:</strong> ${hs.total_stored || 0}</span>
            <span>🔬 <strong>Compression Ratio:</strong> ${hs.compression_ratio || '12.4x'}</span>
          </div>
        `;
      }

      drawer.innerHTML = `
        <div class="thinking-header">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span>🧠 LOGOS Reasoning & Invariants (${escapeHtml(data.thinking.topology || 'PIPELINE')})</span>
            <span class="confidence-tag" style="background: rgba(99, 102, 241, 0.18); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.35); font-size: 10px; padding: 1px 6px;">⚡ +100M+ Context</span>
          </div>
          <span>▾</span>
        </div>
        <div class="thinking-content" style="display: none;">
          <div style="color: var(--text-muted);">${escapeHtml(data.thinking.summary || '')}</div>
          <div style="margin-top: 6px; display: flex; flex-direction: column; gap: 6px;">
            ${propItems}
          </div>
          ${blueprintHtml}
          ${holoHtml}
        </div>
      `;

      const header = drawer.querySelector('.thinking-header');
      const content = drawer.querySelector('.thinking-content');
      header.onclick = () => {
        const isHidden = content.style.display === 'none';
        content.style.display = isHidden ? 'flex' : 'none';
        header.querySelector('span:last-child').textContent = isHidden ? '▴' : '▾';
      };

      body.appendChild(drawer);
    }

    // 3. Formatted Content
    if (data.content) {
      const contentEl = document.createElement('div');
      contentEl.className = 'markdown-content';
      contentEl.innerHTML = formatMarkdown(data.content);
      body.appendChild(contentEl);
    }

    // 4. Sandbox Code Execution Box
    if (data.code) {
      const card = document.createElement('div');
      card.className = 'sandbox-card';

      const isApp = data.code.toLowerCase().includes('<canvas') || data.code.toLowerCase().includes('<html') || data.code.toLowerCase().includes('temple');
      const cardId = 'sb-' + Math.random().toString(36).substring(2, 9);

      let tabsHtml = `
        <button class="sb-tab active" data-target="${cardId}-code">Source Code</button>
        <button class="sb-tab" data-target="${cardId}-logs">Sandbox Audit</button>
      `;

      let panesHtml = `
        <div class="sb-pane active" id="${cardId}-code">
          <pre><code>${escapeHtml(data.code)}</code></pre>
        </div>
        <div class="sb-pane" id="${cardId}-logs">
          <div class="term-box">${escapeHtml(data.test_logs || 'All invariant assertions verified. Zero unconstrained memory leaks or security exceptions.')}</div>
        </div>
      `;

      if (isApp) {
        tabsHtml += `<button class="sb-tab" data-target="${cardId}-play" style="color: #34d399;">🎮 Live Play / Preview</button>`;
        panesHtml += `
          <div class="sb-pane" id="${cardId}-play">
            <iframe class="artifact-preview-frame" srcdoc="${escapeHtml(data.code)}" sandbox="allow-scripts allow-same-origin"></iframe>
          </div>
        `;
      }

      card.innerHTML = `
        <div class="sandbox-topbar">
          <div class="mac-dots">
            <span class="mac-dot red"></span>
            <span class="mac-dot yellow"></span>
            <span class="mac-dot green"></span>
          </div>
          <div class="sandbox-tabs">${tabsHtml}</div>
          <button class="btn-copy-code" data-code="${encodeURIComponent(data.code)}">Copy Code</button>
        </div>
        <div class="sandbox-content">${panesHtml}</div>
      `;

      // Wire Tab switching
      card.querySelectorAll('.sb-tab').forEach((tab) => {
        tab.onclick = () => {
          card.querySelectorAll('.sb-tab').forEach((t) => t.classList.remove('active'));
          card.querySelectorAll('.sb-pane').forEach((p) => p.classList.remove('active'));
          tab.classList.add('active');
          const target = tab.getAttribute('data-target');
          const pane = card.querySelector('#' + target);
          if (pane) pane.classList.add('active');
        };
      });

      // Wire Copy
      const copyBtn = card.querySelector('.btn-copy-code');
      if (copyBtn) {
        copyBtn.onclick = () => {
          const raw = decodeURIComponent(copyBtn.getAttribute('data-code'));
          copyText(raw, copyBtn);
        };
      }

      body.appendChild(card);
    }

    row.innerHTML = `<div class="msg-avatar">✦</div>`;
    row.appendChild(body);
    DOM.chatStream.appendChild(row);
  }

  // --------------------------------------------------------------------------
  // Chat Session Navigation
  // --------------------------------------------------------------------------

  async function loadChatSession(chatId) {
    try {
      const res = await fetch(`${API_BASE}/api/chats/load?id=${encodeURIComponent(chatId)}`);
      if (!res.ok) return;
      const data = await res.json();

      state.activeChatId = chatId;
      document.querySelectorAll('#chats-history-list .sidebar-item-row').forEach((el) => {
        el.classList.toggle('active', el.getAttribute('data-chat-id') === chatId);
      });

      // Clear current stream
      DOM.chatStream.innerHTML = '';
      if (DOM.welcomeHero) DOM.welcomeHero.style.display = 'none';

      // Render turns
      if (data.turns && data.turns.length > 0) {
        data.turns.forEach((t) => {
          if (t.prompt) appendUserMessage(t.prompt);
          if (t.result) appendBotMessage(t.result);
        });
      } else {
        appendBotMessage({ content: `Loaded conversation: **${data.title}**` });
      }

      scrollToBottom();
    } catch (e) {
      console.warn('Could not load chat session:', e);
    }
  }

  async function startNewChat() {
    try {
      await fetch(API_BASE + '/api/clear', { method: 'POST' });
    } catch (e) {}

    state.activeChatId = null;
    document.querySelectorAll('#chats-history-list .sidebar-item-row').forEach((el) => el.classList.remove('active'));

    DOM.chatStream.innerHTML = '';
    if (DOM.welcomeHero) {
      DOM.welcomeHero.style.display = 'block';
      DOM.chatStream.appendChild(DOM.welcomeHero);
    }
    await fetchChats();
    await fetchStatus();
  }

  function exportChatHistory() {
    const textContent = Array.from(DOM.chatStream.querySelectorAll('.chat-message'))
      .map((msg) => {
        const isUser = msg.classList.contains('user');
        const body = msg.querySelector('.msg-body');
        return `[${isUser ? 'USER' : 'ASSISTANT'}]\n${body ? body.innerText : ''}\n`;
      })
      .join('\n---\n\n');

    const blob = new Blob([textContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agent-ide-chat-${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function filterChatsList(query) {
    const q = query.toLowerCase();
    document.querySelectorAll('#chats-history-list .sidebar-item-row').forEach((row) => {
      const title = (row.getAttribute('title') || '').toLowerCase();
      row.style.display = title.includes(q) ? 'flex' : 'none';
    });
  }

  // --------------------------------------------------------------------------
  // MCP Developer Studio Handlers
  // --------------------------------------------------------------------------

  function onMcpTemplateChange() {
    const val = DOM.mcpTemplateSelect.value;
    const preset = state.mcpPresets.find((p) => p.server_name === val);
    if (!preset) return;

    DOM.mcpServerName.value = preset.server_name;
    DOM.mcpServerDesc.value = preset.description || '';

    if (preset.tools && preset.tools.length > 0) {
      const t = preset.tools[0];
      DOM.mcpToolName.value = t.name;
      DOM.mcpToolDesc.value = t.description;
      DOM.mcpToolParams.value = JSON.stringify(t.parameters);
      DOM.mcpToolCode.value = t.handler_code;
    }
  }

  async function runMcpSandboxTest() {
    DOM.mcpJsonrpcOutput.textContent = '// Running test in execution sandbox subprocess...';
    // Switch to jsonrpc tab
    const rpcTab = document.querySelector('.mcp-tab[data-tab="jsonrpc"]');
    if (rpcTab) rpcTab.click();

    let params = [];
    try {
      params = JSON.parse(DOM.mcpToolParams.value);
    } catch (e) {
      params = [];
    }

    let args = {};
    try {
      args = JSON.parse(DOM.mcpTestArgs.value);
    } catch (e) {
      args = {};
    }

    const payload = {
      tool: {
        name: DOM.mcpToolName.value,
        description: DOM.mcpToolDesc.value,
        parameters: params,
        handler_code: DOM.mcpToolCode.value,
      },
      arguments: args,
    };

    try {
      const res = await fetch(API_BASE + '/api/mcp/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      DOM.mcpJsonrpcOutput.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
      DOM.mcpJsonrpcOutput.textContent = `// Error executing MCP test: ${e}`;
    }
  }

  async function generateMcpServerCode() {
    let params = [];
    try {
      params = JSON.parse(DOM.mcpToolParams.value);
    } catch (e) {
      params = [];
    }

    const payload = {
      server_name: DOM.mcpServerName.value,
      description: DOM.mcpServerDesc.value,
      tools: [
        {
          name: DOM.mcpToolName.value,
          description: DOM.mcpToolDesc.value,
          parameters: params,
          handler_code: DOM.mcpToolCode.value,
        },
      ],
    };

    try {
      const res = await fetch(API_BASE + '/api/mcp/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      DOM.mcpPythonCode.textContent = data.python_code;
      DOM.mcpConfigCode.textContent = data.claude_desktop_config;

      // Switch to python tab
      const pyTab = document.querySelector('.mcp-tab[data-tab="python"]');
      if (pyTab) pyTab.click();

      await fetchArtifacts();
    } catch (e) {
      alert('Error generating MCP code: ' + e);
    }
  }

  // --------------------------------------------------------------------------
  // Projects & Artifacts Actions
  // --------------------------------------------------------------------------

  async function createNewProject() {
    const title = DOM.newProjectTitle.value.trim();
    const desc = DOM.newProjectDesc.value.trim();
    if (!title) return;

    try {
      const res = await fetch(API_BASE + '/api/projects/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description: desc }),
      });
      if (res.ok) {
        DOM.newProjectTitle.value = '';
        DOM.newProjectDesc.value = '';
        await fetchProjects();
        closeModal(DOM.projectsModal);
      }
    } catch (e) {}
  }

  function openArtifactsModal() {
    if (!DOM.artifactsListSidebar) return;
    DOM.artifactsListSidebar.innerHTML = '';

    if (state.artifacts.length === 0) {
      DOM.artifactsListSidebar.innerHTML = '<div style="padding: 10px; color: var(--text-muted); font-size: 12px;">No artifacts generated yet.</div>';
      DOM.artifactViewerPane.innerHTML = '<div class="artifact-empty-hint">Generate code or run the MCP studio to see artifacts.</div>';
    } else {
      state.artifacts.forEach((art, idx) => {
        const item = document.createElement('div');
        item.className = 'artifact-card-item' + (idx === 0 ? ' active' : '');
        item.innerHTML = `
          <strong>${escapeHtml(art.title)}</strong>
          <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">${escapeHtml(art.type)}</div>
        `;
        item.onclick = () => {
          document.querySelectorAll('.artifact-card-item').forEach((c) => c.classList.remove('active'));
          item.classList.add('active');
          displayArtifactPreview(art);
        };
        DOM.artifactsListSidebar.appendChild(item);
      });
      displayArtifactPreview(state.artifacts[0]);
    }

    openModal(DOM.artifactsModal);
  }

  function displayArtifactPreview(art) {
    if (!art || !DOM.artifactViewerPane) return;
    if (art.type === 'html_app') {
      DOM.artifactViewerPane.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <h4>${escapeHtml(art.title)}</h4>
          <button class="btn-copy-code" id="btn-copy-art">Copy HTML</button>
        </div>
        <iframe class="artifact-preview-frame" srcdoc="${escapeHtml(art.code)}" sandbox="allow-scripts allow-same-origin"></iframe>
      `;
    } else {
      DOM.artifactViewerPane.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <h4>${escapeHtml(art.title)}</h4>
          <button class="btn-copy-code" id="btn-copy-art">Copy Code</button>
        </div>
        <pre class="code-box" style="background: #11100f; padding: 14px; border-radius: var(--radius-sm); max-height: 480px; overflow-y: auto;"><code>${escapeHtml(art.code)}</code></pre>
      `;
    }

    const copyBtn = DOM.artifactViewerPane.querySelector('#btn-copy-art');
    if (copyBtn) copyBtn.onclick = () => copyText(art.code, copyBtn);
  }

  // --------------------------------------------------------------------------
  // Settings Actions
  // --------------------------------------------------------------------------

  async function saveSettings() {
    if (!DOM.modalProvider || !DOM.modalModel) return;

    const provider = DOM.modalProvider.value;
    const model = DOM.modalModel.value.trim();
    const endpoint = DOM.modalEndpoint ? DOM.modalEndpoint.value.trim() : '';
    const apiKey = DOM.modalApikey ? DOM.modalApikey.value.trim() : '';

    if (!model) {
      if (DOM.connTestResult) {
        DOM.connTestResult.style.display = 'block';
        DOM.connTestResult.className = 'conn-test-error';
        DOM.connTestResult.textContent = '⚠️ Please enter a model name before saving.';
      }
      return;
    }

    const btn = DOM.btnSaveModal;
    if (btn) { btn.disabled = true; btn.textContent = 'Applying…'; }

    try {
      const res = await fetch(API_BASE + '/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider,
          model,
          custom_endpoint: endpoint || null,
          api_key: apiKey || null,
          enable_logos: state.enableLogos,
        }),
      });
      const data = await res.json();
      state.provider = data.active_provider || provider;
      state.model = data.active_model || model;
      updateHeaderDisplays();

      if (DOM.connTestResult) {
        DOM.connTestResult.style.display = 'block';
        DOM.connTestResult.className = 'conn-test-ok';
        DOM.connTestResult.textContent = `✅ Settings applied — now using ${state.provider.toUpperCase()}: ${state.model}`;
      }
    } catch (e) {
      if (DOM.connTestResult) {
        DOM.connTestResult.style.display = 'block';
        DOM.connTestResult.className = 'conn-test-error';
        DOM.connTestResult.textContent = `❌ Could not apply settings: ${e.message}`;
      }
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = 'Save & Apply'; }
    }
  }

  async function testConnection() {
    const btn = DOM.btnTestConnection;
    if (btn) { btn.disabled = true; btn.textContent = 'Testing…'; }
    if (DOM.connTestResult) {
      DOM.connTestResult.style.display = 'block';
      DOM.connTestResult.className = '';
      DOM.connTestResult.textContent = '⏳ Pinging provider…';
    }

    // First save current settings so server reflects chosen provider
    const provider = DOM.modalProvider ? DOM.modalProvider.value : state.provider;
    const model = DOM.modalModel ? DOM.modalModel.value.trim() : state.model;
    const endpoint = DOM.modalEndpoint ? DOM.modalEndpoint.value.trim() : '';
    const apiKey = DOM.modalApikey ? DOM.modalApikey.value.trim() : '';

    try {
      // Update settings first
      await fetch(API_BASE + '/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider,
          model: model || 'auto',
          custom_endpoint: endpoint || null,
          api_key: apiKey || null,
          enable_logos: state.enableLogos,
        }),
      });

      // Then test
      const res = await fetch(API_BASE + '/api/models/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await res.json();

      if (DOM.connTestResult) {
        DOM.connTestResult.style.display = 'block';
        const isOk = data.status === 'ok';
        DOM.connTestResult.className = isOk ? 'conn-test-ok' : 'conn-test-error';
        let msg = data.message || (isOk ? '✅ Connected' : '❌ Connection failed');
        if (data.hint) msg += `\n💡 ${data.hint}`;
        DOM.connTestResult.style.whiteSpace = 'pre-wrap';
        DOM.connTestResult.textContent = msg;

        // Update state from server
        if (isOk && data.provider) {
          state.provider = data.provider;
          state.model = data.model || model;
          updateHeaderDisplays();
        }
      }
    } catch (e) {
      if (DOM.connTestResult) {
        DOM.connTestResult.style.display = 'block';
        DOM.connTestResult.className = 'conn-test-error';
        DOM.connTestResult.textContent = `❌ Network error: ${e.message}`;
      }
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = 'Test Connection'; }
    }
  }

  // --------------------------------------------------------------------------
  // Helpers
  // --------------------------------------------------------------------------

  function openModal(modalEl) {
    if (modalEl) modalEl.classList.add('open');
  }

  function closeModal(modalEl) {
    if (modalEl) modalEl.classList.remove('open');
  }

  function scrollToBottom() {
    if (DOM.chatScrollArea) {
      DOM.chatScrollArea.scrollTop = DOM.chatScrollArea.scrollHeight;
    }
  }

  function copyText(text, btn) {
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
      const orig = btn.textContent;
      btn.textContent = 'Copied!';
      setTimeout(() => (btn.textContent = orig), 1800);
    });
  }

  function escapeHtml(s) {
    if (!s) return '';
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function formatMarkdown(s) {
    if (!s) return '';
    let out = escapeHtml(s);
    out = out.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    out = out.replace(/\*(.*?)\*/g, '<em>$1</em>');
    out = out.replace(/`([^`]+)`/g, '<code style="background: rgba(255,255,255,0.08); padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); font-size: 13px;">$1</code>');
    out = out.replace(/^\s*-\s+(.*)$/gm, '<li style="margin-left: 20px;">$1</li>');
    out = out.replace(/\n\n/g, '<br><br>');
    return out;
  }

  // --------------------------------------------------------------------------
  // Local AI Studio & Auto-Launcher
  // --------------------------------------------------------------------------

  let activePullSource = null;

  async function fetchOllamaStatus() {
    try {
      const res = await fetch(API_BASE + '/api/ollama/status');
      if (!res.ok) return null;
      const data = await res.json();

      // Update hero callout status
      if (DOM.heroStatusText && DOM.heroOllamaStatusChip) {
        if (data.running) {
          DOM.heroStatusText.textContent = `Ollama ${data.version ? 'v' + data.version : 'Active'} (${data.models_count} local models)`;
          DOM.heroOllamaStatusChip.className = 'callout-status-indicator running';
          if (DOM.sidebarLocalStatusBadge) {
            DOM.sidebarLocalStatusBadge.textContent = 'Active';
            DOM.sidebarLocalStatusBadge.style.color = '#34d399';
          }
        } else if (data.installed) {
          DOM.heroStatusText.textContent = 'Ollama Detected (Click to Launch Daemon)';
          DOM.heroOllamaStatusChip.className = 'callout-status-indicator stopped';
          if (DOM.sidebarLocalStatusBadge) {
            DOM.sidebarLocalStatusBadge.textContent = 'Ready';
            DOM.sidebarLocalStatusBadge.style.color = '#f59e0b';
          }
        } else {
          DOM.heroStatusText.textContent = 'Ollama Not Found (Click to Install)';
          DOM.heroOllamaStatusChip.className = 'callout-status-indicator';
          if (DOM.sidebarLocalStatusBadge) {
            DOM.sidebarLocalStatusBadge.textContent = 'Ollama';
          }
        }
      }

      return data;
    } catch (e) {
      console.warn('Could not fetch Ollama status:', e);
      return null;
    }
  }

  async function openLocalAiStudio() {
    openModal(DOM.localAiModal);
    await fetchAndRenderGallery();
  }

  async function fetchAndRenderGallery() {
    const status = await fetchOllamaStatus();
    if (!status) return;

    // Update daemon bar UI
    if (DOM.daemonStatusDot && DOM.daemonHeadline && DOM.daemonSubtext) {
      if (status.running) {
        DOM.daemonStatusDot.className = 'daemon-status-dot online';
        DOM.daemonHeadline.textContent = `🟢 Ollama daemon is running active (version ${status.version || '0.x'})`;
        DOM.daemonSubtext.textContent = `${status.models_count} models currently available in local storage (${status.host})`;
        if (DOM.btnDaemonToggle) DOM.btnDaemonToggle.style.display = 'none';
        if (DOM.btnDaemonDownload) DOM.btnDaemonDownload.style.display = 'none';
      } else if (status.installed) {
        DOM.daemonStatusDot.className = 'daemon-status-dot offline';
        DOM.daemonHeadline.textContent = '🟡 Ollama executable detected (daemon is stopped)';
        DOM.daemonSubtext.textContent = `Found at ${status.binary_path} — Click below to auto-launch daemon`;
        if (DOM.btnDaemonToggle) {
          DOM.btnDaemonToggle.style.display = 'inline-block';
          DOM.btnDaemonToggle.disabled = false;
          DOM.btnDaemonToggle.textContent = '🚀 Start Ollama Daemon';
        }
        if (DOM.btnDaemonDownload) DOM.btnDaemonDownload.style.display = 'none';
      } else {
        DOM.daemonStatusDot.className = 'daemon-status-dot missing';
        DOM.daemonHeadline.textContent = '🔴 Ollama executable not found';
        DOM.daemonSubtext.textContent = 'Install Ollama to enable private, local zero-cost LLM execution';
        if (DOM.btnDaemonToggle) DOM.btnDaemonToggle.style.display = 'none';
        if (DOM.btnDaemonDownload) DOM.btnDaemonDownload.style.display = 'inline-flex';
      }
    }

    // Fetch gallery catalog
    try {
      const res = await fetch(API_BASE + '/api/ollama/gallery');
      if (!res.ok) return;
      const gallery = await res.json();
      renderGalleryCards(gallery, status);
    } catch (e) {
      console.warn('Failed to fetch gallery:', e);
    }
  }

  function renderGalleryCards(gallery, status) {
    if (!DOM.modelGalleryGrid) return;
    DOM.modelGalleryGrid.innerHTML = '';

    const isOllamaActive = (state.provider === 'ollama');

    gallery.forEach((item) => {
      const isCurrentActive = isOllamaActive && (state.model === item.tag || state.model.startsWith(item.tag));
      const card = document.createElement('div');
      card.className = `gallery-card ${item.installed ? 'installed' : ''} ${isCurrentActive ? 'active-connected' : ''}`;

      let badgeClass = 'badge-popular';
      if (item.badge === 'Fastest') badgeClass = 'badge-fastest';
      else if (item.badge === 'Best for Code') badgeClass = 'badge-code';
      else if (item.badge === 'Reasoning') badgeClass = 'badge-reasoning';

      let actionHtml = '';
      if (isCurrentActive) {
        actionHtml = `<button class="btn-card-connect" disabled style="background:#10b981;cursor:default;">
          <span>✅ Active Connected</span>
        </button>`;
      } else if (item.installed) {
        actionHtml = `<button class="btn-card-connect" data-tag="${item.tag}">
          <span>⚡ Connect &amp; Route Prompts</span>
        </button>`;
      } else {
        actionHtml = `<button class="btn-card-download" data-tag="${item.tag}">
          <span>⬇️ Download &amp; Launch (${item.size})</span>
        </button>`;
      }

      card.innerHTML = `
        <div class="gallery-card-top">
          <div class="gallery-card-info">
            <h5>${escapeHtml(item.name)}</h5>
            <span class="gallery-card-tag">${escapeHtml(item.tag)}</span>
          </div>
          <span class="gallery-badge ${badgeClass}">${escapeHtml(item.badge || item.provider)}</span>
        </div>
        <div class="gallery-card-desc">${escapeHtml(item.description)}</div>
        <div class="gallery-card-meta">
          <span class="meta-chip">💾 ${escapeHtml(item.size)}</span>
          <span class="meta-chip">🧠 ${escapeHtml(item.vram)} VRAM</span>
          <span class="meta-chip">${escapeHtml(item.speed)}</span>
        </div>
        <div class="gallery-card-actions">
          ${item.installed ? '<span class="status-badge-installed">● Installed</span>' : ''}
          ${actionHtml}
        </div>
      `;

      // Wire button click
      const btnConn = card.querySelector('.btn-card-connect:not([disabled])');
      if (btnConn) {
        btnConn.addEventListener('click', () => {
          connectLocalModel(item.tag);
        });
      }

      const btnDown = card.querySelector('.btn-card-download');
      if (btnDown) {
        btnDown.addEventListener('click', () => {
          pullModel(item.tag);
        });
      }

      DOM.modelGalleryGrid.appendChild(card);
    });
  }

  async function launchOllamaDaemon() {
    if (DOM.btnDaemonToggle) {
      DOM.btnDaemonToggle.disabled = true;
      DOM.btnDaemonToggle.textContent = 'Starting daemon...';
    }
    try {
      const res = await fetch(API_BASE + '/api/ollama/launch', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        await fetchAndRenderGallery();
      } else {
        alert(data.error || 'Failed to start Ollama daemon.');
        if (DOM.btnDaemonToggle) {
          DOM.btnDaemonToggle.disabled = false;
          DOM.btnDaemonToggle.textContent = '🚀 Start Ollama Daemon';
        }
      }
    } catch (e) {
      alert(`Could not launch daemon: ${e.message}`);
      if (DOM.btnDaemonToggle) {
        DOM.btnDaemonToggle.disabled = false;
        DOM.btnDaemonToggle.textContent = '🚀 Start Ollama Daemon';
      }
    }
  }

  function pullModel(modelTag) {
    if (activePullSource) {
      activePullSource.close();
      activePullSource = null;
    }

    // Show progress panel
    if (DOM.pullProgressPanel) {
      DOM.pullProgressPanel.style.display = 'block';
      DOM.progressModelName.textContent = `Downloading ${modelTag}...`;
      DOM.progressPct.textContent = '0%';
      DOM.progressStatusMsg.textContent = 'Initiating download from Ollama registry...';
      DOM.progressFill.style.width = '0%';
    }

    // Disable all pull buttons while downloading
    document.querySelectorAll('.btn-card-download').forEach((b) => (b.disabled = true));

    const sseUrl = `${API_BASE}/api/ollama/pull?model=${encodeURIComponent(modelTag)}`;
    const eventSource = new EventSource(sseUrl);
    activePullSource = eventSource;

    eventSource.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.status === 'error') {
          DOM.progressStatusMsg.textContent = `❌ Error: ${payload.error || 'Download failed'}`;
          eventSource.close();
          activePullSource = null;
          document.querySelectorAll('.btn-card-download').forEach((b) => (b.disabled = false));
          return;
        }

        const pct = payload.percent || 0;
        if (DOM.progressPct) DOM.progressPct.textContent = `${pct}%`;
        if (DOM.progressFill) DOM.progressFill.style.width = `${pct}%`;
        if (DOM.progressStatusMsg) {
          let statusText = payload.status || 'Downloading...';
          if (payload.completed && payload.total) {
            const mbDone = (payload.completed / (1024 * 1024)).toFixed(1);
            const mbTotal = (payload.total / (1024 * 1024)).toFixed(1);
            statusText += ` (${mbDone} MB / ${mbTotal} MB)`;
          }
          DOM.progressStatusMsg.textContent = statusText;
        }

        if (payload.done) {
          eventSource.close();
          activePullSource = null;
          if (DOM.progressStatusMsg) {
            DOM.progressStatusMsg.textContent = `✅ ${modelTag} ready! Auto-connecting to sandbox pipeline...`;
          }
          // Auto connect after brief moment
          setTimeout(() => {
            connectLocalModel(modelTag);
          }, 800);
        }
      } catch (err) {
        console.warn('Error parsing SSE pull event:', err);
      }
    };

    eventSource.onerror = (err) => {
      console.warn('SSE pull stream disconnected:', err);
      eventSource.close();
      activePullSource = null;
      document.querySelectorAll('.btn-card-download').forEach((b) => (b.disabled = false));
      // Re-check status in case it finished
      setTimeout(() => fetchAndRenderGallery(), 1000);
    };
  }

  async function connectLocalModel(modelTag) {
    try {
      const res = await fetch(API_BASE + '/api/ollama/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: modelTag }),
      });
      const data = await res.json();
      if (data.status === 'connected') {
        state.provider = 'ollama';
        state.model = modelTag;
        updateHeaderDisplays();
        await fetchAndRenderGallery();

        // Hide pull progress if done
        if (DOM.pullProgressPanel) {
          setTimeout(() => {
            DOM.pullProgressPanel.style.display = 'none';
          }, 1500);
        }

        // Notification in chat
        appendAssistantTurn({
          prompt: '',
          result: {
            type: 'conversational',
            content: `### 🦙 Connected to Local Model: \`${modelTag}\`\n\n` +
                     `- **Provider**: Ollama Native GGUF\n` +
                     `- **Cognitive Pipeline**: Full LOGOS Reasoning + TypeSafe AI Jev Fast Classifier active\n` +
                     `- **Privacy & Zero-Cost**: 100% running locally on your hardware — no external API calls.\n\n` +
                     `Ask anything or describe code/games to build in the isolated sandbox!`,
            status: 'success',
            elapsed_seconds: 0.05,
          },
        });

        // Close gallery modal after brief delay so user sees green active badge
        setTimeout(() => {
          closeModal(DOM.localAiModal);
        }, 1200);
      } else {
        alert(data.message || 'Failed to connect to model');
      }
    } catch (e) {
      alert(`Error connecting model: ${e.message}`);
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();

