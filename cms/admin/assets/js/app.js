import {
  api,
  Auth,
  clearTokens,
  getTokens,
  getUser,
  setTokens,
  setUser,
} from './api.js';
import {
  bindPublish,
  bindRoles,
  bindSecurity,
  bindTranslationForm,
  bindWebhooks,
  viewPublish,
  viewRoles,
  viewSecurity,
  viewTranslationForm,
  viewTranslations,
  viewWebhooks,
} from './features.js';

const app = document.getElementById('app');
const toastStack = document.getElementById('toast-stack');
const commandDialog = document.getElementById('commandPalette');
const commandInput = document.getElementById('commandInput');
const commandResults = document.getElementById('commandResults');

let quillEditor = null;
let activityChart = null;
let routeSeq = 0;
let globalUiBound = false;

function currentHash() {
  const h = location.hash.trim();
  return h || '#/dashboard';
}

function isEditorHash(hash) {
  return /^#\/(pages|posts)\/(new|edit\/[^/?#]+)$/.test(hash);
}

function navIsActive(itemHash, hash) {
  if (itemHash === '#/dashboard') return hash === '#/dashboard';
  return hash === itemHash || hash.startsWith(`${itemHash}/`);
}

function destroyQuill() {
  const mount = document.getElementById('editor');
  if (mount) mount.innerHTML = '';
  quillEditor = null;
}

const NAV = [
  { section: 'Overview', items: [{ hash: '#/dashboard', label: 'Dashboard', icon: '◉' }] },
  {
    section: 'Content',
    items: [
      { hash: '#/pages', label: 'Pages', icon: '▤' },
      { hash: '#/posts', label: 'Posts', icon: '✎' },
      { hash: '#/media', label: 'Media library', icon: '▣' },
    ],
  },
  {
    section: 'Engagement',
    items: [{ hash: '#/contacts', label: 'Inquiries', icon: '✉' }],
  },
  {
    section: 'Deploy',
    items: [{ hash: '#/publish', label: 'Static publish', icon: '⬆' }],
  },
  {
    section: 'System',
    items: [
      { hash: '#/users', label: 'Users', icon: '◎' },
      { hash: '#/roles', label: 'Role matrix', icon: '◈' },
      { hash: '#/webhooks', label: 'Webhooks', icon: '⇄' },
      { hash: '#/translations', label: 'Translations', icon: '文' },
      { hash: '#/security', label: '2FA security', icon: '🔐' },
      { hash: '#/settings', label: 'Site settings', icon: '⚙' },
    ],
  },
];

const COMMANDS = [
  { label: 'Go to Dashboard', hash: '#/dashboard' },
  { label: 'Go to Pages', hash: '#/pages' },
  { label: 'Go to Posts', hash: '#/posts' },
  { label: 'Go to Media', hash: '#/media' },
  { label: 'Go to Inquiries', hash: '#/contacts' },
  { label: 'Go to Users', hash: '#/users' },
  { label: 'Go to Settings', hash: '#/settings' },
  { label: 'Static publish', hash: '#/publish' },
  { label: 'Webhooks', hash: '#/webhooks' },
  { label: 'Role matrix', hash: '#/roles' },
  { label: 'Translations', hash: '#/translations' },
  { label: '2FA security', hash: '#/security' },
  { label: 'Create new page', hash: '#/pages/new' },
  { label: 'Create new post', hash: '#/posts/new' },
  { label: 'Toggle theme', action: 'toggle-theme' },
  { label: 'Sign out', action: 'logout' },
];

function toast(message, type = 'info') {
  const el = document.createElement('div');
  el.className = `toast ${type === 'error' ? 'error' : ''}`;
  el.textContent = message;
  toastStack.appendChild(el);
  setTimeout(() => el.remove(), 4200);
}

function esc(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/"/g, '&quot;');
}

function statusBadge(status) {
  const cls = status === 'published' ? 'badge-published' : 'badge-draft';
  return `<span class="badge ${cls}">${esc(status)}</span>`;
}

