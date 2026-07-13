/**
 * Cloudflare Worker — static site + POST /api/v1/contact (Email Routing send_email).
 */

import { EmailMessage } from 'cloudflare:email';

const REGIONS = new Set(['USA', 'Canada', 'Australia', 'Europe', 'Other']);
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const URL_RE = /^https?:\/\//i;

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-store',
    },
  });
}

function validate(body) {
  const errors = [];
  if (body.honeypot) return errors;
  if (!body.name?.trim()) errors.push('Name is required.');
  if (!body.email?.trim() || !EMAIL_RE.test(body.email)) errors.push('Valid email required.');
  if (!body.website?.trim() || !URL_RE.test(body.website)) errors.push('Website must start with http:// or https://.');
  if (!REGIONS.has(body.region)) errors.push('Invalid market.');
  if ((body.goal?.trim() || '').length < 12) errors.push('Goal text too short.');
  return errors;
}

function base64Utf8(value) {
  const bytes = new TextEncoder().encode(value);
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary);
}

function encodeMimeWord(value) {
  if (/^[\x20-\x7E]*$/.test(value)) return value;
  return `=?UTF-8?B?${base64Utf8(value)}?=`;
}

function formatAddress(name, email) {
  if (!name) return email;
  const escaped = name.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
  if (/^[\x20-\x7E]*$/.test(name) && !/[<>",]/.test(name)) {
    return `"${escaped}" <${email}>`;
  }
  return `${encodeMimeWord(name)} <${email}>`;
}

function buildRawMime({ fromName, fromEmail, toName, toEmail, replyToName, replyToEmail, subject, text }) {
  return [
    `From: ${formatAddress(fromName, fromEmail)}`,
    `To: ${formatAddress(toName, toEmail)}`,
    `Reply-To: ${formatAddress(replyToName, replyToEmail)}`,
    `Subject: ${encodeMimeWord(subject)}`,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    '',
    text,
  ].join('\r\n');
}

async function sendMail(env, submission) {
  const notifyTo = env.CONTACT_NOTIFY_TO || 'md.faiz.ahmed62@gmail.com';
  const fromEmail = env.CONTACT_FROM_EMAIL || 'win@seowithfaiz.com';
  const fromName = env.CONTACT_FROM_NAME || 'SEO With Faiz';

  const text = [
    'New inquiry from seowithfaiz.com',
    '',
    `Name: ${submission.name}`,
    `Email: ${submission.email}`,
    `Website: ${submission.website}`,
    `Market: ${submission.region}`,
    '',
    submission.goal,
  ].join('\n');

  const subject = `New SEO inquiry — ${submission.name} (${submission.region})`;
  const raw = buildRawMime({
    fromName,
    fromEmail,
    toName: 'Faiz Ahmed',
    toEmail: notifyTo,
    replyToName: submission.name,
    replyToEmail: submission.email,
    subject,
    text,
  });

  const message = new EmailMessage(fromEmail, notifyTo, raw);
  await env.CONTACT_EMAIL.send(message);
}

// ── LinkedIn Conversions API (server-side lead conversion) ──
// Conversion "Website Lead — Strategy Call Request" (id 29401001). Fire-and-
// forget after a lead email sends; gated on the visitor's advertising consent
// (the banner sets swf_consent=...'m' when granted). Requires the account
// secret LINKEDIN_CONVERSIONS_TOKEN (rw_conversions scope); no-ops without it.
const LINKEDIN_CONVERSION_URN = 'urn:lla:llaPartnerConversion:29401001';

function readCookie(request, name) {
  const header = request.headers.get('Cookie') || '';
  const match = header.match(new RegExp('(?:^|;\\s*)' + name + '=([^;]*)'));
  return match ? decodeURIComponent(match[1]) : '';
}

async function sha256Hex(value) {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value));
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

async function sendLinkedInConversion(env, submission, request) {
  try {
    const token = env.LINKEDIN_CONVERSIONS_TOKEN;
    if (!token) return; // not configured yet — no-op

    // Only send when the visitor granted advertising consent.
    if (readCookie(request, 'swf_consent').indexOf('m') === -1) return;

    const emailHash = await sha256Hex(submission.email.trim().toLowerCase());
    const res = await fetch('https://api.linkedin.com/rest/conversionEvents', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer ' + token,
        'LinkedIn-Version': env.LINKEDIN_API_VERSION || '202505',
        'X-Restli-Protocol-Version': '2.0.0',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        conversion: LINKEDIN_CONVERSION_URN,
        conversionHappenedAt: Date.now(),
        eventId: crypto.randomUUID(),
        user: { userIds: [{ idType: 'SHA256_EMAIL', idValue: emailHash }] },
      }),
    });
    if (!res.ok) {
      console.error('LinkedIn CAPI non-2xx', res.status, await res.text());
    }
  } catch (err) {
    console.error('LinkedIn CAPI send failed', err);
  }
}

