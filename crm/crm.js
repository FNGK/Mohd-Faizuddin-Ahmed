(function () {
  var API = '/api/crm';
  var $ = function (id) { return document.getElementById(id); };

  function msg(text) {
    var el = $('crmMsg');
    el.textContent = text;
    el.classList.add('show');
    setTimeout(function () { el.classList.remove('show'); }, 2200);
  }

  function req(path, opts) {
    opts = opts || {};
    opts.headers = Object.assign({ 'Content-Type': 'application/json' }, opts.headers || {});
    opts.credentials = 'same-origin';
    return fetch(API + path, opts).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (d) {
        return { ok: r.ok, status: r.status, data: d };
      });
    });
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  // ── Boot: check session ──
  req('/me').then(function (r) {
    if (r.data && r.data.authed) { showApp(); } else { showLogin(); }
  });

  function showLogin() {
    $('crmLogin').classList.remove('hidden');
    $('crmApp').classList.add('hidden');
  }

  function showApp() {
    $('crmLogin').classList.add('hidden');
    $('crmApp').classList.remove('hidden');
    loadLeads();
    loadBlogs();
    loadIntegrations();
  }

  $('crmLoginBtn').addEventListener('click', doLogin);
  $('crmKey').addEventListener('keydown', function (e) { if (e.key === 'Enter') doLogin(); });
  function doLogin() {
    $('crmLoginErr').textContent = '';
    req('/login', { method: 'POST', body: JSON.stringify({ key: $('crmKey').value }) }).then(function (r) {
      if (r.ok) { showApp(); } else { $('crmLoginErr').textContent = r.data.error || 'Login failed'; }
    });
  }

  $('crmLogout').addEventListener('click', function () {
    req('/logout', { method: 'POST' }).then(showLogin);
  });

  // ── Tabs ──
  document.querySelectorAll('.crm-tab').forEach(function (tab) {
    tab.addEventListener('click', function () {
      document.querySelectorAll('.crm-tab').forEach(function (t) { t.classList.remove('active'); });
      tab.classList.add('active');
      ['leads', 'blogs', 'integrations'].forEach(function (name) {
        $('tab-' + name).classList.toggle('hidden', name !== tab.dataset.tab);
      });
    });
  });

  // ── Leads ──
  var STATUSES = ['new', 'contacted', 'replied', 'call', 'won', 'lost'];

  function loadLeads() {
    req('/leads').then(function (r) {
      var box = $('leadsList');
      if (!r.ok) {
        box.innerHTML = '<div class="crm-card crm-empty">' +
          (r.status === 503
            ? 'Lead storage isn’t provisioned yet — create the D1 database (2-minute step in <code>seo/crm-setup.md</code>). New contact-form leads will start saving automatically once it exists.'
            : 'Could not load leads (' + esc(r.data.error || r.status) + ').') + '</div>';
        return;
      }
      var leads = r.data.leads || [];
      if (!leads.length) {
        box.innerHTML = '<div class="crm-card crm-empty">No leads yet. Contact-form inquiries land here automatically — and you can add outbound replies manually above.</div>';
        return;
      }
      box.innerHTML = leads.map(function (l) {
        return '<div class="crm-card crm-lead" data-id="' + l.id + '">' +
          '<div>' +
            '<h3>' + esc(l.name) + ' <span class="crm-status" data-s="' + esc(l.status) + '">' + esc(l.status) + '</span></h3>' +
            '<p><a href="mailto:' + esc(l.email) + '">' + esc(l.email) + '</a>' +
            (l.website ? ' · <a href="' + esc(l.website) + '" target="_blank" rel="noopener noreferrer">' + esc(l.website) + '</a>' : '') +
            ' · ' + esc(l.region || '') + ' · ' + esc((l.created_at || '').slice(0, 10)) + ' · ' + esc(l.source) + '</p>' +
            (l.goal ? '<p class="goal">' + esc(l.goal) + '</p>' : '') +
            '<textarea class="crm-notes" placeholder="Notes…">' + esc(l.notes || '') + '</textarea>' +
          '</div>' +
          '<div class="crm-controls">' +
            '<select class="lead-status">' + STATUSES.map(function (s) {
              return '<option value="' + s + '"' + (s === l.status ? ' selected' : '') + '>' + s + '</option>';
            }).join('') + '</select>' +
            '<button class="crm-btn crm-btn--primary lead-save" type="button">Save</button>' +
          '</div>' +
        '</div>';
      }).join('');

      box.querySelectorAll('.lead-save').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var card = btn.closest('.crm-lead');
          req('/leads', {
            method: 'POST',
            body: JSON.stringify({
              id: parseInt(card.dataset.id, 10),
              status: card.querySelector('.lead-status').value,
              notes: card.querySelector('.crm-notes').value,
            }),
          }).then(function (r2) {
            if (r2.ok) { msg('Lead updated — signals sent to configured tools'); loadLeads(); }
            else { msg('Update failed: ' + (r2.data.error || r2.status)); }
          });
        });
      });
    });
  }

  $('mlAdd').addEventListener('click', function () {
    req('/leads/add', {
      method: 'POST',
      body: JSON.stringify({ name: $('mlName').value, email: $('mlEmail').value, website: $('mlWebsite').value, source: 'outbound' }),
    }).then(function (r) {
      if (r.ok) { msg('Lead added'); $('mlName').value = ''; $('mlEmail').value = ''; $('mlWebsite').value = ''; loadLeads(); }
      else { msg('Add failed: ' + (r.data.error || r.status)); }
    });
  });

  // ── Blog approvals ──
  function loadBlogs() {
    Promise.all([
      fetch('/blog/drafts/manifest.json', { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : { drafts: [] }; }).catch(function () { return { drafts: [] }; }),
      req('/decisions'),
    ]).then(function (results) {
      var drafts = (results[0].drafts || []);
      var decisions = {};
      if (results[1].ok) {
        (results[1].data.decisions || []).forEach(function (d) { decisions[d.slug] = d; });
      }
      var box = $('blogsList');
      if (!drafts.length) {
        box.innerHTML = '<div class="crm-card crm-empty">No drafts in the manifest yet. It regenerates on every editorial run.</div>';
        return;
      }
      box.innerHTML = drafts.map(function (d) {
        var dec = decisions[d.slug];
        var decLabel = dec ? (dec.decision + (dec.applied ? ' · applied' : ' · pending editor run')) : '';
        return '<div class="crm-card crm-draft" data-slug="' + esc(d.slug) + '">' +
          '<h3>' + esc(d.title) + '</h3>' +
          '<p class="crm-note">' + esc(d.date || '') + ' · pipeline status: <strong>' + esc(d.review_status) + '</strong>' +
          (decLabel ? ' · your decision: <strong>' + esc(decLabel) + '</strong>' : '') + '</p>' +
          (d.meta_description ? '<p class="crm-note">' + esc(d.meta_description) + '</p>' : '') +
          '<div class="crm-draft-row">' +
            '<button class="crm-btn crm-btn--primary bd" data-d="approve" type="button">Approve → publish</button>' +
            '<button class="crm-btn bd" data-d="hold" type="button">Hold</button>' +
            '<button class="crm-btn crm-btn--danger bd" data-d="reject" type="button">Reject → revise</button>' +
          '</div>' +
        '</div>';
      }).join('');

      box.querySelectorAll('.bd').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var slug = btn.closest('.crm-draft').dataset.slug;
          req('/decisions', { method: 'POST', body: JSON.stringify({ slug: slug, decision: btn.dataset.d }) }).then(function (r) {
            if (r.ok) { msg('Decision saved — the editor applies it next run (Tue/Fri)'); loadBlogs(); }
            else { msg('Failed: ' + (r.data.error || r.status)); }
          });
        });
      });
    });
  }

  // ── Integrations ──
  function loadIntegrations() {
    req('/integrations').then(function (r) {
      var box = $('intList');
      if (!r.ok) { box.innerHTML = '<p class="crm-note">Could not load integration status.</p>'; return; }
      var labels = {
        storage_d1: 'Lead storage (Cloudflare D1)',
        ga4_measurement_protocol: 'Google Analytics 4 (Measurement Protocol)',
        linkedin_conversions_api: 'LinkedIn Conversions API',
        meta_conversions_api: 'Meta Conversions API (Meta ads option)',
        email_notifications: 'Email notifications (lead alerts)',
      };
      box.innerHTML = Object.keys(labels).map(function (k) {
        var on = !!r.data[k];
        return '<div class="crm-int"><span>' + esc(labels[k]) + '</span><span class="' + (on ? 'crm-pill-ok' : 'crm-pill-no') + '">' + (on ? '✅ connected' : '⏳ pending setup') + '</span></div>';
      }).join('');
    });
  }
})();