function renderLogin() {
  app.innerHTML = `
    <div class="login-screen">
      <form class="login-card" id="loginForm">
        <div class="login-brand">
          <div class="login-brand-mark">SF</div>
          <div>
            <strong>SEO With Faiz</strong>
            <span style="display:block;color:var(--adm-muted);font-size:0.8rem;">Command Center</span>
          </div>
        </div>
        <h1>Sign in</h1>
        <p>Enterprise CMS for seowithfaiz.com — secured with JWT and role-based access.</p>
        <div class="field">
          <label for="email">Email</label>
          <input id="email" name="email" type="email" required autocomplete="username">
        </div>
        <div class="field">
          <label for="password">Password</label>
          <input id="password" name="password" type="password" required autocomplete="current-password">
        </div>
        <button class="btn btn-primary btn-block" type="submit">Enter command center</button>
        <div id="totpStep" class="field" hidden>
          <label for="totpCode">Authenticator code</label>
          <input id="totpCode" name="totp" inputmode="numeric" autocomplete="one-time-code" placeholder="6-digit code">
        </div>
        <p style="margin:1rem 0 0;font-size:0.78rem;color:var(--adm-muted);">
          Default credentials are set in <code class="kbd">cms/backend/.env</code> on first deploy.
        </p>
      </form>
    </div>`;
  const form = document.getElementById('loginForm');
  let pendingTotp = null;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const totpStep = document.getElementById('totpStep');
    const totpCode = document.getElementById('totpCode')?.value?.trim();
    try {
      const result = await Auth.login(fd.get('email'), fd.get('password'), totpCode, pendingTotp);
      if (result.requires_totp) {
        pendingTotp = result.totp_token;
        totpStep.hidden = false;
        document.getElementById('email').readOnly = true;
        document.getElementById('password').readOnly = true;
        form.querySelector('button[type="submit"]').textContent = 'Verify authenticator code';
        document.getElementById('totpCode')?.focus();
        toast('Enter the 6-digit code from your authenticator app');
        return;
      }
      if (result.access_token) setTokens(result.access_token, result.refresh_token);
      const me = await Auth.me();
      setUser(me);
      toast('Welcome back, ' + me.full_name);
      location.hash = '#/dashboard';
      await route();
    } catch (err) {
      toast(err.message, 'error');
    }
  });
}

function renderShell(contentHtml) {
  const user = getUser();
  const initials = (user?.full_name || 'A')
    .split(' ')
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
  const hash = currentHash();
  const navHtml = NAV.map(
    (group) => `
    <div class="nav-section">${esc(group.section)}</div>
    ${group.items
      .map(
        (item) => `
      <a class="nav-link ${navIsActive(item.hash, hash) ? 'active' : ''}" href="${item.hash}">
        <span aria-hidden="true">${item.icon}</span> ${esc(item.label)}
      </a>`
      )
      .join('')}`
  ).join('');

  app.innerHTML = `
    <div class="shell">
      <aside class="sidebar">
        <div class="sidebar-brand">SEO With Faiz<span>Command Center v1</span></div>
        <nav>${navHtml}</nav>
        <div style="margin-top:auto;padding:0.5rem;">
          <button type="button" class="btn btn-ghost btn-block" id="logoutBtn">Sign out</button>
        </div>
      </aside>
      <div class="main">
        <header class="topbar">
          <div class="topbar-search">
            <input type="search" id="globalSearch" placeholder="Search or press Ctrl+K" readonly>
          </div>
          <div class="topbar-actions">
            <button type="button" class="btn btn-secondary" id="themeBtn" title="Toggle theme">◐</button>
            <button type="button" class="btn btn-secondary" id="cmdBtn"><span class="kbd">Ctrl+K</span></button>
            <div class="user-chip">
              <div class="user-avatar">${esc(initials)}</div>
              <div>
                <div style="font-size:0.82rem;font-weight:600;">${esc(user?.full_name)}</div>
                <div style="font-size:0.7rem;color:var(--adm-muted);">${esc(user?.role)}</div>
              </div>
            </div>
          </div>
        </header>
        <main class="content" id="viewRoot">${contentHtml}</main>
      </div>
    </div>`;

  document.getElementById('logoutBtn').onclick = async () => {
    await Auth.logout();
    clearTokens();
    location.hash = '';
    boot();
  };
  document.getElementById('themeBtn').onclick = toggleTheme;
  document.getElementById('cmdBtn').onclick = openCommandPalette;
  document.getElementById('globalSearch').onclick = openCommandPalette;
  bindCommandPalette();
}

