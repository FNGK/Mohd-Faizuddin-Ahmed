import { api } from './api.js';

export async function viewPublish() {
  return `
    <div class="page-head">
      <div><h1>Static publish</h1><p>Export published CMS content to live HTML files in this repository.</p></div>
    </div>
    <section class="panel">
      <div class="panel-body">
        <div class="field"><label>Locale</label>
          <select id="publishLocale"><option value="en">en</option><option value="es">es</option><option value="fr">fr</option><option value="de">de</option><option value="ar">ar</option><option value="hi">hi</option></select>
        </div>
        <p style="color:var(--adm-muted);font-size:0.88rem;">Writes <code class="kbd">blog/posts/*.html</code>, rebuilds <code class="kbd">blog/index.html</code> cards, and exports CMS pages.</p>
        <button class="btn btn-primary" type="button" id="runPublish">Publish to site files</button>
        <pre id="publishResult" class="kbd" style="margin-top:1rem;white-space:pre-wrap;display:block;padding:1rem;background:var(--adm-surface-2);border-radius:10px;"></pre>
      </div>
    </section>`;
}

export function bindPublish(toast) {
  document.getElementById('runPublish')?.addEventListener('click', async () => {
    const locale = document.getElementById('publishLocale')?.value || 'en';
    const pre = document.getElementById('publishResult');
    try {
      pre.textContent = 'Publishing…';
      const res = await api('/publish/static', {
        method: 'POST',
        body: JSON.stringify({ locale }),
      });
      pre.textContent = JSON.stringify(res, null, 2);
      toast('Published to static HTML');
    } catch (err) {
      pre.textContent = err.message;
      toast(err.message, 'error');
    }
  });
}

export async function viewWebhooks() {
  const hooks = await api('/webhooks');
  const rows = hooks.length
    ? hooks
        .map(
          (h) => `<tr>
        <td><strong>${h.name}</strong><br><span style="color:var(--adm-muted);font-size:0.75rem;">${h.url}</span></td>
        <td>${(h.events || []).map((e) => `<span class="badge badge-new">${e}</span>`).join(' ')}</td>
        <td>${h.is_active ? 'Active' : 'Off'}</td>
        <td><button class="btn btn-danger" data-del-wh="${h.id}">Delete</button></td>
      </tr>`
        )
        .join('')
    : '<tr><td colspan="4" class="empty">No webhooks configured.</td></tr>';

  return `
    <div class="page-head">
      <div><h1>Webhooks</h1><p>POST signed JSON to Zapier, Slack, or custom endpoints on CMS events.</p></div>
    </div>
    <section class="panel" style="margin-bottom:1rem;">
      <div class="panel-head"><strong>Add webhook</strong></div>
      <div class="panel-body">
        <form id="webhookForm" class="grid-2">
          <div class="field"><label>Name</label><input name="name" required placeholder="Zapier contact"></div>
          <div class="field"><label>URL</label><input name="url" type="url" required placeholder="https://hooks.zapier.com/..."></div>
          <div class="field" style="grid-column:1/-1;"><label>Events (comma separated)</label>
            <input name="events" value="contact.created,publish.completed,content.published,user.login">
          </div>
          <button class="btn btn-primary" type="submit">Create webhook</button>
        </form>
      </div>
    </section>
    <section class="panel"><div class="panel-body" style="padding:0;">
      <table class="data-table"><thead><tr><th>Endpoint</th><th>Events</th><th>Status</th><th></th></tr></thead><tbody>${rows}</tbody></table>
    </div></section>`;
}

export function bindWebhooks(route, toast) {
  document.getElementById('webhookForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      await api('/webhooks', {
        method: 'POST',
        body: JSON.stringify({
          name: fd.get('name'),
          url: fd.get('url'),
          events: String(fd.get('events'))
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean),
        }),
      });
      toast('Webhook created');
      location.hash = '#/webhooks';
      route();
    } catch (err) {
      toast(err.message, 'error');
    }
  });
  document.querySelectorAll('[data-del-wh]').forEach((btn) => {
    btn.onclick = async () => {
      if (!confirm('Delete webhook?')) return;
      await api(`/webhooks/${btn.dataset.delWh}`, { method: 'DELETE' });
      toast('Deleted');
      route();
    };
  });
}

export async function viewRoles() {
  const [catalog, perms] = await Promise.all([
    api('/roles/catalog'),
    api('/roles/permissions'),
  ]);
  const rows = catalog.permissions
    .map((perm) => {
      const cells = catalog.roles
        .map((role) => {
          const match = perms.find((p) => p.role === role && p.permission === perm);
          const allowed = match ? match.allowed : false;
          return `<td><input type="checkbox" data-role="${role}" data-perm="${perm}" ${allowed ? 'checked' : ''}></td>`;
        })
        .join('');
      return `<tr><td><code class="kbd">${perm}</code></td>${cells}</tr>`;
    })
    .join('');

  return `
    <div class="page-head"><div><h1>Roles & permissions</h1><p>Fine-grained RBAC matrix (superadmin only to save).</p></div>
      <button class="btn btn-primary" type="button" id="saveRoles">Save matrix</button>
    </div>
    <section class="panel"><div class="panel-body" style="padding:0;overflow:auto;">
      <table class="data-table"><thead><tr><th>Permission</th>${catalog.roles.map((r) => `<th>${r}</th>`).join('')}</tr></thead><tbody>${rows}</tbody></table>
    </div></section>`;
}