// ═══════════════════════════════════════════════════════════════
// CRM — leads (Cloudflare D1) + blog approvals + ad-tool signal fan-out.
// UI at /crm/ (static asset). Auth: CRM_ACCESS_KEY secret → HMAC session
// cookie. Every D1 route degrades to 503 "storage_pending" until the
// CRM_DB binding exists. Integrations (GA4 MP, LinkedIn CAPI, Meta CAPI)
// no-op until their secrets are configured — see /api/crm/integrations.
// ═══════════════════════════════════════════════════════════════

const CRM_COOKIE = 'swf_crm_s';
const CRM_STATUSES = ['new', 'contacted', 'replied', 'call', 'won', 'lost'];

async function crmSessionToken(env) {
  const key = await crypto.subtle.importKey(
    'raw', new TextEncoder().encode(env.CRM_ACCESS_KEY), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
  );
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode('swf-crm-session-v1'));
  return Array.from(new Uint8Array(sig)).map((b) => b.toString(16).padStart(2, '0')).join('');
}

async function crmAuthed(request, env) {
  if (!env.CRM_ACCESS_KEY) return false;
  const headerKey = request.headers.get('X-CRM-Key');
  if (headerKey && headerKey === env.CRM_ACCESS_KEY) return true; // scheduled roles
  const cookie = readCookie(request, CRM_COOKIE);
  if (!cookie) return false;
  return cookie === (await crmSessionToken(env));
}

// ── Signal fan-out: push CRM conversion data to ad/analytics tools ──
async function sendGa4Event(env, lead, eventName, params) {
  try {
    if (!env.GA4_API_SECRET || !lead.an_consent) return;
    const cid = (await sha256Hex('swf-cid-' + lead.email)).slice(0, 16) + '.' + (await sha256Hex('swf-cid2-' + lead.email)).slice(0, 10);
    await fetch(
      'https://www.google-analytics.com/mp/collect?measurement_id=' + (env.GA4_MEASUREMENT_ID || 'G-LQZ72RK5LM') + '&api_secret=' + env.GA4_API_SECRET,
      { method: 'POST', body: JSON.stringify({ client_id: cid, events: [{ name: eventName, params: Object.assign({ source: 'crm' }, params || {}) }] }) }
    );
  } catch (err) { console.error('GA4 MP send failed', err); }
}

async function sendMetaEvent(env, lead, eventName) {
  try {
    if (!env.META_PIXEL_ID || !env.META_CAPI_TOKEN || !lead.ad_consent) return;
    const res = await fetch('https://graph.facebook.com/v21.0/' + env.META_PIXEL_ID + '/events?access_token=' + env.META_CAPI_TOKEN, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data: [{
          event_name: eventName,
          event_time: Math.floor(Date.now() / 1000),
          action_source: 'system_generated',
          event_id: 'swf-' + lead.id + '-' + eventName,
          user_data: { em: [await sha256Hex(lead.email.trim().toLowerCase())] },
        }],
      }),
    });
    if (!res.ok) console.error('Meta CAPI non-2xx', res.status, await res.text());
  } catch (err) { console.error('Meta CAPI send failed', err); }
}

async function sendLinkedInCrmEvent(env, lead) {
  try {
    if (!env.LINKEDIN_CONVERSIONS_TOKEN || !lead.ad_consent) return;
    const res = await fetch('https://api.linkedin.com/rest/conversionEvents', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer ' + env.LINKEDIN_CONVERSIONS_TOKEN,
        'LinkedIn-Version': env.LINKEDIN_API_VERSION || '202505',
        'X-Restli-Protocol-Version': '2.0.0',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        conversion: LINKEDIN_CONVERSION_URN,
        conversionHappenedAt: Date.now(),
        eventId: 'swf-crm-' + lead.id + '-' + Date.now(),
        user: { userIds: [{ idType: 'SHA256_EMAIL', idValue: await sha256Hex(lead.email.trim().toLowerCase()) }] },
      }),
    });
    if (!res.ok) console.error('LinkedIn CAPI (CRM) non-2xx', res.status, await res.text());
  } catch (err) { console.error('LinkedIn CAPI (CRM) send failed', err); }
}