function toggleTheme() {
  const html = document.documentElement;
  const next = html.getAttribute('data-admin-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-admin-theme', next);
  localStorage.setItem('cms_theme', next);
}

async function viewDashboard() {
  const [stats, activity] = await Promise.all([
    api('/dashboard/stats'),
    api('/dashboard/activity'),
  ]);
  const activityHtml = activity.length
    ? activity
        .map(
          (a) => `
      <div class="activity-item">
        <time>${new Date(a.created_at).toLocaleString()}</time>
        <div><strong>${esc(a.user_name || 'System')}</strong> ${esc(a.action)} ${esc(a.resource_type)}${
            a.resource_id ? ` <code class="kbd">${esc(a.resource_id.slice(0, 8))}</code>` : ''
          }</div>
      </div>`
        )
        .join('')
    : '<p class="empty">No activity yet.</p>';

  return `
    <div class="page-head">
      <div>
        <h1>Dashboard</h1>
        <p>Operational overview for seowithfaiz.com</p>
      </div>
      <button class="btn btn-primary" type="button" onclick="location.hash='#/posts/new'">New post</button>
    </div>
    <div class="stats-grid">
      <div class="stat-card"><div class="label">Published pages</div><div class="value">${stats.pages_published}</div></div>
      <div class="stat-card"><div class="label">Published posts</div><div class="value">${stats.posts_published}</div></div>
      <div class="stat-card"><div class="label">New inquiries</div><div class="value">${stats.contacts_new}</div></div>
      <div class="stat-card"><div class="label">Drafts</div><div class="value">${stats.drafts_total}</div></div>
      <div class="stat-card"><div class="label">Media assets</div><div class="value">${stats.media_total}</div></div>
      <div class="stat-card"><div class="label">Team users</div><div class="value">${stats.users_total}</div></div>
    </div>
    <div class="grid-2">
      <section class="panel">
        <div class="panel-head"><strong>Content pipeline</strong></div>
        <div class="panel-body"><canvas id="pipelineChart" height="120"></canvas></div>
      </section>
      <section class="panel">
        <div class="panel-head"><strong>Recent activity</strong></div>
        <div class="panel-body">${activityHtml}</div>
      </section>
    </div>`;
}

function afterDashboardPaint() {
  const canvas = document.getElementById('pipelineChart');
  if (!canvas || !window.Chart) return;
  if (activityChart) activityChart.destroy();
  api('/dashboard/stats').then((s) => {
    activityChart = new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: ['Pages live', 'Posts live', 'Drafts', 'New leads'],
        datasets: [
          {
            data: [s.pages_published, s.posts_published, s.drafts_total, s.contacts_new],
            backgroundColor: ['#2dd4bf', '#38bdf8', '#f59e0b', '#a78bfa'],
            borderWidth: 0,
          },
        ],
      },
      options: { plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } } },
    });
  });
}

async function viewPagesList() {
  const pages = await api('/pages');
  const rows = pages.length
    ? pages
        .map(
          (p) => `<tr>
        <td><strong>${esc(p.title)}</strong><br><span style="color:var(--adm-muted);font-size:0.75rem;">/${esc(p.slug)} · ${esc(p.locale || 'en')}</span></td>
        <td>${statusBadge(p.status)}</td>
        <td>${new Date(p.updated_at).toLocaleDateString()}</td>
        <td><a class="btn btn-secondary" href="#/pages/edit/${p.id}">Edit</a></td>
      </tr>`
        )
        .join('')
    : `<tr><td colspan="4" class="empty">No pages yet.</td></tr>`;

  return `
    <div class="page-head">
      <div><h1>Pages</h1><p>Marketing pages, landers, and structured site content.</p></div>
      <a class="btn btn-primary" href="#/pages/new">New page</a>
    </div>
    <section class="panel"><div class="panel-body" style="padding:0;">
      <table class="data-table"><thead><tr><th>Title</th><th>Status</th><th>Updated</th><th></th></tr></thead><tbody>${rows}</tbody></table>
    </div></section>`;
}

