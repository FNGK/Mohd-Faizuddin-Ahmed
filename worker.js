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

    return env.ASSETS.fetch(request);
  },
};
