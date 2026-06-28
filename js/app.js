/**
 * Offline ATS — Main Application Logic
 * Orchestrates UI, PDF extraction, parsing, DB, and matching.
 */

// ─── PDF.js setup ───
pdfjsLib.GlobalWorkerOptions.workerSrc =
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

// ─── State ───
let currentTab = 'upload';
let deferredInstallPrompt = null;

// ─── Init ───
document.addEventListener('DOMContentLoaded', async () => {
  await DB.openDB();
  setupTabs();
  setupUpload();
  setupSearch();
  setupMatch();
  updateStats();
  updateOnlineStatus();

  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);

  // PWA install prompt
  window.addEventListener('beforeinstallprompt', e => {
    e.preventDefault();
    deferredInstallPrompt = e;
    document.getElementById('install-banner').classList.add('visible');
  });

  document.getElementById('install-btn')?.addEventListener('click', async () => {
    if (deferredInstallPrompt) {
      deferredInstallPrompt.prompt();
      await deferredInstallPrompt.userChoice;
      deferredInstallPrompt = null;
      document.getElementById('install-banner').classList.remove('visible');
    }
  });

  document.getElementById('dismiss-install')?.addEventListener('click', () => {
    document.getElementById('install-banner').classList.remove('visible');
  });
});

// ─── Online / Offline Status ───
function updateOnlineStatus() {
  const badge = document.getElementById('status-badge');
  if (navigator.onLine) {
    badge.className = 'status-badge status-online';
    badge.innerHTML = '<span class="status-dot"></span> Online';
  } else {
    badge.className = 'status-badge status-offline';
    badge.innerHTML = '<span class="status-dot"></span> Offline';
  }
}

// ─── Stats ───
async function updateStats() {
  const count = await DB.getCandidateCount();
  document.getElementById('stat-candidates').textContent = count;

  const all = await DB.getAllCandidates();
  const skillSet = new Set();
  all.forEach(c => (c.skills || []).forEach(s => skillSet.add(s.toLowerCase())));
  document.getElementById('stat-skills').textContent = skillSet.size;
  document.getElementById('stat-resumes').textContent = count;
}

// ─── Tabs ───
function setupTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      switchTab(tab);
    });
  });
}

function switchTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.toggle('active', p.id === `panel-${tab}`));

  if (tab === 'candidates') renderCandidates();
  if (tab === 'search') renderCandidates('search');
}

// ─── Upload ───
function setupUpload() {
  const zone = document.getElementById('upload-zone');
  const input = document.getElementById('file-input');

  zone.addEventListener('click', () => input.click());
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
  });
  input.addEventListener('change', () => handleFiles(input.files));
}

async function handleFiles(fileList) {
  const log = document.getElementById('process-log');
  log.classList.add('visible');
  log.innerHTML = '';

  for (const file of fileList) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      addLog(log, `⚠️ Skipped ${file.name} — only PDF supported`, 'error');
      continue;
    }

    addLog(log, `📄 Reading ${file.name}...`, 'info');

    try {
      // Extract text from PDF
      const text = await extractPDFText(file);
      if (!text || text.trim().length < 20) {
        addLog(log, `❌ ${file.name} — could not extract text`, 'error');
        continue;
      }

      addLog(log, `🤖 Parsing resume fields...`, 'info');
      const parsed = ResumeParser.parseResume(text);

      // Store in IndexedDB
      const id = await DB.addCandidate(parsed);
      addLog(log, `✅ ${parsed.name || file.name} saved (ID: ${id})`, 'success');
    } catch (err) {
      addLog(log, `❌ ${file.name} — ${err.message}`, 'error');
    }
  }

  await updateStats();
  toast('Resumes processed successfully!', 'success');

  // Clear input
  document.getElementById('file-input').value = '';
}

function addLog(container, message, type) {
  const div = document.createElement('div');
  div.className = `log-entry ${type}`;
  div.textContent = message;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

async function extractPDFText(file) {
  const arrayBuffer = await file.arrayBuffer();
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
  let fullText = '';
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();
    const strings = content.items.map(item => item.str);
    fullText += strings.join(' ') + '\n';
  }
  return fullText;
}