async function viewPostsList() {
  const posts = await api('/posts');
  const rows = posts.length
    ? posts
        .map(
          (p) => `<tr>
        <td><strong>${esc(p.title)}</strong><br><span style="color:var(--adm-muted);font-size:0.75rem;">/${esc(p.slug)} · ${esc(p.locale || 'en')}</span></td>
        <td>${statusBadge(p.status)}</td>
        <td>${(p.tags || []).map((t) => `<span class="badge badge-draft">${esc(t)}</span>`).join(' ')}</td>
        <td><a class="btn btn-secondary" href="#/posts/edit/${p.id}">Edit</a></td>
      </tr>`
        )
        .join('')
    : `<tr><td colspan="4" class="empty">No posts yet.</td></tr>`;

  return `
    <div class="page-head">
      <div><h1>Posts</h1><p>Blog articles with SEO metadata and revision history.</p></div>
      <a class="btn btn-primary" href="#/posts/new">New post</a>
    </div>
    <section class="panel"><div class="panel-body" style="padding:0;">
      <table class="data-table"><thead><tr><th>Title</th><th>Status</th><th>Tags</th><th></th></tr></thead><tbody>${rows}</tbody></table>
    </div></section>`;
}

const LOCALE_OPTIONS = ['en', 'es', 'fr', 'de', 'ar', 'hi'];

function localeSelect(name, value = 'en') {
  return `<select name="${name}">${LOCALE_OPTIONS.map((l) => `<option value="${l}" ${value === l ? 'selected' : ''}>${l}</option>`).join('')}</select>`;
}

function editorForm(type, item = {}) {
  const isPost = type === 'post';
  return `
    <div class="page-head">
      <div><h1>${item.id ? 'Edit' : 'Create'} ${isPost ? 'post' : 'page'}</h1></div>
      <a class="btn btn-secondary" href="#/${isPost ? 'posts' : 'pages'}">Back</a>
    </div>
    <form id="contentForm" class="editor-layout">
      <div class="editor-main panel">
        <div class="panel-body">
          <div class="field"><label>Title</label><input name="title" required value="${esc(item.title || '')}"></div>
          <div class="field"><label>Slug</label><input name="slug" required value="${esc(item.slug || '')}" pattern="[a-z0-9-]+"></div>
          <div class="field"><label>Locale</label>${localeSelect('locale', item.locale || 'en')}</div>
          <div class="field"><label>Excerpt</label><textarea name="excerpt" rows="2">${esc(item.excerpt || '')}</textarea></div>
          <label>Body</label>
          <div id="editor"></div>
        </div>
      </div>
      <aside class="panel">
        <div class="panel-body">
          <div class="field"><label>Status</label>
            <select name="status">
              ${['draft', 'review', 'scheduled', 'published', 'archived']
                .map((s) => `<option value="${s}" ${item.status === s ? 'selected' : ''}>${s}</option>`)
                .join('')}
            </select>
          </div>
          <div class="field"><label>SEO title</label><input name="seo_title" value="${esc(item.seo_title || '')}"></div>
          <div class="field"><label>SEO description</label><textarea name="seo_description" rows="3">${esc(item.seo_description || '')}</textarea></div>
          ${
            isPost
              ? `<div class="field"><label>Primary keyword</label><input name="primary_keyword" value="${esc(item.primary_keyword || '')}"></div>
                 <div class="field"><label>Intro hook</label><input name="intro_hook" value="${esc(item.intro_hook || '')}"></div>
                 <div class="field"><label>Tags (comma separated)</label><input name="tags" value="${esc((item.tags || []).join(', '))}"></div>`
              : `<div class="field"><label>Template</label><input name="template" value="${esc(item.template || 'default')}"></div>
                 <div class="field"><label>Publish path</label><input name="publish_path" placeholder="pages/cms/about.html" value="${esc(item.publish_path || '')}"></div>`
          }
          <button class="btn btn-primary btn-block" type="submit">Save</button>
          ${item.id ? `<button class="btn btn-danger btn-block" type="button" id="deleteContent" style="margin-top:0.5rem;">Delete</button>` : ''}
        </div>
      </aside>
    </form>`;
}