export function bindRoles(toast) {
  document.getElementById('saveRoles')?.addEventListener('click', async () => {
    const updates = [];
    document.querySelectorAll('input[data-role][data-perm]').forEach((el) => {
      updates.push({
        role: el.dataset.role,
        permission: el.dataset.perm,
        allowed: el.checked,
      });
    });
    try {
      await api('/roles/permissions', { method: 'PUT', body: JSON.stringify(updates) });
      toast('Permissions saved');
    } catch (err) {
      toast(err.message, 'error');
    }
  });
}

export async function viewTranslations() {
  const { supported, default: def } = await api('/translations/locales');
  const items = await api('/translations');
  const rows = items.length
    ? items
        .map(
          (t) => `<tr>
        <td>${t.locale}</td><td>${t.content_type}</td><td>${t.title}</td>
        <td>${t.status}</td><td><code class="kbd">${t.parent_id.slice(0, 8)}</code></td>
      </tr>`
        )
        .join('')
    : '<tr><td colspan="5" class="empty">No translations yet. Create one linked to a page/post ID.</td></tr>';

  return `
    <div class="page-head"><div><h1>Translations</h1><p>Multi-language content overlays (default: ${def}). Supported: ${supported.join(', ')}</p></div>
      <a class="btn btn-primary" href="#/translations/new">New translation</a>
    </div>
    <section class="panel"><div class="panel-body" style="padding:0;">
      <table class="data-table"><thead><tr><th>Locale</th><th>Type</th><th>Title</th><th>Status</th><th>Parent</th></tr></thead><tbody>${rows}</tbody></table>
    </div></section>`;
}

export function viewTranslationForm() {
  return `
    <div class="page-head"><div><h1>New translation</h1></div><a class="btn btn-secondary" href="#/translations">Back</a></div>
    <form id="translationForm" class="panel"><div class="panel-body">
      <div class="field"><label>Content type</label><select name="content_type"><option value="post">post</option><option value="page">page</option></select></div>
      <div class="field"><label>Parent content ID</label><input name="parent_id" required placeholder="UUID from Pages/Posts"></div>
      <div class="field"><label>Locale</label><input name="locale" value="es" required></div>
      <div class="field"><label>Title</label><input name="title" required></div>
      <div class="field"><label>Body HTML</label><textarea name="body_html" rows="8"></textarea></div>
      <button class="btn btn-primary" type="submit">Save translation</button>
    </div></form>`;
}

export function bindTranslationForm(route, toast) {
  document.getElementById('translationForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      await api('/translations', { method: 'POST', body: JSON.stringify(Object.fromEntries(fd.entries())) });
      toast('Translation saved');
      location.hash = '#/translations';
      route();
    } catch (err) {
      toast(err.message, 'error');
    }
  });
}

export async function viewSecurity() {
  const setup = await api('/auth/totp/setup', { method: 'POST' });
  return `
    <div class="page-head"><div><h1>Security — 2FA</h1><p>Authenticator app (TOTP). Scan URI in Google Authenticator / Authy.</p></div></div>
    <section class="panel"><div class="panel-body">
      <p><strong>Status:</strong> ${setup.enabled ? 'Enabled' : 'Not enabled'}</p>
      <p style="word-break:break-all;font-size:0.82rem;"><strong>Provisioning URI:</strong><br>${setup.provisioning_uri}</p>
      <p><strong>Secret (manual entry):</strong> <code class="kbd">${setup.secret}</code></p>
      <div class="field"><label>6-digit code to enable</label><input id="totpCode" maxlength="8" placeholder="123456"></div>
      <div class="hero-actions">
        <button class="btn btn-primary" type="button" id="enableTotp">Enable 2FA</button>
        <button class="btn btn-danger" type="button" id="disableTotp">Disable 2FA</button>
      </div>
    </div></section>`;
}

export function bindSecurity(toast) {
  document.getElementById('enableTotp')?.addEventListener('click', async () => {
    const code = document.getElementById('totpCode')?.value;
    try {
      await api('/auth/totp/enable', { method: 'POST', body: JSON.stringify({ code }) });
      toast('2FA enabled');
    } catch (err) {
      toast(err.message, 'error');
    }
  });
  document.getElementById('disableTotp')?.addEventListener('click', async () => {
    try {
      await api('/auth/totp/disable', { method: 'POST' });
      toast('2FA disabled');
    } catch (err) {
      toast(err.message, 'error');
    }
  });
}