// ─── Render Candidates ───
async function renderCandidates(mode = 'all') {
  let candidates;
  const container = mode === 'search'
    ? document.getElementById('search-results')
    : document.getElementById('candidates-list');

  if (mode === 'search') {
    const query = document.getElementById('search-input').value.trim();
    candidates = query ? await DB.searchCandidates(query) : await DB.getAllCandidates();
  } else {
    candidates = await DB.getAllCandidates();
  }

  if (candidates.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="icon">📭</div>
        <h3>No candidates found</h3>
        <p>${mode === 'search' ? 'Try a different search term' : 'Upload resumes to get started'}</p>
      </div>`;
    return;
  }

  container.innerHTML = '<div class="candidates-grid">' +
    candidates.map(c => buildCandidateCard(c)).join('') +
    '</div>';

  // Attach delete handlers
  container.querySelectorAll('.btn-delete').forEach(btn => {
    btn.addEventListener('click', async () => {
      await DB.deleteCandidate(Number(btn.dataset.id));
      await updateStats();
      renderCandidates(mode);
      toast('Candidate removed', 'info');
    });
  });
}

function buildCandidateCard(c, score = null) {
  const initials = (c.name || '?').split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
  const scoreHTML = score !== null ? `
    <div class="score-badge ${score >= 70 ? 'score-high' : score >= 40 ? 'score-medium' : 'score-low'}">
      ${score}%
    </div>` : '';

  const skillsHTML = (c.skills || []).slice(0, 8).map(s =>
    `<span class="skill-tag">${s}</span>`
  ).join('');

  const eduHTML = (c.education || []).map(e =>
    `<li>${e.degree}${e.college ? ' — ' + e.college : ''}</li>`
  ).join('');

  const expHTML = (c.experience || []).map(e =>
    `<li>${e.role}${e.company ? ' @ ' + e.company : ''}${e.years ? ' (' + e.years + ' yrs)' : ''}</li>`
  ).join('');

  const projHTML = (c.projects || []).map(p => `<li>${p}</li>`).join('');

  return `
    <div class="candidate-card">
      ${scoreHTML}
      <div class="card-header">
        <div class="avatar">${initials}</div>
        <div>
          <div class="card-name">${c.name || 'Unknown'}</div>
          ${c.email ? `<div class="card-email">📧 ${c.email}</div>` : ''}
          ${c.phone ? `<div class="card-phone">📱 ${c.phone}</div>` : ''}
        </div>
      </div>
      ${skillsHTML ? `<div class="skills-list">${skillsHTML}</div>` : ''}
      ${eduHTML ? `<div class="card-section"><h4>🎓 Education</h4><ul>${eduHTML}</ul></div>` : ''}
      ${expHTML ? `<div class="card-section"><h4>💼 Experience</h4><ul>${expHTML}</ul></div>` : ''}
      ${projHTML ? `<div class="card-section"><h4>🚀 Projects</h4><ul>${projHTML}</ul></div>` : ''}
      <div class="card-actions">
        <button class="btn btn-danger btn-delete" data-id="${c.id}">🗑 Remove</button>
      </div>
    </div>`;
}

// ─── Search ───
function setupSearch() {
  const input = document.getElementById('search-input');
  let timeout;
  input?.addEventListener('input', () => {
    clearTimeout(timeout);
    timeout = setTimeout(() => renderCandidates('search'), 300);
  });
}

// ─── Match ───
function setupMatch() {
  document.getElementById('match-btn')?.addEventListener('click', async () => {
    const jdText = document.getElementById('jd-input').value.trim();
    if (!jdText) {
      toast('Please enter a job description', 'error');
      return;
    }

    const candidates = await DB.getAllCandidates();
    if (candidates.length === 0) {
      toast('No candidates to match against. Upload resumes first!', 'error');
      return;
    }

    const ranked = Matcher.rankCandidates(jdText, candidates);
    const container = document.getElementById('match-results');
    container.innerHTML = '<div class="candidates-grid">' +
      ranked.map(c => buildCandidateCard(c, c.finalScorePct)).join('') +
      '</div>';

    // Attach delete handlers for matched results too
    container.querySelectorAll('.btn-delete').forEach(btn => {
      btn.addEventListener('click', async () => {
        await DB.deleteCandidate(Number(btn.dataset.id));
        await updateStats();
        document.getElementById('match-btn').click(); // re-run match
        toast('Candidate removed', 'info');
      });
    });
  });

  document.getElementById('clear-all-btn')?.addEventListener('click', async () => {
    if (confirm('Delete ALL candidates? This cannot be undone.')) {
      await DB.deleteAllCandidates();
      await updateStats();
      renderCandidates();
      toast('All candidates cleared', 'info');
    }
  });
}

// ─── Toast Notifications ───
function toast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  el.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;
  container.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateX(100%)';
    el.style.transition = '0.4s ease';
    setTimeout(() => el.remove(), 400);
  }, 3500);
}