function mountQuill(html = '') {
  const el = document.getElementById('editor');
  if (!el || !window.Quill) return;
  destroyQuill();
  const mount = document.createElement('div');
  mount.id = 'editor';
  el.replaceWith(mount);
  quillEditor = new Quill(mount, {
    theme: 'snow',
    modules: {
      toolbar: [
        [{ header: [2, 3, false] }],
        ['bold', 'italic', 'underline', 'link'],
        [{ list: 'ordered' }, { list: 'bullet' }],
        ['blockquote', 'code-block'],
        ['clean'],
      ],
    },
  });
  quillEditor.root.innerHTML = html || '';
}

async function bindContentForm(type, id) {
  const form = document.getElementById('contentForm');
  if (!form) return;
  const endpoint = type === 'post' ? '/posts' : '/pages';
  form.onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const payload = Object.fromEntries(fd.entries());
    payload.body_html = quillEditor?.root.innerHTML || '';
    if (type === 'post' && payload.tags) {
      payload.tags = payload.tags.split(',').map((t) => t.trim()).filter(Boolean);
    }
    try {
      if (id) await api(`${endpoint}/${id}`, { method: 'PATCH', body: JSON.stringify(payload) });
      else await api(endpoint, { method: 'POST', body: JSON.stringify(payload) });
      toast('Saved successfully');
      location.hash = `#/${type === 'post' ? 'posts' : 'pages'}`;
      route();
    } catch (err) {
      toast(err.message, 'error');
    }
  };
  const del = document.getElementById('deleteContent');
  if (del) {
    del.onclick = async () => {
      if (!confirm('Delete permanently?')) return;
      await api(`${endpoint}/${id}`, { method: 'DELETE' });
      toast('Deleted');
      location.hash = `#/${type === 'post' ? 'posts' : 'pages'}`;
      route();
    };
  }
}

async function viewMedia() {
  const items = await api('/media');
  const grid = items.length
    ? items
        .map(
          (m) => `
      <article class="media-card">
        ${m.mime_type.startsWith('image/') ? `<img src="${esc(m.url)}" alt="${esc(m.alt_text || '')}">` : `<div class="empty">PDF</div>`}
        <div class="meta">${esc(m.filename)}</div>
      </article>`
        )
        .join('')
    : '<p class="empty">Upload brand assets, OG images, and content media.</p>';

  return `
    <div class="page-head">
      <div><h1>Media library</h1><p>Centralized asset management with CDN-ready paths.</p></div>
      <label class="btn btn-primary">Upload<input type="file" id="mediaUpload" hidden accept="image/*,application/pdf"></label>
    </div>
    <section class="panel"><div class="panel-body media-grid" id="mediaGrid">${grid}</div></section>`;
}

function afterMediaPaint() {
  const input = document.getElementById('mediaUpload');
  if (!input) return;
  input.onchange = async () => {
    const file = input.files?.[0];
    if (!file) return;
    const fd = new FormData();
    fd.append('file', file);
    fd.append('folder', 'content');
    try {
      await api('/media/upload', { method: 'POST', body: fd });
      toast('Uploaded');
      route();
    } catch (err) {
      toast(err.message, 'error');
    }
  };
}