function crmSignalsForStatus(env, lead, status) {
  // Map pipeline milestones to tool events (consent-gated inside senders).
  const jobs = [];
  if (status === 'call') {
    jobs.push(sendGa4Event(env, lead, 'qualify_lead', {}));
    jobs.push(sendMetaEvent(env, lead, 'Schedule'));
    jobs.push(sendLinkedInCrmEvent(env, lead));
  } else if (status === 'won') {
    jobs.push(sendGa4Event(env, lead, 'close_won', {}));
    jobs.push(sendMetaEvent(env, lead, 'Purchase'));
    jobs.push(sendLinkedInCrmEvent(env, lead));
  }
  return Promise.all(jobs);
}

async function crmInsertLead(env, submission, request) {
  if (!env.CRM_DB) return null;
  const consent = readCookie(request, 'swf_consent');
  const adConsent = consent.indexOf('m') > -1 ? 1 : 0;
  const anConsent = consent.indexOf('a') > -1 ? 1 : 0;
  const res = await env.CRM_DB.prepare(
    'INSERT INTO leads (created_at, name, email, website, region, goal, status, ad_consent, an_consent, source) VALUES (?,?,?,?,?,?,?,?,?,?)'
  ).bind(new Date().toISOString(), submission.name, submission.email, submission.website, submission.region, submission.goal, 'new', adConsent, anConsent, 'contact_form').run();
  return { id: res.meta.last_row_id, email: submission.email, ad_consent: adConsent, an_consent: anConsent };
}

async function handleCrmApi(request, env, ctx, url) {
  const path = url.pathname.replace(/\/$/, '');
  const method = request.method;

  if (path === '/api/crm/login' && method === 'POST') {
    if (!env.CRM_ACCESS_KEY) return json({ error: 'CRM_ACCESS_KEY secret not configured yet' }, 503);
    let body;
    try { body = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }
    if ((body.key || '') !== env.CRM_ACCESS_KEY) return json({ error: 'Wrong access key' }, 401);
    const token = await crmSessionToken(env);
    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Set-Cookie': CRM_COOKIE + '=' + token + '; Max-Age=2592000; Path=/; HttpOnly; Secure; SameSite=Strict',
      },
    });
  }

  if (path === '/api/crm/logout' && method === 'POST') {
    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json', 'Set-Cookie': CRM_COOKIE + '=; Max-Age=0; Path=/; HttpOnly; Secure; SameSite=Strict' },
    });
  }

  const authed = await crmAuthed(request, env);
  if (path === '/api/crm/me') return json({ authed: authed, storage: !!env.CRM_DB });
  if (!authed) return json({ error: 'Unauthorized' }, 401);

  if (path === '/api/crm/integrations' && method === 'GET') {
    return json({
      storage_d1: !!env.CRM_DB,
      ga4_measurement_protocol: !!env.GA4_API_SECRET,
      linkedin_conversions_api: !!env.LINKEDIN_CONVERSIONS_TOKEN,
      meta_conversions_api: !!(env.META_PIXEL_ID && env.META_CAPI_TOKEN),
      email_notifications: true,
      notes: 'Missing items need secrets/bindings — see seo/crm-setup.md in the repo.',
    });
  }

  if (path === '/api/crm/leads' && method === 'GET') {
    if (!env.CRM_DB) return json({ error: 'storage_pending' }, 503);
    const rows = await env.CRM_DB.prepare('SELECT * FROM leads ORDER BY created_at DESC LIMIT 500').all();
    return json({ leads: rows.results });
  }

  if (path === '/api/crm/leads' && method === 'POST') {
    if (!env.CRM_DB) return json({ error: 'storage_pending' }, 503);
    let body;
    try { body = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }
    const id = parseInt(body.id, 10);
    if (!id) return json({ error: 'id required' }, 400);
    const existing = await env.CRM_DB.prepare('SELECT * FROM leads WHERE id = ?').bind(id).first();
    if (!existing) return json({ error: 'Lead not found' }, 404);
    if (body.status !== undefined) {
      if (CRM_STATUSES.indexOf(body.status) === -1) return json({ error: 'Invalid status' }, 400);
      await env.CRM_DB.prepare('UPDATE leads SET status = ? WHERE id = ?').bind(body.status, id).run();
      if (body.status !== existing.status && ctx) {
        ctx.waitUntil(crmSignalsForStatus(env, existing, body.status));
      }
    }
    if (body.notes !== undefined) {
      await env.CRM_DB.prepare('UPDATE leads SET notes = ? WHERE id = ?').bind(String(body.notes).slice(0, 4000), id).run();
    }
    if (body.manual_lead) {
      // Manually add an outbound prospect as a lead (e.g. a teardown reply).
    }
    return json({ ok: true });
  }

  if (path === '/api/crm/leads/add' && method === 'POST') {
    if (!env.CRM_DB) return json({ error: 'storage_pending' }, 503);
    let body;
    try { body = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }
    if (!body.name || !body.email) return json({ error: 'name and email required' }, 400);
    await env.CRM_DB.prepare(
      'INSERT INTO leads (created_at, name, email, website, region, goal, status, ad_consent, an_consent, source) VALUES (?,?,?,?,?,?,?,?,?,?)'
    ).bind(new Date().toISOString(), String(body.name).slice(0, 200), String(body.email).slice(0, 200), String(body.website || '').slice(0, 300), String(body.region || 'Other').slice(0, 40), String(body.goal || '').slice(0, 2000), 'new', 0, 0, String(body.source || 'manual').slice(0, 60)).run();
    return json({ ok: true });
  }

  if (path === '/api/crm/decisions' && method === 'GET') {
    if (!env.CRM_DB) return json({ error: 'storage_pending' }, 503);
    const onlyUnapplied = url.searchParams.get('unapplied') === '1';
    const rows = onlyUnapplied
      ? await env.CRM_DB.prepare('SELECT * FROM blog_decisions WHERE applied = 0 ORDER BY decided_at DESC').all()
      : await env.CRM_DB.prepare('SELECT * FROM blog_decisions ORDER BY decided_at DESC LIMIT 200').all();
    return json({ decisions: rows.results });
  }

  if (path === '/api/crm/decisions' && method === 'POST') {
    if (!env.CRM_DB) return json({ error: 'storage_pending' }, 503);
    let body;
    try { body = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }
    if (!body.slug) return json({ error: 'slug required' }, 400);
    if (body.applied === true) {
      await env.CRM_DB.prepare('UPDATE blog_decisions SET applied = 1 WHERE slug = ?').bind(body.slug).run();
      return json({ ok: true });
    }
    if (['approve', 'hold', 'reject'].indexOf(body.decision) === -1) return json({ error: 'decision must be approve|hold|reject' }, 400);
    await env.CRM_DB.prepare(
      'INSERT INTO blog_decisions (slug, decision, decided_at, applied) VALUES (?,?,?,0) ON CONFLICT(slug) DO UPDATE SET decision = excluded.decision, decided_at = excluded.decided_at, applied = 0'
    ).bind(String(body.slug).slice(0, 300), body.decision, new Date().toISOString()).run();
    return json({ ok: true });
  }

  return json({ error: 'Not found' }, 404);
}