async function viewContacts() {
  const rows = await api('/submissions');
  const table = rows.length
    ? rows
        .map(
          (r) => `<tr>
        <td><strong>${esc(r.name)}</strong><br>${esc(r.email)}</td>
        <td><a href="${esc(r.website)}" target="_blank" rel="noopener">${esc(r.website)}</a></td>
        <td>${esc(r.region)}</td>
        <td><span class="badge badge-${r.status === 'new' ? 'new' : 'draft'}">${esc(r.status)}</span></td>
        <td>${new Date(r.created_at).toLocaleString()}</td>
        <td><button class="btn btn-secondary" data-mark="${r.id}">Mark read</button></td>
      </tr>
      <tr><td colspan="6" style="font-size:0.85rem;color:var(--adm-muted);">${esc(r.goal)}</td></tr>`
        )
        .join('')
    : `<tr><td colspan="6" class="empty">No inquiries yet.</td></tr>`;

  return `
    <div class="page-head"><div><h1>Inquiries</h1><p>Contact form submissions from the live site.</p></div></div>
    <section class="panel"><div class="panel-body" style="padding:0;">
      <table class="data-table"><thead><tr><th>Contact</th><th>Website</th><th>Market</th><th>Status</th><th>Received</th><th></th></tr></thead>
      <tbody>${table}</tbody></table>
    </div></section>`;
}

function afterContactsPaint() {
  document.querySelectorAll('[data-mark]').forEach((btn) => {
    btn.onclick = async () => {
      await api(`/submissions/${btn.dataset.mark}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: 'read' }),
      });
      toast('Marked as read');
      route();
    };
  });
}

async function viewUsers() {
  const users = await api('/users');
  const rows = users
    .map(
      (u) => `<tr>
      <td>${esc(u.full_name)}<br><span style="color:var(--adm-muted)">${esc(u.email)}</span></td>
      <td><span class="badge badge-published">${esc(u.role)}</span></td>
      <td>${u.is_active ? 'Active' : 'Disabled'}</td>
      <td>${u.last_login_at ? new Date(u.last_login_at).toLocaleString() : '—'}</td>
    </tr>`
    )
    .join('');
  return `
    <div class="page-head"><div><h1>Users & roles</h1><p>RBAC — superadmin, admin, editor, viewer.</p></div></div>
    <section class="panel"><div class="panel-body" style="padding:0;">
      <table class="data-table"><thead><tr><th>User</th><th>Role</th><th>Status</th><th>Last login</th></tr></thead><tbody>${rows}</tbody></table>
    </div></section>`;
}

async function viewSettings() {
  const settings = await api('/settings');
  const rows = settings
    .map(
      (s) => `<tr>
      <td><code class="kbd">${esc(s.key)}</code></td>
      <td><pre style="margin:0;white-space:pre-wrap;font-size:0.78rem;">${esc(JSON.stringify(s.value, null, 0))}</pre></td>
      <td>${new Date(s.updated_at).toLocaleDateString()}</td>
    </tr>`
    )
    .join('');
  return `
    <div class="page-head"><div><h1>Site settings</h1><p>Global configuration, brand, and deployment metadata.</p></div></div>
    <section class="panel"><div class="panel-body" style="padding:0;">
      <table class="data-table"><thead><tr><th>Key</th><th>Value</th><th>Updated</th></tr></thead><tbody>${rows || '<tr><td colspan="3" class="empty">No settings</td></tr>'}</tbody></table>
    </div></section>
    <p style="color:var(--adm-muted);font-size:0.85rem;margin-top:1rem;">Hostinger deploy: run <code class="kbd">python cms/run.py</code> on VPS, proxy HTTPS to port 8780, set MySQL in <code class="kbd">DATABASE_URL</code>.</p>`;
}

async function route() {
  if (!getTokens().access) {
    renderLogin();
    return;
  }

  const seq = ++routeSeq;
  const hash = location.hash || '#/dashboard';
  let html = '';
  try {
    if (hash === '#/dashboard') {
      html = await viewDashboard();
    } else if (hash === '#/pages') {
      html = await viewPagesList();
    } else if (hash === '#/posts') {
      html = await viewPostsList();
    } else if (hash === '#/media') {
      html = await viewMedia();
    } else if (hash === '#/contacts') {
      html = await viewContacts();
    } else if (hash === '#/users') {
      html = await viewUsers();
    } else if (hash === '#/settings') {
      html = await viewSettings();
    } else if (hash === '#/publish') {
      html = await viewPublish();
    } else if (hash === '#/webhooks') {
      html = await viewWebhooks();
    } else if (hash === '#/roles') {
      html = await viewRoles();
    } else if (hash === '#/translations') {
      html = await viewTranslations();
    } else if (hash === '#/translations/new') {
      html = viewTranslationForm();
    } else if (hash === '#/security') {
      html = await viewSecurity();
    } else if (hash === '#/pages/new') {
      html = editorForm('page');
    } else if (hash.startsWith('#/pages/edit/')) {
      const id = hash.split('/').pop();
      const item = await api(`/pages/${id}`);
      html = editorForm('page', item);
    } else if (hash === '#/posts/new') {
      html = editorForm('post');
    } else if (hash.startsWith('#/posts/edit/')) {
      const id = hash.split('/').pop();
      const item = await api(`/posts/${id}`);
      html = editorForm('post', item);
    } else {
      html = await viewDashboard();
    }
  } catch (err) {
    if (String(err.message).includes('Session') || String(err.message).includes('authenticated')) {
      clearTokens();
      renderLogin();
      return;
    }
    html = `<p class="empty">${esc(err.message)}</p>`;
  }

  if (seq !== routeSeq) return;

  renderShell(html);

  if (seq !== routeSeq) return;

  if (hash === '#/dashboard') afterDashboardPaint();
  if (hash === '#/media') afterMediaPaint();
  if (hash === '#/contacts') afterContactsPaint();
  if (hash === '#/publish') bindPublish(toast);
  if (hash === '#/webhooks') bindWebhooks(route, toast);
  if (hash === '#/roles') bindRoles(toast);
  if (hash === '#/translations/new') bindTranslationForm(route, toast);
  if (hash === '#/security') bindSecurity(toast);
  if (isEditorHash(hash)) {
    const type = hash.startsWith('#/posts') ? 'post' : 'page';
    const id = hash.includes('/edit/') ? hash.split('/').pop() : null;
    let body = '';
    if (id) {
      const item = await api(`/${type === 'post' ? 'posts' : 'pages'}/${id}`);
      if (seq !== routeSeq) return;
      body = item.body_html;
    }
    mountQuill(body);
    bindContentForm(type, id);
  }
}

function openCommandPalette() {
  commandDialog.showModal();
  commandInput.value = '';
  renderCommands('');
  commandInput.focus();
}

function renderCommands(q) {
  const query = q.toLowerCase();
  const items = COMMANDS.filter((c) => c.label.toLowerCase().includes(query));
  commandResults.innerHTML = items
    .map(
      (c, i) => `<li><button type="button" data-idx="${i}">${esc(c.label)}</button></li>`
    )
    .join('');
  commandResults.querySelectorAll('button').forEach((btn) => {
    btn.onclick = () => {
      const cmd = items[Number(btn.dataset.idx)];
      commandDialog.close();
      if (cmd.hash) location.hash = cmd.hash;
      else if (cmd.action === 'toggle-theme') toggleTheme();
      else if (cmd.action === 'logout') document.getElementById('logoutBtn')?.click();
      route();
    };
  });
}

function bindCommandPalette() {
  commandInput.oninput = () => renderCommands(commandInput.value);
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      openCommandPalette();
    }
  });
}

async function boot() {
  const theme = localStorage.getItem('cms_theme') || 'dark';
  document.documentElement.setAttribute('data-admin-theme', theme);
  if (!getTokens().access) {
    renderLogin();
    return;
  }
  if (!getUser()) {
    try {
      setUser(await Auth.me());
    } catch {
      clearTokens();
      renderLogin();
      return;
    }
  }
  await route();
}

window.addEventListener('hashchange', () => {
  if (getTokens().access) route();
});

window.addEventListener('pageshow', (event) => {
  if (event.persisted && getTokens().access) route();
});

if (!location.hash) location.replace('#/dashboard');

boot();