async function handleContact(request, env, ctx) {
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  }

  if (request.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 });
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ detail: 'Invalid JSON' }, 400);
  }

  if (body.honeypot) {
    return json(
      { success: true, message: 'Thank you. Your inquiry was received.', emailDelivered: true },
      201
    );
  }

  const errors = validate(body);
  if (errors.length) {
    return json({ errors }, 400);
  }

  const submission = {
    name: body.name.trim(),
    email: body.email.trim(),
    website: body.website.trim(),
    region: body.region.trim(),
    goal: body.goal.trim(),
  };

  try {
    await sendMail(env, submission);
    if (ctx && typeof ctx.waitUntil === 'function') {
      ctx.waitUntil(sendLinkedInConversion(env, submission, request));
      // CRM capture + generate_lead signal (no-ops until CRM_DB is bound).
      ctx.waitUntil(
        crmInsertLead(env, submission, request)
          .then(function (lead) {
            if (lead) return sendGa4Event(env, lead, 'generate_lead', { method: 'contact_form' });
          })
          .catch(function (err) { console.error('CRM lead insert failed', err); })
      );
    }
    return json(
      {
        success: true,
        message: 'Thank you. Your inquiry was received.',
        emailDelivered: true,
      },
      201
    );
  } catch (err) {
    console.error('contact send failed', err);
    return json(
      {
        success: false,
        message: 'Could not deliver email. Please use win@seowithfaiz.com or WhatsApp.',
        emailDelivered: false,
      },
      503
    );
  }
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.hostname === 'www.seowithfaiz.com') {
      const target = new URL(url.pathname + url.search + url.hash, 'https://seowithfaiz.com');
      return Response.redirect(target.toString(), 301);
    }

    if (url.pathname === '/api/v1/contact') {
      return handleContact(request, env, ctx);
    }

    if (url.pathname.startsWith('/api/crm/')) {
      return handleCrmApi(request, env, ctx, url);
    }

    return env.ASSETS.fetch(request);
  },
};
